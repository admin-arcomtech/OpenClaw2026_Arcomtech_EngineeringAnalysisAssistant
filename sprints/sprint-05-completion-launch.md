# Sprint 5 — Completion, Why-Why & Launch Readiness (F-006 + Polish)

**Durasi:** Minggu 9–10  
**Tujuan:** Menyelesaikan MVP Phase 1 — **Why-Why draft**, **approval Senior**, **knowledge base search**, **admin & import**, **performance**, dan **launch readiness**.

**Prasyarat:** Sprint 4 selesai (trials, status machine, knowledge indexing).

---

## Ringkasan

| Aspek | Detail |
|-------|--------|
| Fitur PRD | **F-006** Why-Why Draft (P1), sisa **F-007**, Admin, NFR, KPI instrumentation |
| Exit criteria | MVP Phase 1 deployable ke pilot IJP/SIDM; semua P0 acceptance criteria terpenuhi |

---

## Deliverables

1. Why-Why AI draft + editor + approval flow
2. Knowledge base search screen (`/knowledge-base`)
3. Historical data batch import (Excel/Why-Why)
4. Engineer feedback pipeline untuk AI (full)
5. Admin panel: users, system health, KB metrics
6. Audit log UI (Manager/Admin)
7. Performance hardening & test suite
8. i18n Bahasa Indonesia lengkap untuk UI utama

---

## Task Breakdown

### 5.1 Why-Why Draft Generator (F-006)

| Endpoint | Method | Auth |
|----------|--------|------|
| `POST /api/ai/why-why-draft` | Generate draft | JUNIOR+ |

**Trigger:**

- Manual: tombol "Generate Why-Why Draft"
- Auto-suggest setelah root cause confirmed (optional banner)

**Input:** confirmed root cause, trial logs, symptom, fatal_error, optional notes

**Output:**

- Minimum 5 Why levels
- 4M1E per Why step
- Immediate countermeasure, corrective action, preventive action
- Editable JSON/document structure

- [ ] Tabel `why_why`: `case_id` (1:1), `draft`, `approved_version`, `status` (DRAFT|PENDING_APPROVAL|APPROVED)
- [ ] Block generate jika root cause belum confirmed
- [ ] Partial AI failure → editable partial draft
- [ ] Target generation < 30 detetik

### 5.2 Why-Why Approval Flow

| Route | Role |
|-------|------|
| `/cases/:id/why-why` | Editor |

- [ ] Engineer edit setiap Why step
- [ ] Submit for approval → notify Senior
- [ ] Senior approve / reject with comment
- [ ] Approved Why-Why → index ke knowledge base (F-007)
- [ ] Read-only view setelah approved

### 5.3 Knowledge Base Search (F-007 UI)

| Route | Fitur |
|-------|-------|
| `/knowledge-base` | Semantic + keyword search across cases, trials, Why-Why |

- [ ] Search bar dengan filters: model, process, date range
- [ ] Result cards: case summary, root cause, key trials
- [ ] Link ke archived case detail
- [ ] Admin metrics: total indexed docs, last import date

### 5.4 Historical Data Batch Import

- [ ] Admin tool: upload Excel/CSV (Why-Why, fatal error logs — last 2 years per PRD Q#3)
- [ ] Normalization pipeline: map columns → schema
- [ ] Flag low-quality rows untuk manual review
- [ ] Batch embed job dengan progress bar
- [ ] Dry-run mode: validate without insert

### 5.5 AI Feedback Collection (Complete)

| Endpoint | Body |
|----------|------|
| `POST /api/ai/feedback` | `{ rec_id, feedback_type: USEFUL\|NOT_RELEVANT\|ALREADY_TRIED }` |

- [ ] Similar case "Not Relevant" → training signal storage
- [ ] Dashboard metric: % useful (KPI PRD §11)
- [ ] Manager read-only analytics card on `/dashboard`

### 5.6 Admin Panel

| Route | Fitur | Role |
|-------|-------|------|
| `/admin` | User CRUD, activate/deactivate | ADMIN |
| `/admin/settings` | AI model config, similarity threshold defaults | MANAGER+ |
| `/admin/import` | Batch import | ADMIN |
| `/admin/audit` | Audit log viewer | ADMIN |

**User management:**

- [ ] Create user: employee_id, name, email, role, division
- [ ] Soft delete `is_active = false`
- [ ] Cannot modify investigation content (Admin IT rule PRD §4)

### 5.7 Notifications (In-App)

- [ ] HIGH severity case → notify Seniors (PRD F-001)
- [ ] Why-Why pending approval
- [ ] Bell icon + unread count on dashboard

### 5.8 Case Archive & Knowledge Consolidation

- [ ] Transition CONFIRMED → ARCHIVED (Senior/Manager)
- [ ] Set `archived_at`
- [ ] Consolidated embed: full case narrative for F-002
- [ ] Archived cases read-only

### 5.9 Non-Functional Requirements

| NFR | Task |
|-----|------|
| Performance | Profiling similar-cases p95 < 10s; page load < 3s WiFi |
| Security | Audit immutability; review RBAC all endpoints |
| i18n | Semua string UI utama ID; EN fallback |
| AI Safety | Confidence + evidence mandatory in UI components |
| Reliability | Verify offline trial sync E2E |

### 5.10 Testing & Launch

- [ ] Unit tests: status machine, trial scoring, Case ID, auth RBAC
- [ ] Integration tests: AI endpoints (mocked LLM)
- [ ] E2E critical path: Login → Create Case → Similar Cases → AI Rec → Trial Queue → Log Trial → Confirm Root Cause → Why-Why → Archive
- [ ] Load test: 50 concurrent users (PRD Q#7)
- [ ] Deployment runbook: intranet Docker, backup DB, env secrets
- [ ] Pilot checklist IJP/SIDM lines

### 5.11 KPI Instrumentation

| KPI | Implementation |
|-----|----------------|
| Time to Root Cause | `confirmed_at - created_at` |
| Why-Why creation time | `why_why.approved_at - confirmed_at` |
| Similar case speed | API metrics middleware |
| Repeat abnormality | Query same model+fatal_error within 90 days |
| AI usefulness | Feedback ratio |
| KB growth | Count archived + indexed |

---

## Acceptance Criteria

### F-006
- [ ] Draft dalam 30 detik
- [ ] Min 5 Why levels
- [ ] 4M1E per Why
- [ ] Fully editable
- [ ] Senior approval required before final
- [ ] Approved indexed in KB

### MVP Phase 1 (P0 recap)
- [ ] F-001 through F-005, F-007 acceptance dari PRD terpenuhi
- [ ] Platform functional when AI unavailable
- [ ] Mobile usable on 10" factory tablet
- [ ] Bahasa Indonesia default

---

## Definition of Done (MVP Launch)

- [ ] Stakeholder sign-off: Engineering Manager (Brian Ramdhani)
- [ ] Security review: JWT, RBAC, no plaintext passwords
- [ ] Pilot deployment ke staging intranet
- [ ] Training deck 30 menit untuk Junior + Senior engineers
- [ ] PRD living doc version tagged dengan release MVP 1.0

---

## Out of Scope (Phase 2+ — Reminder)

Tidak dikerjakan di Sprint 5:

- SPC Insight Intelligence
- Investigation analytics dashboard (full)
- Predictive AI / real-time SPC
- Image similarity AI
- LDAP SSO (optional Phase 2)
- Email notifications

---

## Risk Register (Sprint 5 Focus)

| Risk | Mitigasi |
|------|----------|
| Unstructured Excel import | Dry-run + manual curation queue |
| Engineer distrust AI | Evidence UI; pilot dengan Senior champions |
| Launch delay dari data migration | Parallel manual seed 20 golden cases |

---

## Post-Launch Backlog (Phase 2 Seeds)

1. Engineering taxonomy normalization
2. Analytics dashboard untuk Manager
3. LDAP/AD SSO
4. Email notifications
5. Qdrant migration jika pgvector insufficient
