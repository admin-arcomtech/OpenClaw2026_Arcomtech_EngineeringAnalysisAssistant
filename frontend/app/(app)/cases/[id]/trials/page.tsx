"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useAuth } from "@/lib/useAuth";
import { api, type TrialLog, type TrialQueueItem } from "@/lib/api";
import { TrialQueuePanel } from "@/components/trials/TrialQueuePanel";
import { LogTrialModal } from "@/components/trials/LogTrialModal";
import { CaseTimeline } from "@/components/trials/CaseTimeline";

const OUTCOME_STYLE: Record<string, string> = {
  IMPROVED: "text-emerald-700 bg-emerald-50",
  NO_CHANGE: "text-gray-600 bg-gray-50",
  WORSENED: "text-red-700 bg-red-50",
  INCONCLUSIVE: "text-amber-700 bg-amber-50",
};

export default function TrialsPage() {
  const { id } = useParams<{ id: string }>();
  const { token, user, ready } = useAuth();
  const [trials, setTrials] = useState<TrialLog[]>([]);
  const [showLog, setShowLog] = useState(false);

  const loadTrials = () => {
    if (!token || !id) return;
    api.listTrials(token, id).then(setTrials);
  };

  useEffect(() => {
    if (ready) loadTrials();
  }, [token, ready, id]);

  if (!ready || !token) return null;

  return (
    <div className="p-4 pt-6 pb-8 space-y-4">
      <div className="flex items-center gap-3">
        <Link href={`/cases/${id}`} className="p-2 rounded-xl hover:bg-gray-100 min-h-touch">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </Link>
        <h1 className="text-xl font-bold">Trial & Queue</h1>
      </div>

      <TrialQueuePanel token={token} caseId={id} userRole={user?.role ?? "JUNIOR"} onRefresh={loadTrials} />

      <div className="bg-white border border-gray-200 rounded-2xl p-4">
        <div className="flex items-center justify-between mb-3">
          <p className="text-xs font-semibold text-gray-500 uppercase">Riwayat Trial ({trials.length})</p>
          <button onClick={() => setShowLog(true)} className="text-sm text-brand font-medium min-h-touch px-2">
            + Log Manual
          </button>
        </div>
        {trials.length === 0 ? (
          <p className="text-sm text-gray-400 text-center py-6">Belum ada trial dicatat</p>
        ) : (
          <div className="space-y-3">
            {trials.map((t) => (
              <div key={t.id} className="border border-gray-100 rounded-xl p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-mono text-xs text-gray-400">#{t.sequence}</span>
                  {t.outcome && (
                    <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${OUTCOME_STYLE[t.outcome] ?? ""}`}>
                      {t.outcome}
                    </span>
                  )}
                </div>
                <p className="text-sm font-medium text-gray-800">{t.trial_action}</p>
                {t.observation && <p className="text-xs text-gray-500 mt-1 line-clamp-2">{t.observation}</p>}
                <p className="text-[10px] text-gray-400 mt-1">
                  {t.time_spent_min && `${t.time_spent_min} min · `}
                  {new Date(t.created_at).toLocaleString("id-ID")}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      <CaseTimeline token={token} caseId={id} />

      {showLog && (
        <LogTrialModal
          token={token}
          caseId={id}
          onClose={() => setShowLog(false)}
          onSaved={loadTrials}
        />
      )}
    </div>
  );
}
