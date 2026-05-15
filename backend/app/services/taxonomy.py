"""
Taxonomy / master data for dropdown fields.
Sprint 2: JSON-based (editable via Admin Sprint 5).
Seed data for IJP/SIDM pilot lines (PRD open Q#4).
"""

TAXONOMY: dict = {
    "models": [
        "IJP-A1", "IJP-A2", "IJP-B1", "IJP-B2",
        "SIDM-C1", "SIDM-C2", "SIDM-D1",
        "COMMON-X1", "COMMON-X2",
    ],
    "processes": [
        "Printing", "Curing", "Laminating", "Die-cutting",
        "Assembly", "Inspection", "Packaging", "Testing",
        "SMT", "Reflow", "Wave Soldering",
    ],
    "lines": [
        "Line-IJP-01", "Line-IJP-02", "Line-IJP-03",
        "Line-SIDM-01", "Line-SIDM-02",
        "Line-COMMON-01",
    ],
    "fatal_errors": [
        "Nozzle Clog", "Head Misalignment", "Ink Overflow",
        "Motor Fault", "Encoder Error", "Temperature Overshoot",
        "Vacuum Loss", "Feed Jam", "Print Streak",
        "Color Deviation", "Registration Error",
        "Mechanical Vibration", "Sensor Failure",
        "Software Timeout", "Communication Loss",
    ],
    "severities": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
    "shifts": ["PAGI", "SIANG", "MALAM"],
    "statuses": ["OPEN", "INVESTIGATING", "SUSPECTED_CAUSE", "TRIAL_IN_PROGRESS", "RESOLVED", "CLOSED", "ARCHIVED"],
}


def get_taxonomy() -> dict:
    return TAXONOMY
