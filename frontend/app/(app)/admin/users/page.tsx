"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/useAuth";
import { api, type AdminUser, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/Toast";

export default function AdminUsersPage() {
  const { token, user, ready } = useAuth();
  const { showToast } = useToast();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [form, setForm] = useState({ employee_id: "", full_name: "", email: "", division: "", role: "JUNIOR", password: "changeme123" });

  const load = () => {
    if (!token) return;
    api.adminListUsers(token).then(setUsers).catch(() => {});
  };

  useEffect(() => { load(); }, [token]);

  const create = async () => {
    if (!token) return;
    try {
      await api.adminCreateUser(token, form);
      showToast("User dibuat", "success");
      setForm({ employee_id: "", full_name: "", email: "", division: "", role: "JUNIOR", password: "changeme123" });
      load();
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : "Gagal", "error");
    }
  };

  const toggleActive = async (u: AdminUser) => {
    if (!token) return;
    await api.adminUpdateUser(token, u.id, { is_active: !u.is_active } as never);
    load();
  };

  if (!ready || user?.role !== "ADMIN") return null;

  return (
    <div className="p-4 pt-6">
      <Link href="/admin" className="text-brand text-sm">← Admin</Link>
      <h1 className="text-xl font-bold mt-2 mb-4">Manajemen User</h1>

      <div className="bg-white border rounded-xl p-4 mb-6 space-y-2">
        <p className="text-sm font-semibold text-gray-700">Buat User Baru</p>
        {(["employee_id", "full_name", "email", "division"] as const).map((f) => (
          <input
            key={f}
            className="w-full border rounded-lg px-3 py-2 text-sm"
            placeholder={f}
            value={form[f]}
            onChange={(e) => setForm({ ...form, [f]: e.target.value })}
          />
        ))}
        <select className="w-full border rounded-lg px-3 py-2 text-sm" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
          {["JUNIOR", "SENIOR", "MANAGER", "ADMIN"].map((r) => <option key={r} value={r}>{r}</option>)}
        </select>
        <button type="button" onClick={create} className="w-full py-2.5 bg-brand text-white rounded-xl text-sm font-medium">
          Tambah User
        </button>
      </div>

      <div className="space-y-2">
        {users.map((u) => (
          <div key={u.id} className="bg-white border rounded-xl p-3 flex justify-between items-center">
            <div>
              <p className="font-medium text-sm">{u.full_name}</p>
              <p className="text-xs text-gray-400">{u.employee_id} · {u.role}</p>
            </div>
            <button
              type="button"
              onClick={() => toggleActive(u)}
              className={`text-xs px-2 py-1 rounded-full ${u.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}
            >
              {u.is_active ? "Aktif" : "Nonaktif"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
