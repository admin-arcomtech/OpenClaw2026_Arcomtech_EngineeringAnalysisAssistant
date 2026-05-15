# Sprint 4 — Investigation Workflow: Trials & Knowledge Memory (F-004, F-005, F-007)

**Durasi:** Minggu 7–8  
**Tujuan:** Menyelesaikan alur investigasi operasional — **rekomendasi trial**, **logging trial**, **status machine penuh**, dan **indeks knowledge otomatis**.

**Prasyarat:** Sprint 3 selesai (AI panels, similar cases, recommendations).

---

## Ringkasan

| Aspek | Detail |
|-------|--------|
| Fitur PRD | **F-004** Trial Recommendation (P0), **F-005** Trial Logging (P0), **F-007** Knowledge Memory (P0) |
| Exit criteria | Engineer dapat approve trial queue, log hasil trial, dan knowledge terindeks untuk retrieval |

---

## Deliverables

1. Trial Recommendation Engine + Trial Queue UI
2. Trial Logging form + API
3. Case lifecycle: 7 status dengan validasi role
4. Knowledge Memory: auto-embed on trial log, root cause confirm, archive
5. Offline draft save untuk trial logs (localStorage + sync)
6. Root cause confirmation endpoint (Senior+)

---

## Task Breakdown

### 4.1 Trial Recommendation Engine (F-004)

| Endpoint | Method | Body | Response |
|----------|--------|------|----------|
| `/api/ai/trial-priority` | POST | `{ case_id, manual_trial? }` | `{ trial_queue[] }` |

**Scoring formula (PRD):**  
`priority = f(LOW_RISK, HIGH_SUCCESS_RATE, LOW_TIME)` — weight LOW_RISK × SUCCESS × (1/TIME)

**Input sources:**

- AI hypotheses (F-003)
- Trials dari similar historical cases (F-002)
- Manual trial suggestion engineer

**Output per trial item:**

| Field | Contoh |
|-------|--------|
| trial_action | Visual jig inspection |
| risk_level | LOW |
| estimated_time_min | 10 |
| historical_success_rate | 82% atau N/A |
| destructive | false |
| required_tools | [] |
| priority_rank | 1 |

- [ ] Sort: LOW risk before HIGH
- [ ] Warning jika semua HIGH risk
- [ ] HIGH risk: flag `requires_senior_approval`
- [ ] Engineer reorder + add + skip → save `trial_queue` JSON pada case
- [ ] Two-step confirmation UI untuk HIGH risk trial start

### 4.2 Trial Queue Persistence

- [ ] Tabel `case_trial_queue` atau kolom `cases.trial_queue` JSONB
- [ ] Status queue: `DRAFT` | `APPROVED`
- [ ] Engineer approve queue sebelum execution

### 4.3 Trial Logging System (F-005)

| Endpoint | Method | Role |
|----------|--------|------|
| `POST /api/cases/:id/trials` | Create trial log | JUNIOR+ |
| `GET /api/cases/:id/trials` | List trials | JUNIOR+ |

**Payload:**

- `trial_action`, `result` (IMPROVED|NO_CHANGE|WORSENED|INCONCLUSIVE)
- `observation` (min 20 chars)
- `improvement_pct`, `time_spent_min`
- `scrap_impact`, `scrap_qty` (conditional)
- `risk_level`, photo evidence (max 3)
- `engineer_comment` optional

- [ ] Pre-fill dari trial queue item
- [ ] Duplicate log warning
- [ ] On IMPROVED/WORSENED → prompt update case status
- [ ] Embed trial: update `trials.embedding`
- [ ] Link trial ke `case_id` + `engineer_id`

### 4.4 Frontend — Trial Screens

| Route | Fitur |
|-------|-------|
| `/cases/:id` | Trial Queue panel bottom |
| `/cases/:id/trials` | Full queue + log history |

- [ ] Drag-and-drop reorder (desktop) + move up/down (mobile)
- [ ] "Log Trial Result" modal/form
- [ ] Photo upload trial evidence
- [ ] Case Timeline: trial logged, status changed, AI actions
- [ ] Offline: localStorage draft key `trial-draft-{caseId}`, sync on reconnect

### 4.5 Case Status Machine (Full)

| Status | Advance by |
|--------|------------|
| OPEN | Any engineer |
| INVESTIGATING | Any engineer |
| SUSPECTED_CAUSE | Any engineer |
| TRIAL_RUNNING | Any engineer |
| MONITORING | Any engineer |
| CONFIRMED | Senior / Manager |
| ARCHIVED | Senior / Manager |

- [ ] `PATCH /api/cases/:id/status` dengan transition matrix
- [ ] `POST /api/cases/:id/confirm` `{ root_cause }` — SENIOR+
- [ ] Set `confirmed_root_cause`, timestamp
- [ ] Trigger knowledge index + Why-Why eligible flag (Sprint 5)

### 4.6 Knowledge Memory Engine (F-007)

**Auto-trigger:**

| Event | Action |
|-------|--------|
| Trial logged | Embed trial action + observation + result |
| Root cause confirmed | Embed root cause + case metadata |
| Case archived | Consolidated case document embed |

- [ ] Retry queue jika embedding gagal
- [ ] Admin alert hook (80% storage — stub metric)
- [ ] Normalization pipeline basic: trim, lowercase fatal_error codes

### 4.7 Case Timeline & Audit

- [ ] Timeline aggregator: status, trials, AI calls, photos
- [ ] Audit log entries untuk setiap trial log dan status change

---

## Acceptance Criteria

### F-004
- [ ] Trials ranked by risk×time×success
- [ ] LOW risk displayed before HIGH
- [ ] Historical success rate when available
- [ ] HIGH risk requires senior approval flag
- [ ] Engineer can reorder queue
- [ ] Queue persisted on case

### F-005
- [ ] All required fields saved
- [ ] Trial linked to correct case
- [ ] Trial indexed in vector DB
- [ ] Scrap qty required when scrap_impact = YES
- [ ] Offline auto-save works

### F-007
- [ ] Every trial log triggers indexing
- [ ] Archived case indexed (when archive implemented Sprint 5)
- [ ] Retrieval still < 10 sec after index growth

---

## Definition of Done

- E2E: create case → AI recommendations → trial queue → approve → log trial → status INVESTIGATING → TRIAL_RUNNING
- Unit tests: priority scoring, status transitions, validation min observation length
- Senior review: HIGH risk confirmation UX acceptable on factory tablet

---

## Dependencies & Risks

| Risk | Mitigasi |
|------|----------|
| Poor trial logging discipline | UX minimal clicks; pre-fill from queue |
| No historical trial data | Show N/A success rate; rely on AI-suggested trials only |
| Offline sync conflicts | Last-write-wins + conflict toast |

---

## Handoff ke Sprint 5

- Cases dengan confirmed root cause siap untuk **Why-Why (F-006)**
- Knowledge base memiliki cukup entries untuk search UI
- Audit log data untuk admin reporting
