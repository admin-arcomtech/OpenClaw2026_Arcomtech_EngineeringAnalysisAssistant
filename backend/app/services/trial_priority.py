"""
Trial Recommendation Engine (F-004).

priority = LOW_RISK_WEIGHT × success_rate × (1 / normalized_time)
Sorted: LOW risk before HIGH; flag requires_senior_approval on HIGH risk items.
"""
from __future__ import annotations

import uuid
import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.ai_recommendation import AIRecommendation
from app.models.case import Case
from app.models.trial import Trial, TrialOutcome
from app.schemas.trial import TrialQueueItem

logger = logging.getLogger(__name__)

RISK_SCORE = {"LOW": 3.0, "MEDIUM": 2.0, "HIGH": 1.0}
MAX_TIME_MIN = 120


def _score_item(risk: str, success_rate: Optional[float], time_min: int) -> float:
    risk_w = RISK_SCORE.get(risk.upper(), 1.0)
    success = (success_rate / 100.0) if success_rate is not None else 0.5
    time_factor = 1.0 / max(1, time_min / 30.0)
    return risk_w * success * time_factor


def _from_ai_hypotheses(db: Session, case_id: str) -> List[TrialQueueItem]:
    rec = (
        db.query(AIRecommendation)
        .filter(AIRecommendation.case_id == case_id)
        .order_by(AIRecommendation.created_at.desc())
        .first()
    )
    if not rec or not rec.hypotheses:
        return []

    items = []
    for h in rec.hypotheses:
        risk = h.get("trial_risk", "MEDIUM")
        verifications = h.get("suggested_verification") or []
        action = verifications[0] if verifications else h.get("title", "Investigasi")
        items.append(TrialQueueItem(
            id=str(uuid.uuid4()),
            trial_action=action,
            risk_level=risk,
            estimated_time_min=h.get("estimated_time_min", 30),
            historical_success_rate=None,
            destructive=risk == "HIGH",
            required_tools=[],
            priority_rank=0,
            requires_senior_approval=risk == "HIGH",
            source="ai",
        ))
    return items


def _from_similar_trials(db: Session, case: Case) -> List[TrialQueueItem]:
    """Pull successful trials from cases with same model+fatal_error."""
    if not case.model or not case.fatal_error:
        return []

    similar_cases = (
        db.query(Case)
        .filter(
            Case.model == case.model,
            Case.fatal_error == case.fatal_error,
            Case.id != case.id,
            Case.status.in_(["CONFIRMED", "ARCHIVED", "RESOLVED", "CLOSED"]),
        )
        .limit(5)
        .all()
    )
    items = []
    for sc in similar_cases:
        trials = (
            db.query(Trial)
            .filter(Trial.case_id == sc.id)
            .filter(Trial.outcome.in_([TrialOutcome.IMPROVED, TrialOutcome.NO_CHANGE]))
            .limit(3)
            .all()
        )
        for t in trials:
            action = t.trial_action or t.action_taken or t.hypothesis
            if not action:
                continue
            risk = (t.risk_level or "LOW").upper()
            items.append(TrialQueueItem(
                id=str(uuid.uuid4()),
                trial_action=action,
                risk_level=risk,
                estimated_time_min=t.time_spent_min or 30,
                historical_success_rate=82.0,
                destructive=t.destructive or False,
                required_tools=[],
                priority_rank=0,
                requires_senior_approval=risk == "HIGH",
                source="similar_case",
            ))
    return items


def build_trial_queue(
    db: Session,
    case: Case,
    manual_trial: Optional[dict] = None,
) -> tuple[List[TrialQueueItem], bool, Optional[str]]:
    items: List[TrialQueueItem] = []
    items.extend(_from_ai_hypotheses(db, case.id))
    items.extend(_from_similar_trials(db, case))

    if manual_trial:
        risk = manual_trial.get("risk_level", "MEDIUM").upper()
        items.append(TrialQueueItem(
            id=str(uuid.uuid4()),
            trial_action=manual_trial.get("trial_action", "Manual trial"),
            risk_level=risk,
            estimated_time_min=manual_trial.get("estimated_time_min", 30),
            historical_success_rate=None,
            destructive=manual_trial.get("destructive", False),
            required_tools=manual_trial.get("required_tools", []),
            priority_rank=0,
            requires_senior_approval=risk == "HIGH",
            source="manual",
        ))

    # Deduplicate by trial_action text
    seen = set()
    unique: List[TrialQueueItem] = []
    for item in items:
        key = item.trial_action.strip().lower()[:80]
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)

    # Score and sort: LOW risk first, then by priority score desc
    for item in unique:
        item.priority_rank = int(_score_item(item.risk_level, item.historical_success_rate, item.estimated_time_min) * 100)

    unique.sort(key=lambda x: (RISK_SCORE.get(x.risk_level, 0) * -1, -x.priority_rank))

    for rank, item in enumerate(unique, start=1):
        item.priority_rank = rank
        item.requires_senior_approval = item.risk_level == "HIGH"

    all_high = len(unique) > 0 and all(i.risk_level == "HIGH" for i in unique)
    warning = None
    if all_high:
        warning = "Semua trial berisiko HIGH — diperlukan persetujuan Senior sebelum eksekusi."
    elif not unique:
        warning = "Tidak ada rekomendasi trial. Tambahkan manual atau jalankan AI Recommendations terlebih dahulu."

    return unique, all_high, warning
