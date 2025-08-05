import os
import json
import uuid
from typing import List, Dict, Any, Optional

import numpy as np
import faiss
from openai import OpenAI

# ————— Configuration —————
EMBEDDING_MODEL = "text-embedding-ada-002"
INDEX_PATH       = "vector_store.index"
META_PATH        = "vector_store_meta.json"


class VectorStore:
    """
    A FAISS-backed vector store with on-disk persistence.
    - add_text / add_texts
    - search → returns id, text, metadata, score
    - delete / clear
    - len(vector_store) → number of entries
    """

    def __init__(
        self,
        client: Optional[OpenAI] = None,
        embedding_model: str = EMBEDDING_MODEL,
        index_path: str = INDEX_PATH,
        meta_path:  str = META_PATH,
    ):
        # OpenAI client
        self.client = client or OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model  = embedding_model

        # FAISS index: inner-product on normalized vectors → cosine similarity
        self.dim   = self._fetch_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dim)

        # persistence paths
        self.index_path = index_path
        self.meta_path  = meta_path

        # in-RAM metadata: parallel lists of IDs and their text+metadata
        self.ids: List[str] = []
        self.meta: Dict[str, Dict[str, Any]] = {}

        # try loading existing index + metadata
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self._load()

    def _fetch_embedding_dimension(self) -> int:
        """Probe the model on a dummy input to get dimensionality."""
        resp = self.client.embeddings.create(
            model=self.model,
            input="test"
        )
        return len(resp.data[0].embedding)

    def _embed(self, texts: List[str]) -> np.ndarray:
        """Batch-embed via OpenAI and return a (N×dim) float32 normalized array."""
        resp = self.client.embeddings.create(model=self.model, input=texts)
        arr = np.array([e.embedding for e in resp.data], dtype=np.float32)
        # normalize rows for cosine-sim
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        return arr / (norms + 1e-12)

    def add_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        persist: bool = True,
    ) -> str:
        """
        Embed `text`, add to FAISS, record metadata.
        Returns the generated UUID.
        """
        emb = self._embed([text])[0]              # shape (dim,)
        self.index.add(emb.reshape(1, -1))        # add to FAISS

        entry_id = str(uuid.uuid4())
        self.ids.append(entry_id)
        self.meta[entry_id] = {
            "text": text,
            "metadata": metadata or {},
        }

        if persist:
            self._save()
        return entry_id

    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        persist: bool = True,
    ) -> List[str]:
        """
        Batch-add multiple texts. Returns list of UUIDs.
        """
        embs = self._embed(texts)  # shape (N,dim)
        self.index.add(embs)

        ids: List[str] = []
        for i, txt in enumerate(texts):
            eid = str(uuid.uuid4())
            ids.append(eid)
            self.ids.append(eid)
            self.meta[eid] = {
                "text": txt,
                "metadata": (metadatas[i] if metadatas else {}),
            }

        if persist:
            self._save()
        return ids

    def search(
        self,
        query: str,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Embed `query`, search top-k similar texts,
        return list of { id, text, metadata, score }.
        """
        if self.index.ntotal == 0:
            return []

        q_emb = self._embed([query])               # (1,dim)
        scores, idxs = self.index.search(q_emb, k) # both (1,k)
        results: List[Dict[str, Any]] = []
        for score, idx in zip(scores[0], idxs[0]):
            if idx < 0 or idx >= len(self.ids):
                continue
            eid = self.ids[idx]
            entry = self.meta[eid]
            results.append({
                "id": eid,
                "text": entry["text"],
                "metadata": entry["metadata"],
                "score": float(score),
            })
        return results

    def delete(self, entry_id: str, persist: bool = True) -> bool:
        """
        Remove a single entry by its ID by rebuilding the index.
        Returns True if deleted.
        """
        if entry_id not in self.ids:
            return False

        # build new list without that entry
        keep = [(i, eid) for i, eid in enumerate(self.ids) if eid != entry_id]
        new_embs: List[np.ndarray] = []
        new_ids: List[str] = []
        for _, eid in keep:
            vec = self.index.reconstruct(self.ids.index(eid))
            new_embs.append(vec)
            new_ids.append(eid)

        # rebuild index
        self.index.reset()
        self.index.add(np.vstack(new_embs))
        self.ids = new_ids
        self.meta.pop(entry_id, None)

        if persist:
            self._save()
        return True

    def clear(self, persist: bool = True) -> None:
        """Remove all entries."""
        self.index.reset()
        self.ids.clear()
        self.meta.clear()
        if persist:
            self._save()

    def __len__(self) -> int:
        """
        Return the total number of stored entries.
        """
        return self.index.ntotal

    def _save(self) -> None:
        """Persist FAISS index + metadata to disk."""
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump({"ids": self.ids, "meta": self.meta}, f, ensure_ascii=False, indent=2)

    def _load(self) -> None:
        """Load FAISS index + metadata from disk."""
        self.index = faiss.read_index(self.index_path)
        with open(self.meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.ids  = data["ids"]
            self.meta = data["meta"]


# — Example usage —
if __name__ == "__main__":
    store = VectorStore()
    tid = store.add_text("Test entry", {"source": "example"})
    print(f"Added {tid}, total entries:", len(store))
    print("Search for 'test':", store.search("test", k=1))
