"""
AI providers — abstraction for LLM + Embedding backends.

Sprint 3 plumbs Openclaw Gateway (OpenAI-compatible) on this server with a
deterministic local fallback so the platform stays functional when AI is down
(PRD F-003 / sprint-03-ai-core.md NFR).
"""
from __future__ import annotations

import hashlib
import json
import logging
import math
import re
from abc import ABC, abstractmethod
from typing import List, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


# ─── Interfaces ──────────────────────────────────────────────────────────────


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        ...

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        ...


class LLMProvider(ABC):
    @abstractmethod
    def complete_json(self, system: str, user: str, schema_hint: Optional[str] = None) -> dict:
        """Run an LLM completion expected to return JSON. Returns parsed dict."""
        ...


# ─── Openclaw Provider (real LLM via gateway on this server) ────────────────


class OpenclawProvider(EmbeddingProvider, LLMProvider):
    """OpenAI-compatible client targeting the Openclaw Gateway."""

    def __init__(
        self,
        base_url: str,
        token: str,
        chat_model: str,
        embedding_model: str,
        chat_backend_model: str = "",
        embedding_backend_model: str = "",
        llm_timeout: int = 60,
        embedding_timeout: int = 30,
        embedding_dim: int = 1536,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.chat_model = chat_model
        self.embedding_model = embedding_model
        self.chat_backend_model = chat_backend_model
        self.embedding_backend_model = embedding_backend_model
        self.llm_timeout = llm_timeout
        self.embedding_timeout = embedding_timeout
        self.embedding_dim = embedding_dim

    def _headers(self, backend_model: str = "") -> dict:
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        if backend_model:
            h["x-openclaw-model"] = backend_model
        return h

    def embed(self, text: str) -> List[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        try:
            r = httpx.post(
                f"{self.base_url}/embeddings",
                headers=self._headers(self.embedding_backend_model),
                json={"model": self.embedding_model, "input": texts},
                timeout=self.embedding_timeout,
            )
            r.raise_for_status()
            data = r.json()
            return [item["embedding"] for item in data["data"]]
        except Exception as exc:
            logger.warning("Openclaw embed_batch failed (%s); falling back", exc)
            raise

    def complete_json(self, system: str, user: str, schema_hint: Optional[str] = None) -> dict:
        prompt_user = user
        if schema_hint:
            prompt_user = f"{user}\n\nReturn ONLY valid JSON matching this shape:\n{schema_hint}"

        try:
            r = httpx.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(self.chat_backend_model),
                json={
                    "model": self.chat_model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt_user},
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.3,
                },
                timeout=self.llm_timeout,
            )
            r.raise_for_status()
            data = r.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)
        except Exception as exc:
            logger.warning("Openclaw chat completion failed (%s); falling back", exc)
            raise


# ─── Local Deterministic Fallback ────────────────────────────────────────────


class LocalFallbackProvider(EmbeddingProvider, LLMProvider):
    """
    Offline-safe fallback used when Openclaw is unreachable or upstream LLM is
    not configured. Guarantees Sprint 3 features remain demoable:

    - Embedding: hashed bag-of-words vector (deterministic, 1536d).
    - Completion: rule-based 4M1E hypothesis generator using similar cases.
    """

    def __init__(self, embedding_dim: int = 1536):
        self.embedding_dim = embedding_dim

    # ── Embedding ──
    @staticmethod
    def _tokens(text: str) -> List[str]:
        return [t for t in re.split(r"\W+", (text or "").lower()) if t and len(t) > 1]

    def embed(self, text: str) -> List[float]:
        vec = [0.0] * self.embedding_dim
        for tok in self._tokens(text):
            h = hashlib.md5(tok.encode()).digest()
            idx = int.from_bytes(h[:4], "big") % self.embedding_dim
            sign = 1.0 if (h[4] % 2 == 0) else -1.0
            vec[idx] += sign
        # L2 normalize for cosine similarity
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed(t) for t in texts]

    # ── Rule-based completion ──
    # Engineering taxonomy 4M1E mapping for fatal-error keywords
    TAXONOMY_HINTS: dict[str, dict] = {
        "Nozzle Clog":            {"category_4m1e": "Material",    "trial_risk": "LOW",    "verifications": ["Cek viskositas tinta vs spec batch", "Bersihkan & purge nozzle", "Ganti filter inlet"]},
        "Head Misalignment":      {"category_4m1e": "Machine",     "trial_risk": "MEDIUM", "verifications": ["Kalibrasi alignment menggunakan jig referensi", "Cek baut mounting head", "Verifikasi tegangan belt drive"]},
        "Ink Overflow":           {"category_4m1e": "Material",    "trial_risk": "LOW",    "verifications": ["Periksa level sensor reservoir", "Cek seal valve drain", "Test mode purge manual"]},
        "Motor Fault":            {"category_4m1e": "Machine",     "trial_risk": "HIGH",   "verifications": ["Cek arus motor di kondisi idle vs load", "Test encoder feedback", "Ukur tegangan suplai driver"]},
        "Encoder Error":          {"category_4m1e": "Machine",     "trial_risk": "MEDIUM", "verifications": ["Bersihkan disc encoder", "Cek konektor & shielding", "Verifikasi resolusi & arah pulse"]},
        "Temperature Overshoot":  {"category_4m1e": "Method",      "trial_risk": "MEDIUM", "verifications": ["Tuning PID setpoint zona curing", "Cek sensor thermocouple drift", "Verifikasi ramp-up profile"]},
        "Vacuum Loss":            {"category_4m1e": "Machine",     "trial_risk": "LOW",    "verifications": ["Cek seal & gasket chamber", "Test vacuum pump performance", "Inspect line untuk pinhole/kebocoran"]},
        "Feed Jam":               {"category_4m1e": "Material",    "trial_risk": "LOW",    "verifications": ["Periksa ketebalan material vs spec", "Sesuaikan tension feeder", "Cek roller wear pattern"]},
        "Color Deviation":        {"category_4m1e": "Material",    "trial_risk": "LOW",    "verifications": ["Verifikasi color profile dengan spectrophotometer", "Cek expired date tinta", "Re-kalibrasi ICC profile"]},
        "Registration Error":     {"category_4m1e": "Method",      "trial_risk": "MEDIUM", "verifications": ["Re-kalibrasi mark sensor", "Cek tension uniformity web", "Verifikasi setting offset cutting blade"]},
        "Sensor Failure":         {"category_4m1e": "Machine",     "trial_risk": "LOW",    "verifications": ["Bersihkan permukaan sensor", "Test response time", "Ganti sensor jika output drift > 10%"]},
        "Software Timeout":       {"category_4m1e": "Method",      "trial_risk": "LOW",    "verifications": ["Cek log error sequence", "Reset & re-flash firmware terbaru", "Monitor CPU/memory selama test"]},
        "Communication Loss":     {"category_4m1e": "Machine",     "trial_risk": "LOW",    "verifications": ["Cek kabel & konektor jaringan", "Test ping device", "Restart switch / verify routing"]},
        "Print Streak":           {"category_4m1e": "Machine",     "trial_risk": "LOW",    "verifications": ["Wipe head cartridge", "Cek tekanan negative pressure", "Verifikasi waveform driver"]},
        "Mechanical Vibration":   {"category_4m1e": "Machine",     "trial_risk": "MEDIUM", "verifications": ["Cek balance & bearing", "Verifikasi torque baut mounting", "Test isolator anti-vibration"]},
    }

    GENERIC_HUMAN = {
        "category_4m1e": "Man", "trial_risk": "LOW",
        "verifications": ["Wawancara operator shift terkait perubahan prosedur", "Cek log handover", "Review checklist start-of-shift"],
    }

    def complete_json(self, system: str, user: str, schema_hint: Optional[str] = None) -> dict:
        # Expects `user` to contain JSON payload with current_case + similar_cases
        try:
            payload = json.loads(user)
        except json.JSONDecodeError:
            payload = {}

        current = payload.get("current_case", {})
        similar = payload.get("similar_cases", []) or []
        fatal_error = (current.get("fatal_error") or "").strip()
        model = current.get("model") or "—"
        process = current.get("process") or "—"

        # Build hypotheses — primary from fatal_error taxonomy, secondary from process
        hypotheses = []
        primary_hint = self.TAXONOMY_HINTS.get(fatal_error)
        if primary_hint:
            evidence = [f"Fatal error '{fatal_error}' terdeteksi pada {model}/{process}"]
            sim_with_root = [s for s in similar if s.get("countermeasure")][:2]
            evidence.extend([
                f"Kasus serupa {s['case_id']}: {s.get('countermeasure', 'tidak ada root cause')}"
                for s in sim_with_root
            ])
            hypotheses.append({
                "title": f"{fatal_error} — penyebab primer (taxonomy {primary_hint['category_4m1e']})",
                "confidence": 70 if sim_with_root else 55,
                "category_4m1e": primary_hint["category_4m1e"],
                "evidence": evidence,
                "suggested_verification": primary_hint["verifications"],
                "trial_risk": primary_hint["trial_risk"],
                "estimated_time_min": 30,
                "similar_case_count": len(sim_with_root),
            })

        # Secondary — process-related
        if process and process != "—":
            hypotheses.append({
                "title": f"Proses {process} — parameter drift atau out-of-spec",
                "confidence": 45,
                "category_4m1e": "Method",
                "evidence": [
                    f"Symptom dilaporkan saat proses {process}",
                    "Periksa SPC chart untuk drift parameter terbaru" if not similar else f"Cross-check {len(similar)} kasus serupa",
                ],
                "suggested_verification": [
                    "Review SPC parameter terakhir 24 jam",
                    "Bandingkan setting current vs golden recipe",
                    "Cek log perubahan parameter shift sebelumnya",
                ],
                "trial_risk": "LOW",
                "estimated_time_min": 20,
                "similar_case_count": len(similar),
            })

        # Tertiary — human factor (always include as low-cost check)
        if len(hypotheses) < 3:
            hypotheses.append({
                "title": "Faktor operator / handover prosedur",
                "confidence": 30,
                **self.GENERIC_HUMAN,
                "evidence": ["Kemungkinan perubahan setting atau prosedur saat handover shift"],
                "suggested_verification": self.GENERIC_HUMAN["verifications"],
                "estimated_time_min": 15,
                "similar_case_count": 0,
            })

        # Sort: low-risk first (matches PRD acceptance criteria F-003)
        risk_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
        hypotheses.sort(key=lambda h: risk_order.get(h.get("trial_risk", "MEDIUM"), 1))

        return {"hypotheses": hypotheses[:3], "model_version": "fallback-rule-v1"}


# ─── Provider Selection ──────────────────────────────────────────────────────


_provider_instance: Optional["AIProvider"] = None


class AIProvider:
    """
    Composite provider that tries Openclaw first, falls back deterministically.
    Single entry-point used by routers/services.
    """

    def __init__(self, primary: Optional[OpenclawProvider], fallback: LocalFallbackProvider):
        self.primary = primary
        self.fallback = fallback

    def embed(self, text: str) -> tuple[List[float], str]:
        """Returns (vector, source_tag)."""
        if self.primary:
            try:
                return self.primary.embed(text), "openclaw"
            except Exception:
                pass
        return self.fallback.embed(text), "fallback"

    def embed_batch(self, texts: List[str]) -> tuple[List[List[float]], str]:
        if self.primary:
            try:
                return self.primary.embed_batch(texts), "openclaw"
            except Exception:
                pass
        return self.fallback.embed_batch(texts), "fallback"

    def recommend(self, system: str, user: str, schema_hint: Optional[str] = None) -> tuple[dict, str]:
        if self.primary:
            try:
                return self.primary.complete_json(system, user, schema_hint), "openclaw"
            except Exception:
                pass
        return self.fallback.complete_json(system, user, schema_hint), "fallback"


def get_provider() -> AIProvider:
    global _provider_instance
    if _provider_instance is not None:
        return _provider_instance

    fallback = LocalFallbackProvider(embedding_dim=settings.EMBEDDING_DIM)
    primary: Optional[OpenclawProvider] = None
    if settings.AI_ENABLED and settings.OPENCLAW_BASE_URL:
        primary = OpenclawProvider(
            base_url=settings.OPENCLAW_BASE_URL,
            token=settings.OPENCLAW_TOKEN,
            chat_model=settings.OPENCLAW_CHAT_MODEL,
            embedding_model=settings.OPENCLAW_EMBEDDING_MODEL,
            chat_backend_model=settings.OPENCLAW_CHAT_BACKEND_MODEL,
            embedding_backend_model=settings.OPENCLAW_EMBEDDING_BACKEND_MODEL,
            llm_timeout=settings.OPENCLAW_LLM_TIMEOUT_S,
            embedding_timeout=settings.OPENCLAW_EMBEDDING_TIMEOUT_S,
            embedding_dim=settings.EMBEDDING_DIM,
        )
        logger.info("AI primary: Openclaw at %s", settings.OPENCLAW_BASE_URL)
    else:
        logger.info("AI primary: disabled, using local fallback only")

    _provider_instance = AIProvider(primary=primary, fallback=fallback)
    return _provider_instance
