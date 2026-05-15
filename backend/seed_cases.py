"""
Seed 12 synthetic cases for Sprint 2 / Sprint 3 similarity testing.
Run: python seed_cases.py
"""
import uuid
import random
import sys
import os
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.case import Case, CaseStatus, Severity, Shift
from app.models.user import User

CASES_DATA = [
    {
        "model": "IJP-A1", "process": "Printing", "line": "Line-IJP-01",
        "fatal_error": "Nozzle Clog", "symptom": "Head unit tidak mengeluarkan tinta pada nozzle #3-7, hasil cetak bergaris.",
        "description": "Nozzle clog parah setelah ganti tinta batch baru",
        "severity": Severity.HIGH, "shift": Shift.PAGI,
    },
    {
        "model": "IJP-A1", "process": "Printing", "line": "Line-IJP-01",
        "fatal_error": "Nozzle Clog", "symptom": "Nozzle #1-4 tersumbat, warna cyan tidak keluar.",
        "description": "Nozzle clog berulang pada model yang sama",
        "severity": Severity.MEDIUM, "shift": Shift.SIANG,
    },
    {
        "model": "IJP-A2", "process": "Printing", "line": "Line-IJP-02",
        "fatal_error": "Head Misalignment", "symptom": "Teks bergeser 0.2mm dari baseline, barcode tidak terbaca scanner.",
        "description": "Head alignment drift setelah maintenance rutin",
        "severity": Severity.HIGH, "shift": Shift.MALAM,
    },
    {
        "model": "SIDM-C1", "process": "Assembly", "line": "Line-SIDM-01",
        "fatal_error": "Motor Fault", "symptom": "Motor feed mengalami overload error code E-F04, conveyor berhenti otomatis.",
        "description": "Motor fault pada feed unit SIDM-C1",
        "severity": Severity.CRITICAL, "shift": Shift.PAGI,
    },
    {
        "model": "SIDM-C1", "process": "Assembly", "line": "Line-SIDM-01",
        "fatal_error": "Encoder Error", "symptom": "Sinyal encoder hilang intermiten, posisi tidak akurat.",
        "description": "Encoder signal loss pada SIDM assembly line",
        "severity": Severity.MEDIUM, "shift": Shift.SIANG,
    },
    {
        "model": "IJP-B1", "process": "Inspection", "line": "Line-IJP-02",
        "fatal_error": "Color Deviation", "symptom": "Delta E > 5 pada warna magenta, produk tidak lolos QC visual.",
        "description": "Deviasi warna melebihi toleransi pada batch pagi",
        "severity": Severity.MEDIUM, "shift": Shift.PAGI,
    },
    {
        "model": "SIDM-D1", "process": "Testing", "line": "Line-SIDM-02",
        "fatal_error": "Software Timeout", "symptom": "Test sequence timeout pada step 7, unit tidak merespons perintah reset.",
        "description": "Software timeout berulang di unit SIDM-D1",
        "severity": Severity.LOW, "shift": Shift.MALAM,
    },
    {
        "model": "IJP-A1", "process": "Curing", "line": "Line-IJP-01",
        "fatal_error": "Temperature Overshoot", "symptom": "Suhu curing mencapai 185°C (setpoint 175°C), sensor alarm aktif.",
        "description": "Temperature overshoot di zona curing IJP-A1",
        "severity": Severity.HIGH, "shift": Shift.PAGI,
    },
    {
        "model": "COMMON-X1", "process": "Packaging", "line": "Line-COMMON-01",
        "fatal_error": "Feed Jam", "symptom": "Material tersangkut di feeder unit, aliran terhenti tiap ~500 lembar.",
        "description": "Feed jam periodik di packaging line",
        "severity": Severity.MEDIUM, "shift": Shift.SIANG,
    },
    {
        "model": "IJP-B2", "process": "Laminating", "line": "Line-IJP-02",
        "fatal_error": "Vacuum Loss", "symptom": "Tekanan vakum turun ke 0.3 bar (normal 0.7 bar), film tidak menempel rata.",
        "description": "Vacuum pump degradasi pada laminator IJP-B2",
        "severity": Severity.HIGH, "shift": Shift.MALAM,
    },
    {
        "model": "SIDM-C2", "process": "Assembly", "line": "Line-SIDM-01",
        "fatal_error": "Sensor Failure", "symptom": "Sensor optik tidak mendeteksi produk pada jalur conveyor, false negative terus menerus.",
        "description": "Optical sensor kotor / rusak di SIDM-C2",
        "severity": Severity.MEDIUM, "shift": Shift.PAGI,
    },
    {
        "model": "IJP-A2", "process": "Die-cutting", "line": "Line-IJP-02",
        "fatal_error": "Registration Error", "symptom": "Posisi cutting meleset 1.2mm dari mark, reject rate naik ke 8%.",
        "description": "Registration error setelah penggantian blade",
        "severity": Severity.HIGH, "shift": Shift.SIANG,
    },
]


def seed_cases():
    db = SessionLocal()
    try:
        junior = db.query(User).filter(User.employee_id == "EMP001").first()
        senior = db.query(User).filter(User.employee_id == "EMP002").first()

        if not junior or not senior:
            print("Run seed.py first to create users.")
            return

        from datetime import date
        base_date = datetime.now(timezone.utc) - timedelta(days=7)

        for i, data in enumerate(CASES_DATA):
            offset_hours = random.randint(0, 7 * 24)
            created_at = base_date + timedelta(hours=offset_hours)
            today_str = created_at.strftime("%Y%m%d")
            case_display_id = f"IEI-{today_str}-{(i + 1):04d}"

            if db.query(Case).filter(Case.case_id == case_display_id).first():
                print(f"  Skipping {case_display_id} — already exists")
                continue

            status = random.choice([
                CaseStatus.OPEN, CaseStatus.INVESTIGATING,
                CaseStatus.INVESTIGATING, CaseStatus.RESOLVED,
            ])

            case = Case(
                id=str(uuid.uuid4()),
                case_id=case_display_id,
                title=f"{data['model']} — {data['fatal_error']}",
                description=data["description"],
                model=data["model"],
                process=data["process"],
                line=data["line"],
                fatal_error=data["fatal_error"],
                symptom=data["symptom"],
                status=status,
                severity=data["severity"],
                shift=data["shift"],
                reporter_id=junior.id,
                assigned_to_id=senior.id,
                created_at=created_at,
                updated_at=created_at,
            )
            db.add(case)
            print(f"  Created {case_display_id}: {data['model']} / {data['fatal_error']} [{status}]")

        db.commit()
        print(f"Seed cases selesai ({len(CASES_DATA)} kasus).")
    finally:
        db.close()


if __name__ == "__main__":
    seed_cases()
