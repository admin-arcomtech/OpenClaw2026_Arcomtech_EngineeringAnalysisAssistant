"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { saveSession } from "@/lib/auth";
import { useToast } from "@/components/ui/Toast";

export function LoginForm() {
  const router = useRouter();
  const { showToast } = useToast();
  const [employeeId, setEmployeeId] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const loginRes = await api.login(employeeId, password);
      const userRes = await api.me(loginRes.access_token);
      saveSession(loginRes.access_token, userRes);
      router.replace("/dashboard");
    } catch (err) {
      const msg =
        err instanceof ApiError
          ? err.message
          : "Terjadi kesalahan, coba lagi";
      showToast(msg, "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <label htmlFor="employee_id" className="block text-sm font-medium text-gray-700 mb-1.5">
          Employee ID
        </label>
        <input
          id="employee_id"
          type="text"
          autoComplete="username"
          required
          value={employeeId}
          onChange={(e) => setEmployeeId(e.target.value)}
          className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-brand focus:ring-2 focus:ring-brand/20 outline-none text-gray-900 text-base transition min-h-touch"
          placeholder="Contoh: EMP001"
        />
      </div>
      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1.5">
          Password
        </label>
        <input
          id="password"
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-brand focus:ring-2 focus:ring-brand/20 outline-none text-gray-900 text-base transition min-h-touch"
          placeholder="••••••••"
        />
      </div>
      <button
        type="submit"
        disabled={loading}
        className="w-full py-3 bg-brand hover:bg-brand-dark text-white font-semibold rounded-xl transition min-h-touch disabled:opacity-60 disabled:cursor-not-allowed text-base"
      >
        {loading ? "Memproses..." : "Masuk"}
      </button>
    </form>
  );
}
