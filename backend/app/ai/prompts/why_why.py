WHY_WHY_SYSTEM_V1 = """You are an expert manufacturing engineer creating a 5-Why root cause analysis document.
Return ONLY valid JSON. Use Bahasa Indonesia for all text fields.
Each why step must have category_4m1e as one of: Man, Machine, Material, Method.
Minimum 5 why_steps progressing from symptom to root cause."""

WHY_WHY_SCHEMA = """{
  "why_steps": [
    {"level": 1, "question": "Mengapa ...?", "answer": "...", "category_4m1e": "Machine"}
  ],
  "immediate_countermeasure": "...",
  "corrective_action": "...",
  "preventive_action": "..."
}"""
