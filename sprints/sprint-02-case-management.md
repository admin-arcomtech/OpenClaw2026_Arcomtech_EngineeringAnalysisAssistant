# Sprint 2 — Case Management (F-001)

**Durasi:** Minggu 3–4  
**Tujuan:** Engineer dapat membuat, melihat, dan mengelola kasus investigasi secara end-to-end **tanpa AI** — fondasi data untuk Similar Case Retrieval di Sprint 3.

**Prasyarat:** Sprint 1 selesai (auth, DB, navigation shell).

---

## Ringkasan

| Aspek | Detail |
|-------|--------|
| Fitur PRD | **F-001** Case Creation & Management (P0) |
| API | `POST/GET/PATCH /api/cases`, upload foto |
| Exit criteria | Case dibuat dengan Case ID valid, foto terupload, list & detail berfungsi |

---

## Deliverables

1. Form pembuatan kasus lengkap (`/cases/new`)
2. Auto-generate Case ID: `IEI-YYYYMMDD-XXXX` (sesuai PRD; sesuaikan prefix factory jika berbeda)
3. Case list dengan filter status / model / process
4. Case detail shell — info kasus, timeline kosong, placeholder panel AI
5. Upload foto kasus (max 5, 10MB, jpg/png/webp)
6. Validasi duplicate case (model + fatal_error dalam 24 jam) → warning banner
7. Status awal `OPEN`; transisi dasar ke `INVESTIGATING`

---

## Task Breakdown

### 2.1 Backend — Cases API

| Endpoint | Method | Role | Deskripsi |
|----------|--------|------|-----------|
| `/api/cases` | POST | JUNIOR+ | Create case |
| `/api/cases` | GET | JUNIOR+ | List + pagination + filter |
| `/api/cases/:id` | GET | JUNIOR+ | Detail + photos + investigator |
| `/api/cases/:id/status` | PATCH | JUNIOR+ | Update status (subset Sprint 2) |
| `/api/cases/:id/photos` | POST | JUNIOR+ | Upload photo |

**Payload create case (PRD F-001):**

- `model` (required, dropdown source)
- `process` (required)
- `line` (required)
- `symptom` (required, max 500)
- `fatal_error` (required)
- `description` (required, max 200)
- `investigator_id` (auto dari JWT, editable Senior+)
- `temporary_action`, `shift`, `operator_id`, `spc_reference` (optional)
- `severity` (default MEDIUM; HIGH → trigger notifikasi in-app Sprint 5)

- [ ] Validasi server-side mirror client-side
- [ ] Case ID generator: sequence harian per factory prefix
- [ ] Duplicate detection query: same `model` + `fatal_error` within 24h
- [ ] Simpan `investigator_id` dari token
- [ ] Audit log: case created, status changed, photo uploaded

### 2.2 Taxonomy & Master Data

- [ ] Tabel atau config: `models`, `processes`, `lines`, `fatal_errors` (dropdown)
- [ ] Endpoint `GET /api/taxonomy/*` atau single `/api/metadata`
- [ ] Seed data untuk pilot IJP/SIDM (PRD open Q#4)

### 2.3 File Upload

- [ ] Storage: folder intranet / object storage internal
- [ ] Validasi MIME: jpg, png, webp only
- [ ] Max 5 files per case, 10MB each
- [ ] Error message ID: *"Ukuran file melebihi 10MB. Compress dulu sebelum upload."*
- [ ] Tabel `case_photos`: `case_id`, `file_path`, `uploaded_by`, `created_at`

### 2.4 Frontend — Case Flows

| Screen | Komponen |
|--------|----------|
| `/cases/new` | Multi-step atau single scroll form, validasi inline |
| `/cases` | Tabel/kartu mobile, filter chips status/model |
| `/cases/:id` | Header (ID, badges), symptom/fatal error, photo gallery |
| `/dashboard` | Open cases count, recent cases list |

- [ ] Client validation sebelum submit
- [ ] Offline message: *"Koneksi terputus. Coba lagi setelah online."*
- [ ] Duplicate warning banner dengan opsi "Lanjutkan"
- [ ] Case detail: panel placeholder "Similar Cases — Sprint 3", "AI Recommendations — Sprint 3"

### 2.5 Case Lifecycle (Partial)

Status penuh (7 state) diselesaikan di Sprint 4. Sprint 2:

| Status | Supported |
|--------|-----------|
| OPEN | ✅ Default on create |
| INVESTIGATING | ✅ Manual advance |
| SUSPECTED_CAUSE → ARCHIVED | ⏳ Sprint 4 |

- [ ] State machine stub dengan valid transitions terbatas
- [ ] UI badge warna per status

### 2.6 Notifications (Stub)

- [ ] Jika `severity = HIGH`, insert in-app notification untuk Senior (tabel `notifications` — deliver UI Sprint 5)

---

## Acceptance Criteria (F-001)

- [ ] Semua field wajib divalidasi sebelum submit (client + server)
- [ ] Case ID format `IEI-YYYYMMDD-XXXX` unik per hari
- [ ] Photo upload terima jpg/png/webp, tolak lainnya
- [ ] Status = `OPEN` setelah create
- [ ] Engineer tidak bisa create tanpa login
- [ ] Duplicate warning muncul untuk kasus sama dalam 24 jam
- [ ] Hook background job placeholder untuk Similar Case (no-op / log only — implementasi Sprint 3)

> **Catatan PRD:** Similar case retrieval < 3 detik setelah create — **dicapai di Sprint 3** setelah embedding pipeline aktif.

---

## Definition of Done

- E2E manual: login → create case → lihat di list → buka detail → upload foto
- Unit test: Case ID generator, duplicate detection, validation schemas
- API documented (OpenAPI / Swagger FastAPI)

---

## Dependencies & Risks

| Item | Catatan |
|------|---------|
| **Blocks** | Sprint 3 (butuh cases di DB untuk embedding) |
| **Risk:** Taxonomy belum final | Mitigasi: JSON seed + admin editable di Sprint 5 |
| **Risk:** Format Case ID factory | Konfirmasi prefix `IEI` vs `FACTORY` dengan stakeholder |

---

## Handoff ke Sprint 3

- Minimal 10+ kasus seed (synthetic atau import parsial) untuk uji similarity
- Field `symptom`, `fatal_error`, `model`, `process` terisi konsisten
- Kolom `embedding` siap di-update oleh pipeline Sprint 3
