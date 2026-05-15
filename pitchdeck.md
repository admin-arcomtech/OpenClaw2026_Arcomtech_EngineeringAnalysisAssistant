# Arcom Engineering Intelligence — Pitch Deck

> **AI‑Guided Manufacturing Investigation & Engineering Memory Platform**
> Mempercepat root cause analysis, mengurangi destructive trial, dan melestarikan pengetahuan engineering senior.

| | |
|---|---|
| **Produk** | Arcom Engineering Intelligence (AEI) |
| **Versi** | MVP Phase 1 — Pilot Ready |
| **Owner** | Brian Ramdhani (Chief Staff IJP/SIDM), Arcomtech |
| **Target Pengguna** | Junior Engineer · Senior Engineer · Engineering Manager · Admin |
| **Platform** | Web (mobile‑first) · Desktop browser · On‑prem intranet |

---

## 1. Problem Statement

### 1.1 Pain points di lapangan

| Pain Point | Dampak Bisnis |
|------------|---------------|
| Root cause analysis terlalu lama, banyak trial‑and‑error | Downtime panjang, kehilangan produksi |
| Ketergantungan tinggi pada Senior — knowledge bottleneck | Antrian investigasi, eskalasi macet |
| Pengetahuan engineering tersebar di Excel / PPT / catatan manual | Tidak dapat dicari ulang |
| Tidak ada sistem retrieval kasus historis | Investigasi mulai "dari nol" setiap kali |
| Urutan investigasi tidak standar | Kualitas troubleshooting inkonsisten antar line |
| Pembuatan Why‑Why analysis lambat dan manual | Dokumentasi tertunda, audit gap |
| Destructive trial dilakukan dulu sebelum hipotesis matang | Scrap cost tinggi |
| Repeat abnormality — root cause yang sama berulang | Biaya berulang yang tidak terdeteksi |

### 1.2 Core insight

> Bottleneck sebenarnya bukan **menemukan jawaban akhir**, melainkan **menemukan jalur investigasi yang benar dengan cepat**.

Manufacturing troubleshooting bersifat **hypothesis‑driven**, **iterative**, **multi‑factor**, dan **kontekstual**. Itu adalah masalah retrieval + ranking, bukan klasifikasi otomatis.

### 1.3 Kenapa solusi lain tidak cukup

- **AI generic chat** → tidak punya konteks taxonomy 4M1E, model, line, fatal error spesifik factory.
- **Excel / SharePoint search** → keyword‑only, tidak paham sinonim engineering & semantic similarity.
- **MES / SPC tool** → fokus monitoring, bukan investigasi.

---

## 2. Solution Overview

**Arcom Engineering Intelligence** adalah platform AI investigation co‑pilot yang:

1. **Menyimpan setiap kasus** sebagai vektor + metadata terstruktur (model, process, fatal_error, severity, dst.).
2. **Memunculkan kasus serupa** dari riwayat menggunakan semantic search (pgvector / RAG) yang dipicu otomatis ketika kasus baru dibuat.
3. **Memberi rekomendasi hipotesis 4M1E** dengan confidence + evidence + sugesti verifikasi.
4. **Memberi rekomendasi trial** dengan ranking risiko & ekspektasi waktu, melindungi engineer dari destructive trial.
5. **Memandu pembuatan Why‑Why draft** otomatis setelah root cause dikonfirmasi.
6. **Menjadi memori engineering pabrik** — setiap trial, root cause, dan Why‑Why yang disetujui otomatis ter‑embed ke knowledge base.

### 2.1 Otoritas tetap pada manusia

| Bukan | Adalah |
|-------|--------|
| Replacement engineer | AI investigation advisor |
| Autonomous diagnosis AI | Engineering co‑pilot |
| Fully‑automated decision maker | Similarity intelligence engine |
| Black‑box | Trial prioritization system dengan evidence visible |

> **Final engineering authority always remains with the human engineer.**

### 2.2 Outcome yang dijanjikan (PRD §11)

| KPI | Baseline | Target |
|-----|----------|--------|
| Time to Root Cause | current avg | **−50%** |
| Repeat abnormality | current avg | **−30%** |
| Why‑Why creation time | current avg | **−70%** |
| Junior engineer onboarding | high‑touch | self‑service via KB |

---

## 3. AI Agent Workflow / Architecture & Technical Explanation

### 3.1 High‑level architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  Next.js 14 (App Router) — Mobile-first PWA, role-aware UI       │
└──────┬───────────────────────────────────────────────────────────┘
       │ HTTPS (JWT bearer)
┌──────▼───────────────────────────────────────────────────────────┐
│  FastAPI Backend                                                 │
│  ┌───────────────┐  ┌──────────────────┐  ┌───────────────────┐  │
│  │ Auth & RBAC   │  │ Case + Trial     │  │ Why-Why & KB      │  │
│  │ (JWT/bcrypt)  │  │ APIs (F-001..5)  │  │ APIs (F-006/F-007)│  │
│  └───────────────┘  └──────────────────┘  └───────────────────┘  │
│           │                  │                       │           │
│           ▼                  ▼                       ▼           │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  AI Provider (composite)                                 │    │
│  │   primary  → Openclaw Gateway (OpenAI-compatible)        │    │
│  │   fallback → LocalDeterministicProvider                  │    │
│  │     • embed: 1536-d hashed bag-of-words                  │    │
│  │     • recommend: 4M1E rule engine + taxonomy             │    │
│  │     • why-why: 5-step template w/ trial context          │    │
│  └──────────────────────────────────────────────────────────┘    │
│           │                                                      │
│           ▼                                                      │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  PostgreSQL 16 + pgvector (HNSW index)                   │    │
│  │  cases · trials · why_why · audit_log · notifications    │    │
│  │  ai_recommendations · ai_feedback · import_jobs          │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
       │
       ▼
  Openclaw Gateway (on‑prem, port 18789) → upstream LLM provider
                                          (OpenAI / Ollama / Anthropic)
```

### 3.2 Investigation Agent Workflow

End‑to‑end flow dari sebuah abnormality sampai knowledge memory:

```
[1] Junior Engineer → Buat Case (F-001)
        │  fields: model, process, line, fatal_error, symptom, photo
        ▼
[2] AUTO: Embedding(case_text) → cases.embedding (pgvector)
        ▼
[3] AUTO: Similar Case Retrieval (F-002)
        │  cosine_distance < threshold → top-K kasus historis
        ▼
[4] AI Recommendations (F-003)
        │  Hypothesis (4M1E) + confidence + evidence + verification
        │  • Low risk trial diutamakan
        │  • Cross-reference dengan countermeasure kasus serupa
        ▼
[5] Trial Recommendation Engine (F-004)
        │  score = (1/risk) × success_rate × (1/time)
        │  HIGH risk → wajib Senior approval
        ▼
[6] Trial Logging (F-005)
        │  trial_action, outcome (IMPROVED/NO_CHANGE/WORSENED/INCONCLUSIVE)
        │  observation min 20 char, scrap impact, evidence photos
        │  AUTO: embed_trial(trial) → trials.embedding
        ▼
[7] Status Machine
        OPEN → INVESTIGATING → SUSPECTED_CAUSE → TRIAL_RUNNING
            → MONITORING → CONFIRMED (Senior+) → ARCHIVED
        ▼
[8] Confirm Root Cause (Senior+)
        │  AUTO: embed_root_cause(case) → cases.embedding (updated)
        │  flag: why_why_eligible = true
        │  notify: Senior bell
        ▼
[9] Why-Why Draft (F-006)
        │  AI generate 5+ levels × 4M1E
        │  Junior edit → submit → Senior approve/reject
        │  AUTO on APPROVE: embed_why_why(doc) → why_why.embedding
        ▼
[10] Archive
        │  AUTO: embed_archived_case(case) (full narrative)
        ▼
[11] Knowledge Memory Engine (F-007)
        Cases + Trials + Why-Why menjadi search index untuk
        kasus berikutnya → loop balik ke step [3].
```

### 3.3 Retrieval & similarity strategy

| Tahap | Teknik |
|-------|--------|
| Encoding | Openclaw `text-embedding` (1536d) atau fallback hash 1536d |
| Storage | pgvector `vector(1536)` + HNSW index |
| Ranking | `1 - (a <=> b)` cosine similarity, threshold default 0.5 |
| Fallback | Keyword OR pada `model` + `fatal_error` + `process` |
| Filter | Status (CONFIRMED/ARCHIVED), date range, model |
| Evidence UI | `similarity_pct`, `source` badge (openclaw / fallback / keyword) |

### 3.4 Trial priority scoring

```
priority_score = (LOW_RISK_BONUS / risk_weight)
               × historical_success_rate
               × (1 / estimated_time_min)

risk_weight    = {LOW: 1.0, MEDIUM: 2.5, HIGH: 5.0}
LOW_RISK_BONUS = 1.5

if ALL items HIGH risk → all_high_risk=true → warning ke user
if HIGH risk diapprove oleh JUNIOR → 403 Forbidden (gate Senior)
```

### 3.5 Why‑Why generation pipeline

1. **Pre‑check** — `case.why_why_eligible == "true"`. Kalau belum confirmed → 400.
2. **Context build** — root cause + symptom + fatal_error + trial summary.
3. **Provider call** — Openclaw chat completion JSON mode (`response_format: json_object`).
4. **Validate** — minimal 5 why_steps, masing‑masing punya `category_4m1e`.
5. **Fallback** — jika partial/gagal: template deterministic + flag `partial: true` (jangan blok user, PRD F‑006 acceptance).
6. **Approval** — Senior‑only transition `PENDING_APPROVAL → APPROVED`. Setelah approved → `embed_why_why()` background task.

### 3.6 Safety, governance, & audit

- **RBAC** di setiap endpoint via `require_role([...])` dependency.
- **Audit log immutable** (`audit_log` table, append‑only, no update/delete API).
- **Archived = read‑only** untuk cases/trials/why‑why.
- **AI Safety UI rule** — setiap kartu rekomendasi *wajib* menampilkan confidence + evidence + sumber (openclaw/fallback). Tidak ada hidden auto‑decision.
- **Audit trail per AI feedback** — useful / not_relevant / already_tried tersimpan untuk model improvement loop.

### 3.7 Offline / factory floor reliability

- **OfflineBanner** + `trialDraft` localStorage (drafting trial saat WiFi mati).
- **AI fallback provider** menjamin platform tetap fungsional ketika gateway/upstream LLM down.
- **Mobile‑first** Tailwind UI dengan `min-h-touch` target 48px untuk tablet 10".

---

## 4. Key Features & Tech Stack

### 4.1 PRD Feature Map

| ID | Feature | Status | Sprint |
|----|---------|--------|--------|
| F‑001 | Case Management (CRUD + photos + duplicate detect) | ✅ | 2 |
| F‑002 | Similar Case Retrieval (RAG semantic + keyword) | ✅ | 3 |
| F‑003 | AI Investigation Recommendations (4M1E hypotheses) | ✅ | 3 |
| F‑004 | Trial Recommendation Engine (LOW‑first ranking) | ✅ | 4 |
| F‑005 | Trial Logging (outcomes, scrap, evidence photos) | ✅ | 4 |
| F‑006 | Why‑Why Draft Generator + Senior approval | ✅ | 5 |
| F‑007 | Knowledge Memory Engine (auto‑index) | ✅ | 3–5 |
| — | Admin Panel (users, audit, import, AI settings) | ✅ | 5 |
| — | Notifications + KPI Dashboard | ✅ | 5 |

### 4.2 Tech Stack

| Layer | Pilihan | Alasan |
|-------|--------|--------|
| **Frontend** | Next.js 14 App Router, TypeScript, Tailwind CSS | Mobile‑first PWA, SSR/CSR hybrid, factory tablet ready |
| **Backend** | FastAPI 0.111 (Python 3.11), Pydantic v2 | Async, typed, openapi docs auto |
| **ORM / Migrations** | SQLAlchemy 2.0 + Alembic | Versioned schema, migration audit |
| **Database** | PostgreSQL 16 + **pgvector** (HNSW) | One DB untuk relational + vector search |
| **AI Gateway** | **Openclaw Gateway** (OpenAI‑compatible) | On‑prem proxy ke upstream LLM (factory intranet) |
| **AI Fallback** | LocalDeterministicProvider (hash embed + rule engine) | Platform tetap fungsional saat LLM down |
| **Auth** | JWT HS256 + bcrypt 12 rounds | Stateless, RBAC dependency |
| **Container** | Docker Compose v2 | Single‑command deploy intranet |
| **Storage** | Local volume (`/uploads`) | On‑prem, max 5 photos × 10MB |
| **Observability** | Structured logging + request_id + audit_log | Compliance & post‑incident review |
| **i18n** | Bahasa Indonesia default (UI), EN fallback | User base factory IJP/SIDM |
| **Testing** | pytest (status machine, case ID, RBAC) | Regression protection |

### 4.3 Highlight UX

- 🔍 **Bottom nav** — Dashboard · Kasus · KB · Buat · Admin (role‑gated).
- 🔔 **Notification bell** — HIGH severity case, Why‑Why pending approval.
- 🧭 **Case detail** — Trial queue panel, Senior confirm form, Why‑Why entry point, Timeline.
- 📈 **Dashboard KPI cards** — AI usefulness %, avg time‑to‑root‑cause (Manager+).
- 📥 **Admin CSV import** — Dry‑run validation sebelum bulk insert historical Why‑Why.

---

## 5. Future Development / Impact

### 5.1 Roadmap Phase 2+

| Area | Initiative |
|------|------------|
| **AI Quality** | Cross‑model learning, countermeasure effectiveness scoring, taxonomy normalization, embedding fine‑tune per factory |
| **Predictive** | SPC Insight Intelligence (real‑time drift), predictive abnormality alert |
| **Visual** | Image similarity AI (defect photo matching), OCR untuk SOP/Excel legacy |
| **Knowledge Graph** | Factory knowledge graph (model ↔ process ↔ root cause ↔ countermeasure) |
| **Cross‑line** | Cross‑model & cross‑line intelligence, golden recipe diff |
| **Integration** | LDAP/AD SSO, MES integration, email/Teams notification |
| **Analytics** | Manager full analytics dashboard (TTRC distribution, root cause heatmap, scrap delta) |
| **Storage** | Qdrant migration kalau pgvector tidak cukup (>1M kasus) |

### 5.2 Business Impact (estimated, Phase 1 pilot)

| Metrik | Baseline | Target Phase 1 | Mekanisme |
|--------|----------|----------------|-----------|
| Time to Root Cause | 100% | **−50%** | Similar case retrieval + trial ranking |
| Repeat abnormality (90d) | 100% | **−30%** | Knowledge memory + Why‑Why approved |
| Why‑Why doc time | hours | **−70%** | AI draft auto‑populate |
| Junior productive solo case | 0 / week | **3–5 / week** | AI co‑pilot guidance |
| Knowledge loss saat turnover | high | **low** | Embedded archived narrative |
| Destructive trial scrap | baseline | **measurable reduction** | LOW‑risk prioritization + Senior gate |

### 5.3 Beyond MVP — Vision

Arcom Engineering Intelligence menjadi **engineering memory layer** yang dimiliki pabrik:

- Setiap kasus baru = retrieval terhadap **seluruh sejarah pabrik**, bukan memori personal Senior.
- Senior berubah peran dari "single point of knowledge" → **knowledge curator & quality reviewer**.
- Junior onboarding turun dari berbulan‑bulan → minggu, didampingi AI yang sudah belajar dari pabriknya sendiri.
- Multi‑factory: setiap line / divisi punya tenant terpisah; group‑level analytics jadi mungkin.
- Foundation untuk **predictive intelligence** Phase 2 — karena data structured + embeddings sudah terkumpul.

> *"AI tidak menggantikan engineer kami. AI menggantikan amnesia institusional pabrik kami."*

---

## Appendix — Quick Demo Path

1. Login sebagai `EMP001` (Junior) → buat case `Nozzle Clog` di model `X-123` → AI recommendations + similar cases muncul otomatis.
2. Generate **Trial Queue** → approve queue → log trial dengan outcome `IMPROVED`.
3. Login sebagai `EMP002` (Senior) → advance status ke `CONFIRMED` → input root cause.
4. Klik **Generate Why‑Why Draft** → edit → submit → switch ke Senior login → approve.
5. Login sebagai `EMP003` (Manager) → lihat dashboard KPI + Knowledge Base search.
6. Login sebagai `EMP004` (Admin) → CSV dry‑run import historical Why‑Why.

Selesai — 6 langkah untuk full E2E flow F‑001 → F‑007.
