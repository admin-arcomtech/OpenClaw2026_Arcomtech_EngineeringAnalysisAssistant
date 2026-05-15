"""
Prompt template v1 for AI investigation recommendations (F-003).
Bound to the 4M1E engineering taxonomy and RAG-grounded by similar cases.
"""
import json

RECOMMENDATIONS_SYSTEM_V1 = """Anda adalah asisten investigasi manufaktur untuk engineer di pabrik.

ATURAN MUTLAK:
1. Maksimal 3 hipotesis akar penyebab (root cause hypotheses).
2. Setiap hipotesis WAJIB punya kategori 4M1E: Man, Machine, Material, Method, Environment.
3. Setiap hipotesis WAJIB punya minimal 1 evidence yang ground pada data kasus saat ini ATAU kasus serupa yang diberikan.
4. JANGAN mengarang root cause tanpa evidence — jika tidak ada similar case, gunakan symptom + fatal_error sebagai evidence.
5. Verifikasi yang berisiko RENDAH (LOW) harus diurut pertama; HIGH terakhir.
6. Output HARUS JSON valid sesuai schema, tanpa markdown atau penjelasan tambahan.

Konteks: Anda membantu Junior/Senior Engineer mempercepat root cause analysis, BUKAN menggantikan otoritas engineer. Tampilkan confidence yang konservatif jika data tipis.
"""


def build_recommendations_user(current_case: dict, similar_cases: list) -> str:
    """Returns JSON payload string passed as `user` content."""
    payload = {
        "current_case": {
            "case_id": current_case.get("case_id"),
            "model": current_case.get("model"),
            "process": current_case.get("process"),
            "line": current_case.get("line"),
            "fatal_error": current_case.get("fatal_error"),
            "symptom": current_case.get("symptom"),
            "description": current_case.get("description"),
            "severity": current_case.get("severity"),
            "temporary_action": current_case.get("temporary_action"),
        },
        "similar_cases": [
            {
                "case_id": s.get("case_id"),
                "similarity_pct": s.get("similarity_pct"),
                "model": s.get("model"),
                "fatal_error": s.get("fatal_error"),
                "root_cause": s.get("root_cause"),
                "countermeasure": s.get("countermeasure"),
                "resolution_days": s.get("resolution_days"),
            }
            for s in (similar_cases or [])[:5]
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


HYPOTHESIS_SCHEMA = """{
  "hypotheses": [
    {
      "title": "string (judul hipotesis ringkas)",
      "confidence": "integer 0-100",
      "category_4m1e": "Man | Machine | Material | Method | Environment",
      "evidence": ["string", "string"],
      "suggested_verification": ["string langkah verifikasi"],
      "trial_risk": "LOW | MEDIUM | HIGH",
      "estimated_time_min": "integer",
      "similar_case_count": "integer"
    }
  ]
}"""
