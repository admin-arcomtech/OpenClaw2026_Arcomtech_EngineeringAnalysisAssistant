"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { saveSession } from "@/lib/auth";
import { useToast } from "@/components/ui/Toast";

const SEED_USERS: { id: string; password: string; role: string }[] = [
  { id: "EMP001", password: "Junior@12345", role: "Junior" },
  { id: "EMP002", password: "Senior@12345", role: "Senior" },
  { id: "EMP003", password: "Manager@12345", role: "Manager" },
  { id: "EMP004", password: "Admin@12345", role: "Admin" },
];

export function LoginForm() {
  const router = useRouter();
  const { showToast } = useToast();
  const [employeeId, setEmployeeId] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const [errMsg, setErrMsg] = useState<string | null>(null);

  const fill = (id: string, pwd: string) => {
    setEmployeeId(id);
    setPassword(pwd);
    setErrMsg(null);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrMsg(null);
    try {
      const loginRes = await api.login(employeeId, password);
      const userRes = await api.me(loginRes.access_token);
      saveSession(loginRes.access_token, userRes);
      router.replace("/dashboard");
    } catch (err) {
      let msg = "Terjadi kesalahan, coba lagi";
      if (err instanceof ApiError) {
        if (err.status === 401) {
          msg = "Employee ID atau password salah";
        } else if (err.status === 0 || err.message.startsWith("HTTP 0")) {
          msg = "Tidak dapat terhubung ke server. Cek koneksi atau hubungi Admin.";
        } else {
          msg = err.message;
        }
      } else if (err instanceof TypeError) {
        msg = "Tidak dapat terhubung ke server (network). Pastikan backend port 8000 dapat diakses.";
      }
      setErrMsg(msg);
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

      {errMsg && (
        <p className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg p-2.5">
          {errMsg}
        </p>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full py-3 bg-brand hover:bg-brand-dark text-white font-semibold rounded-xl transition min-h-touch disabled:opacity-60 disabled:cursor-not-allowed text-base"
      >
        {loading ? "Memproses..." : "Masuk"}
      </button>

      <div className="pt-2 border-t border-gray-100">
        <button
          type="button"
          onClick={() => setShowHelp(!showHelp)}
          className="text-sm text-brand font-medium w-full text-center py-1"
        >
          {showHelp ? "Tutup" : "Belum punya akun / Lihat akun pilot demo"}
        </button>

        {showHelp && (
          <div className="mt-3 space-y-3 text-xs text-gray-600">
            <div>
              <p className="font-semibold text-gray-700 mb-1.5">Akun pilot (klik untuk isi otomatis):</p>
              <div className="space-y-1.5">
                {SEED_USERS.map((u) => (
                  <button
                    type="button"
                    key={u.id}
                    onClick={() => fill(u.id, u.password)}
                    className="w-full text-left px-3 py-2 bg-gray-50 hover:bg-brand-light border border-gray-200 rounded-lg flex justify-between items-center"
                  >
                    <span><span className="font-mono">{u.id}</span> · {u.role}</span>
                    <span className="text-gray-400 font-mono text-[10px]">{u.password}</span>
                  </button>
                ))}
              </div>
            </div>
            <div className="bg-blue-50 border border-blue-100 rounded-lg p-2.5">
              <p className="font-semibold text-blue-800 mb-1">Cara membuat akun baru:</p>
              <p className="text-blue-700">
                Self‑registration tidak tersedia (sesuai kebijakan ISP/SIDM). Akun baru
                dibuat oleh <b>Admin (EMP004)</b> melalui menu <b>Admin → Manajemen User</b>.
              </p>
            </div>
          </div>
        )}
      </div>
    </form>
  );
}
