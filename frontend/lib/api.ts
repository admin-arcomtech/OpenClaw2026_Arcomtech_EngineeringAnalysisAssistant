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
};
