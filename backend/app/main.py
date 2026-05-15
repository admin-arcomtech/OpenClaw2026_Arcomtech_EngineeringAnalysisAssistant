import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.logging import setup_logging, request_id_middleware
from app.routers import auth, health, cases, metadata

setup_logging(settings.LOG_LEVEL)

app = FastAPI(
    title="Arcom Engineering Intelligence API",
    version="0.1.0",
    description="Backend API untuk platform AI-guided manufacturing investigation",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(request_id_middleware)

app.include_router(auth.router)
app.include_router(health.router)
app.include_router(cases.router)
app.include_router(metadata.router)

# Serve uploaded files
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/tmp/arcom_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
