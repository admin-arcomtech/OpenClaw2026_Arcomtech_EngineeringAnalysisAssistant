# Sprint 1 — Foundation & Infrastructure

**Durasi:** Minggu 1–2  
**Tujuan:** Menyiapkan fondasi teknis, database, autentikasi, dan kerangka aplikasi agar fitur investigasi dapat dibangun di sprint berikutnya.

---

## Ringkasan

Sprint ini fokus pada **project scaffolding**, **PostgreSQL + pgvector**, **auth & RBAC**, dan **navigation shell** mobile-first. Belum ada AI atau workflow investigasi penuh.

| Aspek | Detail |
|-------|--------|
| Fitur PRD | Prasyarat untuk F-001, F-007 |
| Peran pengguna | Semua role (login dasar) |
| Exit criteria | Engineer dapat login, melihat shell dashboard, dan environment siap untuk development fitur |

---

## Deliverables

1. Monorepo / struktur proyek: `backend/` (FastAPI), `frontend/` (Next.js 14 App Router), `docker-compose.yml`
2. PostgreSQL 15+ dengan ekstensi `pgvector` berjalan via Docker Compose
3. Migrasi schema awal: `users`, `cases`, `trials`, `case_photos`, `audit_log` (struktur dasar)
4. API autentikasi: login, logout, `/me`
5. Middleware JWT + RBAC (JUNIOR | SENIOR | MANAGER | ADMIN)
6. Layout navigasi responsif (mobile-first, touch target ≥ 44px)
7. Halaman login (`/`) dan dashboard kosong (`/dashboard`)

---

## Task Breakdown

### 1.1 Project Setup

- [ ] Inisialisasi FastAPI: struktur `app/`, `routers/`, `models/`, `schemas/`, `services/`, `core/config.py`
- [ ] Inisialisasi Next.js 14 App Router: `app/`, layout, Tailwind/CSS sesuai design system internal
- [ ] `.env.example` untuk backend & frontend (DB URL, JWT secret, CORS origins)
- [ ] Docker Compose: `postgres` (pgvector image), `backend`, `frontend` (dev)
- [ ] Alembic / migrasi DB terhubung ke pipeline CI lokal
- [ ] README setup: `docker compose up`, seed dev user

### 1.2 Database Schema (Core Tables)

Implementasi sesuai PRD §7.1:

| Tabel | Prioritas Sprint 1 |
|-------|-------------------|
| `users` | ✅ Lengkap |
| `cases` | ✅ Struktur (tanpa embedding pipeline aktif) |
| `trials` | ✅ Struktur kosong |
| `case_photos` | ✅ Metadata upload |
| `audit_log` | ✅ Struktur dasar (write pada auth events) |
| `ai_recommendations` | ⏳ Stub / migrasi kosong (Sprint 3) |
| `why_why` | ⏳ Stub (Sprint 5) |

- [ ] ENUM: `case_status`, `severity`, `shift`, `user_role`, `trial_result`, `scrap_impact`, `risk_level`
- [ ] Index: `cases(case_id)`, `cases(status)`, `cases(model, fatal_error)`
- [ ] Kolom `embedding vector(1536)` nullable pada `cases` dan `trials` (siap pgvector)
- [ ] HNSW index pada `cases.embedding` (dapat diaktifkan setelah data ada)

### 1.3 Authentication & Authorization

| Endpoint | Method | Auth |
|----------|--------|------|
| `/api/auth/login` | POST | No |
| `/api/auth/logout` | POST | Yes |
| `/api/auth/me` | GET | Yes |

- [ ] Password hashing: bcrypt, min 12 rounds
- [ ] JWT access token (expiry configurable, e.g. 8h shift)
- [ ] Dependency `get_current_user` + `require_role([...])`
- [ ] Seed users: 1 Junior, 1 Senior, 1 Manager, 1 Admin (development)
- [ ] Audit log: login success/failure, logout

### 1.4 Frontend — Navigation Shell

| Route | Status Sprint 1 |
|-------|-----------------|
| `/` | Login form (employee_id + password) |
| `/dashboard` | Placeholder: "Selamat datang" + nav |
| `/cases` | Placeholder list |
| `/cases/new` | Placeholder (form Sprint 2) |
| `/cases/:id` | Placeholder detail |
| `/admin` | Guard ADMIN only, placeholder |

- [ ] Protected routes: redirect ke `/` jika belum login
- [ ] Bottom nav / sidebar mobile-first
- [ ] i18n scaffold: default locale `id`, struktur `en` siap
- [ ] Error boundary & toast untuk error API

### 1.5 Non-Functional (Sprint 1)

- [ ] CORS dikonfigurasi untuk intranet dev
- [ ] Health check: `GET /api/health` → DB connectivity
- [ ] Logging terstruktur (request ID, user ID)
- [ ] `.gitignore` untuk secrets, uploads lokal

---

## Acceptance Criteria

- [ ] `docker compose up` menjalankan Postgres + backend + frontend tanpa error
- [ ] Migrasi DB berjalan clean pada environment baru
- [ ] Login dengan employee_id/password mengembalikan JWT valid
- [ ] Endpoint terproteksi menolak request tanpa token (401)
- [ ] Role JUNIOR tidak dapat mengakses route ADMIN (403)
- [ ] Halaman login dan dashboard render baik di viewport mobile (375px)
- [ ] Audit log mencatat event login

---

## Definition of Done

- Code review internal selesai
- Dokumentasi env variables di `.env.example`
- Tidak ada secret di repository
- Manual smoke test: login → dashboard → logout

---

## Dependencies & Risks

| Item | Catatan |
|------|---------|
| **Depends on** | Keputusan hosting intranet (dev/staging URL) |
| **Risk:** pgvector image compatibility | Mitigasi: gunakan `pgvector/pgvector:pg16` image teruji |
| **Risk:** LDAP SSO | Out of scope Sprint 1; auth sendiri sesuai PRD open Q#5 |

---

## Handoff ke Sprint 2

Sprint 2 membangun **F-001 Case Management** di atas fondasi ini. Pastikan:

- Tabel `cases` dan `case_photos` siap untuk CRUD
- RBAC JUNIOR+ dapat memanggil endpoint cases
- Upload service (local/S3 intranet) terdefinisi di config
