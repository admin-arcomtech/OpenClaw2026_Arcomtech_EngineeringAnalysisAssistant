"""
Development seed script — creates 4 users (1 per role).
Run: python seed.py
"""
import uuid
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole

SEED_USERS = [
    {"employee_id": "EMP001", "full_name": "Budi Santoso (Junior)", "role": UserRole.JUNIOR, "password": "Junior@12345"},
    {"employee_id": "EMP002", "full_name": "Siti Rahayu (Senior)", "role": UserRole.SENIOR, "password": "Senior@12345"},
    {"employee_id": "EMP003", "full_name": "Ahmad Fauzi (Manager)", "role": UserRole.MANAGER, "password": "Manager@12345"},
    {"employee_id": "EMP004", "full_name": "Dewi Admin (Admin)", "role": UserRole.ADMIN, "password": "Admin@12345"},
]


def seed():
    db = SessionLocal()
    try:
        for u in SEED_USERS:
            existing = db.query(User).filter(User.employee_id == u["employee_id"]).first()
            if existing:
                print(f"  Skipping {u['employee_id']} — already exists")
                continue
            user = User(
                id=str(uuid.uuid4()),
                employee_id=u["employee_id"],
                full_name=u["full_name"],
                role=u["role"],
                hashed_password=hash_password(u["password"]),
                is_active=True,
            )
            db.add(user)
            print(f"  Created {u['employee_id']} ({u['role'].value})")
        db.commit()
        print("Seed selesai.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
