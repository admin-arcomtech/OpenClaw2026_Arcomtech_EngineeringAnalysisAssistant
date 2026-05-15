"""Unit tests — Case ID format."""
import re

CASE_ID_PATTERN = re.compile(r"^IEI-\d{8}-\d{4}$")


def test_case_id_format():
    assert CASE_ID_PATTERN.match("IEI-20260515-0001")
    assert not CASE_ID_PATTERN.match("INVALID")
