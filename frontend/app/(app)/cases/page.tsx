"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/useAuth";
import { api, type CaseSummary, type CaseListResponse } from "@/lib/api";
import { StatusBadge, SeverityBadge } from "@/components/ui/StatusBadge";

const STATUS_FILTERS = [
  { value: "", label: "Semua" },
  { value: "OPEN", label: "Terbuka" },
  { value: "INVESTIGATING", label: "Investigasi" },
  { value: "RESOLVED", label: "Selesai" },
  { value: "CLOSED", label: "Ditutup" },
];

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("id-ID", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });
}

export default function CasesPage() {
  const { token, ready } = useAuth();
  const [data, setData] = useState<CaseListResponse | null>(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [modelFilter, setModelFilter] = useState("");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);

  const fetchCases = async () => {
    if (!token) return;
    setLoading(true);
    try {
      const res = await api.listCases(token, {
        status: statusFilter || undefined,
        model: modelFilter || undefined,
        page,
      });
      setData(res);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (ready) fetchCases();
  }, [token, ready, statusFilter, modelFilter, page]);

  if (!ready) return null;

  return (
    <div className="p-4 pt-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Daftar Kasus</h1>
          {data && <p className="text-xs text-gray-400 mt-0.5">{data.total} kasus ditemukan</p>}
        </div>
        <Link
          href="/cases/new"
          className="flex items-center gap-1.5 px-4 py-2.5 bg-brand text-white text-sm font-semibold rounded-xl min-h-touch"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 4v16m8-8H4" />
          </svg>
          Baru
        </Link>
      </div>

      {/* Status filter chips */}
      <div className="flex gap-2 overflow-x-auto pb-2 mb-3 -mx-4 px-4 scrollbar-none">
        {STATUS_FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => { setStatusFilter(f.value); setPage(1); }}
            className={`flex-shrink-0 px-3.5 py-1.5 rounded-full text-sm font-medium transition min-h-touch ${
              statusFilter === f.value
                ? "bg-brand text-white"
                : "bg-white border border-gray-200 text-gray-600"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Model search */}
      <div className="mb-4">
        <input
          type="search"
          placeholder="Cari model..."
          value={modelFilter}
          onChange={(e) => { setModelFilter(e.target.value); setPage(1); }}
          className="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm bg-white outline-none focus:border-brand focus:ring-2 focus:ring-brand/20 min-h-touch"
        />
      </div>

      {/* Case cards */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white border border-gray-100 rounded-2xl p-4 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/3 mb-2" />
              <div className="h-3 bg-gray-100 rounded w-2/3" />
            </div>
          ))}
        </div>
      ) : data?.items.length === 0 ? (
        <div className="bg-white border border-gray-200 rounded-2xl p-10 text-center text-gray-400">
          <p className="font-medium">Belum ada kasus</p>
          <p className="text-sm mt-1">Buat kasus pertama dengan tombol Baru</p>
        </div>
      ) : (
        <div className="space-y-3">
          {data?.items.map((c) => (
            <Link key={c.id} href={`/cases/${c.id}`} className="block bg-white border border-gray-200 rounded-2xl p-4 hover:border-brand/40 hover:shadow-sm transition">
              <div className="flex items-start justify-between gap-2 mb-2">
                <span className="font-mono text-xs text-gray-400">{c.case_id}</span>
                <div className="flex gap-1.5 flex-shrink-0">
                  <StatusBadge status={c.status} />
                  {c.severity && <SeverityBadge severity={c.severity} />}
                </div>
              </div>
              <p className="font-semibold text-gray-800 text-sm leading-snug mb-1">{c.title}</p>
              <div className="flex items-center gap-3 text-xs text-gray-400">
                {c.process && <span>{c.process}</span>}
                {c.line && <span>·  {c.line}</span>}
                <span className="ml-auto">{formatDate(c.created_at)}</span>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Pagination */}
      {data && data.pages > 1 && (
        <div className="flex justify-center items-center gap-3 mt-6">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 rounded-xl border border-gray-200 text-sm disabled:opacity-40 min-h-touch"
          >
            ← Sebelumnya
          </button>
          <span className="text-sm text-gray-500">{page} / {data.pages}</span>
          <button
            onClick={() => setPage((p) => Math.min(data.pages, p + 1))}
            disabled={page === data.pages}
            className="px-4 py-2 rounded-xl border border-gray-200 text-sm disabled:opacity-40 min-h-touch"
          >
            Berikutnya →
          </button>
        </div>
      )}
    </div>
  );
}
