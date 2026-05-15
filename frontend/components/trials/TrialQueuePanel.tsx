"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type TrialQueueItem, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/Toast";
import { LogTrialModal } from "./LogTrialModal";

const RISK_STYLE: Record<string, string> = {
  LOW: "bg-emerald-100 text-emerald-700",
  MEDIUM: "bg-amber-100 text-amber-700",
  HIGH: "bg-red-100 text-red-700",
};

interface Props {
  token: string;
  caseId: string;
  userRole: string;
  onRefresh?: () => void;
}

export function TrialQueuePanel({ token, caseId, userRole, onRefresh }: Props) {
  const { showToast } = useToast();
  const [items, setItems] = useState<TrialQueueItem[]>([]);
  const [queueStatus, setQueueStatus] = useState("DRAFT");
  const [loading, setLoading] = useState(true);
  const [warning, setWarning] = useState<string | null>(null);
  const [logItem, setLogItem] = useState<TrialQueueItem | null>(null);
  const [highConfirm, setHighConfirm] = useState<TrialQueueItem | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const res = await api.getTrialQueue(token, caseId);
      setItems(res.items || []);
      setQueueStatus(res.status);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [caseId]);

  const generateQueue = async () => {
    setLoading(true);
    try {
      const res = await api.trialPriority(token, caseId);
      setItems(res.trial_queue);
      setWarning(res.warning ?? null);
      showToast("Trial queue dihasilkan", "success");
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : "Gagal generate queue", "error");
    } finally {
      setLoading(false);
    }
  };

  const moveItem = (idx: number, dir: -1 | 1) => {
    const next = [...items];
    const j = idx + dir;
    if (j < 0 || j >= next.length) return;
    [next[idx], next[j]] = [next[j], next[idx]];
    next.forEach((it, i) => { it.priority_rank = i + 1; });
    setItems(next);
  };

  const saveQueue = async () => {
    try {
      await api.saveTrialQueue(token, caseId, items, queueStatus);
      showToast("Queue disimpan", "success");
    } catch {
      showToast("Gagal menyimpan queue", "error");
    }
  };

  const approveQueue = async () => {
    try {
      await api.approveTrialQueue(token, caseId);
      setQueueStatus("APPROVED");
      showToast("Queue disetujui — siap dieksekusi", "success");
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : "Gagal approve", "error");
    }
  };

  const startTrial = (item: TrialQueueItem) => {
    if (item.risk_level === "HIGH" && item.requires_senior_approval) {
      setHighConfirm(item);
      return;
    }
    setLogItem(item);
  };

  const active = items.filter((i) => !i.skipped);

  return (
    <>
      <div className="bg-white border border-gray-200 rounded-2xl p-4">
        <div className="flex items-center justify-between mb-3">
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Trial Queue (F-004)</p>
            <p className="text-[11px] text-gray-400">
              {active.length} trial · status: <span className="font-semibold">{queueStatus}</span>
            </p>
          </div>
          <Link href={`/cases/${caseId}/trials`} className="text-xs text-brand font-medium">Lihat semua →</Link>
        </div>

        {warning && (
          <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg p-2 mb-3">{warning}</p>
        )}

        {loading ? (
          <div className="space-y-2">{[1, 2].map((i) => <div key={i} className="h-14 bg-gray-100 rounded-xl animate-pulse" />)}</div>
        ) : active.length === 0 ? (
          <div className="text-center py-6 text-gray-400 text-sm">
            <p>Belum ada trial queue</p>
            <button onClick={generateQueue} className="mt-3 px-4 py-2 bg-brand text-white text-sm font-medium rounded-xl min-h-touch">
              Generate dari AI
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            {active.map((item, idx) => (
              <div key={item.id} className="border border-gray-100 rounded-xl p-3">
                <div className="flex items-start gap-2">
                  <span className="text-xs font-bold text-gray-400 w-5 pt-0.5">#{item.priority_rank}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800 leading-snug">{item.trial_action}</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${RISK_STYLE[item.risk_level] ?? ""}`}>
                        {item.risk_level}
                      </span>
                      <span className="text-[10px] text-gray-400">~{item.estimated_time_min} min</span>
                      {item.historical_success_rate != null && (
                        <span className="text-[10px] text-emerald-600">{item.historical_success_rate}% sukses</span>
                      )}
                      {item.requires_senior_approval && (
                        <span className="text-[10px] text-red-600 font-semibold">⚠ Senior approval</span>
                      )}
                    </div>
                  </div>
                  <div className="flex flex-col gap-1">
                    <button onClick={() => moveItem(idx, -1)} disabled={idx === 0} className="p-1 text-gray-400 disabled:opacity-30 min-h-touch">↑</button>
                    <button onClick={() => moveItem(idx, 1)} disabled={idx === active.length - 1} className="p-1 text-gray-400 disabled:opacity-30 min-h-touch">↓</button>
                  </div>
                </div>
                {queueStatus === "APPROVED" && (
                  <button
                    onClick={() => startTrial(item)}
                    className="mt-2 w-full py-2 text-xs font-semibold bg-brand text-white rounded-lg min-h-touch"
                  >
                    Log Trial Result
                  </button>
                )}
              </div>
            ))}
          </div>
        )}

        <div className="flex gap-2 mt-4 flex-wrap">
          <button onClick={generateQueue} className="flex-1 py-2 text-sm border border-gray-200 rounded-xl min-h-touch font-medium">
            Regenerate
          </button>
          <button onClick={saveQueue} className="flex-1 py-2 text-sm border border-brand text-brand rounded-xl min-h-touch font-medium">
            Simpan
          </button>
          {queueStatus !== "APPROVED" && active.length > 0 && (
            <button onClick={approveQueue} className="flex-1 py-2 text-sm bg-brand text-white rounded-xl min-h-touch font-semibold">
              Approve Queue
            </button>
          )}
        </div>
      </div>

      {highConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-2xl p-6 max-w-sm w-full">
            <p className="font-bold text-red-700 mb-2">⚠ Trial HIGH Risk</p>
            <p className="text-sm text-gray-600 mb-4">
              Trial ini berisiko tinggi dan memerlukan persetujuan Senior. Lanjutkan?
            </p>
            <p className="text-sm font-medium bg-gray-50 rounded-lg p-3 mb-4">{highConfirm.trial_action}</p>
            <div className="flex gap-2">
              <button onClick={() => setHighConfirm(null)} className="flex-1 py-2.5 border rounded-xl min-h-touch">Batal</button>
              <button
                onClick={() => { setLogItem(highConfirm); setHighConfirm(null); }}
                className="flex-1 py-2.5 bg-red-600 text-white rounded-xl font-semibold min-h-touch"
              >
                Lanjutkan
              </button>
            </div>
          </div>
        </div>
      )}

      {logItem && (
        <LogTrialModal
          token={token}
          caseId={caseId}
          queueItem={logItem}
          onClose={() => setLogItem(null)}
          onSaved={() => { load(); onRefresh?.(); }}
        />
      )}
    </>
  );
}
