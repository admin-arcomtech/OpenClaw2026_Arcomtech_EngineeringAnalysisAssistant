# Arcom Engineering Intelligence

> **AI‑Guided Manufacturing Investigation & Engineering Memory Platform**
> Mempercepat root cause analysis, mengurangi destructive trial, dan melestarikan pengetahuan engineering senior.

[![Pitch Deck](https://img.shields.io/badge/docs-PitchDeck-blue)](./pitchdeck.md)
[![PRD](https://img.shields.io/badge/docs-PRD-green)](./PRD.md)
[![Stack](https://img.shields.io/badge/stack-FastAPI%20%2B%20Next.js%2014%20%2B%20pgvector-purple)]()

> Lihat [`pitchdeck.md`](./pitchdeck.md) untuk problem statement, solution overview, arsitektur AI agent, fitur, dan roadmap.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [How to Setup](#how-to-setup) — install & jalankan aplikasi
  - [1. Prasyarat](#1-prasyarat)
  - [2. Setup Dasar (3 Perintah)](#2-setup-dasar-3-perintah)
  - [3. Verifikasi Instalasi](#3-verifikasi-instalasi)
  - [4. Setup AI (Opsional — Openclaw)](#4-setup-ai-opsional--openclaw)
  - [5. Konfigurasi Network LAN / Pilot Intranet](#5-konfigurasi-network-lan--pilot-intranet)
  - [6. Local Development (tanpa Docker)](#6-local-development-tanpa-docker)
  - [7. Troubleshooting Setup](#7-troubleshooting-setup)
- [How to Use this App](#how-to-use-this-app) — workflow E2E per role
  - [Akun Pilot (Login)](#akun-pilot-login)
  - [A. Workflow Junior Engineer (Engineer Baru)](#a-workflow-junior-engineer-engineer-baru)
  - [B. Workflow Senior Engineer](#b-workflow-senior-engineer)
  - [C. Workflow Engineering Manager](#c-workflow-engineering-manager)
  - [D. Workflow Admin](#d-workflow-admin)
  - [Tips Penggunaan](#tips-penggunaan)
- [Reference](#reference)

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

# How to Setup

## 1. Prasyarat

| Wajib | Versi minimum | Cek |
|-------|--------------|-----|
| Docker Engine | 24.x | `docker --version` |
| Docker Compose v2 | 2.20.x | `docker compose version` |
| Port bebas | 3000, 8000, 5432 | `ss -tlnp \| grep -E '3000\|8000\|5432'` |
| Disk space | ≥ 3 GB | `df -h .` |
| Memory | ≥ 2 GB | `free -h` |

| Opsional | Untuk |
|----------|-------|
| Openclaw Gateway (port 18789) | AI penuh (recommendations + Why‑Why) |
| `socat` | Bridge Openclaw ke Docker (lihat §4) |

Tanpa Openclaw, aplikasi tetap jalan menggunakan **deterministic local fallback** (embedding hash 1536d + rule‑based 4M1E generator).

---

## 2. Setup Dasar (3 Perintah)

```bash
# 1. Clone repository
git clone https://github.com/admin-arcomtech/OpenClaw2026_Arcomtech_EngineeringAnalysisAssistant.git arcom
cd arcom

# 2. Build & jalankan seluruh stack (Postgres + Backend + Frontend)
docker compose up -d --build

# 3. Tunggu ~60 detik, lalu cek health
curl http://localhost:8000/api/health
# Expected: {"status":"ok","database":"ok"}
```

Saat pertama kali start, backend akan otomatis menjalankan:

| Step | Skrip | Hasil |
|------|-------|-------|
| 1 | `alembic upgrade head` | Apply migrasi DB 001 → 005 |
| 2 | `python seed.py` | Buat 4 user pilot (Junior, Senior, Manager, Admin) |
| 3 | `python seed_cases.py` | Buat 12 kasus contoh |
| 4 | `python embed_existing.py` | Generate embedding untuk kasus seed |
| 5 | `uvicorn app.main:app --host 0.0.0.0` | Start API di port 8000 |

> Total waktu first boot: **~60–120 detik** tergantung kecepatan disk dan apakah Openclaw aktif.

---

## 3. Verifikasi Instalasi

| URL | Expected | Yang dicek |
|-----|----------|-----------|
| http://localhost:3000 | Halaman login | Frontend UI |
| http://localhost:8000/api/health | `{"status":"ok"}` | Backend + DB |
| http://localhost:8000/docs | Swagger UI | Semua endpoint |
| http://localhost:8000/api/ai/health *(perlu token)* | JSON status AI | Provider AI |

Tes login API (CLI):

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"employee_id":"EMP004","password":"Admin@12345"}'
# Expected: {"access_token":"eyJ...","token_type":"bearer","expires_in_hours":8}
```

Tes login UI: buka http://localhost:3000, klik **"Belum punya akun / Lihat akun pilot demo"**, pilih salah satu akun → otomatis terisi → klik **Masuk**.

---

## 4. Setup AI (Opsional — Openclaw)

Kalau Anda **tidak punya Openclaw**, skip bagian ini — aplikasi sudah jalan dengan fallback.

### 4.1 Install Openclaw Gateway di host

```bash
openclaw gateway --port 18789
```

Konfigurasi `~/.openclaw/openclaw.json`:

```json
{
  "gateway": {
    "auth": { "mode": "token", "token": "GANTI_TOKEN_ANDA" },
    "http": {
      "endpoints": {
        "chatCompletions": { "enabled": true },
        "responses":       { "enabled": true }
      }
    }
  }
}
```

Lalu konfigurasi upstream LLM (OpenAI / Ollama / Anthropic) di Openclaw.

### 4.2 Setup relay (karena Openclaw bind ke 127.0.0.1)

Openclaw Gateway default bind ke loopback, **tidak bisa dijangkau dari Docker container**. Pakai socat relay:

```bash
# Install socat
sudo apt-get install -y socat

# Mode 1 — manual (sekali pakai)
nohup socat TCP-LISTEN:18790,fork,reuseaddr,bind=0.0.0.0 \
  TCP:127.0.0.1:18789 > /tmp/openclaw-relay.log 2>&1 &

# Mode 2 — systemd service (persist setelah reboot, RECOMMENDED)
sudo cp deploy/openclaw-relay.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now openclaw-relay
systemctl status openclaw-relay
```

### 4.3 Set environment variable

Buat file `.env` di root project:

```bash
cat > .env <<'EOF'
JWT_SECRET_KEY=ubah-rahasia-ini-saat-produksi
CORS_ORIGINS=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000

AI_ENABLED=true
OPENCLAW_BASE_URL=http://host.docker.internal:18790/v1
OPENCLAW_TOKEN=token-yang-sama-dengan-openclaw.json

# Set false jika upstream LLM tidak punya endpoint /v1/embeddings
# (chat tetap pakai Openclaw, embedding pakai fallback deterministik 1536d)
OPENCLAW_EMBEDDINGS_ENABLED=false
EOF
```

### 4.4 Restart & verifikasi

```bash
docker compose restart backend
sleep 10

# Login → ambil token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"employee_id":"EMP002","password":"Senior@12345"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Cek AI health
curl -s http://localhost:8000/api/ai/health -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

Expected:

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

`openclaw_chat_reachable: true` berarti **AI Recommendations & Why‑Why Draft sudah pakai LLM nyata**.

---

## 5. Konfigurasi Network LAN / Pilot Intranet

### Akses dari mesin yang sama (developer)

Pakai `http://localhost:3000` — sudah otomatis.

### Akses dari laptop lain di LAN (pilot factory)

Frontend mendeteksi hostname browser **secara runtime**, jadi tidak perlu rebuild:

1. Cari IP server: `hostname -I | awk '{print $1}'` → mis. `10.11.8.231`
2. Buka di browser laptop pilot: `http://10.11.8.231:3000`
3. Login akan otomatis hit `http://10.11.8.231:8000` (sama hostname dengan UI).

> Pastikan port 3000 + 8000 + 5432 tidak diblokir firewall server: `sudo ufw allow 3000,8000/tcp`.

CORS sudah longgar saat `APP_ENV != production` untuk pilot intranet. Untuk produksi: set `APP_ENV=production` dan whitelist origin spesifik di `CORS_ORIGINS`.

---

## 6. Local Development (tanpa Docker)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Setup DB (butuh PostgreSQL 16 + pgvector lokal)
export DATABASE_URL=postgresql://arcom_user:arcom_pass@localhost:5432/arcom_db
alembic upgrade head
python seed.py
python seed_cases.py

uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

### Run unit tests

```bash
cd backend
pytest -q
```

---

## 7. Troubleshooting Setup

| Gejala | Penyebab | Solusi |
|--------|----------|--------|
| `curl: (56) Connection reset` saat login | Backend masih running seed | Tunggu 60–120s, cek `docker logs arcom_backend` sampai `Uvicorn running` |
| Backend restart loop, error enum | Volume DB lama tidak compatible | `docker compose down -v && docker compose up -d` |
| Login UI tidak respond | `NEXT_PUBLIC_API_URL` tidak reachable dari browser | Cek DevTools Network tab. Akses UI dengan hostname/IP yang sama dengan API |
| Login 401 padahal password benar | Akun belum diseed atau password berubah | `docker exec arcom_backend python seed.py` |
| `openclaw_reachable: false` | Gateway bind 127.0.0.1, container tidak bisa reach | Setup socat relay (§4.2) |
| `openclaw_embed_reachable: false` | Upstream LLM tidak ada `/v1/embeddings` | Set `OPENCLAW_EMBEDDINGS_ENABLED=false` (chat tetap jalan) |
| `Failed to fetch` / CORS error di browser | UI dari host berbeda dengan API | `lib/api.ts` sudah handle otomatis. Restart frontend `docker restart arcom_frontend` |
| Frontend 502 / blank ~30s | npm install masih jalan first‑boot | `docker logs arcom_frontend` → tunggu `✓ Ready` |
| `password cannot be longer than 72 bytes` | bcrypt 5.x incompatible | `bcrypt==4.0.1` sudah dipin |

---

# How to Use this App

## Akun Pilot (Login)

Saat pertama kali start, 4 akun pilot otomatis diseed:

| Role | Employee ID | Password | Akses |
|------|-------------|----------|-------|
| Junior Engineer | `EMP001` | `Junior@12345` | Buat case, lihat AI, log trial, draft Why‑Why |
| Senior Engineer | `EMP002` | `Senior@12345` | Junior + konfirmasi root cause, approve Why‑Why |
| Engineering Manager | `EMP003` | `Manager@12345` | Senior + dashboard KPI, knowledge metrics |
| Admin | `EMP004` | `Admin@12345` | User CRUD, audit log, CSV import |

> ⚠ Self‑registration **tidak tersedia** (sesuai PRD §4 RBAC ISP/SIDM). Akun baru dibuat oleh **Admin** via `/admin/users`.

**Cara login UI:**
1. Buka http://localhost:3000 (atau http://IP_SERVER:3000 dari laptop pilot)
2. Klik tombol **"Belum punya akun / Lihat akun pilot demo"** di bawah form
3. Pilih salah satu akun → otomatis terisi Employee ID + Password
4. Klik **Masuk**

---

## A. Workflow Junior Engineer (Engineer Baru)

> Skenario: Junior baru menemukan abnormality **"Nozzle Clog"** di model `X-123` line A pada shift PAGI. Total durasi flow: ±15 menit (dengan AI Openclaw, ±5 menit dengan fallback).

### Step 1 — Login sebagai Junior

- Login `EMP001` / `Junior@12345` → masuk ke Dashboard.
- Dashboard menampilkan jumlah case Terbuka / Investigasi / Selesai dan 5 case terbaru.

### Step 2 — Buat Case Baru (F‑001)

Klik tombol **"+ Buat Kasus Baru"** atau bottom nav **Baru**, isi:

| Field | Wajib | Contoh |
|-------|-------|--------|
| Model | ✓ | `X-123` (atau dropdown `IJP-A1`, `SIDM-C1`, …) |
| Process | ✓ | `Print` |
| Line | ✓ | `A` |
| Fatal Error | ✓ | `Nozzle Clog` |
| Symptom | ✓ | `Tinta tidak keluar pada nozzle 3 dan 7 setelah 2 jam runtime`<br>(max 500 char) |
| Severity | ✓ | `HIGH` |
| Shift | – | `PAGI` |
| Foto evidence | – | max 5 foto × 10MB (JPG/PNG/WebP) |
| Temporary Action | – | mis. `Stop line, isolasi unit` |

Klik **Buat Kasus**. Sistem akan:

1. Generate Case ID **`IEI-YYYYMMDD-XXXX`**
2. Auto‑embed kasus dan **cari kasus serupa** (F‑002) di background
3. **Notifikasi Senior** jika severity HIGH/CRITICAL (bell icon di pojok kanan atas)
4. Redirect ke halaman detail kasus

### Step 3 — Pelajari Similar Cases (F‑002)

Di halaman detail kasus, **panel Similar Cases** otomatis muncul:

- Kartu kasus historis dengan **similarity %** (mis. `82%`)
- Badge sumber: `openclaw` / `fallback` / `keyword`
- Klik kartu → buka detail kasus historis (siapa investigator, root cause, countermeasure)
- Klik **Useful** / **Not Relevant** → feedback dipakai untuk meningkatkan ranking (PRD F‑002)

### Step 4 — Baca AI Recommendations (F‑003)

Panel **AI Recommendations** menampilkan **3 hipotesis 4M1E**:

```
1. Feeder unit aus/kotor menyebabkan feed jam periodik
   Category: Machine | Confidence: 60% | Trial Risk: LOW
   Evidence:
     - Symptom dilaporkan pada feeder section
     - Kasus serupa IEI-20260512-0009 menyebutkan roller wear
   Suggested Verification:
     - Inspect roller wear pattern
     - Cek tension feeder
     - Periksa ketebalan material vs spec

2. Variasi material …
3. Parameter metode feeding …
```

- **Confidence + Evidence + Verification wajib ditampilkan** (PRD AI Safety rule)
- Sumber: badge `openclaw` (AI nyata) atau `fallback` (rule‑based 4M1E)
- Klik **Useful** / **Already Tried** untuk feedback

### Step 5 — Generate & Approve Trial Queue (F‑004)

Di panel **Trial Queue** → klik **Generate dari AI**:

- Sistem score setiap trial: `priority = (1/risk) × success_rate × (1/time)`
- Trial **LOW risk** muncul duluan
- Klik ↑↓ untuk reorder manual
- Klik **Setujui Queue** → status `DRAFT → APPROVED`

> ⚠ Kalau ada trial **HIGH risk**, Junior **tidak bisa approve sendiri** — perlu Senior.

### Step 6 — Log Trial (F‑005)

Klik **Log Trial** dari item queue (form auto‑filled):

| Field | Catatan |
|-------|---------|
| Trial Action | auto‑filled dari queue |
| Observation | **min 20 karakter** |
| Outcome | `IMPROVED` / `NO_CHANGE` / `WORSENED` / `INCONCLUSIVE` |
| Improvement % | numeric, 0–100 |
| Time spent (min) | berapa menit dihabiskan |
| Scrap Impact + Qty | jika ada scrap |
| Foto evidence | max 3 foto |
| Risk level | dari queue, dapat diubah |

Saat outcome **IMPROVED/WORSENED**, status case otomatis advance ke `TRIAL_RUNNING`.

> Tip offline: jika WiFi mati saat ngetik, draft tersimpan di browser localStorage. Saat online, klik **Submit** akan kirim ulang.

### Step 7 — Update Status

Tombol di panel Status:
- `OPEN → INVESTIGATING` (klik mulai investigasi)
- `INVESTIGATING → SUSPECTED_CAUSE` (sudah punya hipotesis)
- `SUSPECTED_CAUSE → TRIAL_RUNNING` (sudah jalan trial)
- `TRIAL_RUNNING → MONITORING` (sudah verifikasi, tunggu konfirmasi Senior)

`CONFIRMED` dan `ARCHIVED` hanya bisa di‑transition oleh Senior+.

### Step 8 — Generate Why‑Why Draft (F‑006) — setelah root cause confirmed

Setelah Senior konfirmasi root cause (Step B.2), Junior bisa buka link **Why‑Why Analysis** dari case detail atau langsung ke `/cases/:id/why-why`:

1. Klik **Generate Why‑Why Draft** → AI buat ≥5 level Why × 4M1E + immediate countermeasure + corrective + preventive action (dalam ±30 detik via Openclaw, atau instant via fallback)
2. Edit setiap field (Why pertanyaan & jawaban, category 4M1E)
3. Klik **Simpan Draft** untuk auto‑save sementara
4. Klik **Kirim untuk Persetujuan** → status `PENDING_APPROVAL`, Senior dapat notifikasi

---

## B. Workflow Senior Engineer

> Skenario: Senior `EMP002` menerima notifikasi case HIGH severity dari Junior dan harus konfirmasi root cause + approve Why‑Why.

### Step 1 — Lihat Notifikasi

- Klik **bell icon** di kanan atas (badge angka = unread count)
- Daftar notifikasi:
  - `case.high_severity` → kasus baru HIGH severity
  - `why_why.pending_approval` → Why‑Why menunggu approve
- Klik **Lihat kasus** untuk langsung navigate

### Step 2 — Konfirmasi Root Cause (Senior‑Only)

Buka case → scroll ke panel hijau **"Konfirmasi Root Cause"**:

1. Isi root cause (min 10 karakter), mis. `Roller feeder #2 aus menyebabkan slip → feed jam`
2. Klik **Konfirmasi Root Cause**
3. Sistem set `status = CONFIRMED`, `confirmed_by = Anda`, `why_why_eligible = true`
4. Auto‑embed root cause ke knowledge base (background task)

### Step 3 — Approve / Reject Why‑Why

Saat dapat notifikasi `why_why.pending_approval`:

1. Buka case → klik **Why‑Why Analysis**
2. Review setiap level Why + 4M1E mapping
3. Edit langsung kalau ada koreksi minor (status balik ke `DRAFT` kalau diedit)
4. Klik **Setujui** → status `APPROVED` → auto‑embed ke knowledge base ✅
5. Atau klik **Tolak** → masukkan komentar → status `REJECTED`, Junior dapat notifikasi untuk revisi

### Step 4 — Archive case setelah monitoring

Setelah trial monitoring stabil (mis. 1 minggu produksi normal):

1. Di case detail, klik tombol **Archive** (status `CONFIRMED → ARCHIVED`)
2. Sistem set `archived_at`, lakukan **consolidated embedding** (full narrative + trials + Why‑Why)
3. Kasus jadi **read‑only** — knowledge tersimpan permanen untuk engineer lain

---

## C. Workflow Engineering Manager

> Skenario: Manager `EMP003` perlu melihat metrics KPI dan trend investigasi.

### Step 1 — Dashboard KPI

Login → Dashboard menampilkan kartu Manager‑only:

| KPI | Sumber |
|-----|--------|
| **AI Berguna %** | `useful_feedback / total_feedback` |
| **Avg TTRC (jam)** | `mean(case.confirmed_at - case.created_at)` |
| Indexed cases | Total kasus ber‑embedding |
| Archived cases | Total kasus ARCHIVED |

### Step 2 — Knowledge Base Search

Bottom nav **KB** → halaman `/knowledge-base`:

- Kotak search → cari symptom / fatal error / root cause (mis. `nozzle clog`)
- Filter model
- Hasil menampilkan kartu dengan **similarity %** (vector) atau keyword match
- Kartu menunjukkan ikon `✓ Why-Why` jika kasus punya Why‑Why approved
- Klik kartu → buka case detail historis (read‑only kalau ARCHIVED)

### Step 3 — Review semua case

- Bottom nav **Kasus** → lihat semua case dengan filter status
- Filter berdasarkan status, model, severity, dst

---

## D. Workflow Admin

> Skenario: Admin `EMP004` perlu setup user baru dan migrasi data historis dari Excel/CSV.

### Step 1 — Buat User Baru

Bottom nav **Admin** → **Manajemen User** (`/admin/users`):

1. Isi form:
   - `employee_id` (unik, mis. `EMP005`)
   - `full_name`
   - `email` (opsional)
   - `division` (opsional, mis. `IJP-Production`)
   - `role`: `JUNIOR` / `SENIOR` / `MANAGER` / `ADMIN`
   - `password` (default: `changeme123`, user wajib ganti pada login pertama — TODO Phase 2)
2. Klik **Tambah User**
3. User langsung bisa login

Klik **Aktif/Nonaktif** untuk soft delete (kasus existing milik user tetap utuh).

### Step 2 — Batch Import Historical Data (`/admin/import`)

Untuk migrasi Excel/CSV historis (mis. Why‑Why 2 tahun terakhir):

1. Siapkan file CSV dengan kolom **wajib**:
   - `model, fatal_error, symptom, root_cause`
   - Kolom **opsional**: `process, line, title, severity, temporary_action`
2. Upload file → **centang "Dry-run"** dulu untuk validasi (TIDAK insert)
3. Lihat hasil validasi (total rows, errors, warnings)
4. Uncheck dry-run → klik **Import** → kasus dibuat dengan status `ARCHIVED` + `confirmed_root_cause` di‑set + auto‑embed ke knowledge base

Contoh CSV:

```csv
model,fatal_error,symptom,root_cause,process,line
IJP-A1,Nozzle Clog,"Nozzle 5 buntu setelah 4 jam","Filter inlet kotor, diganti","Print","A"
SIDM-C1,Motor Fault,"Motor servo overheat","Cooling fan rusak, replace","Assembly","C"
```

### Step 3 — Audit Log (`/admin/audit`)

Lihat semua aksi terjadi di sistem (immutable log):

- `auth.login_success` / `auth.login_failed`
- `case.created` / `case.status_changed` / `case.root_cause_confirmed`
- `trial_queue.approved`
- `why_why.submitted` / `why_why.approved` / `why_why.rejected`
- `case.photo_uploaded`

Filter by event name. Audit log **tidak bisa di‑edit/delete** dari UI maupun API.

### Step 4 — AI Settings (`/admin/settings`)

Menampilkan env vars AI aktif (read‑only di UI). Untuk ubah, edit `.env` di server lalu `docker compose restart backend`.

---

## Tips Penggunaan

| Tip | Detail |
|-----|--------|
| **Bahasa Indonesia first** | Semua UI label & AI response default Bahasa Indonesia. Engineer factory lebih nyaman. |
| **Mobile‑first** | UI dioptimasi untuk tablet 10" / smartphone. Tombol min height 48px (touch target). |
| **Offline trial draft** | Saat WiFi mati di line, trial draft otomatis disimpan di browser. Reload saat online untuk submit. |
| **AI source badge** | Selalu lihat badge `openclaw` vs `fallback` di setiap rekomendasi. Fallback = no‑LLM mode, akurasi lebih rendah. |
| **HIGH severity → Senior notif** | Selalu set severity benar saat buat case. Sistem otomatis notif Senior. |
| **Feedback loop** | Klik **Useful** / **Not Relevant** sesering mungkin — sistem belajar dari feedback. |
| **Knowledge base growth** | Setiap kasus yang di‑archive memperkaya KB. Target pilot: archive ≥20 kasus dalam minggu pertama. |
| **Why‑Why approval gate** | Why‑Why baru ter‑index ke KB **setelah Senior approve**. Encourage Senior untuk review tepat waktu. |

---

# Reference

## API Endpoints — Ringkasan

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
| GET | `/api/cases/{id}/timeline` | * | Timeline aktivitas |
| GET/PUT | `/api/cases/{id}/trial-queue` | * | Queue read/save |
| POST | `/api/cases/{id}/trial-queue/approve` | * | Approve queue |
| GET/POST | `/api/cases/{id}/trials` | * | List/Log trial (F‑005) |
| GET/PUT | `/api/cases/{id}/why-why` | * | Why‑Why read/edit |
| POST | `/api/cases/{id}/why-why/submit` | * | Submit untuk approval |
| POST | `/api/cases/{id}/why-why/approve` | Senior+ | Approve/reject |
| POST | `/api/ai/similar-cases` | * | F‑002 |
| POST | `/api/ai/recommendations` | * | F‑003 |
| POST | `/api/ai/trial-priority` | * | F‑004 |
| POST | `/api/ai/why-why-draft` | * | F‑006 generate |
| POST | `/api/ai/feedback` | * | AI feedback |
| GET | `/api/ai/health` | * | Provider status |
| GET | `/api/knowledge/search` | * | KB search (F‑007) |
| GET | `/api/knowledge/metrics` | Manager+ | KB metrics |
| GET | `/api/notifications` | * | List notifikasi |
| POST | `/api/notifications/{id}/read` | * | Mark read |
| GET/POST/PATCH | `/api/admin/users` | Admin | CRUD user |
| GET | `/api/admin/audit` | Admin | Audit log |
| POST | `/api/admin/import` | Admin | CSV import |
| GET | `/api/admin/kpis` | Manager+ | KPI metrics |

Swagger lengkap: **http://localhost:8000/docs**

## Project Structure

```
arcom/
├── backend/
│   ├── app/
│   │   ├── core/              # config, db, security, logging
│   │   ├── models/            # ORM: User, Case, Trial, WhyWhy, …
│   │   ├── schemas/           # Pydantic v2
│   │   ├── routers/           # auth, cases, ai, trials, why_why,
│   │   │                      # knowledge, notifications, admin
│   │   ├── services/          # business logic (embed, knowledge,
│   │   │                      # trial_priority, why_why, kpi, import)
│   │   ├── ai/
│   │   │   ├── providers.py   # Openclaw + Fallback
│   │   │   └── prompts/
│   │   └── main.py
│   ├── alembic/versions/      # 001 → 005
│   ├── tests/                 # pytest
│   ├── seed.py, seed_cases.py, embed_existing.py
│   └── Dockerfile
├── frontend/
│   ├── app/(app)/             # dashboard, cases/, knowledge-base/, admin/
│   ├── components/            # ai/, trials/, nav/, ui/
│   ├── lib/                   # api.ts, auth.ts, useAuth.ts, trialDraft.ts
│   └── next.config.mjs
├── deploy/
│   └── openclaw-relay.service # systemd unit untuk relay
├── docker-compose.yml
├── pitchdeck.md
├── PRD.md
├── sprints/
└── README.md
```

## Smoke Test (CLI lengkap)

```bash
# Health
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

# AI provider status
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/ai/health

# Knowledge base search
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/knowledge/search?q=nozzle"

# Trial priority (ambil case_id dari list di atas)
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  http://localhost:8000/api/ai/trial-priority \
  -d '{"case_id":"<uuid_case>"}'

# AI recommendations (real LLM jika Openclaw aktif)
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  http://localhost:8000/api/ai/recommendations \
  -d '{"case_id":"<uuid_case>"}'
```

## Sprint Roadmap

| Sprint | Scope | Status | PR |
|--------|-------|--------|----|
| 1 — Foundation | Auth, DB, nav shell | ✅ | #6 |
| 2 — Case Management | F‑001 CRUD + photos + duplicate | ✅ | #7 |
| 3 — AI Core | F‑002 similar, F‑003 advisor, Openclaw integ | ✅ | #8 |
| 4 — Investigation Workflow | F‑004 trials, F‑005, status machine, F‑007 indexing | ✅ | #9 |
| 5 — Completion & Launch | F‑006 Why‑Why, KB search, admin, NFR, deploy | ✅ | #10 |

## Dokumen Terkait

- **[pitchdeck.md](./pitchdeck.md)** — Problem, solution, AI agent workflow, tech stack, future development & impact
- **[PRD.md](./PRD.md)** — Product Requirements Document (v1.0 Draft, Brian Ramdhani)
- **[sprints/](./sprints/)** — Per‑sprint detail (Sprint 1 → 5)

---

*Stop guessing — start retrieving. Engineer pakai memori pabrik, bukan memori pribadi.*
