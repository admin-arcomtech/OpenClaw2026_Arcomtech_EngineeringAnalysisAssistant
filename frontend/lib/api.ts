const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {}
    throw new ApiError(res.status, detail);
  }
  return res.json() as Promise<T>;
}

// ── Auth ─────────────────────────────────────────────────────────────────────

export type LoginResponse = {
  access_token: string;
  token_type: string;
  expires_in_hours: number;
};

export type UserMe = {
  id: string;
  employee_id: string;
  full_name: string;
  role: "JUNIOR" | "SENIOR" | "MANAGER" | "ADMIN";
  is_active: boolean;
};

// ── Cases ─────────────────────────────────────────────────────────────────────

export type CaseStatus =
  | "OPEN"
  | "INVESTIGATING"
  | "SUSPECTED_CAUSE"
  | "TRIAL_RUNNING"
  | "MONITORING"
  | "CONFIRMED"
  | "ARCHIVED"
  | "TRIAL_IN_PROGRESS"
  | "RESOLVED"
  | "CLOSED";

export type Severity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type Shift = "PAGI" | "SIANG" | "MALAM";

export type PhotoOut = {
  id: string;
  filename: string;
  storage_path: string;
  mime_type: string | null;
  file_size_bytes: number | null;
  caption: string | null;
  created_at: string;
};

export type UserBrief = {
  id: string;
  employee_id: string;
  full_name: string;
  role: string;
};

export type CaseOut = {
  id: string;
  case_id: string;
  title: string;
  description: string | null;
  model: string | null;
  process: string | null;
  line: string | null;
  fatal_error: string | null;
  symptom: string | null;
  temporary_action: string | null;
  operator_id: string | null;
  spc_reference: string | null;
  status: CaseStatus;
  severity: Severity | null;
  shift: Shift | null;
  reporter_id: string;
  assigned_to_id: string | null;
  reporter: UserBrief | null;
  assigned_to: UserBrief | null;
  photos: PhotoOut[];
  created_at: string;
  updated_at: string;
};

export type CaseSummary = {
  id: string;
  case_id: string;
  title: string;
  model: string | null;
  process: string | null;
  line: string | null;
  fatal_error: string | null;
  status: CaseStatus;
  severity: Severity | null;
  reporter_id: string;
  created_at: string;
};

export type CaseListResponse = {
  items: CaseSummary[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
};

export type DuplicateWarning = {
  has_duplicate: boolean;
  cases: CaseSummary[];
};

export type Taxonomy = {
  models: string[];
  processes: string[];
  lines: string[];
  fatal_errors: string[];
  severities: string[];
  shifts: string[];
  statuses: string[];
};

// ── AI (Sprint 3) ─────────────────────────────────────────────────────────────

export type SimilarCaseItem = {
  id: string;
  case_id: string;
  similarity_pct: number;
  title: string;
  model: string | null;
  process: string | null;
  fatal_error: string | null;
  status: string;
  root_cause: string | null;
  countermeasure: string | null;
  resolution_days: number | null;
  created_at: string;
};

export type SimilarCaseResponse = {
  items: SimilarCaseItem[];
  source: string;
  mode: "vector" | "keyword";
  warning: string | null;
  threshold: number;
  total_candidates: number;
};

export type Hypothesis = {
  title: string;
  confidence: number;
  category_4m1e: "Man" | "Machine" | "Material" | "Method" | "Environment";
  evidence: string[];
  suggested_verification: string[];
  trial_risk: "LOW" | "MEDIUM" | "HIGH";
  estimated_time_min: number;
  similar_case_count: number;
};

export type RecommendationsResponse = {
  id: string;
  case_id: string;
  hypotheses: Hypothesis[];
  source: string;
  model_version: string;
  created_at: string;
};

export type AIHealth = {
  openclaw_configured: boolean;
  openclaw_reachable: boolean;
  fallback_available: boolean;
  openclaw_base_url: string | null;
};

export type CaseCreatePayload = {
  model: string;
  process: string;
  line: string;
  fatal_error: string;
  symptom: string;
  description: string;
  severity?: string;
  shift?: string;
  temporary_action?: string;
  operator_id?: string;
  spc_reference?: string;
  assigned_to_id?: string;
};

export const api = {
  login: (employee_id: string, password: string) =>
    request<LoginResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ employee_id, password }),
    }),

  logout: (token: string) =>
    request<{ message: string }>("/api/auth/logout", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    }),

  me: (token: string) =>
    request<UserMe>("/api/auth/me", {
      headers: { Authorization: `Bearer ${token}` },
    }),

  // Cases
  createCase: (token: string, data: CaseCreatePayload) =>
    request<CaseOut>("/api/cases", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify(data),
    }),

  listCases: (
    token: string,
    params?: { status?: string; model?: string; process?: string; severity?: string; page?: number }
  ) => {
    const qs = new URLSearchParams();
    if (params?.status) qs.set("status", params.status);
    if (params?.model) qs.set("model", params.model);
    if (params?.process) qs.set("process", params.process);
    if (params?.severity) qs.set("severity", params.severity);
    if (params?.page) qs.set("page", String(params.page));
    return request<CaseListResponse>(`/api/cases?${qs}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  getCase: (token: string, id: string) =>
    request<CaseOut>(`/api/cases/${id}`, {
      headers: { Authorization: `Bearer ${token}` },
    }),

  updateStatus: (token: string, id: string, status: string, note?: string) =>
    request<CaseOut>(`/api/cases/${id}/status`, {
      method: "PATCH",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify({ status, note }),
    }),

  checkDuplicate: (token: string, data: { model: string; fatal_error: string }) =>
    request<DuplicateWarning>("/api/cases/check-duplicate", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify(data),
    }),

  getMetadata: (token: string) =>
    request<Taxonomy>("/api/metadata", {
      headers: { Authorization: `Bearer ${token}` },
    }),

  // AI — Sprint 3
  similarCases: (token: string, case_id: string, threshold = 0.5, limit = 10) =>
    request<SimilarCaseResponse>("/api/ai/similar-cases", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify({ case_id, threshold, limit }),
    }),

  recommendations: (token: string, case_id: string, extra_context?: string) =>
    request<RecommendationsResponse>("/api/ai/recommendations", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify({ case_id, extra_context }),
    }),

  aiFeedback: (token: string, case_id: string, data: { target_type: string; target_id: string; rating: string; note?: string }) =>
    request<{ ok: boolean; id: string }>(`/api/ai/feedback?case_id=${encodeURIComponent(case_id)}`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify(data),
    }),

  aiHealth: (token: string) =>
    request<AIHealth>("/api/ai/health", {
      headers: { Authorization: `Bearer ${token}` },
    }),

  // Sprint 4 — Trials & Queue
  trialPriority: (token: string, case_id: string, manual_trial?: object) =>
    request<{ trial_queue: TrialQueueItem[]; all_high_risk: boolean; warning?: string }>(
      "/api/ai/trial-priority",
      { method: "POST", headers: { Authorization: `Bearer ${token}` }, body: JSON.stringify({ case_id, manual_trial }) }
    ),

  getTrialQueue: (token: string, caseId: string) =>
    request<{ items: TrialQueueItem[]; status: string }>(`/api/cases/${caseId}/trial-queue`, {
      headers: { Authorization: `Bearer ${token}` },
    }),

  saveTrialQueue: (token: string, caseId: string, items: TrialQueueItem[], status = "DRAFT") =>
    request<{ items: TrialQueueItem[]; status: string }>(`/api/cases/${caseId}/trial-queue`, {
      method: "PUT",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify({ items, status }),
    }),

  approveTrialQueue: (token: string, caseId: string) =>
    request<{ status: string; items: TrialQueueItem[] }>(`/api/cases/${caseId}/trial-queue/approve`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    }),

  listTrials: (token: string, caseId: string) =>
    request<TrialLog[]>(`/api/cases/${caseId}/trials`, {
      headers: { Authorization: `Bearer ${token}` },
    }),

  createTrial: (token: string, caseId: string, data: TrialCreatePayload) =>
    request<TrialLog>(`/api/cases/${caseId}/trials`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify(data),
    }),

  confirmRootCause: (token: string, caseId: string, root_cause: string) =>
    request<CaseOut>(`/api/cases/${caseId}/confirm`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify({ root_cause }),
    }),

  getTimeline: (token: string, caseId: string) =>
    request<TimelineEvent[]>(`/api/cases/${caseId}/timeline`, {
      headers: { Authorization: `Bearer ${token}` },
    }),

  // Sprint 5 — Why-Why
  generateWhyWhyDraft: (token: string, case_id: string, notes?: string) =>
    request<WhyWhyDoc>("/api/ai/why-why-draft", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify({ case_id, notes }),
    }),

  getWhyWhy: (token: string, caseId: string) =>
    request<WhyWhyDoc>(`/api/cases/${caseId}/why-why`, {
      headers: { Authorization: `Bearer ${token}` },
    }),

  updateWhyWhy: (token: string, caseId: string, draft: object) =>
    request<WhyWhyDoc>(`/api/cases/${caseId}/why-why`, {
      method: "PUT",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify({ draft }),
    }),

  submitWhyWhy: (token: string, caseId: string) =>
    request<WhyWhyDoc>(`/api/cases/${caseId}/why-why/submit`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify({}),
    }),

  approveWhyWhy: (token: string, caseId: string, approved: boolean, comment?: string) =>
    request<WhyWhyDoc>(`/api/cases/${caseId}/why-why/approve`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify({ approved, comment }),
    }),

  // Sprint 5 — Knowledge Base
  searchKnowledge: (token: string, params: { q?: string; model?: string; process?: string; limit?: number }) => {
    const qs = new URLSearchParams();
    if (params.q) qs.set("q", params.q);
    if (params.model) qs.set("model", params.model);
    if (params.process) qs.set("process", params.process);
    if (params.limit) qs.set("limit", String(params.limit));
    return request<{ items: KnowledgeItem[]; mode: string; total: number }>(
      `/api/knowledge/search?${qs}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
  },

  knowledgeMetrics: (token: string) =>
    request<KnowledgeMetrics>("/api/knowledge/metrics", {
      headers: { Authorization: `Bearer ${token}` },
    }),

  // Sprint 5 — Notifications
  listNotifications: (token: string, unread_only = false) =>
    request<{ items: NotificationItem[]; unread_count: number }>(
      `/api/notifications?unread_only=${unread_only}`,
      { headers: { Authorization: `Bearer ${token}` } }
    ),

  markNotificationRead: (token: string, id: string) =>
    request<{ ok: boolean }>(`/api/notifications/${id}/read`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    }),

  // Sprint 5 — Admin
  adminKpis: (token: string) =>
    request<AdminKpis>("/api/admin/kpis", { headers: { Authorization: `Bearer ${token}` } }),

  adminListUsers: (token: string) =>
    request<AdminUser[]>(`/api/admin/users`, { headers: { Authorization: `Bearer ${token}` } }),

  adminCreateUser: (token: string, data: AdminUserCreate) =>
    request<AdminUser>(`/api/admin/users`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify(data),
    }),

  adminUpdateUser: (token: string, userId: string, data: Partial<AdminUserCreate>) =>
    request<AdminUser>(`/api/admin/users/${userId}`, {
      method: "PATCH",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify(data),
    }),

  adminAuditLog: (token: string, limit = 100) =>
    request<{ items: AuditEntry[] }>(`/api/admin/audit?limit=${limit}`, {
      headers: { Authorization: `Bearer ${token}` },
    }),

  adminImport: async (token: string, file: File, dry_run: boolean) => {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${BASE}/api/admin/import?dry_run=${dry_run}`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: form,
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new ApiError(res.status, body.detail ?? `HTTP ${res.status}`);
    }
    return res.json() as Promise<ImportResult>;
  },
};

export type TrialQueueItem = {
  id: string;
  trial_action: string;
  risk_level: string;
  estimated_time_min: number;
  historical_success_rate?: number | null;
  destructive: boolean;
  required_tools: string[];
  priority_rank: number;
  requires_senior_approval: boolean;
  source: string;
  skipped?: boolean;
};

export type TrialLog = {
  id: string;
  case_id: string;
  sequence: number;
  trial_action?: string;
  observation?: string;
  outcome?: string;
  improvement_pct?: number;
  time_spent_min?: number;
  scrap_impact?: string;
  scrap_qty?: number;
  risk_level?: string;
  destructive: boolean;
  engineer_comment?: string;
  performed_by_id?: string;
  queue_item_id?: string;
  created_at: string;
};

export type TrialCreatePayload = {
  trial_action: string;
  outcome: string;
  observation: string;
  improvement_pct?: number;
  time_spent_min?: number;
  scrap_impact?: string;
  scrap_qty?: number;
  risk_level?: string;
  destructive?: boolean;
  engineer_comment?: string;
  queue_item_id?: string;
  hypothesis?: string;
};

export type TimelineEvent = {
  id: string;
  event_type: string;
  title: string;
  detail?: string;
  actor?: string;
  created_at: string;
};

export type WhyWhyDoc = {
  id: string;
  case_id: string;
  draft?: {
    why_steps: { level: number; question: string; answer: string; category_4m1e: string }[];
    immediate_countermeasure?: string;
    corrective_action?: string;
    preventive_action?: string;
    partial?: boolean;
    source?: string;
  };
  approved_version?: object;
  status: string;
  is_readonly?: boolean;
  submitted_at?: string;
  approved_at?: string;
  rejection_comment?: string;
};

export type KnowledgeItem = {
  case_id: string;
  id: string;
  title: string;
  model?: string;
  process?: string;
  fatal_error?: string;
  root_cause?: string;
  status: string;
  similarity_pct?: number;
  has_why_why: boolean;
  created_at?: string;
};

export type KnowledgeMetrics = {
  indexed_cases: number;
  archived_cases: number;
  approved_why_why: number;
  last_import_at?: string | null;
};

export type NotificationItem = {
  id: string;
  event: string;
  message: string;
  case_id?: string;
  is_read: boolean;
  created_at: string;
};

export type AdminKpis = {
  avg_time_to_root_cause_hours?: number | null;
  avg_why_why_creation_hours?: number | null;
  ai_usefulness_pct?: number | null;
  total_feedback: number;
  kb_archived_cases: number;
  kb_indexed_cases: number;
  repeat_abnormality_cases_90d: number;
};

export type AdminUser = {
  id: string;
  employee_id: string;
  full_name: string;
  email?: string | null;
  division?: string | null;
  role: string;
  is_active: boolean;
};

export type AdminUserCreate = {
  employee_id: string;
  full_name: string;
  email?: string;
  division?: string;
  role: string;
  password?: string;
};

export type AuditEntry = {
  id: string;
  event: string;
  user_id?: string;
  detail?: object;
  created_at?: string;
};

export type ImportResult = {
  job_id: string;
  status: string;
  dry_run: boolean;
  total_rows?: number;
  imported_rows?: number;
  skipped_rows?: number;
  errors?: { row: number; error: string }[];
};
