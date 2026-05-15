"use client";

import { useState } from "react";
import { api, type Hypothesis, type RecommendationsResponse, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/Toast";

interface Props {
  token: string;
  caseId: string;
}

const RISK_COLORS: Record<string, string> = {
  LOW:    "bg-emerald-100 text-emerald-700 border-emerald-200",
  MEDIUM: "bg-amber-100 text-amber-700 border-amber-200",
  HIGH:   "bg-red-100 text-red-700 border-red-200",
};

const CATEGORY_COLORS: Record<string, string> = {
  Man:         "bg-purple-100 text-purple-700",
  Machine:     "bg-blue-100 text-blue-700",
  Material:    "bg-orange-100 text-orange-700",
  Method:      "bg-cyan-100 text-cyan-700",
  Environment: "bg-teal-100 text-teal-700",
};

function ConfidenceBar({ pct }: { pct: number }) {
  const color = pct >= 70 ? "bg-emerald-500" : pct >= 40 ? "bg-amber-500" : "bg-gray-400";
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div className={`h-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-bold text-gray-700">{pct}%</span>
    </div>
  );
}

function SourceBadge({ source }: { source: string }) {
  const colors: Record<string, string> = {
    openclaw: "bg-emerald-100 text-emerald-700",
    fallback: "bg-amber-100 text-amber-700",
  };
  return (
    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide ${colors[source] ?? "bg-gray-100 text-gray-600"}`}>
      {source === "openclaw" ? "Openclaw" : "Lokal (fallback)"}
    </span>
  );
}

function HypothesisCard({ h, onFeedback }: { h: Hypothesis; index: number; onFeedback: (rating: string) => void }) {
  const lowConfidence = h.confidence < 30;
  return (
    <div className="border border-gray-200 rounded-2xl p-3">
      <div className="flex items-start justify-between gap-2 mb-2">
        <h3 className="font-semibold text-gray-800 text-sm leading-snug flex-1">{h.title}</h3>
      </div>

      <div className="flex flex-wrap gap-1.5 mb-2">
        <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${CATEGORY_COLORS[h.category_4m1e] ?? "bg-gray-100 text-gray-600"}`}>
          {h.category_4m1e}
        </span>
        <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${RISK_COLORS[h.trial_risk] ?? "bg-gray-100 text-gray-600"}`}>
          Risk {h.trial_risk}
        </span>
        <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-gray-100 text-gray-600">
          ~{h.estimated_time_min} min
        </span>
        {h.similar_case_count > 0 && (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-blue-50 text-blue-600">
            {h.similar_case_count} ref
          </span>
        )}
      </div>

      <ConfidenceBar pct={h.confidence} />

      {lowConfidence && (
        <p className="text-[11px] text-amber-700 bg-amber-50 border border-amber-200 rounded-lg p-2 mt-2">
          ⚠️ Confidence rendah — gunakan sebagai petunjuk awal, bukan kesimpulan.
        </p>
      )}

      {h.evidence.length > 0 && (
        <div className="mt-3">
          <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wide mb-1">Evidence</p>
          <ul className="text-xs text-gray-700 space-y-0.5 list-disc list-inside">
            {h.evidence.map((e, i) => <li key={i}>{e}</li>)}
          </ul>
        </div>
      )}

      {h.suggested_verification.length > 0 && (
        <div className="mt-3">
          <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wide mb-1">Verifikasi (urut prioritas)</p>
          <ol className="text-xs text-gray-700 space-y-0.5 list-decimal list-inside">
            {h.suggested_verification.map((s, i) => <li key={i}>{s}</li>)}
          </ol>
        </div>
      )}

      <div className="flex gap-1.5 mt-3 pt-2 border-t border-gray-100">
        <button onClick={() => onFeedback("useful")} className="text-[11px] text-emerald-700 font-medium px-2 py-1 rounded hover:bg-emerald-50 min-h-touch">
          👍 Useful
        </button>
        <button onClick={() => onFeedback("not_relevant")} className="text-[11px] text-gray-500 font-medium px-2 py-1 rounded hover:bg-gray-50 min-h-touch">
          ✕ Not Relevant
        </button>
        <button onClick={() => onFeedback("already_tried")} className="text-[11px] text-amber-700 font-medium px-2 py-1 rounded hover:bg-amber-50 min-h-touch">
          ↻ Already Tried
        </button>
      </div>
    </div>
  );
}

export function AIRecommendationsPanel({ token, caseId }: Props) {
  const { showToast } = useToast();
  const [data, setData] = useState<RecommendationsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [unavailable, setUnavailable] = useState(false);

  const fetchAdvice = async () => {
    setLoading(true);
    setUnavailable(false);
    try {
      const res = await api.recommendations(token, caseId);
      setData(res);
    } catch (err) {
      if (err instanceof ApiError && err.status === 503) {
        setUnavailable(true);
      } else {
        showToast(err instanceof ApiError ? err.message : "Gagal memuat rekomendasi", "error");
      }
    } finally {
      setLoading(false);
    }
  };

  const sendFeedback = async (target_id: string, rating: string) => {
    try {
      await api.aiFeedback(token, caseId, {
        target_type: "recommendation",
        target_id,
        rating,
      });
      showToast("Feedback tersimpan", "success");
    } catch {}
  };

  return (
    <div className="bg-purple-50 border border-purple-200 rounded-2xl p-4">
      <div className="flex items-start justify-between gap-2 mb-3">
        <div>
          <p className="text-xs font-semibold text-purple-700 uppercase tracking-wider">AI Recommendations (F-003)</p>
          {data && (
            <p className="text-[11px] text-purple-500 mt-0.5">
              {data.hypotheses.length} hipotesis · model {data.model_version}
            </p>
          )}
        </div>
        {data && <SourceBadge source={data.source} />}
      </div>

      {!data && !loading && !unavailable && (
        <button
          onClick={fetchAdvice}
          className="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-xl transition min-h-touch flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          Get AI Advice
        </button>
      )}

      {loading && (
        <div className="text-center py-8">
          <div className="inline-block animate-spin h-8 w-8 border-4 border-purple-200 border-t-purple-600 rounded-full mb-3" />
          <p className="text-sm text-purple-600 font-medium">Menganalisis kasus...</p>
          <p className="text-xs text-purple-400 mt-1">RAG + similar cases (timeout 60s)</p>
        </div>
      )}

      {unavailable && (
        <div className="text-center py-6 bg-white border border-purple-100 rounded-xl">
          <p className="text-sm font-semibold text-gray-800">AI tidak tersedia saat ini</p>
          <p className="text-xs text-gray-500 mt-1">Gunakan manual investigation mode.</p>
          <button onClick={fetchAdvice} className="mt-3 text-sm text-purple-600 font-medium min-h-touch px-4 py-2">
            Coba lagi
          </button>
        </div>
      )}

      {data && (
        <div className="space-y-2.5">
          {data.hypotheses.map((h, i) => (
            <HypothesisCard
              key={i}
              h={h}
              index={i}
              onFeedback={(rating) => sendFeedback(`${data.id}:${i}`, rating)}
            />
          ))}
          <button
            onClick={fetchAdvice}
            disabled={loading}
            className="w-full text-sm text-purple-600 font-medium py-2 min-h-touch"
          >
            ↻ Regenerate
          </button>
        </div>
      )}
    </div>
  );
}
