# backend/app/routers/admin.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.orm import Session

from app.auth import get_db, User

admin_router = APIRouter(prefix="/admin", tags=["admin"])

@admin_router.get("/users/pending")
def list_pending_users(db: Session = Depends(get_db)):
    return db.exec(select(User).where(User.is_active == False)).all()

@admin_router.post("/approve/{user_id}")
def approve_user(user_id: int, db: Session = Depends(get_db)):
    user = db.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = True
    db.add(user)
    db.commit()
    return {"msg": f"User {user.email} approved"}
