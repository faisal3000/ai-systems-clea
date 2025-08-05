from __future__ import annotations

import logging
import math
import mimetypes
import os
import sqlite3
import uuid
from datetime import datetime
from io import BytesIO
from typing import Dict, List, Optional

import requests
import uvicorn
import redis.asyncio as aioredis
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter
from openai import OpenAI
from pydantic import BaseModel, EmailStr
from pypdf import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Local helpers (auth, vector store)
from .auth          import create_access_token, verify_password, get_password_hash, require_token
from .vector_store import VectorStore

# ───────────────────────── Setup ────────────────────────────
load_dotenv()
REDIS_URL     = os.getenv("REDIS_URL", "redis://localhost:6379/0")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NASA_API_KEY   = os.getenv("NASA_API_KEY")

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)
logger.info("🔑 Loaded OPENAI key: %s", bool(OPENAI_API_KEY))
logger.info("🔑 Loaded NASA key: %s", bool(NASA_API_KEY))

# ───────────────────────── FastAPI ──────────────────────────
app = FastAPI(title="AI Systems Engineering Agent", version="0.2.1")

@app.on_event("startup")
async def startup_rate_limiter() -> None:
    redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://your-production-frontend.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("reports", exist_ok=True)
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

client = OpenAI(api_key=OPENAI_API_KEY)

# ─────────────────────── Database (SQLite) ─────────────────────
SQLITE_DB = "systems_engineering.db"
TABLES: Dict[str, str] = {
    "knowledge": """
        CREATE TABLE IF NOT EXISTS knowledge (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT,
          category TEXT,
          source TEXT,
          summary TEXT,
          key_topics TEXT
        );
    """,
    "ai_recommendations": """
        CREATE TABLE IF NOT EXISTS ai_recommendations (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          query TEXT NOT NULL,
          recommendation TEXT NOT NULL,
          confidence_score FLOAT DEFAULT 0.95,
          source TEXT,
          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """,
    "users": """
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          email TEXT UNIQUE NOT NULL,
          hashed_password TEXT NOT NULL,
          is_approved BOOLEAN DEFAULT 0,
          confirmation_token TEXT,
          is_confirmed BOOLEAN DEFAULT 0
        );
    """,
    "kb_files": """
        CREATE TABLE IF NOT EXISTS kb_files (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          filename TEXT,
          chunks INTEGER,
          uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """,
}

def get_sqlite_connection() -> sqlite3.Connection:
    return sqlite3.connect(SQLITE_DB, check_same_thread=False)

def setup_database() -> None:
    with get_sqlite_connection() as conn:
        for ddl in TABLES.values():
            conn.execute(ddl)
        conn.commit()

setup_database()

# ───────────────────── FAISS Vector Store ─────────────────────
vector_store = VectorStore()

def _populate_vector_store() -> None:
    with get_sqlite_connection() as conn:
        for (summary,) in conn.execute("SELECT summary FROM knowledge"):
            if summary:
                vector_store.add_text(summary)
    # use ntotal or ids length instead of len()
    logger.info("Vector store pre-loaded with %d summaries", vector_store.index.ntotal)

_populate_vector_store()

# ───────────────────────── Models ──────────────────────────
class ConsultRequest(BaseModel):
    user_question: str
    industry: str
    role: str = "general"

class DeepDiveRequest(BaseModel):
    company_name: str
    system_type: str
    uploaded_doc_ids: List[str]
    objectives: str
    constraints: Optional[Dict[str, str]] = None

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class ApproveRequest(BaseModel):
    user_id: int
    approve: bool

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# ───────────────────────── Helpers ─────────────────────────
def fetch_nasa_data(q: str) -> str:
    if not NASA_API_KEY:
        return "🔑 NASA_API_KEY missing."
    url = f"https://api.nasa.gov/techport/api/projects?search={q}&api_key={NASA_API_KEY}"
    try:
        projects = requests.get(url, timeout=30).json().get("projects", [])
        return projects[0].get("title", "No NASA data found.") if projects else "No NASA data."
    except Exception as exc:
        logger.error("NASA API error: %s", exc)
        return "NASA API request failed."

def search_knowledge(q: str) -> Optional[str]:
    with get_sqlite_connection() as conn:
        row = conn.execute(
            "SELECT summary FROM knowledge WHERE key_topics LIKE ?",
            (f"%{q}%",)
        ).fetchone()
        return row[0] if row else None

MAX_TOKENS = 800

def approx_tokens(n_words: int) -> int:
    return math.ceil(n_words * 0.75)

def _token_chunks(text: str, max_tokens: int = MAX_TOKENS) -> List[str]:
    words, chunk, chunks = text.split(), [], []
    for w in words:
        if approx_tokens(len(chunk) + 1) > max_tokens:
            chunks.append(" ".join(chunk)); chunk = []
        chunk.append(w)
    if chunk:
        chunks.append(" ".join(chunk))
    return chunks

def _extract_text(raw: bytes, fname: str) -> str:
    mime, _ = mimetypes.guess_type(fname)
    if mime == "application/pdf":
        return "\n".join((p.extract_text() or "") for p in PdfReader(BytesIO(raw)).pages)
    return raw.decode("utf-8", errors="ignore")

# ──────────────────── GPT-4 Consultant ────────────────────
def ask_expert_system(question: str, industry: str, role: str) -> str:
    kb_match = search_knowledge(question) or "None"
    nasa = fetch_nasa_data(question)
    mem_ctx = "\n".join(f"- {m}" for m in vector_store.search(question, 3)) or "None"
    system_prompt = (
        f"You are a senior systems engineering consultant specialized in {role}.\n"
        "Provide a structured answer (Introduction, Analysis, Recommendations, …)."
    )
    user_prompt = (
        f"Industry: {industry}\nQuestion: {question}\nContext:\n"
        f"- Knowledge Base: {kb_match}\n- Related Memories:\n{mem_ctx}\n"
        f"- NASA Research: {nasa}\n"
    )
    resp = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": system_prompt + "\n\n" + user_prompt}],
        timeout=60,
    )
    return resp.choices[0].message.content

# ───────────────────────── PDF Report ──────────────────────────
def generate_pdf_report(title: str, answer: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"reports/AI_Report_{ts}.pdf"
    c = canvas.Canvas(fname, pagesize=letter)
    w, h = letter
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(w/2, h-80, "AI Systems Engineering Report")
    c.setFont("Helvetica", 12)
    c.drawCentredString(w/2, h-110, f"Generated {datetime.now():%B %d, %Y}")
    y = h-150
    for ln in answer.split("\n"):
        if y < 100:
            c.showPage(); y = h-50
        c.drawString(50, y, ln[:95]); y -= 14
    c.save()
    return os.path.basename(fname)

# ───────────────────────── Public Routes ──────────────────────────
@app.get("/memory_search")
def memory_search(q: str = Query(..., min_length=3), k: int = Query(3, ge=1, le=10)):
    return {"query": q, "top_k": k, "results": vector_store.search(q, k)}

# Agent demo
tool_registry = {
    "search_nasa": fetch_nasa_data,
    "query_memory": lambda q: "\n".join(vector_store.search(q, 3)) or "No similar memories."
}

@app.post("/agent_decide")
def agent_decide(
    query: str = Query(...),
    tool: str  = Query(..., regex="search_nasa|query_memory")
):
    fn = tool_registry.get(tool)
    if not fn:
        raise HTTPException(400, "Tool not available.")
    return {"tool": tool, "input": query, "result": fn(query)}

# ───────────────────────── Auth Endpoints ──────────────────────────
@app.post("/register")
def register_user(req: RegisterRequest):
    token = str(uuid.uuid4())
    with get_sqlite_connection() as conn:
        try:
            conn.execute(
                "INSERT INTO users (email,hashed_password,is_approved,confirmation_token,is_confirmed) VALUES (?,?,?,?,0)",
                (req.email.lower(), get_password_hash(req.password), 0, token),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(400, "Email already registered.")
    logger.info("Email confirmation link: /confirm_email?token=%s", token)
    return {"message": "Registered. Check server log for confirmation link."}

@app.get("/confirm_email")
def confirm_email(token: str = Query(...)):
    with get_sqlite_connection() as conn:
        row = conn.execute(
            "SELECT id FROM users WHERE confirmation_token=? AND is_confirmed=0",
            (token,),
        ).fetchone()
        if not row:
            raise HTTPException(404, "Invalid or used token.")
        conn.execute(
            "UPDATE users SET is_confirmed=1, confirmation_token=NULL WHERE id=?",
            (row[0],),
        )
        conn.commit()
    return {"message": f"Email confirmed for user {row[0]}. Awaiting admin approval."}

@app.post("/approve_user")
def approve_user(req: ApproveRequest, payload=Depends(require_token)):
    with get_sqlite_connection() as conn:
        cur = conn.execute("UPDATE users SET is_approved=? WHERE id=?",
                           (1 if req.approve else 0, req.user_id))
        if cur.rowcount == 0:
            raise HTTPException(404, "User not found.")
        conn.commit()
    return {"message": f"User {req.user_id} {'approved' if req.approve else 'unapproved'}."}

@app.get("/list_pending_users")
def list_pending_users(payload=Depends(require_token)):
    with get_sqlite_connection() as conn:
        rows = conn.execute("SELECT id,email FROM users WHERE is_approved=0").fetchall()
    return [{"id": r[0], "email": r[1]} for r in rows]

@app.post("/login")
def login(req: LoginRequest):
    with get_sqlite_connection() as conn:
        row = conn.execute(
            "SELECT id,hashed_password,is_approved,is_confirmed FROM users WHERE email=?",
            (req.email.lower(),),
        ).fetchone()
        if not row or not verify_password(req.password, row[1]):
            raise HTTPException(401, "Invalid credentials.")
        if not (row[2] and row[3]):
            raise HTTPException(403, "Account not confirmed or approved.")
    return {"access_token": create_access_token({"sub": str(row[0])})}

# ─────────────────── Protected AI/LLM Routes ───────────────────
uploaded_specs: Dict[str, str] = {}

@app.post("/consult")
def consult(req: ConsultRequest, payload=Depends(require_token)):
    answer = ask_expert_system(req.user_question, req.industry, req.role)
    return {"answer": answer, "report": generate_pdf_report(req.user_question, answer)}

@app.get("/list_uploaded_docs")
def list_uploaded_docs(payload=Depends(require_token)):
    return list(uploaded_specs.keys())

@app.post("/upload_specs")
async def upload_specs(file: UploadFile = File(...), payload=Depends(require_token)):
    text = (await file.read()).decode("utf-8", errors="ignore")
    uploaded_specs[file.filename] = text
    vector_store.add_text(text)
    return {"filename": file.filename, "status": "Uploaded", "length": len(text)}

@app.post("/deep_dive")
async def deep_dive(req: DeepDiveRequest, payload=Depends(require_token)):
    specs = "\n".join(uploaded_specs.get(doc_id, "") for doc_id in req.uploaded_doc_ids).strip()
    if not specs:
        raise HTTPException(404, "Specs not found.")
    prompt = (
        f"Company: {req.company_name}\nSystem Type: {req.system_type}\n"
        f"Objectives: {req.objectives}\nConstraints: {req.constraints}\n\n"
        f"Specs Provided:\n{specs[:4000]}..."
    )
    resp = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a systems engineering consultant."},
            {"role": "user", "content": prompt},
        ],
        timeout=120,
    )
    answer = resp.choices[0].message.content
    return {"answer": answer, "report": generate_pdf_report(req.objectives, answer), "summary": answer[:250] + "…"}

@app.post("/upload_knowledge_base")
async def upload_kb(file: UploadFile = File(...), payload=Depends(require_token)):
    raw = await file.read()
    text = _extract_text(raw, file.filename)
    if not text.strip():
        raise HTTPException(400, "Unable to extract text.")
    chunks = _token_chunks(text)
    for ch in chunks:
        vector_store.add_text(ch)
    doc_id = str(uuid.uuid4())
    uploaded_specs[doc_id] = text
    with get_sqlite_connection() as conn:
        conn.execute("INSERT INTO kb_files (filename,chunks) VALUES (?,?)",
                     (file.filename, len(chunks)))
        conn.commit()
    return {"status": "indexed", "doc_id": doc_id, "filename": file.filename, "chunks": len(chunks)}

@app.get("/")
def root():
    return {"message": "🚀 AI Systems Engineering Agent is running!"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
