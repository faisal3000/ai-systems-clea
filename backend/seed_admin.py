# backend/seed_admin.py

import os
from pathlib import Path
from sqlmodel import create_engine, Session, select
from app.auth import User, hash_password, DB_PATH

def main():
    # 1. DB_PATH comes from app/auth.py and points to your root users.db
    engine = create_engine(
        f"sqlite:///{DB_PATH}",
        connect_args={"check_same_thread": False},
    )

    with Session(engine) as session:
        # 2. Only add if it doesn’t already exist
        existing = session.exec(
            select(User).where(User.email == "admin@example.com")
        ).first()

        if existing:
            print("ℹ️  Admin already exists:", existing.email)
            return

        # 3. Otherwise create it
        admin = User(
            email="admin@example.com",
            password=hash_password("AdminPass123"),
            is_active=True,
            is_admin=True,
        )
        session.add(admin)
        session.commit()
        print("✅ Admin created: admin@example.com / AdminPass123")

if __name__ == "__main__":
    main()
