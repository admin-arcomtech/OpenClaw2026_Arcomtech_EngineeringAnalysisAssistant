# Arcom Engineering Intelligence

> **AI‑Guided Manufacturing Investigation & Engineering Memory Platform**
> Mempercepat root cause analysis, mengurangi destructive trial, dan melestarikan pengetahuan engineering senior.

[![Pitch Deck](https://img.shields.io/badge/docs-PitchDeck-blue)](./pitchdeck.md)
[![PRD](https://img.shields.io/badge/docs-PRD-green)](./PRD.md)
[![Stack](https://img.shields.io/badge/stack-FastAPI%20%2B%20Next.js%2014%20%2B%20pgvector-purple)]()

> Lihat [`pitchdeck.md`](./pitchdeck.md) untuk problem statement, solution overview, arsitektur AI agent, fitur, dan roadmap.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + SQLAlchemy 2.0 + Alembic |
| Database | PostgreSQL 16 + pgvector (HNSW) |
| Frontend | Next.js 14 App Router + Tailwind CSS |
| AI Gateway | Openclaw (OpenAI‑compatible) + deterministic local fallback |
| Auth | JWT HS256 + bcrypt |
| Deploy | Docker Compose v2 |

---

## 1. Quick Start (Docker — direkomendasikan)

### Prasyarat

- **Docker** ≥ 24 + **Docker Compose v2** (`docker compose version`)
- Port bebas: `3000` (frontend), `8000` (backend), `5432` (postgres)
- (Opsional) **Openclaw Gateway** running di host pada port `18789` — kalau tidak ada, sistem otomatis pakai *local fallback*

### Langkah

```bash
# 1. Clone
git clone https://github.com/admin-arcomtech/OpenClaw2026_Arcomtech_EngineeringAnalysisAssistant.git arcom
cd arcom

# 2. (Opsional) buat .env di root untuk override default
cat > .env <<'EOF'
JWT_SECRET_KEY=ubah-rahasia-ini-saat-produksi
CORS_ORIGINS=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000

# Hanya jika Openclaw aktif
AI_ENABLED=true
OPENCLAW_BASE_URL=http://host.docker.internal:18789/v1
OPENCLAW_TOKEN=ganti-dengan-token-openclaw-anda
EOF

# 3. Jalankan seluruh stack
docker compose up -d --build

# 4. Cek status
docker compose ps
docker compose logs -f backend   # ikuti log sampai "Application startup complete"
```

Container yang aktif:

| Container | Port | Keterangan |
|-----------|------|------------|
| `arcom_postgres` | 5432 | PostgreSQL 16 + pgvector |
| `arcom_backend` | 8000 | FastAPI + Alembic migrations + seed otomatis |
| `arcom_frontend` | 3000 | Next.js 14 (dev mode di pilot intranet) |

Saat pertama kali start, backend akan:
1. `alembic upgrade head` — apply migrasi 001 sampai 005
2. `python seed.py` — buat 4 user seed (Junior, Senior, Manager, Admin)
3. `python seed_cases.py` — buat 12 kasus contoh
4. `python embed_existing.py` — generate embedding untuk kasus seed
5. Start uvicorn pada `:8000`

### Verifikasi

| URL | Yang dicek |
|-----|-----------|
| http://localhost:3000 | UI login |
| http://localhost:8000/api/health | `{"status":"ok","database":"ok"}` |
| http://localhost:8000/docs | Swagger UI (semua endpoint) |
| http://localhost:8000/api/ai/health | Status Openclaw vs fallback |

---

## 2. Seed Users — Login untuk testing

| Role | Employee ID | Password |
|------|-------------|----------|
| Junior Engineer | `EMP001` | `Junior@12345` |
| Senior Engineer | `EMP002` | `Senior@12345` |
| Engineering Manager | `EMP003` | `Manager@12345` |
| Admin | `EMP004` | `Admin@12345` |

> Ganti password user ini sebelum produksi. Admin dapat menambah user via `/admin/users`.

---

## 3. Use Case — Engineering Baru (End‑to‑End)

> Skenario: **Junior Engineer baru** menemukan abnormality "Nozzle Clog" di model X‑123 pada line A, shift PAGI. Berikut alur full investigasi sampai knowledge tersimpan.

### Step 1 — Buat kasus (Junior)

1. Buka **http://localhost:3000** → login `EMP001` / `Junior@12345`.
2. Tap **Buat Kasus Baru** di dashboard (atau bottom nav `Baru`).
3. Isi form:
   - **Model**: `X-123`
   - **Process**: `Print`
   - **Line**: `A`
   - **Fatal Error**: `Nozzle Clog`
   - **Symptom**: `Tinta tidak keluar pada nozzle 3 dan 7 setelah 2 jam runtime`
   - **Severity**: `HIGH`
   - **Shift**: `PAGI`
   - (Opsional) Upload max 5 foto evidence
4. Klik **Buat Kasus**.
5. Sistem akan:
   - Generate Case ID `IEI-YYYYMMDD-XXXX`
   - Auto‑embed kasus → cari kasus serupa (F‑002)
   - Kirim notifikasi ke Senior karena severity HIGH

### Step 2 — Lihat Similar Cases + AI Recommendations (Junior)

Di halaman detail kasus:

1. **Panel Similar Cases** otomatis menampilkan kasus historis dengan badge `similarity_pct`. Sumber ditampilkan: `openclaw` / `fallback` / `keyword`.
2. **AI Recommendations** menampilkan 3 hipotesis 4M1E:
   - Title, category (Man/Machine/Material/Method), confidence %, evidence list, suggested verifications, trial_risk.
3. Tap **Useful** / **Not Relevant** untuk feedback (menjadi sinyal training).

### Step 3 — Trial Queue (F‑004)

1. Buka tab **Trial Queue** atau di case detail klik **Generate Trial Priority**.
2. Sistem menampilkan queue trial diurutkan LOW‑risk dulu, dengan estimasi waktu & success rate dari kasus serupa.
3. **Reorder** (↑↓) jika perlu, lalu klik **Approve Queue**.
   - Jika ada trial **HIGH risk** → Junior diminta minta approval Senior.
   - Junior tidak bisa approve queue yang semua HIGH risk.

### Step 4 — Log Trial (F‑005)

1. Pilih item queue → **Log Trial**.
2. Form akan auto‑filled dari queue item (trial_action, risk_level).
3. Isi:
   - **Observation** (minimal 20 karakter)
   - **Outcome**: `IMPROVED` / `NO_CHANGE` / `WORSENED` / `INCONCLUSIVE`
   - **Improvement %**, **Time spent (min)**, **Scrap impact**
   - (Opsional) Upload max 3 foto evidence
4. Jika offline, draft otomatis tersimpan di `localStorage` (`trial-draft-{caseId}`).
5. Status case otomatis maju ke `TRIAL_RUNNING` saat outcome IMPROVED/WORSENED.

### Step 5 — Confirm Root Cause (Senior)

> Logout → login `EMP002` / `Senior@12345`.

1. Buka case yang sama (atau klik notifikasi bell).
2. Di panel **Konfirmasi Root Cause**, isi teks root cause (≥10 karakter).
3. Klik **Konfirmasi Root Cause**.
4. Sistem set `case.status = CONFIRMED`, `why_why_eligible = true`, lalu **auto‑embed root cause** ke knowledge base.

### Step 6 — Generate & Approve Why‑Why (F‑006)

1. Senior klik link **Why‑Why Analysis** di case detail (atau Junior buka `/cases/:id/why-why`).
2. Klik **Generate Why‑Why Draft** → AI menghasilkan minimal 5 level Why × 4M1E + immediate countermeasure + corrective + preventive action.
3. Edit jika perlu (semua field editable).
4. Junior klik **Kirim untuk Persetujuan** → status `PENDING_APPROVAL`, Senior dapat notifikasi.
5. Senior buka halaman Why‑Why → klik **Setujui** (atau **Tolak** dengan komentar).
6. Setelah disetujui → otomatis ter‑embed ke knowledge base & menjadi searchable di `/knowledge-base`.

### Step 7 — Archive (Senior/Manager)

1. Setelah monitoring stabil, advance status `CONFIRMED → ARCHIVED`.
2. Sistem set `archived_at`, lakukan **consolidated embedding** (full narrative + trials + Why‑Why).
3. Case menjadi read‑only.

### Step 8 — Knowledge reuse (Engineer berikutnya)

Saat ada engineer lain buat kasus baru dengan symptom serupa di model X‑123:

- Similar Cases panel **akan langsung memunculkan kasus ini** dengan root cause + Why‑Why approved.
- Trial Queue akan diranking dengan success rate dari trial yang sudah ada.
- AI recommendations akan reference countermeasure dari kasus arsip.

> **Loop knowledge** ini adalah esensi dari Engineering Memory Engine (F‑007).

---

## 4. Use Case — Manager & Admin

### Manager (`EMP003`)

| Aksi | Lokasi |
|------|--------|
| Lihat KPI dashboard (TTRC, AI usefulness %, KB growth) | `/dashboard` (cards atas) |
| Lihat semua kasus & filter status | `/cases` |
| Lihat audit & analytics admin | `/admin` |
| Buka knowledge base | bottom nav **KB** atau `/knowledge-base` |

### Admin (`EMP004`)

| Aksi | Lokasi |
|------|--------|
| CRUD users (role, division, aktif/nonaktif) | `/admin/users` |
| Import CSV historical Why-Why (dry-run dulu) | `/admin/import` |
| Audit log (immutable, viewer only) | `/admin/audit` |
| Lihat env AI settings | `/admin/settings` |

CSV import format (kolom wajib): `model, fatal_error, symptom, root_cause`
Kolom opsional: `process, line, title, severity, temporary_action`.

---

## 5. Smoke Test (CLI)

```bash
# Health check
curl http://localhost:8000/api/health

# Login → ambil token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"employee_id":"EMP002","password":"Senior@12345"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# /me
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/auth/me

# List cases
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/cases

# Knowledge base search
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/knowledge/search?q=nozzle"

# AI provider status
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/ai/health
```

---

## 6. Local Development (tanpa Docker)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Setup DB (butuh PostgreSQL + pgvector lokal)
export DATABASE_URL=postgresql://arcom_user:arcom_pass@localhost:5432/arcom_db
alembic upgrade head
python seed.py
python seed_cases.py

# Jalankan
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

### Run tests

```bash
cd backend
pytest -q
```

---

## 7. Openclaw Gateway (opsional, untuk AI penuh)

Tanpa Openclaw, sistem tetap jalan menggunakan **deterministic local fallback** (embedding hash + rule‑based 4M1E generator). Untuk AI penuh:

### Catatan penting — Gateway bind & embeddings

Openclaw Gateway secara default bind ke `127.0.0.1` (loopback), sehingga **tidak dapat dijangkau dari container Docker**. Dua solusi:

**A. Relay via socat** (paling sederhana, sudah dipakai pada deploy ini):

```bash
sudo apt-get install -y socat
# Jalankan relay 0.0.0.0:18790 → 127.0.0.1:18789
nohup socat TCP-LISTEN:18790,fork,reuseaddr,bind=0.0.0.0 TCP:127.0.0.1:18789 \
  > /tmp/openclaw-relay.log 2>&1 &
# Pakai port 18790 di .env:
# OPENCLAW_BASE_URL=http://host.docker.internal:18790/v1
```

Atau jadikan systemd service (lihat `deploy/openclaw-relay.service` di repo).

**B. Konfigurasi Openclaw bind 0.0.0.0** (jika gateway mendukung — periksa dokumentasi versi anda).

### Embedding tidak didukung oleh upstream LLM?

Beberapa upstream provider Openclaw (mis. model lokal kecil) tidak expose endpoint `/v1/embeddings`. Set:

```bash
OPENCLAW_EMBEDDINGS_ENABLED=false
```

Hasilnya: chat completion (recommendations & Why‑Why) tetap pakai LLM Openclaw, sedangkan embedding (similar cases & KB search) pakai fallback deterministik 1536d. Ini direkomendasikan untuk pilot.

### Langkah setup

1. **Install & jalankan Openclaw Gateway** pada host:

   ```bash
   openclaw gateway --port 18789
   ```

2. **Aktifkan endpoint OpenAI‑compatible** di `~/.openclaw/openclaw.json`:

   ```json
   {
     "gateway": {
       "auth": { "mode": "token", "token": "GANTI_TOKEN" },
       "http": {
         "endpoints": {
           "chatCompletions": { "enabled": true },
           "responses":       { "enabled": true }
         }
       }
     }
   }
   ```

3. **Konfigurasi upstream provider** di Openclaw (OpenAI / Ollama / Anthropic / lokal).

4. Set di `.env`:

   ```bash
   AI_ENABLED=true
   # Gunakan port relay (lihat di atas), bukan 18789
   OPENCLAW_BASE_URL=http://host.docker.internal:18790/v1
   OPENCLAW_TOKEN=token-dari-openclaw.json
   # Set false jika upstream tidak punya endpoint embeddings
   OPENCLAW_EMBEDDINGS_ENABLED=false
   ```

5. Restart backend: `docker compose restart backend`.

Verifikasi:

```bash
curl -H "Authorization: Bearer $JWT" http://localhost:8000/api/ai/health
```

Output:

```json
{
  "openclaw_configured": true,
  "openclaw_reachable": true,
  "openclaw_chat_reachable": true,
  "openclaw_embed_reachable": false,
  "embeddings_via_primary": false,
  "fallback_available": true
}
```

Response `/api/ai/recommendations` akan punya `source: "openclaw"`.

---

## 8. Project Structure

```
arcom/
├── backend/
│   ├── app/
│   │   ├── core/              # config, db, security, logging
│   │   ├── models/            # ORM: User, Case, Trial, WhyWhy, ...
│   │   ├── schemas/           # Pydantic v2
│   │   ├── routers/           # auth, cases, ai, trials, why_why,
│   │   │                      # knowledge, notifications, admin
│   │   ├── services/          # business logic, AI providers
│   │   │   ├── embedding_service.py
│   │   │   ├── knowledge_service.py
│   │   │   ├── knowledge_search.py
│   │   │   ├── why_why_service.py
│   │   │   ├── trial_priority.py
│   │   │   ├── timeline_service.py
│   │   │   ├── import_service.py
│   │   │   └── kpi_service.py
│   │   ├── ai/
│   │   │   ├── providers.py   # Openclaw + Fallback
│   │   │   └── prompts/       # System prompts
│   │   └── main.py
│   ├── alembic/versions/      # 001 → 005
│   ├── tests/                 # pytest
│   ├── seed.py, seed_cases.py, embed_existing.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/(app)/
│   │   ├── dashboard/
│   │   ├── cases/[id]/
│   │   │   ├── trials/
│   │   │   └── why-why/
│   │   ├── knowledge-base/
│   │   └── admin/
│   │       ├── users/
│   │       ├── import/
│   │       ├── audit/
│   │       └── settings/
│   ├── components/
│   │   ├── ai/                # SimilarCasesPanel, AIRecommendationsPanel
│   │   ├── trials/            # TrialQueuePanel, LogTrialModal, CaseTimeline
│   │   ├── nav/               # BottomNav, NotificationBell
│   │   └── ui/                # StatusBadge, Toast, OfflineBanner, ErrorBoundary
│   ├── lib/
│   │   ├── api.ts             # API client (auth, cases, AI, trials, why-why, KB, admin)
│   │   ├── auth.ts
│   │   ├── useAuth.ts
│   │   └── trialDraft.ts      # offline trial draft
│   ├── next.config.mjs
│   └── Dockerfile
├── docker-compose.yml
├── pitchdeck.md               # Pitch deck (problem, solution, AI workflow, stack, impact)
├── PRD.md
├── sprints/
│   ├── sprint-01-foundation.md
│   ├── sprint-02-case-management.md
│   ├── sprint-03-ai-core.md
│   ├── sprint-04-investigation-workflow.md
│   └── sprint-05-completion-launch.md
└── README.md                  # ← file ini
```

---

## 9. API Endpoints — Ringkasan

| Method | Path | Role | Fitur |
|--------|------|------|-------|
| POST | `/api/auth/login` | — | Login |
| GET | `/api/auth/me` | * | Profil |
| POST | `/api/cases` | * | Buat case (F‑001) |
| GET | `/api/cases` | * | List + filter |
| GET | `/api/cases/{id}` | * | Detail |
| POST | `/api/cases/{id}/photos` | * | Upload foto |
| POST | `/api/cases/{id}/confirm` | Senior+ | Konfirmasi root cause |
| POST | `/api/cases/{id}/status` | * | Status transition |
| GET | `/api/cases/{id}/timeline` | * | Timeline |
| GET/PUT | `/api/cases/{id}/trial-queue` | * | Queue read/save |
| POST | `/api/cases/{id}/trial-queue/approve` | * | Approve queue |
| GET/POST | `/api/cases/{id}/trials` | * | List/Log trial (F‑005) |
| GET/PUT | `/api/cases/{id}/why-why` | * | Why‑Why read/edit |
| POST | `/api/cases/{id}/why-why/submit` | * | Submit approval |
| POST | `/api/cases/{id}/why-why/approve` | Senior+ | Approve/reject |
| POST | `/api/ai/similar-cases` | * | F‑002 |
| POST | `/api/ai/recommendations` | * | F‑003 |
| POST | `/api/ai/trial-priority` | * | F‑004 |
| POST | `/api/ai/why-why-draft` | * | F‑006 generate |
| POST | `/api/ai/feedback` | * | AI feedback |
| GET | `/api/ai/health` | * | Provider status |
| GET | `/api/knowledge/search` | * | KB search (F‑007) |
| GET | `/api/knowledge/metrics` | Manager+ | KB metrics |
| GET | `/api/notifications` | * | List |
| POST | `/api/notifications/{id}/read` | * | Mark read |
| GET/POST/PATCH | `/api/admin/users` | Admin | CRUD user |
| GET | `/api/admin/audit` | Admin | Audit log |
| POST | `/api/admin/import` | Admin | CSV import |
| GET | `/api/admin/kpis` | Manager+ | KPI metrics |

Swagger lengkap: **http://localhost:8000/docs**

---

## 10. Troubleshooting

| Gejala | Penyebab umum | Solusi |
|--------|---------------|--------|
| Backend restart loop saat migration | Volume DB lama tidak compatible | `docker compose down -v && docker compose up -d` |
| `password cannot be longer than 72 bytes` | bcrypt mismatch | Pastikan `bcrypt==4.0.1` di requirements (sudah di‑pin) |
| Frontend 502 / blank | Next.js belum siap (npm install) | Tunggu ~30s saat first boot; cek `docker logs arcom_frontend` |
| AI `source: "fallback"` terus | Openclaw down / belum dikonfigurasi | Cek `/api/ai/health` → `openclaw_reachable` |
| Similar cases kosong | KB masih < 10 kasus | UI munculkan warning; tambah case atau import CSV historis |
| Login gagal | Password berubah pasca seed | `docker exec arcom_postgres psql -U arcom_user -d arcom_db -c "DELETE FROM users"` lalu restart backend |

---

## 11. Sprint Roadmap

| Sprint | Scope | Status | PR |
|--------|-------|--------|----|
| 1 — Foundation | Auth, DB, nav shell | ✅ | #6 |
| 2 — Case Management | F‑001 CRUD + photos + duplicate | ✅ | #7 |
| 3 — AI Core | F‑002 similar, F‑003 advisor, Openclaw integ | ✅ | #8 |
| 4 — Investigation Workflow | F‑004 trials, F‑005, status machine, F‑007 indexing | ✅ | #9 |
| 5 — Completion & Launch | F‑006 Why‑Why, KB search, admin, NFR, deploy | ✅ | #10 |

---

## 12. Dokumen terkait

- **[pitchdeck.md](./pitchdeck.md)** — Problem, solution, AI workflow, tech stack, future development
- **[PRD.md](./PRD.md)** — Product Requirements Document
- **[sprints/](./sprints/)** — Per‑sprint detail (Sprint 1 → 5)

---

*Stop guessing — start retrieving. Engineer pakai memori pabrik, bukan memori pribadi.*
