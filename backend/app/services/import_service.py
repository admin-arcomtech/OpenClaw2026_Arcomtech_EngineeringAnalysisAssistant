"""Historical data batch import — CSV (Excel via openpyxl optional)."""
import csv
import io
import logging
import uuid
from datetime import datetime, timezone
from typing import BinaryIO

from sqlalchemy.orm import Session

from app.models.case import Case, CaseStatus, Severity
from app.models.import_job import ImportJob
from app.services.case_id import generate_case_id
from app.services.embedding_service import embed_case

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {"model", "fatal_error", "symptom", "root_cause"}
OPTIONAL_COLUMNS = {"process", "line", "title", "severity", "temporary_action"}


def _parse_csv(content: bytes) -> list[dict]:
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    return [dict(row) for row in reader]


def run_import(
    db: Session,
    content: bytes,
    filename: str,
    user_id: str,
    dry_run: bool = False,
) -> ImportJob:
    job = ImportJob(
        id=str(uuid.uuid4()),
        filename=filename,
        status="RUNNING",
        dry_run=dry_run,
        created_by_id=user_id,
    )
    db.add(job)
    db.flush()

    errors: list[dict] = []
    imported = 0
    skipped = 0

    try:
        rows = _parse_csv(content)
    except Exception as exc:
        job.status = "FAILED"
        job.error_rows = [{"row": 0, "error": str(exc)}]
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
        return job

    job.total_rows = len(rows)

    for idx, row in enumerate(rows, start=2):
        normalized = {k.strip().lower(): (v or "").strip() for k, v in row.items()}
        missing = REQUIRED_COLUMNS - set(normalized.keys())
        if missing:
            errors.append({"row": idx, "error": f"Kolom wajib hilang: {missing}"})
            skipped += 1
            continue
        if len(normalized.get("symptom", "")) < 5:
            errors.append({"row": idx, "error": "Symptom terlalu pendek — flag review manual"})
            skipped += 1
            continue

        if dry_run:
            imported += 1
            continue

        case_display_id = generate_case_id(db)
        title = normalized.get("title") or f"{normalized['model']} — {normalized['fatal_error']}"
        case = Case(
            id=str(uuid.uuid4()),
            case_id=case_display_id,
            title=title[:500],
            model=normalized["model"],
            process=normalized.get("process"),
            line=normalized.get("line"),
            fatal_error=normalized["fatal_error"],
            symptom=normalized["symptom"],
            description=normalized.get("root_cause"),
            confirmed_root_cause=normalized["root_cause"],
            temporary_action=normalized.get("temporary_action"),
            status=CaseStatus.ARCHIVED,
            severity=Severity.MEDIUM,
            reporter_id=user_id,
            assigned_to_id=user_id,
            why_why_eligible="true",
            confirmed_at=datetime.now(timezone.utc),
            archived_at=datetime.now(timezone.utc),
        )
        db.add(case)
        db.flush()
        try:
            embed_case(case.id)
        except Exception:
            pass
        imported += 1

    job.imported_rows = imported
    job.skipped_rows = skipped
    job.error_rows = errors[:100]
    job.status = "COMPLETED" if not errors else "COMPLETED_WITH_ERRORS"
    job.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(job)
    return job
