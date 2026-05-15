# Sprint 3 — AI Core: Similar Cases & Investigation Assistant (F-002, F-003)

**Durasi:** Minggu 5–6  
**Tujuan:** Mengaktifkan diferensiator utama platform — **retrieval kasus serupa** dan **asisten investigasi AI** — dengan RAG, embedding, dan panel UI di layar investigasi.

**Prasyarat:** Sprint 2 selesai (cases CRUD, data di PostgreSQL).

---

## Ringkasan

| Aspek | Detail |
|-------|--------|
| Fitur PRD | **F-002** Similar Case Retrieval (P0), **F-003** AI Investigation Assistant (P0) |
| Tech | pgvector, embedding model, LLM (OpenAI / local), RAG |
| Exit criteria | Similar cases muncul < 10 detik; AI mengembalikan max 3 hipotesis dengan 4M1E |

---

## Deliverables

1. Pipeline embedding: generate & simpan vector pada case create/update
2. API Similar Case Retrieval dengan ranking cosine similarity
3. API AI Recommendations (hipotesis terstruktur)
4. Panel **AI Similar Cases** dan **AI Recommendations** di `/cases/:id`
5. Background trigger similar search saat case created (< 3 detik enqueue; hasil < 10 detik)
6. Graceful degradation: keyword fallback, mode tanpa AI

---

## Task Breakdown

### 3.1 AI Infrastructure

- [ ] Abstraksi `LLMProvider` (OpenAI API / local Ollama — PRD §12)
- [ ] Abstraksi `EmbeddingProvider` (dimensi 1536, konsisten dengan schema)
- [ ] Config: API key / local endpoint via env (tanpa hardcode)
- [ ] Rate limiting & timeout (LLM 60s, embedding 30s)
- [ ] Prompt templates versioned di `prompts/`

### 3.2 Embedding Pipeline (F-002 / F-007 partial)

**Input embedding:** `symptom + fatal_error + model + process` (concatenated normalized text)

- [ ] On `POST /api/cases`: async job embed & update `cases.embedding`
- [ ] On case field update relevan: re-embed
- [ ] HNSW index pgvector: `CREATE INDEX ... USING hnsw (embedding vector_cosine_ops)`
- [ ] Batch re-embed script untuk kasus historis existing

### 3.3 Similar Case Retrieval API (F-002)

| Endpoint | Method | Body | Response |
|----------|--------|------|----------|
| `/api/ai/similar-cases` | POST | `{ case_id, keywords?, threshold?, date_range? }` | `{ similar_cases[] }` |

**Process (PRD):**

1. Embed query dari current case fields
2. Vector search pgvector (cosine similarity)
3. Rank descending, filter default threshold > 50%
4. Enrich: root cause, successful/failed trials, countermeasure, resolution time
5. Return top N (default 10, UI show top 3)

- [ ] Response fields: `similarity_pct`, `case_id`, `root_cause`, `countermeasure`, `resolution_days`
- [ ] Endpoint manual + auto-trigger on case create (Celery/BackgroundTasks/asyncio)
- [ ] Fallback keyword search jika vector timeout → warning *"Hasil pencarian menggunakan mode teks"*
- [ ] Empty state: *"Belum ada kasus serupa. Ini investigasi baru."*
- [ ] Low history: *"Knowledge base masih terbatas..."* jika < 10 cases

### 3.4 AI Investigation Assistant API (F-003)

| Endpoint | Method | Body | Response |
|----------|--------|------|----------|
| `/api/ai/recommendations` | POST | `{ case_id, extra_context? }` | `{ hypotheses[] }` |

**RAG context assembly:**

- Current case data
- Top similar cases dari F-002
- Engineering taxonomy 4M1E layer

**Output schema (max 3 hypotheses):**

```json
{
  "title": "Jig Stopper Wear",
  "confidence": 72,
  "category_4m1e": "Machine",
  "evidence": ["...", "..."],
  "suggested_verification": ["...", "..."],
  "trial_risk": "LOW",
  "estimated_time_min": 30,
  "similar_case_count": 2
}
```

- [ ] Simpan ke `ai_recommendations` + link `case_id`
- [ ] Sort: low-risk trials first dalam suggested verifications
- [ ] Low confidence < 30% → disclaimer UI
- [ ] LLM error → *"AI tidak tersedia saat ini. Gunakan manual investigation mode."*
- [ ] Loading state 30s spinner, hard timeout 60s

### 3.5 Frontend — Investigation Panels

**Layout `/cases/:id` (PRD §9.2):**

| Panel | Sprint 3 |
|-------|----------|
| Case Header | ✅ (Sprint 2) |
| AI Similar Cases | ✅ Top 3 + "Lihat semua" |
| AI Recommendations | ✅ Max 3 cards |
| Trial Queue | Placeholder Sprint 4 |
| Action Bar | "Get AI Advice" aktif |

- [ ] Auto-fetch similar cases on page load (polling jika background job)
- [ ] Tombol "Search Similar Cases" manual refresh
- [ ] Threshold slider (advanced, optional MVP)
- [ ] Mark similar case: "Reference" / "Not Relevant" (simpan feedback — full pipeline Sprint 5)
- [ ] Tombol feedback F-003: Useful / Not Relevant / Already Tried (simpan ke DB)

### 3.6 Tabel `ai_recommendations`

| Column | Type |
|--------|------|
| id | UUID PK |
| case_id | UUID FK |
| hypotheses | JSONB |
| model_version | VARCHAR |
| created_at | TIMESTAMP |

### 3.7 Performance & Monitoring

- [ ] Cache embedding query untuk case aktif (in-memory TTL 5 min)
- [ ] Metric: similar-cases API p95 latency
- [ ] Target: retrieval < 10 detik (PRD NFR)

---

## Acceptance Criteria

### F-002
- [ ] Retrieval selesai < 10 detik (p95 pada staging dengan 100+ cases)
- [ ] Hasil sorted by similarity descending
- [ ] Setiap hasil: similarity %, root cause, countermeasure
- [ ] Klik hasil → navigasi ke historical case detail (read-only jika archived)
- [ ] Partial input graceful degradation

### F-003
- [ ] Max 3 hipotesis per request
- [ ] Confidence % + visual bar
- [ ] Setiap hipotesis punya kategori 4M1E
- [ ] Low-risk suggestions ranked before high-risk
- [ ] Platform tetap fungsional jika AI down

---

## Definition of Done

- Integration test: create case → embedding job → similar cases returned
- Integration test: recommendations dengan mocked LLM
- Manual UAT dengan 1 Senior Engineer: relevansi similar cases
- Prompt review: tidak ada rekomendasi tanpa evidence dari similar cases

---

## Dependencies & Risks

| Risk | Mitigasi |
|------|----------|
| AI hallucination | RAG wajib; tampilkan link similar cases sebagai bukti |
| Data ke luar factory | Default local LLM; proxy OpenAI dengan anonymization (PRD Q#1) |
| pgvector lambat | HNSW + limit top-k; monitor query plan |

---

## Handoff ke Sprint 4

- `ai_recommendations` dan similar case results tersedia untuk **Trial Recommendation Engine (F-004)**
- Trial history dari similar cases dapat di-query per `case_id`
