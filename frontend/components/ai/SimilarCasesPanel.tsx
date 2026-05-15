"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type SimilarCaseItem, type SimilarCaseResponse, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/Toast";

interface Props {
  token: string;
  caseId: string;
}

function SourceBadge({ source, mode }: { source: string; mode: string }) {
  const colors: Record<string, string> = {
    openclaw: "bg-emerald-100 text-emerald-700",
    fallback: "bg-amber-100 text-amber-700",
    keyword:  "bg-gray-100 text-gray-600",
  };
  const label: Record<string, string> = {
    openclaw: "Openclaw",
    fallback: "Lokal (fallback)",
    keyword:  "Keyword",
  };
  const cls = colors[source] ?? "bg-gray-100 text-gray-600";
  return (
    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide ${cls}`}>
      {label[source] ?? source} · {mode}
    </span>
  );
}

function SimilarityBar({ pct }: { pct: number }) {
  const color = pct >= 80 ? "bg-emerald-500" : pct >= 60 ? "bg-blue-500" : pct >= 40 ? "bg-amber-500" : "bg-gray-400";
  return (
    <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
      <div className={`h-full ${color}`} style={{ width: `${Math.min(100, pct)}%` }} />
    </div>
  );
}

export function SimilarCasesPanel({ token, caseId }: Props) {
  const { showToast } = useToast();
  const [data, setData] = useState<SimilarCaseResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await api.similarCases(token, caseId, 0.4, 10);
      setData(res);
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : "Gagal memuat similar cases", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [caseId]);

  const sendFeedback = async (item: SimilarCaseItem, rating: "useful" | "not_relevant") => {
    try {
      await api.aiFeedback(token, caseId, {
        target_type: "similar_case",
        target_id: item.id,
        rating,
      });
      showToast(rating === "useful" ? "Ditandai sebagai referensi" : "Feedback tersimpan", "success");
    } catch {}
  };

  const items = expanded ? data?.items ?? [] : (data?.items ?? []).slice(0, 3);

  return (
    <div className="bg-white border border-gray-200 rounded-2xl p-4">
      <div className="flex items-start justify-between gap-2 mb-3">
        <div>
          <p className="text-xs font-semibold text-brand uppercase tracking-wider">Similar Cases (F-002)</p>
          {data && (
            <p className="text-[11px] text-gray-400 mt-0.5">
              {data.items.length} hasil · {data.total_candidates} total kasus
            </p>
          )}
        </div>
        <div className="flex items-center gap-2">
          {data && <SourceBadge source={data.source} mode={data.mode} />}
          <button
            onClick={fetchData}
            disabled={loading}
            className="p-1.5 rounded-lg hover:bg-gray-100 min-h-touch min-w-touch flex items-center justify-center disabled:opacity-50"
            title="Refresh"
          >
            <svg className={`w-4 h-4 text-gray-500 ${loading ? "animate-spin" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>

      {data?.warning && (
        <div className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg p-2 mb-3">
          {data.warning}
        </div>
      )}

      {loading ? (
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-gray-100 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <p className="text-sm text-gray-400 text-center py-4">
          {data?.total_candidates && data.total_candidates <= 1
            ? "Belum ada kasus serupa. Ini investigasi baru."
            : "Tidak ada kasus dengan similarity di atas threshold."}
        </p>
      ) : (
        <div className="space-y-2">
          {items.map((item) => (
            <div key={item.id} className="border border-gray-100 rounded-xl p-3 hover:border-brand/30 transition">
              <div className="flex items-start justify-between gap-2 mb-1.5">
                <Link href={`/cases/${item.id}`} className="flex-1 min-w-0">
                  <p className="font-mono text-[11px] text-gray-400">{item.case_id}</p>
                  <p className="text-sm font-semibold text-gray-800 leading-snug truncate">{item.title}</p>
                </Link>
                <span className="font-bold text-brand text-sm flex-shrink-0">{item.similarity_pct.toFixed(0)}%</span>
              </div>
              <SimilarityBar pct={item.similarity_pct} />
              <div className="mt-2 space-y-1 text-xs text-gray-600">
                {item.countermeasure && (
                  <p><span className="text-gray-400">Countermeasure:</span> {item.countermeasure}</p>
                )}
                {item.root_cause && (
                  <p><span className="text-gray-400">Root cause:</span> {item.root_cause}</p>
                )}
                {item.resolution_days != null && (
                  <p><span className="text-gray-400">Resolusi:</span> {item.resolution_days} hari</p>
                )}
              </div>
              <div className="flex gap-2 mt-2 pt-2 border-t border-gray-50">
                <button
                  onClick={() => sendFeedback(item, "useful")}
                  className="text-[11px] text-emerald-700 font-medium px-2 py-1 rounded hover:bg-emerald-50 min-h-touch"
                >
                  ★ Reference
                </button>
                <button
                  onClick={() => sendFeedback(item, "not_relevant")}
                  className="text-[11px] text-gray-500 font-medium px-2 py-1 rounded hover:bg-gray-50 min-h-touch"
                >
                  ✕ Not Relevant
                </button>
              </div>
            </div>
          ))}
          {data && data.items.length > 3 && (
            <button
              onClick={() => setExpanded((e) => !e)}
              className="w-full text-center text-sm text-brand font-medium py-2 min-h-touch"
            >
              {expanded ? "Tampilkan lebih sedikit" : `Lihat semua (${data.items.length})`}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
