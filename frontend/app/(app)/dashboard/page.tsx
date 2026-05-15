"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/useAuth";
import { api, type CaseSummary, type CaseListResponse } from "@/lib/api";
import { StatusBadge, SeverityBadge } from "@/components/ui/StatusBadge";

const ROLE_LABEL: Record<string, string> = {
  JUNIOR: "Junior Engineer",
  SENIOR: "Senior Engineer",
  MANAGER: "Engineering Manager",
  ADMIN: "Administrator",
};

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("id-ID", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });
}

export default function DashboardPage() {
  const { token, user, ready } = useAuth();
  const [open, setOpen] = useState<CaseListResponse | null>(null);
  const [investigating, setInvestigating] = useState<CaseListResponse | null>(null);
  const [resolved, setResolved] = useState<CaseListResponse | null>(null);
  const [recent, setRecent] = useState<CaseSummary[]>([]);
  const [kpis, setKpis] = useState<{ ai_usefulness_pct?: number | null; avg_time_to_root_cause_hours?: number | null; kb_indexed_cases?: number } | null>(null);

  useEffect(() => {
    if (!token) return;
    Promise.all([
      api.listCases(token, { status: "OPEN", page: 1 }),
      api.listCases(token, { status: "INVESTIGATING", page: 1 }),
      api.listCases(token, { status: "RESOLVED", page: 1 }),
      api.listCases(token, { page: 1 }),
    ]).then(([o, i, r, all]) => {
      setOpen(o);
      setInvestigating(i);
      setResolved(r);
      setRecent(all.items.slice(0, 5));
    }).catch(() => {});
    if (user && ["MANAGER", "ADMIN"].includes(user.role)) {
      api.adminKpis(token).then(setKpis).catch(() => {});
    }
  }, [token, user]);

  if (!ready || !user) return null;

  return (
    <div className="p-4 pt-6">
      {/* Header */}
      <div className="mb-6">
        <p className="text-sm text-gray-500">Selamat datang,</p>
        <h1 className="text-2xl font-bold text-gray-900">{user.full_name}</h1>
        <span className="inline-block mt-1 px-2.5 py-0.5 bg-brand-light text-brand text-xs font-semibold rounded-full">
          {ROLE_LABEL[user.role] ?? user.role}
        </span>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        {[
          { label: "Terbuka", value: open?.total ?? "—", color: "bg-blue-50 border-blue-100", text: "text-blue-700" },
          { label: "Investigasi", value: investigating?.total ?? "—", color: "bg-yellow-50 border-yellow-100", text: "text-yellow-700" },
          { label: "Selesai", value: resolved?.total ?? "—", color: "bg-green-50 border-green-100", text: "text-green-700" },
        ].map((stat) => (
          <Link key={stat.label} href={`/cases?status=${stat.label === "Terbuka" ? "OPEN" : stat.label === "Investigasi" ? "INVESTIGATING" : "RESOLVED"}`}
            className={`${stat.color} border rounded-xl p-3 text-center`}
          >
            <p className={`text-2xl font-bold ${stat.text}`}>{stat.value}</p>
            <p className="text-xs text-gray-500 mt-0.5">{stat.label}</p>
          </Link>
        ))}
      </div>

      {kpis && (
        <div className="grid grid-cols-2 gap-3 mb-6">
          <div className="bg-purple-50 border border-purple-100 rounded-xl p-3">
            <p className="text-xs text-gray-500">AI Berguna</p>
            <p className="text-xl font-bold text-purple-700">{kpis.ai_usefulness_pct ?? "—"}%</p>
          </div>
          <div className="bg-teal-50 border border-teal-100 rounded-xl p-3">
            <p className="text-xs text-gray-500">Avg TTRC (jam)</p>
            <p className="text-xl font-bold text-teal-700">{kpis.avg_time_to_root_cause_hours ?? "—"}</p>
          </div>
        </div>
      )}

      {/* Quick action */}
      <Link
        href="/cases/new"
        className="flex items-center justify-center gap-2 w-full py-3.5 bg-brand text-white font-semibold rounded-2xl shadow-sm mb-6 min-h-touch"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 4v16m8-8H4" />
        </svg>
        Buat Kasus Baru
      </Link>

      {/* Recent cases */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-gray-800">Kasus Terbaru</h2>
          <Link href="/cases" className="text-sm text-brand font-medium">Lihat semua →</Link>
        </div>

        {recent.length === 0 ? (
          <div className="bg-white border border-gray-200 rounded-2xl p-6 text-center text-gray-400 text-sm">
            Belum ada kasus. Mulai dengan membuat kasus baru.
          </div>
        ) : (
          <div className="space-y-2.5">
            {recent.map((c) => (
              <Link key={c.id} href={`/cases/${c.id}`}
                className="flex items-center gap-3 bg-white border border-gray-200 rounded-xl p-3 hover:border-brand/40 transition"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5 mb-0.5">
                    <span className="font-mono text-xs text-gray-400">{c.case_id}</span>
                    <StatusBadge status={c.status} />
                  </div>
                  <p className="text-sm font-medium text-gray-800 truncate">{c.title}</p>
                  <p className="text-xs text-gray-400">{formatDate(c.created_at)}</p>
                </div>
                {c.severity && <SeverityBadge severity={c.severity} />}
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
