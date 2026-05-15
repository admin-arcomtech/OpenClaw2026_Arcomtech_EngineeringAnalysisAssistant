"use client";

import { useEffect, useState, FormEvent } from "react";
import { api, ApiError, type TrialCreatePayload, type TrialQueueItem } from "@/lib/api";
import { useToast } from "@/components/ui/Toast";
import { saveTrialDraft, loadTrialDraft, clearTrialDraft } from "@/lib/trialDraft";

interface Props {
  token: string;
  caseId: string;
  queueItem?: TrialQueueItem | null;
  onClose: () => void;
  onSaved: () => void;
}

const FIELD = "w-full px-3 py-2.5 rounded-xl border border-gray-300 text-sm min-h-touch focus:border-brand focus:ring-2 focus:ring-brand/20 outline-none";

export function LogTrialModal({ token, caseId, queueItem, onClose, onSaved }: Props) {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState<Partial<TrialCreatePayload>>({
    trial_action: queueItem?.trial_action ?? "",
    outcome: "NO_CHANGE",
    observation: "",
    time_spent_min: queueItem?.estimated_time_min ?? 30,
    risk_level: queueItem?.risk_level ?? "LOW",
    destructive: queueItem?.destructive ?? false,
    queue_item_id: queueItem?.id,
  });

  useEffect(() => {
    const draft = loadTrialDraft(caseId);
    if (draft) setForm((f) => ({ ...f, ...draft }));
  }, [caseId]);

  useEffect(() => {
    const t = setTimeout(() => saveTrialDraft(caseId, form), 500);
    return () => clearTimeout(t);
  }, [form, caseId]);

  const set = (k: keyof TrialCreatePayload) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!form.observation || form.observation.length < 20) {
      showToast("Observasi minimal 20 karakter", "error");
      return;
    }
    if (form.scrap_impact && ["YES", "MINOR", "MAJOR"].includes(form.scrap_impact.toUpperCase()) && !form.scrap_qty) {
      showToast("Jumlah scrap wajib diisi", "error");
      return;
    }
    setLoading(true);
    try {
      await api.createTrial(token, caseId, form as TrialCreatePayload);
      clearTrialDraft(caseId);
      showToast("Trial berhasil dicatat", "success");
      onSaved();
      onClose();
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : "Gagal menyimpan trial", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/40">
      <div className="bg-white w-full max-w-lg rounded-t-3xl sm:rounded-2xl max-h-[90vh] overflow-y-auto shadow-xl">
        <div className="p-4 border-b flex justify-between sticky top-0 bg-white">
          <h2 className="font-bold">Log Trial Result</h2>
          <button type="button" onClick={onClose} className="p-2 min-h-touch">✕</button>
        </div>
        <form onSubmit={handleSubmit} className="p-4 space-y-4 pb-8">
          <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
            Draft tersimpan otomatis — sync saat online
          </p>
          <div>
            <label className="text-sm font-medium">Trial Action *</label>
            <input value={form.trial_action ?? ""} onChange={set("trial_action")} required className={FIELD} />
          </div>
          <div>
            <label className="text-sm font-medium">Hasil *</label>
            <select value={form.outcome ?? "NO_CHANGE"} onChange={set("outcome")} className={FIELD}>
              <option value="IMPROVED">IMPROVED</option>
              <option value="NO_CHANGE">NO_CHANGE</option>
              <option value="WORSENED">WORSENED</option>
              <option value="INCONCLUSIVE">INCONCLUSIVE</option>
            </select>
          </div>
          <div>
            <label className="text-sm font-medium">Observasi * ({(form.observation ?? "").length}/20)</label>
            <textarea value={form.observation ?? ""} onChange={set("observation")} required rows={4} className={`${FIELD} resize-none`} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-sm font-medium">Waktu (menit)</label>
              <input type="number" value={form.time_spent_min ?? ""} onChange={set("time_spent_min")} className={FIELD} />
            </div>
            <div>
              <label className="text-sm font-medium">Improvement %</label>
              <input type="number" value={form.improvement_pct ?? ""} onChange={set("improvement_pct")} className={FIELD} />
            </div>
          </div>
          <div>
            <label className="text-sm font-medium">Dampak Scrap</label>
            <select value={form.scrap_impact ?? ""} onChange={set("scrap_impact")} className={FIELD}>
              <option value="">Tidak ada</option>
              <option value="MINOR">Minor</option>
              <option value="MAJOR">Major</option>
            </select>
          </div>
          {form.scrap_impact && (
            <div>
              <label className="text-sm font-medium">Jumlah Scrap *</label>
              <input type="number" value={form.scrap_qty ?? ""} onChange={set("scrap_qty")} required className={FIELD} />
            </div>
          )}
          <button type="submit" disabled={loading} className="w-full py-3.5 bg-brand text-white font-bold rounded-2xl min-h-touch disabled:opacity-60">
            {loading ? "Menyimpan..." : "Simpan Trial"}
          </button>
        </form>
      </div>
    </div>
  );
}
