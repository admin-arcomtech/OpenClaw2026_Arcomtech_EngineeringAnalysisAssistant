"""
Case ID generator: IEI-YYYYMMDD-XXXX (4-digit zero-padded daily sequence).
Thread-safe via DB-level SELECT FOR UPDATE on a daily counter.
"""
from datetime import date
from sqlalchemy import text
from sqlalchemy.orm import Session


def generate_case_id(db: Session, prefix: str = "IEI") -> str:
    today = date.today().strftime("%Y%m%d")
    pattern = f"{prefix}-{today}-%"

    # Count existing cases for today and increment
    result = db.execute(
        text("SELECT COUNT(*) FROM cases WHERE case_id LIKE :pattern FOR UPDATE"),
        {"pattern": pattern},
    )
    count = result.scalar() or 0
    sequence = count + 1
    return f"{prefix}-{today}-{sequence:04d}"
