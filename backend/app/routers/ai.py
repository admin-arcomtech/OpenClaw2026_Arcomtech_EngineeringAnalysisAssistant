"""
AI endpoints — F-002 Similar Case Retrieval, F-003 Investigation Assistant.

Sprint 3 — sprint-03-ai-core.md
"""
import logging
import uuid
import time
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, text
from sqlalchemy.orm import Session

from app.ai import get_provider
from app.ai.prompts import RECOMMENDATIONS_SYSTEM_V1, build_recommendations_user
from app.ai.prompts.recommendations import HYPOTHESIS_SCHEMA
from app.core.config import settings
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.ai_recommendation import AIRecommendation, AIFeedback
from app.models.case import Case
from app.models.user import User
from app.schemas.ai import (
    FeedbackRequest,
    RecommendationsRequest,
    RecommendationsResponse,
    SimilarCaseItem,
    SimilarCaseRequest,
    SimilarCaseResponse,
)
from app.schemas.trial import TrialPriorityRequest, TrialPriorityResponse
from app.services.embedding_service import _case_text
from app.services.trial_priority import build_trial_queue

router = APIRouter(prefix="/api/ai", tags=["ai"])
logger = logging.getLogger(__name__)


# ─── F-002 Similar Case Retrieval ───────────────────────────────────────────

def _keyword_search(
    db: Session, current: Case, limit: int
) -> List[Case]:
    """Fallback: token-overlap on model/fatal_error/process/symptom."""
    q = db.query(Case).filter(Case.id != current.id)
    # OR-match key tokens
    filters = []
    if current.model:
        filters.append(Case.model == current.model)
    if current.fatal_error:
        filters.append(Case.fatal_error == current.fatal_error)
    if current.process:
        filters.append(Case.process == current.process)
    if filters:
        q = q.filter(or_(*filters))
    return q.order_by(Case.created_at.desc()).limit(limit).all()


@router.post("/similar-cases", response_model=SimilarCaseResponse)
def similar_cases(
    body: SimilarCaseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not body.case_id:
        raise HTTPException(status_code=400, detail="case_id required")

    current = db.query(Case).filter((Case.id == body.case_id) | (Case.case_id == body.case_id)).first()
    if not current:
        raise HTTPException(status_code=404, detail="Kasus tidak ditemukan")

    total_cases = db.query(Case).count()
    warning: Optional[str] = None
    if total_cases < 10:
        warning = "Knowledge base masih terbatas (< 10 kasus). Hasil mungkin kurang relevan."

    provider = get_provider()
    started = time.time()

    # Ensure current case has an embedding
    if current.embedding is None:
        vector, source = provider.embed(_case_text(current))
        current.embedding = vector
        db.commit()
        db.refresh(current)
    else:
        source = "openclaw" if provider.primary else "fallback"

    # Vector search via pgvector cosine distance
    items: List[Case] = []
    mode = "vector"
    similarities: dict[str, float] = {}
    try:
        sql = text("""
            SELECT id, 1 - (embedding <=> CAST(:vec AS vector)) AS similarity
            FROM cases
            WHERE id != :exclude_id AND embedding IS NOT NULL
            ORDER BY embedding <=> CAST(:vec AS vector)
            LIMIT :lim
        """)
        rows = db.execute(
            sql,
            {
                "vec": str(current.embedding) if isinstance(current.embedding, list) else current.embedding,
                "exclude_id": current.id,
                "lim": body.limit,
            },
        ).fetchall()
        # Map id → similarity
        id_to_sim = {r[0]: float(r[1]) for r in rows}
        if id_to_sim:
            cases_map = {
                c.id: c for c in db.query(Case).filter(Case.id.in_(list(id_to_sim.keys()))).all()
            }
            items = [cases_map[i] for i in id_to_sim.keys() if i in cases_map]
            similarities = id_to_sim
    except Exception as exc:
        logger.warning("pgvector search failed: %s; falling back to keyword", exc)
        items = _keyword_search(db, current, body.limit)
        mode = "keyword"
        warning = "Hasil pencarian menggunakan mode teks (vector search tidak tersedia)"
        source = "keyword"

    # Filter by threshold (only for vector mode)
    if mode == "vector":
        items = [c for c in items if similarities.get(c.id, 0) >= body.threshold]

    # Empty state
    if not items:
        if total_cases <= 1:
            warning = "Belum ada kasus serupa. Ini investigasi baru."
        elif mode == "vector":
            warning = warning or "Tidak ada kasus dengan similarity di atas threshold."

    # Enrich response
    response_items: List[SimilarCaseItem] = []
    for c in items:
        sim = similarities.get(c.id, 0.5)
        resolution_days = None
        if c.status in ("RESOLVED", "CLOSED", "ARCHIVED"):
            delta = (c.updated_at - c.created_at)
            resolution_days = max(1, delta.days)
        response_items.append(SimilarCaseItem(
            case_id=c.case_id,
            id=c.id,
            similarity_pct=round(sim * 100, 1),
            title=c.title,
            model=c.model,
            process=c.process,
            fatal_error=c.fatal_error,
            status=c.status.value if hasattr(c.status, "value") else str(c.status),
            root_cause=c.description if c.status in ("RESOLVED", "CLOSED", "ARCHIVED") else None,
            countermeasure=c.temporary_action,
            resolution_days=resolution_days,
            created_at=c.created_at,
        ))

    elapsed = time.time() - started
    logger.info(
        "similar-cases: case=%s mode=%s source=%s hits=%d elapsed=%.2fs",
        current.case_id, mode, source, len(response_items), elapsed,
    )

    return SimilarCaseResponse(
        items=response_items,
        source=source,
        mode=mode,
        warning=warning,
        threshold=body.threshold,
        total_candidates=total_cases,
    )


# ─── F-003 AI Investigation Recommendations ─────────────────────────────────

@router.post("/recommendations", response_model=RecommendationsResponse)
def recommendations(
    body: RecommendationsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = db.query(Case).filter((Case.id == body.case_id) | (Case.case_id == body.case_id)).first()
    if not case:
        raise HTTPException(status_code=404, detail="Kasus tidak ditemukan")

    # First fetch similar cases as RAG context
    similar_req = SimilarCaseRequest(case_id=case.id, threshold=0.3, limit=5)
    similar_resp = similar_cases(similar_req, db=db, current_user=current_user)
    similar_payload = [item.model_dump() for item in similar_resp.items]

    current_payload = {
        "case_id": case.case_id,
        "model": case.model,
        "process": case.process,
        "line": case.line,
        "fatal_error": case.fatal_error,
        "symptom": case.symptom,
        "description": case.description,
        "severity": case.severity.value if case.severity else None,
        "temporary_action": case.temporary_action,
    }

    user_text = build_recommendations_user(current_payload, similar_payload)
    if body.extra_context:
        user_text += f"\n\nADDITIONAL_CONTEXT:\n{body.extra_context}"

    provider = get_provider()
    try:
        result, source = provider.recommend(
            RECOMMENDATIONS_SYSTEM_V1,
            user_text,
            schema_hint=HYPOTHESIS_SCHEMA,
        )
    except Exception as exc:
        logger.error("recommendations: provider failed completely: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="AI tidak tersedia saat ini. Gunakan manual investigation mode.",
        )

    hypotheses = result.get("hypotheses", [])
    if not hypotheses:
        raise HTTPException(
            status_code=503,
            detail="AI tidak tersedia saat ini. Gunakan manual investigation mode.",
        )

    # Persist
    rec = AIRecommendation(
        id=str(uuid.uuid4()),
        case_id=case.id,
        hypotheses=hypotheses,
        source=source,
        model_version=result.get("model_version", "v1"),
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    return RecommendationsResponse(
        id=rec.id,
        case_id=case.id,
        hypotheses=hypotheses,
        source=source,
        model_version=rec.model_version or "v1",
        created_at=rec.created_at,
    )


# ─── F-004 Trial Priority ────────────────────────────────────────────────────

@router.post("/trial-priority", response_model=TrialPriorityResponse)
def trial_priority(
    body: TrialPriorityRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = db.query(Case).filter((Case.id == body.case_id) | (Case.case_id == body.case_id)).first()
    if not case:
        raise HTTPException(status_code=404, detail="Kasus tidak ditemukan")

    items, all_high, warning = build_trial_queue(db, case, body.manual_trial)
    case.trial_queue = [i.model_dump() for i in items]
    db.commit()

    return TrialPriorityResponse(trial_queue=items, all_high_risk=all_high, warning=warning)


# ─── Feedback (F-002 / F-003) ────────────────────────────────────────────────

@router.post("/feedback")
def submit_feedback(
    body: FeedbackRequest,
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = db.query(Case).filter((Case.id == case_id) | (Case.case_id == case_id)).first()
    if not case:
        raise HTTPException(status_code=404, detail="Kasus tidak ditemukan")

    fb = AIFeedback(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        case_id=case.id,
        target_type=body.target_type,
        target_id=body.target_id,
        rating=body.rating,
        note=body.note,
    )
    db.add(fb)
    db.commit()
    return {"ok": True, "id": fb.id}


# ─── Provider health ────────────────────────────────────────────────────────

@router.get("/health")
def ai_health(current_user: User = Depends(get_current_user)):
    """Reports which AI provider is active right now."""
    provider = get_provider()
    primary_ok = False
    if provider.primary:
        try:
            provider.primary.embed("ping")
            primary_ok = True
        except Exception:
            primary_ok = False
    return {
        "openclaw_configured": provider.primary is not None,
        "openclaw_reachable": primary_ok,
        "fallback_available": True,
        "openclaw_base_url": settings.OPENCLAW_BASE_URL if provider.primary else None,
    }
