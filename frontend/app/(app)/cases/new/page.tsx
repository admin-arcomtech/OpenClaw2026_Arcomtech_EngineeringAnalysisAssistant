"use client";

import { useEffect, useState, FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/useAuth";
import { api, type Taxonomy, type DuplicateWarning, type CaseSummary } from "@/lib/api";
import { useToast } from "@/components/ui/Toast";
import { ApiError } from "@/lib/api";

const FIELD = "w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-brand focus:ring-2 focus:ring-brand/20 outline-none text-gray-900 text-sm transition min-h-touch bg-white";
const LABEL = "block text-sm font-medium text-gray-700 mb-1.5";

export default function NewCasePage() {
  const { token, ready } = useAuth();
  const router = useRouter();
  const { showToast } = useToast();
  const [taxonomy, setTaxonomy] = useState<Taxonomy | null>(null);
  const [loading, setLoading] = useState(false);
  const [duplicate, setDuplicate] = useState<DuplicateWarning | null>(null);
  const [bypassDuplicate, setBypassDuplicate] = useState(false);

  const [form, setForm] = useState({
    model: "",
    process: "",
    line: "",
    fatal_error: "",
    symptom: "",
    description: "",
    severity: "MEDIUM",
    shift: "",
    temporary_action: "",
    operator_id: "",
    spc_reference: "",
  });

  useEffect(() => {
    if (!token) return;
    api.getMetadata(token).then(setTaxonomy).catch(() => {});
  }, [token]);

  const set = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  const checkDuplicate = async () => {
    if (!token || !form.model || !form.fatal_error) return;
    try {
      const result = await api.checkDuplicate(token, { model: form.model, fatal_error: form.fatal_error });
      setDuplicate(result);
    } catch {}
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!token) return;

    // Check duplicate first (unless already bypassed)
    if (!bypassDuplicate) {
      const result = await api.checkDuplicate(token, { model: form.model, fatal_error: form.fatal_error }).catch(() => null);
      if (result?.has_duplicate) {
        setDuplicate(result);
        return;
      }
    }

    setLoading(true);
    try {
      const payload = {
        ...form,
        shift: form.shift || undefined,
        temporary_action: form.temporary_action || undefined,
        operator_id: form.operator_id || undefined,
        spc_reference: form.spc_reference || undefined,
      };
      const created = await api.createCase(token, payload);
      showToast(`Kasus ${created.case_id} berhasil dibuat`, "success");
      router.push(`/cases/${created.id}`);
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "Gagal membuat kasus. Coba lagi.";
      showToast(msg, "error");
    } finally {
      setLoading(false);
    }
  };

  if (!ready) return null;

  return (
    <div className="p-4 pt-6 pb-8">
      <div className="flex items-center gap-3 mb-6">
        <Link href="/cases" className="p-2 rounded-xl hover:bg-gray-100 min-h-touch min-w-touch flex items-center justify-center">
          <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </Link>
        <div>
          <h1 className="text-xl font-bold text-gray-900">Kasus Baru</h1>
          <p className="text-xs text-gray-400">F-001 Case Management</p>
        </div>
      </div>

      {/* Duplicate Warning Banner */}
      {duplicate?.has_duplicate && !bypassDuplicate && (
        <div className="mb-5 p-4 bg-amber-50 border border-amber-300 rounded-xl">
          <p className="font-semibold text-amber-800 text-sm mb-1">⚠️ Kasus serupa ditemukan dalam 24 jam terakhir</p>
          <ul className="text-xs text-amber-700 space-y-0.5 mb-3">
            {duplicate.cases.map((c) => (
              <li key={c.id}>
                <Link href={`/cases/${c.id}`} className="underline">{c.case_id}</Link>
                {" — "}{c.model} / {c.fatal_error}
              </li>
            ))}
          </ul>
          <div className="flex gap-2">
            <button
              onClick={() => { setBypassDuplicate(true); setDuplicate(null); }}
              className="flex-1 py-2 text-sm font-medium bg-amber-600 text-white rounded-lg min-h-touch"
            >
              Tetap Buat Kasus Baru
            </button>
            <Link
              href={`/cases/${duplicate.cases[0]?.id}`}
              className="flex-1 py-2 text-sm font-medium text-center bg-white border border-amber-300 text-amber-700 rounded-lg min-h-touch flex items-center justify-center"
            >
              Buka Kasus Lama
            </Link>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* === Core Fields === */}
        <div className="bg-white rounded-2xl border border-gray-200 p-4 space-y-4">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Informasi Utama</p>

          <div>
            <label className={LABEL}>Model <span className="text-red-500">*</span></label>
            <select value={form.model} onChange={set("model")} required className={FIELD}>
              <option value="">Pilih model...</option>
              {taxonomy?.models.map((m) => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>

          <div>
            <label className={LABEL}>Proses <span className="text-red-500">*</span></label>
            <select value={form.process} onChange={set("process")} required className={FIELD}>
              <option value="">Pilih proses...</option>
              {taxonomy?.processes.map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>

          <div>
            <label className={LABEL}>Lini Produksi <span className="text-red-500">*</span></label>
            <select value={form.line} onChange={set("line")} required className={FIELD}>
              <option value="">Pilih lini...</option>
              {taxonomy?.lines.map((l) => <option key={l} value={l}>{l}</option>)}
            </select>
          </div>

          <div>
            <label className={LABEL}>Fatal Error <span className="text-red-500">*</span></label>
            <select value={form.fatal_error} onChange={(e) => { set("fatal_error")(e); setDuplicate(null); setBypassDuplicate(false); }} required className={FIELD}>
              <option value="">Pilih fatal error...</option>
              {taxonomy?.fatal_errors.map((fe) => <option key={fe} value={fe}>{fe}</option>)}
            </select>
          </div>
        </div>

        {/* === Symptom & Description === */}
        <div className="bg-white rounded-2xl border border-gray-200 p-4 space-y-4">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Deskripsi Masalah</p>

          <div>
            <label className={LABEL}>
              Symptom / Gejala <span className="text-red-500">*</span>
              <span className="text-gray-400 font-normal ml-1">({form.symptom.length}/500)</span>
            </label>
            <textarea
              value={form.symptom}
              onChange={set("symptom")}
              required
              maxLength={500}
              rows={3}
              placeholder="Jelaskan gejala yang diamati secara detail..."
              className={`${FIELD} resize-none`}
            />
          </div>

          <div>
            <label className={LABEL}>
              Deskripsi Singkat <span className="text-red-500">*</span>
              <span className="text-gray-400 font-normal ml-1">({form.description.length}/200)</span>
            </label>
            <textarea
              value={form.description}
              onChange={set("description")}
              required
              maxLength={200}
              rows={2}
              placeholder="Ringkasan singkat masalah..."
              className={`${FIELD} resize-none`}
            />
          </div>
        </div>

        {/* === Severity & Shift === */}
        <div className="bg-white rounded-2xl border border-gray-200 p-4 space-y-4">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Klasifikasi</p>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={LABEL}>Severity</label>
              <select value={form.severity} onChange={set("severity")} className={FIELD}>
                {taxonomy?.severities.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className={LABEL}>Shift</label>
              <select value={form.shift} onChange={set("shift")} className={FIELD}>
                <option value="">—</option>
                {taxonomy?.shifts.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          </div>
        </div>

        {/* === Optional Fields === */}
        <div className="bg-white rounded-2xl border border-gray-200 p-4 space-y-4">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Opsional</p>

          <div>
            <label className={LABEL}>Tindakan Sementara</label>
            <textarea
              value={form.temporary_action}
              onChange={set("temporary_action")}
              rows={2}
              placeholder="Tindakan darurat yang sudah diambil..."
              className={`${FIELD} resize-none`}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={LABEL}>Operator ID</label>
              <input type="text" value={form.operator_id} onChange={set("operator_id")} placeholder="OP-001" className={FIELD} />
            </div>
            <div>
              <label className={LABEL}>Referensi SPC</label>
              <input type="text" value={form.spc_reference} onChange={set("spc_reference")} placeholder="SPC-2026-..." className={FIELD} />
            </div>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3.5 bg-brand hover:bg-brand-dark text-white font-bold rounded-2xl transition min-h-touch disabled:opacity-60 disabled:cursor-not-allowed text-base shadow-sm"
        >
          {loading ? "Menyimpan..." : "Buat Kasus"}
        </button>
      </form>
    </div>
  );
}
