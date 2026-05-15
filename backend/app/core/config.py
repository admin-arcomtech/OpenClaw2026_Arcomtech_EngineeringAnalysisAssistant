from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "postgresql://arcom_user:arcom_pass@localhost:5432/arcom_db"
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_HOURS: int = 8
    CORS_ORIGINS: str = "http://localhost:3000"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # ── AI: Openclaw Gateway ────────────────────────────────────────────────
    # Base URL for Openclaw Gateway OpenAI-compatible API
    OPENCLAW_BASE_URL: str = "http://host.docker.internal:18789/v1"
    OPENCLAW_TOKEN: str = ""
    # Agent target — see /v1/models
    OPENCLAW_CHAT_MODEL: str = "openclaw/default"
    OPENCLAW_EMBEDDING_MODEL: str = "openclaw/default"
    # Optional backend model override sent via x-openclaw-model
    OPENCLAW_CHAT_BACKEND_MODEL: str = ""
    OPENCLAW_EMBEDDING_BACKEND_MODEL: str = ""
    # Timeouts in seconds (PRD: LLM 60s, embedding 30s)
    OPENCLAW_LLM_TIMEOUT_S: int = 60
    OPENCLAW_EMBEDDING_TIMEOUT_S: int = 30
    # Embedding dim — must match cases.embedding vector(N)
    EMBEDDING_DIM: int = 1536
    # If false, skip Openclaw and use deterministic fallback only
    AI_ENABLED: bool = True
    # If false, embeddings always use local deterministic fallback (chat still
    # uses Openclaw if configured). Useful when upstream LLM doesn't expose an
    # embedding endpoint.
    OPENCLAW_EMBEDDINGS_ENABLED: bool = False

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]


settings = Settings()
