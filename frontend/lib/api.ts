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
  | "TRIAL_IN_PROGRESS"
  | "RESOLVED"
  | "CLOSED"
  | "ARCHIVED";

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
};
