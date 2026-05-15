"""Unit tests — case status machine (Sprint 4/5)."""
import pytest
from app.models.case import CaseStatus, can_transition
from app.models.user import UserRole


@pytest.mark.parametrize("role,from_s,to_s,expected", [
    (UserRole.JUNIOR, CaseStatus.OPEN, CaseStatus.INVESTIGATING, True),
    (UserRole.JUNIOR, CaseStatus.MONITORING, CaseStatus.CONFIRMED, False),
    (UserRole.SENIOR, CaseStatus.MONITORING, CaseStatus.CONFIRMED, True),
    (UserRole.SENIOR, CaseStatus.CONFIRMED, CaseStatus.ARCHIVED, True),
    (UserRole.JUNIOR, CaseStatus.CONFIRMED, CaseStatus.ARCHIVED, False),
    (UserRole.SENIOR, CaseStatus.ARCHIVED, CaseStatus.OPEN, False),
])
def test_can_transition(role, from_s, to_s, expected):
    assert can_transition(role, from_s, to_s) is expected
