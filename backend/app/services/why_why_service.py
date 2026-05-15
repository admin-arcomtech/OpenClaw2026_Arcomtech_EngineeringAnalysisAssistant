"""
Why-Why draft generation (F-006) with AI + deterministic fallback.
"""
import json
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai import get_provider
from app.ai.prompts.why_why import WHY_WHY_SCHEMA, WHY_WHY_SYSTEM_V1
from app.models.case import Case
from app.models.trial import Trial
from app.models.why_why import WhyWhy, WhyWhyStatus

logger = logging.getLogger(__name__)

CATEGORIES = ["Machine", "Material", "Method", "Man", "Machine"]


def _fallback_draft(case: Case, trials: list[Trial]) -> dict:
    root = case.confirmed_root_cause or case.fatal_error or "abnormalitas produksi"
    symptom = case.symptom or case.description or "gejala tidak normal"
    steps = []
    questions = [
        f"Mengapa terjadi {symptom[:80]}?",
        f"Mengapa {root[:60]} terjadi?",
        "Mengapa kondisi tersebut tidak terdeteksi lebih awal?",
        "Mengapa sistem kontrol tidak mencegah masalah?",
        "Mengapa prosedur pencegahan tidak efektif?",
    ]
    answers = [
        f"Karena {case.fatal_error or 'parameter proses'} di luar toleransi pada {case.process or 'proses'}",
        f"Karena {root}",
        "Karena monitoring SPC tidak menunjukkan drift signifikan",
        "Karena setting mesin belum dikalibrasi setelah perubahan material",
        f"Akar penyebab sistemik: kurangnya standardisasi prosedur di line {case.line or 'produksi'}",
    ]
    for i in range(5):
        steps.append({
            "level": i + 1,
            "question": questions[i],
            "answer": answers[i],
            "category_4m1e": CATEGORIES[i],
        })
    trial_note = ""
    if trials:
        trial_note = f" Berdasarkan {len(trials)} trial yang dilog."
    return {
        "why_steps": steps,
        "immediate_countermeasure": case.temporary_action or f"Stop line dan isolasi unit terdampak.{trial_note}",
        "corrective_action": f"Perbaiki {root} dan verifikasi dengan trial ulang",
        "preventive_action": f"Update SOP {case.process or 'proses'} dan training operator shift",
        "partial": False,
        "source": "fallback",
    }


def generate_draft(db: Session, case: Case, notes: str | None = None) -> tuple[WhyWhy, dict, str]:
    if case.why_why_eligible != "true" or not case.confirmed_root_cause:
        raise ValueError("Why-Why dapat dibuat hanya setelah root cause dikonfirmasi.")

    trials = db.query(Trial).filter(Trial.case_id == case.id).order_by(Trial.sequence).all()
    trial_payload = [
        {"action": t.trial_action, "outcome": str(t.outcome), "observation": (t.observation or "")[:200]}
        for t in trials
    ]
    user_payload = json.dumps({
        "root_cause": case.confirmed_root_cause,
        "symptom": case.symptom,
        "fatal_error": case.fatal_error,
        "model": case.model,
        "process": case.process,
        "trials": trial_payload,
        "notes": notes or "",
    }, ensure_ascii=False)

    provider = get_provider()
    draft_data: dict
    source: str
    partial = False
    try:
        result, source = provider.recommend(WHY_WHY_SYSTEM_V1, user_payload, schema_hint=WHY_WHY_SCHEMA)
        if result.get("why_steps") and len(result["why_steps"]) >= 5:
            draft_data = {**result, "partial": False, "source": source}
        else:
            draft_data = _fallback_draft(case, trials)
            draft_data["partial"] = True
            source = "fallback-partial"
    except Exception as exc:
        logger.warning("Why-Why AI failed: %s; using fallback", exc)
        draft_data = _fallback_draft(case, trials)
        draft_data["partial"] = True
        source = "fallback"

    doc = db.query(WhyWhy).filter(WhyWhy.case_id == case.id).first()
    if not doc:
        doc = WhyWhy(
            id=str(uuid.uuid4()),
            case_id=case.id,
            draft=draft_data,
            status=WhyWhyStatus.DRAFT,
        )
        db.add(doc)
    else:
        if doc.status == WhyWhyStatus.APPROVED:
            raise ValueError("Why-Why sudah disetujui dan tidak dapat diubah.")
        doc.draft = draft_data
        doc.status = WhyWhyStatus.DRAFT
        doc.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(doc)
    return doc, draft_data, source
