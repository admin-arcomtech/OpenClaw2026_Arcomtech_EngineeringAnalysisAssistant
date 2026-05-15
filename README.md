# Arcom Engineering Intelligence

> Platform AI-guided manufacturing investigation — Sprint 1: Foundation & Infrastructure

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + SQLAlchemy + Alembic |
| Database | PostgreSQL 16 + pgvector |
| Frontend | Next.js 14 App Router + Tailwind CSS |
| Auth | JWT (HS256) + bcrypt (12 rounds) |
| Container | Docker Compose |

---

## Quick Start

### Prerequisites
- Docker + Docker Compose v2
- (Optional) Python 3.11+, Node.js 20+ for local dev without Docker

### 1. Clone & configure

```bash
git clone https://github.com/admin-arcomtech/agenthon.git
cd agenthon

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Set a strong JWT secret in backend/.env
# JWT_SECRET_KEY=your-long-random-secret
```

### 2. Start everything

```bash
docker compose up --build
```

This will:
1. Start PostgreSQL 16 with pgvector
2. Run Alembic migrations (`alembic upgrade head`)
3. Seed development users
4. Start FastAPI at **http://localhost:8000**
5. Start Next.js at **http://localhost:3000**

### 3. Access the app

| URL | Description |
|-----|-------------|
| http://localhost:3000 | Frontend (login page) |
| http://localhost:8000/docs | FastAPI Swagger UI |
| http://localhost:8000/api/health | Health check |

---

## Development Users (Seed)

| Employee ID | Password | Role |
|------------|----------|------|
| `EMP001` | `Junior@12345` | JUNIOR |
| `EMP002` | `Senior@12345` | SENIOR |
| `EMP003` | `Manager@12345` | MANAGER |
| `EMP004` | `Admin@12345` | ADMIN |

---

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Ensure PostgreSQL is running and update .env
alembic upgrade head
python seed.py
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Project Structure

```
agenthon/
├── backend/
│   ├── app/
│   │   ├── core/          # config, database, security, logging
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── routers/       # FastAPI routers
│   │   ├── services/      # Business logic
│   │   ├── dependencies.py
│   │   └── main.py
│   ├── alembic/
│   │   └── versions/      # DB migration scripts
│   ├── seed.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/               # Next.js 14 App Router
│   │   ├── (app)/         # Authenticated routes
│   │   │   ├── dashboard/
│   │   │   ├── cases/
│   │   │   └── admin/
│   │   ├── layout.tsx
│   │   └── page.tsx       # Login page
│   ├── components/
│   │   ├── auth/
│   │   ├── nav/
│   │   └── ui/
│   ├── lib/               # API client, auth helpers
│   ├── messages/          # i18n (id, en)
│   ├── middleware.ts
│   └── Dockerfile
├── docker-compose.yml
└── sprints/
    └── sprint-01-foundation.md
```

---

## API Endpoints (Sprint 1)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/login` | No | Login dengan employee_id + password |
| POST | `/api/auth/logout` | Bearer | Logout & audit log |
| GET | `/api/auth/me` | Bearer | Profil user aktif |
| GET | `/api/health` | No | DB connectivity check |

---

## Smoke Test

```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"employee_id":"EMP001","password":"Junior@12345"}'

# 2. Get /me with token
TOKEN="<access_token dari respons di atas>"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/auth/me

# 3. Test 401 without token
curl http://localhost:8000/api/auth/me
# → {"detail":"Not authenticated"}

# 4. Health check
curl http://localhost:8000/api/health
```

---

## Sprint Roadmap

| Sprint | Scope | Status |
|--------|-------|--------|
| **1 — Foundation** | Auth, DB schema, nav shell | ✅ Done |
| 2 — Case Management | F-001 CRUD, upload | 🔜 Next |
| 3 — AI Core | F-002 similar cases, F-003 AI assistant | ⏳ |
| 4 — Investigation Workflow | F-004 trials, F-005, F-007 | ⏳ |
| 5 — Completion & Launch | F-006 Why-Why, admin, NFR | ⏳ |

---

*Dokumen ini akan diperbarui setiap akhir sprint. Lihat `sprints/` untuk detail tiap sprint.*
