ARCOM
Engineering Intelligence
AI-Guided Manufacturing Investigation & Engineering Memory Platform

Product	Version & Status
Arcom Engineering Intelligence	PRD v1.0 — Draft
Owner	Classification
Brian Ramdhani (Chief Staff IJP/SIDM)	CONFIDENTIAL — Internal Only
Target Platform	Tech Stack
Web (Mobile-first) + Desktop	FastAPI + PostgreSQL + pgvector + Next.js
 
1. Vision & Positioning
Arcom Engineering Intelligence is an AI-powered manufacturing investigation platform designed to accelerate troubleshooting, reduce destructive trial cost, preserve senior engineering knowledge, and guide junior engineers using historical factory intelligence.

This platform is NOT: a replacement for engineers, autonomous diagnosis AI, or a fully-automated decision maker.
This platform IS: an AI investigation advisor, engineering co-pilot, similarity intelligence engine, and trial prioritization system.

Final engineering authority ALWAYS remains with the human engineer.
2. Problem Statement
2.1 Current Pain Points
•	Long root cause analysis time due to trial-and-error investigation
•	Heavy dependency on senior engineers — knowledge bottleneck
•	Engineering knowledge scattered across Excel / PPT / manual notes
•	No historical case retrieval system — investigations restart from zero
•	Non-standard investigation sequence — inconsistent troubleshooting quality
•	Slow Why-Why analysis creation
•	High destructive trial risk and scrap cost
•	Repeated abnormality occurrence — same root causes recur

2.2 Business Impact
Problem	Business Impact
Long root cause time	Increased downtime
No historical retrieval	Repeat abnormality cost
Destructive trial first	Unnecessary scrap
Knowledge not documented	Knowledge loss on engineer turnover
No investigation standard	Inconsistent quality across lines
2.3 Core Insight
The real bottleneck is NOT finding the final answer. The real bottleneck is finding the correct investigation path quickly. Manufacturing troubleshooting is hypothesis-driven, trial-based, iterative, contextual, and multi-factor.
 
3. Product Overview
Attribute	Value
App Name	Arcom Engineering Intelligence
One-liner	AI-guided manufacturing investigation platform that accelerates troubleshooting and preserves engineering knowledge
Platform	Web (Mobile-first) + Desktop Browser
Backend	FastAPI (Python)
Database	PostgreSQL + pgvector (similarity search) OR Qdrant
AI Layer	LLM + RAG + Embedding Similarity Search + Engineering Taxonomy
Frontend	Next.js 14 App Router — Mobile-first investigation UI
Target Users	Junior Engineers, Senior Engineers, Engineering Managers
Primary Success KPI	Time to Root Cause -50% | Repeat Abnormality -30%
4. User Roles & Permissions
Role	Can Do	Cannot Do
Junior Engineer	Create cases, view similar cases, log trials, read AI recommendations, submit Why-Why draft	Approve Why-Why, confirm root cause, manage users, edit AI knowledge base
Senior Engineer	All Junior actions + approve Why-Why, confirm root cause, validate AI recommendations, add to knowledge base	Manage users, system configuration
Engineering Manager	All Senior actions + view analytics dashboard, manage users, configure AI settings, export reports	Delete archived cases
Admin (IT/ISP)	User management, system configuration, data migration, audit log access	Cannot modify engineering investigation content
 
5. MVP Scope — Phase 1
Phase 1 MVP focuses on current case investigation intelligence only. NO predictive AI. NO real-time SPC AI. NO cross-model learning.

IN SCOPE (Phase 1)	OUT OF SCOPE (Phase 2+)	Future Roadmap
Case management system	SPC Insight Intelligence	Visual defect similarity AI
Similar case retrieval (RAG)	Engineering taxonomy normalization	Cross-model learning
AI investigation assistant	Investigation analytics dashboard	Countermeasure effectiveness scoring
Trial recommendation engine	Real-time SPC AI	Predictive abnormality intelligence
Trial logging system	Predictive AI	Factory knowledge graph
Why-Why draft generator	Image similarity AI	Cross-line intelligence system
Knowledge memory engine		
6. Core Features
F-001 — Case Management System

F-001  Case Creation & Management
Priority	P0 — Must have for launch
User Story	As an engineer, I want to create an investigation case so that I can begin systematic root cause analysis with AI assistance.
Trigger	Engineer detects abnormality and initiates investigation in the platform.
Inputs	•	Model (required, dropdown: product model list)
•	Process (required, dropdown: process taxonomy)
•	Line / Machine (required, dropdown: factory line list)
•	Symptom (required, free text, max 500 chars)
•	Fatal Error (required, free text or dropdown from known error taxonomy)
•	Short Description (required, max 200 chars — used for case title)
•	Photo Upload (optional, max 5 files, 10MB each, jpg/png/webp)
•	Investigator (required, auto-filled from login, editable)
•	Temporary Action (optional, free text)
•	Shift (optional: Day/Night/Mid)
•	Operator ID (optional, reference only)
•	SPC Reference (optional, chart link or lot number)
Process	1.	Engineer fills in required fields and clicks Create Case
2.	System validates all required fields client-side before submission
3.	System auto-generates Case ID: [FACTORY-YYYYMMDD-XXXX]
4.	Status set to OPEN
5.	System immediately triggers Similar Case Retrieval (F-002) in background
6.	Case appears in engineer dashboard
7.	Notification sent to senior engineer if severity is HIGH
Output	Investigation case created in database with Case ID; Similar Case search triggered automatically.
Error Handling	•	Network offline → 'Koneksi terputus. Coba lagi setelah online.'
•	Upload file too large → 'Ukuran file melebihi 10MB. Compress dulu sebelum upload.'
•	Required field missing → Inline field-level validation message
•	Duplicate case suspected (same model + fatal error within 24h) → Warning banner shown, user can proceed
Acceptance	□	All required fields validated before submission
□	Case ID auto-generated in correct format
□	Photo upload accepts jpg/png/webp, rejects others
□	Status = OPEN after creation
□	Similar case retrieval triggered within 3 seconds of case creation
□	Engineer cannot create case without login

Case Lifecycle States
Status	Description	Who Can Advance
OPEN	Case created, pending investigation start	Any engineer
INVESTIGATING	Active investigation, trials being planned	Any engineer
SUSPECTED_CAUSE	Hypothesis identified, not yet confirmed	Any engineer
TRIAL_RUNNING	Trial in progress	Any engineer
MONITORING	Trial done, observing result	Any engineer
CONFIRMED	Root cause confirmed by senior engineer	Senior Engineer / Manager only
ARCHIVED	Case closed, added to knowledge base	Senior Engineer / Manager only

 
F-002 — Similar Case Retrieval Engine (Core AI)
This is the most critical feature of the platform. It directly addresses the 'reinventing the wheel' problem in manufacturing investigation.

F-002  Similar Case Retrieval Engine
Priority	P0 — Core differentiator
User Story	As an engineer, I want to see historically similar cases so that I can learn from previous investigations and avoid repeating past mistakes.
Trigger	Triggered automatically on case creation OR manually via 'Search Similar Cases' button.
Inputs	•	Current case fields (auto-passed): Fatal Error, Symptom, Model, Process
•	Manual override: Engineer can add additional search keywords
•	Similarity threshold filter (default: show cases with score > 50%)
•	Date range filter (optional: limit to last N months)
Process	8.	System embeds case inputs (symptom + fatal error + model + process) into vector representation
9.	Vector similarity search executed against historical case embeddings in pgvector/Qdrant
10.	System ranks results by similarity score (cosine similarity)
11.	For each similar case, retrieve: root cause, successful trials, failed trials, countermeasure, resolution time
12.	Results returned and displayed in similarity panel within 10 seconds
13.	Engineer can click any result to view full historical case detail
14.	Engineer can save relevant cases as 'Reference Cases' for current investigation
Output	Ranked list of similar historical cases with similarity scores and key findings shown in investigation panel.
Error Handling	•	No similar cases found (score < 50%) → Show 'Belum ada kasus serupa. Ini investigasi baru.' with option to lower threshold
•	Vector DB timeout → Fallback to keyword search, show warning 'Hasil pencarian menggunakan mode teks'
•	Insufficient history (< 10 cases in DB) → Show 'Knowledge base masih terbatas. AI akan berkembang seiring penambahan kasus.'
Acceptance	□	Retrieval completes in < 10 seconds
□	Results sorted by similarity score descending
□	Each result shows: similarity %, root cause, successful countermeasure
□	Engineer can click result to view full case
□	Engineer can mark result as 'Not Relevant' to improve future recommendations
□	Search works even with partial inputs (graceful degradation)

 
F-003 — AI Investigation Assistant
F-003  AI Investigation Assistant
Priority	P0 — Must have for launch
User Story	As a junior engineer, I want AI to suggest possible root causes and investigation steps so that I can investigate more systematically.
Trigger	Triggered after case creation or when engineer clicks 'Get AI Recommendation'.
Inputs	•	Current case data (auto-passed from F-001): Symptom, Fatal Error, Model, Process
•	Similar case results (auto-passed from F-002)
•	Engineer can provide additional context in free text field
Process	15.	AI system receives case data + similar case context
16.	LLM generates structured investigation recommendations using engineering context
17.	System applies engineering taxonomy layer (4M1E: Man, Machine, Method, Material, Environment)
18.	AI returns max 3 prioritized hypotheses, each with confidence score
19.	Each hypothesis includes: evidence reasoning, suggested verification steps, trial risk level
20.	Results displayed in 'AI Advisory Panel'
21.	Engineer can mark recommendations as 'Useful', 'Not Relevant', or 'Already Tried' — this feeds back to improve AI
Output	Structured AI recommendations panel showing ranked hypotheses with evidence, suggested verifications, and risk levels.
Error Handling	•	AI takes > 30 seconds → Show 'AI sedang memproses...' spinner, timeout at 60s with fallback message
•	AI confidence very low (< 30%) → Show disclaimer 'Confidence rendah. Gunakan sebagai referensi tambahan saja.'
•	LLM API error → 'AI tidak tersedia saat ini. Gunakan manual investigation mode.' — platform still functional without AI
Acceptance	□	AI returns max 3 hypotheses per request
□	Each hypothesis has confidence score shown as percentage
□	Each hypothesis categorized under 4M1E framework
□	Low-risk trial suggestions always ranked before high-risk
□	Engineer feedback (Useful/Not Relevant) stored for AI improvement
□	Platform fully functional even if AI is unavailable

AI Recommendation Output Format
Field	Description
Hypothesis Title	Short name of suspected root cause (e.g., 'Jig Stopper Wear')
Confidence	Percentage 0-100%, shown as visual bar + number
4M1E Category	Machine | Method | Man | Material | Environment
Evidence Reasoning	Bullet list: why AI thinks this is relevant (from similar cases + current data)
Suggested Verification	Step-by-step actions to verify or disprove hypothesis
Trial Risk	LOW | MEDIUM | HIGH with color coding
Est. Time	Estimated time to complete verification trial
Similar Cases	Count and link to similar historical cases that support this hypothesis

 
F-004 — Trial Recommendation Engine
MOST IMPORTANT differentiator. The engine prioritizes investigation trial sequence to minimize destructive trial risk and maximize investigation efficiency.

F-004  Trial Recommendation & Prioritization Engine
Priority	P0 — Key differentiator
User Story	As an engineer, I want the system to recommend which trial to do first so that I minimize scrap risk and investigation time.
Trigger	Triggered after AI recommendations are generated, or manually by engineer from trial planning screen.
Inputs	•	Current case data (auto-passed)
•	AI hypotheses (from F-003)
•	Similar case trial history (from F-002)
•	Manual trial suggestion by engineer (optional free text)
Process	22.	System retrieves all trials from similar historical cases
23.	For each trial option, calculate: historical success rate from past cases, risk level (LOW/MEDIUM/HIGH), estimated time, destructive impact (yes/no), required tools/access
24.	Sort trials using priority scoring: weight LOW_RISK × HIGH_SUCCESS_RATE × LOW_TIME first
25.	Display ranked trial list in Trial Queue
26.	Engineer reviews list and can reorder, add new trials, or skip trials
27.	Engineer approves trial queue before execution starts
Output	Prioritized trial queue displayed with risk/time/success data. Engineer approves before starting.
Error Handling	•	No historical trial data → System shows only AI-suggested trials without historical success rate (shows 'N/A — Data tidak tersedia')
•	All suggested trials are HIGH risk → Show warning: 'Semua opsi trial berisiko tinggi. Konsultasikan dengan Senior Engineer sebelum memulai.'
•	Engineer tries to skip safety confirmation for HIGH risk trial → Require explicit two-step confirmation
Acceptance	□	Trials ranked by risk×time×success priority score
□	LOW risk trials always displayed before HIGH risk
□	Historical success rate shown when available
□	HIGH risk trial requires senior engineer approval flag
□	Engineer can reorder trial queue
□	Trial queue saved to case record

Trial Priority Matrix Example
Trial Action	Risk	Time	Success Rate	Priority
Visual jig inspection	LOW	10 min	82%	#1 — DO FIRST
Cleaning shaft/roller	LOW	15 min	71%	#2
Alignment measurement	LOW	30 min	65%	#3
Replace jig stopper	MEDIUM	45 min	55%	#4
Replace motor unit	HIGH	2 hours	35%	#5 — LAST RESORT

 
F-005 — Trial Logging System
F-005  Trial Execution Logging
Priority	P0 — Required for knowledge base building
User Story	As an engineer, I want to log each trial I perform so that results are preserved and contribute to the engineering knowledge base.
Trigger	Engineer clicks 'Log Trial Result' from the active trial in trial queue.
Inputs	•	Trial Action (required, pre-filled from trial queue, editable)
•	Result (required, dropdown: IMPROVED / NO_CHANGE / WORSENED / INCONCLUSIVE)
•	Observation (required, free text, min 20 chars)
•	Improvement Status (required, % improvement if applicable, else 0)
•	Time Spent (required, in minutes)
•	Scrap Impact (required: YES / NO / PARTIAL)
•	Scrap Quantity (conditional required if Scrap Impact = YES)
•	Photo Evidence (optional, max 3 photos)
•	Engineer Comment (optional, free text)
Process	28.	Engineer selects trial from trial queue and clicks 'Log Result'
29.	System pre-fills trial action from queue
30.	Engineer fills in all required fields
31.	If Result = IMPROVED or WORSENED, system prompts to update case status
32.	Trial log saved to database and linked to case
33.	Trial data added to engineering knowledge base for future similarity search
34.	If Result = IMPROVED and engineer marks 'Root Cause Confirmed', trigger Why-Why draft generation (F-006)
Output	Trial log saved to case record and indexed into engineering knowledge base. Case status optionally updated.
Error Handling	•	Observation text too short (< 20 chars) → 'Observasi terlalu singkat. Jelaskan lebih detail.'
•	Engineer tries to log same trial twice → Warning: 'Trial ini sudah pernah di-log. Buat log baru?'
•	Network error during save → Auto-save to local draft, sync when online
Acceptance	□	All required trial fields saved correctly
□	Trial linked to correct case
□	Trial indexed in vector DB for future retrieval
□	Scrap data captured when scrap impact = YES
□	Photo evidence upload works
□	Offline auto-save works correctly

 
F-006 — Why-Why Draft Generator
F-006  AI Why-Why Draft Generation
Priority	P1 — High value, not blocking MVP
User Story	As an engineer, I want AI to generate an initial Why-Why analysis draft so that I save time and have a structured starting point for documentation.
Trigger	Engineer clicks 'Generate Why-Why Draft' from confirmed case, or system auto-triggers when root cause is confirmed.
Inputs	•	Confirmed root cause (required, from case)
•	Investigation trial log (auto-passed)
•	Case symptom and fatal error (auto-passed)
•	Engineer can add additional context notes (optional)
Process	35.	System assembles case data: symptom → fatal error → trial log → confirmed root cause
36.	LLM generates Why-Why chain (5-Why structure minimum)
37.	System categorizes each Why under 4M1E framework
38.	Draft includes: immediate countermeasure, corrective action, preventive action
39.	Draft displayed in editable form
40.	Engineer reviews and edits each Why step
41.	Senior engineer reviews and approves final version
42.	Approved Why-Why added to knowledge base
Output	Editable Why-Why draft document generated in standard format, ready for senior engineer review.
Error Handling	•	Root cause not confirmed → 'Why-Why dapat dibuat hanya setelah root cause dikonfirmasi.'
•	AI fails to generate coherent Why-Why → Show partial result with message: 'Draft tidak lengkap. Silakan lengkapi manual.' — never block engineer
Acceptance	□	Why-Why draft generated within 30 seconds
□	Minimum 5 Why levels in chain
□	4M1E category assigned to each Why
□	Draft is fully editable by engineer
□	Senior engineer approval required before finalization
□	Approved Why-Why indexed in knowledge base

 
F-007 — Knowledge Memory Engine
F-007  Engineering Knowledge Memory Engine
Priority	P0 — Foundation of AI intelligence
User Story	As an engineering manager, I want all investigation knowledge to be automatically preserved so that the platform becomes smarter over time.
Trigger	Triggered automatically every time: a trial is logged, a root cause is confirmed, a Why-Why is approved, or a case is archived.
Inputs	•	No engineer input required — fully automatic
•	Data sources: Excel engineering files (initial import), Historical Why-Why documents, Fatal error records, SPC database references, Engineering notes (manual input or bulk upload)
Process	43.	On trial log: extract trial action, result, observation — embed and index
44.	On root cause confirmation: extract confirmed root cause, symptoms, model, process — embed and index
45.	On Why-Why approval: extract full Why-Why chain — embed and index
46.	On case archive: create consolidated case record with all metadata — embed and index
47.	Initial knowledge base bootstrap: import existing Excel/PPT engineering history via batch import tool
48.	All data stored in PostgreSQL with pgvector embeddings
Output	Engineering knowledge continuously indexed in vector database. Available for Similar Case Retrieval (F-002) and AI Assistant (F-003).
Error Handling	•	Embedding generation fails → Queue for retry, show admin alert
•	Vector DB storage nearing limit → Alert admin at 80% capacity
•	Inconsistent historical data quality → Apply normalization pipeline, flag low-quality entries for review
Acceptance	□	Every archived case automatically indexed
□	Retrieval speed < 10 seconds for similarity search
□	Initial Excel/historical data can be batch imported
□	Knowledge base grows with each new investigation
□	Admin can view knowledge base size and quality metrics

 
7. Data Model
7.1 Core Tables
Table: cases
Column	Type	Constraints	Notes
id	UUID	PK, auto-generated	Primary key
case_id	VARCHAR(30)	UNIQUE, NOT NULL	Format: IEI-YYYYMMDD-XXXX
model	VARCHAR(100)	NOT NULL	Product model name
process	VARCHAR(100)	NOT NULL	Manufacturing process step
line	VARCHAR(50)	NOT NULL	Production line identifier
symptom	TEXT	NOT NULL	Symptom description
fatal_error	VARCHAR(200)	NOT NULL	Error code or description
description	VARCHAR(200)	NOT NULL	Short case title
status	ENUM	NOT NULL, DEFAULT 'OPEN'	See Case Lifecycle states
severity	ENUM	DEFAULT 'MEDIUM'	LOW | MEDIUM | HIGH | CRITICAL
investigator_id	UUID	FK → users.id	
confirmed_root_cause	TEXT	NULLABLE	Filled on confirmation
embedding	vector(1536)	NULLABLE	pgvector embedding for similarity
shift	ENUM	NULLABLE	DAY | NIGHT | MID
temporary_action	TEXT	NULLABLE	
created_at	TIMESTAMP	DEFAULT NOW()	
updated_at	TIMESTAMP	AUTO-UPDATE	
archived_at	TIMESTAMP	NULLABLE	Set when status = ARCHIVED

Table: trials
Column	Type	Constraints	Notes
id	UUID	PK	
case_id	UUID	FK → cases.id, NOT NULL	
trial_action	TEXT	NOT NULL	What was done
result	ENUM	NOT NULL	IMPROVED|NO_CHANGE|WORSENED|INCONCLUSIVE
observation	TEXT	NOT NULL	Min 20 chars
improvement_pct	DECIMAL(5,2)	NULLABLE	0-100%
time_spent_min	INTEGER	NOT NULL	Minutes
scrap_impact	ENUM	NOT NULL	YES | NO | PARTIAL
scrap_qty	INTEGER	NULLABLE	Required if scrap_impact = YES
risk_level	ENUM	NOT NULL	LOW | MEDIUM | HIGH
engineer_id	UUID	FK → users.id, NOT NULL	Who logged the trial
embedding	vector(1536)	NULLABLE	pgvector for trial similarity
created_at	TIMESTAMP	DEFAULT NOW()	

Table: users
Column	Type	Constraints	Notes
id	UUID	PK	
employee_id	VARCHAR(20)	UNIQUE, NOT NULL	Company employee ID
name	VARCHAR(100)	NOT NULL	
email	VARCHAR(255)	UNIQUE, NOT NULL	Company email only
password_hash	VARCHAR(255)	NOT NULL	bcrypt, min 12 rounds
role	ENUM	NOT NULL	JUNIOR | SENIOR | MANAGER | ADMIN
division	VARCHAR(100)	NOT NULL	e.g., IJP/SIDM Product Engineering
is_active	BOOLEAN	DEFAULT true	Soft delete
created_at	TIMESTAMP	DEFAULT NOW()	

Table Relationships
•	users (1) → cases (N): One user investigates many cases (investigator_id FK)
•	cases (1) → trials (N): One case has many trial logs
•	cases (1) → ai_recommendations (N): One case has many AI recommendation sets
•	cases (1) → why_why (1): One case has one Why-Why document
•	cases (1) → case_photos (N): One case has many uploaded photos

 
8. API Endpoints
8.1 Authentication
Method	Endpoint	Body	Response	Auth
POST	/api/auth/login	{employee_id, password}	{user, token}	No
POST	/api/auth/logout	-	{success}	Yes
GET	/api/auth/me	-	{user}	Yes

8.2 Cases
Method	Endpoint	Body / Params	Response	Auth
POST	/api/cases	Case creation payload	{case}	JUNIOR+
GET	/api/cases	?status=&model=&page=	{cases[], total}	JUNIOR+
GET	/api/cases/:id	-	{case_detail}	JUNIOR+
PATCH	/api/cases/:id/status	{status}	{case}	JUNIOR+
POST	/api/cases/:id/confirm	{root_cause}	{case}	SENIOR+

8.3 AI Intelligence
Method	Endpoint	Body / Params	Response	Auth
POST	/api/ai/similar-cases	{case_id}	{similar_cases[]}	JUNIOR+
POST	/api/ai/recommendations	{case_id}	{hypotheses[]}	JUNIOR+
POST	/api/ai/trial-priority	{case_id}	{trial_queue[]}	JUNIOR+
POST	/api/ai/why-why-draft	{case_id}	{why_why_draft}	JUNIOR+
POST	/api/ai/feedback	{rec_id, feedback_type}	{success}	JUNIOR+

8.4 Trials
Method	Endpoint	Body	Response	Auth
POST	/api/cases/:id/trials	Trial log payload	{trial}	JUNIOR+
GET	/api/cases/:id/trials	-	{trials[]}	JUNIOR+
 
9. Screen Flow & Navigation
9.1 Navigation Structure
•	/ → Login page
•	/dashboard → Engineer dashboard (open cases, recent activity)
•	/cases → Case list with filter/search
•	/cases/new → Create new case (F-001)
•	/cases/:id → Case detail (main investigation screen)
•	/cases/:id/trials → Trial queue & log (F-004, F-005)
•	/cases/:id/why-why → Why-Why editor (F-006)
•	/knowledge-base → Search engineering knowledge base (F-007)
•	/admin → Admin panel (user management, system settings)

9.2 Main Investigation Screen Layout (/cases/:id)
Mobile-first layout. Primary action always accessible with one thumb. Investigation flow: Case Info (top) → AI Similar Cases (center-left) → AI Recommendations (center-right) → Trial Queue (bottom).

Panel / Component	Content
Case Header	Case ID, Model, Process, Status badge, Severity badge, Investigator
Symptom & Fatal Error	Description of the problem (read + editable)
AI Similar Cases Panel	Top 3 similar cases with similarity %, root cause, countermeasure
AI Recommendations Panel	Ranked hypotheses with confidence, evidence, 4M1E category
Trial Queue Panel	Prioritized trial list with risk/time/success data, Log Trial button
Case Timeline	Chronological log of all actions taken on this case
Action Bar (bottom)	Primary CTA: Log Trial | Get AI Advice | Update Status | Generate Why-Why
 
10. Non-Functional Requirements
Category	Requirement	Implementation Notes
Performance	Similar case retrieval < 10 seconds	pgvector HNSW index, caching for frequent patterns
Performance	Page load < 3 seconds on WiFi	Next.js SSR + ISR, image optimization
Security	Factory internal access only (intranet)	JWT auth, RBAC middleware on all endpoints
Security	Full audit log for all investigation actions	Immutable audit_log table with timestamp + user_id
Security	Password hashed, never stored plaintext	bcrypt min 12 rounds
Usability	Mobile-friendly — usable on factory floor tablet	Responsive design, touch targets min 44px
Usability	Language: Bahasa Indonesia primary, English secondary	i18n structure from day 1, default ID locale
Reliability	Platform functional when AI is unavailable	All AI features have graceful degradation fallback
Reliability	Offline draft save for trial logs	Local storage draft with sync-on-reconnect
AI Safety	AI must provide confidence score and evidence for every recommendation	Never display recommendation without source reference
AI Safety	AI must not force or auto-execute destructive trials	HIGH risk trials require 2-step engineer confirmation
Data	All engineering data stored on factory server (internal)	Self-hosted deployment, no data sent to external AI API without approval
 
11. Success KPIs & Measurement
KPI	Baseline	Target	Measurement Method
Time to Root Cause	Current avg	-50%	Case created_at → confirmed_at delta
Why-Why Creation Time	Current avg	-70%	Case confirmed → Why-Why approved delta
Similar Case Retrieval Speed	N/A (manual)	< 10 sec	API response time monitoring
Repeat Abnormality Rate	Current %	-30%	% cases with same model+fatal_error within 90 days
Investigation Trial Efficiency	Current avg	+40%	Avg trials before confirmation (lower = better)
AI Recommendation Usefulness	N/A	> 60%	% recommendations marked 'Useful' by engineers
Knowledge Base Growth	0 cases	100+ cases in 3 months	Total archived cases in vector DB
 
12. Integrations & Dependencies
Service	Purpose	Type	Notes
OpenAI API / Local LLM	AI recommendations, Why-Why generation	External OR Self-hosted	Prefer local model for factory intranet. Fallback: GPT-4o-mini via API proxy
pgvector (PostgreSQL)	Vector similarity search for similar cases	Self-hosted (internal DB)	HNSW index for performance. Alternative: Qdrant self-hosted
D-PRIDES / Existing DB	Historical data import (initial bootstrap)	Internal read-only	One-time migration, not real-time sync in MVP
Factory Intranet	Platform access channel — internal only	Network	No internet access required after deploy
Company LDAP/AD (Optional)	Single Sign-On with company accounts	Optional Phase 2	Phase 1 uses own auth system
 
13. Build Order — Sprint Plan
Build one sprint at a time. Never attempt to build all sprints simultaneously. Each sprint must be reviewed and tested before advancing.

Sprint 1 — Foundation (Week 1–2)
□	Project setup: folder structure, environment config, Docker Compose
□	PostgreSQL + pgvector schema migration (all core tables)
□	User authentication: login, JWT, role middleware
□	Basic case creation form (F-001) — no AI yet
□	Case list view with filter by status/model/process
□	Case detail view shell (static, no AI panels)
□	File upload for case photos
□	Basic navigation shell (mobile-first responsive)

Sprint 2 — AI Core (Week 3–4)
□	LLM integration setup (OpenAI API or local model)
□	Embedding pipeline: embed cases on creation, store in pgvector
□	Similar Case Retrieval Engine (F-002): vector similarity search API
□	Similar Cases panel on case detail screen
□	AI Investigation Assistant (F-003): hypothesis generation
□	AI Recommendations panel on case detail screen

Sprint 3 — Investigation Workflow (Week 5–6)
□	Trial Recommendation Engine (F-004): priority scoring from historical data
□	Trial Queue UI: ranked trial list with risk/time/success
□	Trial Logging System (F-005): trial log form + save
□	Case status machine: all 7 status transitions with validation
□	Knowledge Memory Engine (F-007): auto-index on trial log and case archive
□	Offline draft save for trial logs

Sprint 4 — Completion & Polish (Week 7–8)
□	Why-Why Draft Generator (F-006): AI generation + editable form
□	Senior engineer approval flow for Why-Why and root cause confirmation
□	Knowledge base search screen
□	Historical data batch import tool (Excel/PPT migration)
□	Engineer feedback collection on AI recommendations
□	Audit log for all actions
□	Admin panel: user management, system health
□	Performance optimization: response time < 10 sec for retrieval
□	Full testing: unit tests for core business logic, E2E for critical flows
 
14. Risk Register
Risk	Severity	Trigger	Mitigation
Unstructured historical data — low quality Excel/PPT	HIGH	Existing data has no consistent format or taxonomy	Build normalization pipeline; flag low-quality entries; manual curation sprint before launch
Engineer trust — reluctance to trust AI recommendations	HIGH	AI makes wrong recommendation early on	Always show evidence + confidence; allow engineer to dismiss; never force AI path
AI hallucination — incorrect or unsafe recommendation	HIGH	LLM generates plausible-sounding wrong answer	RAG grounds all recommendations in historical data; disclaimer shown on low confidence
Poor investigation logging discipline	MEDIUM	Engineers skip trial logging	Make logging UX extremely simple; gamification (case score); manager visibility
AI over-reliance risk	MEDIUM	Junior engineers blindly follow AI without thinking	AI always says 'Verify this' not 'This IS the answer'; senior approval for root cause
Intranet latency for LLM	MEDIUM	Local LLM inference slow on factory server hardware	Profile hardware early; option to use API-based LLM as fallback with data sanitization
 
15. Open Questions
#	Question	Impact	Default if Unanswered
1	Self-hosted LLM vs. OpenAI API proxy?	Data privacy, latency, cost	Use OpenAI GPT-4o-mini via API with data anonymization for Phase 1
2	pgvector vs. Qdrant for vector search?	Infrastructure complexity, performance	Use pgvector first (simpler, same DB). Migrate to Qdrant if performance insufficient
3	Initial data migration scope — which Excel files?	Quality of knowledge base at launch	Migrate last 2 years of Why-Why documents and fatal error logs
4	Which factory lines to pilot first?	Scope of Phase 1 rollout	Start with IJP/SIDM lines (Brian's scope)
5	LDAP/Active Directory SSO required from day 1?	Auth system complexity	Phase 1 uses own auth. SSO as Phase 2 optional
6	Notification system — email vs. internal only?	Email server access on intranet	Phase 1: In-app notifications only. Email notifications Phase 2
7	Maximum number of concurrent users?	Server sizing	Design for 50 concurrent users initially

This PRD is a living document. All changes must be reviewed by Engineering Manager before sprint execution. Version control this file alongside the codebase.

END OF DOCUMENT
Arcom Engineering Intelligence — PRD v1.0 — PT. Indonesia Epson Industry

