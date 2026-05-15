"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useAuth } from "@/lib/useAuth";
import { api, type WhyWhyDoc, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/Toast";

const SENIOR_ROLES = new Set(["SENIOR", "MANAGER", "ADMIN"]);

export default function WhyWhyPage() {
  const { id } = useParams<{ id: string }>();
  const { token, user, ready } = useAuth();
  const { showToast } = useToast();
  const [doc, setDoc] = useState<WhyWhyDoc | null>(null);
  const [loading, setLoading] = useState(false);
  const [draft, setDraft] = useState<WhyWhyDoc["draft"] | null>(null);

  const load = () => {
    if (!token || !id) return;
    api.getWhyWhy(token, id).then((d) => {
      setDoc(d);
      setDraft(d.draft ?? null);
    }).catch(() => setDoc(null));
  };

  useEffect(() => { load(); }, [token, id]);

  const generate = async () => {
    if (!token || !id) return;
    setLoading(true);
    try {
      const res = await api.generateWhyWhyDraft(token, id);
      setDoc(res);
      setDraft(res.draft ?? null);
      showToast(res.draft?.partial ? "Draft parsial — silakan lengkapi" : "Draft Why-Why dibuat", "success");
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : "Gagal generate", "error");
    } finally {
      setLoading(false);
    }
  };

  const save = async () => {
    if (!token || !id || !draft) return;
    setLoading(true);
    try {
      const updated = await api.updateWhyWhy(token, id, draft);
      setDoc(updated);
      showToast("Draft disimpan", "success");
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : "Gagal simpan", "error");
    } finally {
      setLoading(false);
    }
  };

  const submit = async () => {
    if (!token || !id) return;
    setLoading(true);
    try {
      const updated = await api.submitWhyWhy(token, id);
      setDoc(updated);
      showToast("Dikirim untuk persetujuan Senior", "success");
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : "Gagal submit", "error");
    } finally {
      setLoading(false);
    }
  };

  const approve = async (approved: boolean) => {
    if (!token || !id) return;
    const comment = approved ? undefined : prompt("Alasan penolakan (opsional):") ?? undefined;
    setLoading(true);
    try {
      const updated = await api.approveWhyWhy(token, id, approved, comment);
      setDoc(updated);
      showToast(approved ? "Why-Why disetujui" : "Why-Why ditolak", approved ? "success" : "error");
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : "Gagal", "error");
    } finally {
      setLoading(false);
    }
  };

  if (!ready) return null;

  const readonly = doc?.is_readonly || doc?.status === "APPROVED";
  const canApprove = user && SENIOR_ROLES.has(user.role) && doc?.status === "PENDING_APPROVAL";

  return (
    <div className="p-4 pt-6 pb-8">
      <div className="flex items-center gap-2 mb-4">
        <Link href={`/cases/${id}`} className="text-brand text-sm">← Kembali</Link>
        <h1 className="text-xl font-bold text-gray-900 flex-1">Why-Why Analysis</h1>
        {doc && (
          <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">{doc.status}</span>
        )}
      </div>

      {!doc && (
        <div className="bg-white border rounded-2xl p-6 text-center mb-4">
          <p className="text-gray-500 text-sm mb-4">Belum ada draft Why-Why untuk kasus ini.</p>
          <button
            type="button"
            onClick={generate}
            disabled={loading}
            className="px-4 py-2.5 bg-brand text-white rounded-xl font-medium min-h-touch disabled:opacity-50"
          >
            {loading ? "Membuat..." : "Generate Why-Why Draft"}
          </button>
        </div>
      )}

      {draft && (
        <div className="space-y-4">
          {draft.why_steps?.map((step, i) => (
            <div key={step.level} className="bg-white border rounded-xl p-4">
              <p className="text-xs text-brand font-semibold mb-1">Why #{step.level} · {step.category_4m1e}</p>
              <label className="text-xs text-gray-400">Pertanyaan</label>
              <input
                className="w-full border rounded-lg px-3 py-2 text-sm mb-2"
                value={step.question}
                disabled={readonly}
                onChange={(e) => {
                  const steps = [...(draft.why_steps ?? [])];
                  steps[i] = { ...step, question: e.target.value };
                  setDraft({ ...draft, why_steps: steps });
                }}
              />
              <label className="text-xs text-gray-400">Jawaban</label>
              <textarea
                className="w-full border rounded-lg px-3 py-2 text-sm"
                rows={2}
                value={step.answer}
                disabled={readonly}
                onChange={(e) => {
                  const steps = [...(draft.why_steps ?? [])];
                  steps[i] = { ...step, answer: e.target.value };
                  setDraft({ ...draft, why_steps: steps });
                }}
              />
            </div>
          ))}

          {(["immediate_countermeasure", "corrective_action", "preventive_action"] as const).map((key) => (
            <div key={key} className="bg-white border rounded-xl p-4">
              <label className="text-xs font-semibold text-gray-600 block mb-1">
                {key === "immediate_countermeasure" ? "Tindakan Segera" : key === "corrective_action" ? "Corrective Action" : "Preventive Action"}
              </label>
              <textarea
                className="w-full border rounded-lg px-3 py-2 text-sm"
                rows={2}
                value={(draft as Record<string, string>)[key] ?? ""}
                disabled={readonly}
                onChange={(e) => setDraft({ ...draft, [key]: e.target.value })}
              />
            </div>
          ))}

          {!readonly && doc?.status !== "PENDING_APPROVAL" && (
            <div className="flex flex-col gap-2">
              <button type="button" onClick={save} disabled={loading} className="py-3 border border-brand text-brand rounded-xl font-medium">
                Simpan Draft
              </button>
              <button type="button" onClick={submit} disabled={loading} className="py-3 bg-brand text-white rounded-xl font-medium">
                Kirim untuk Persetujuan
              </button>
            </div>
          )}

          {canApprove && (
            <div className="flex gap-2">
              <button type="button" onClick={() => approve(true)} disabled={loading} className="flex-1 py-3 bg-green-600 text-white rounded-xl font-medium">
                Setujui
              </button>
              <button type="button" onClick={() => approve(false)} disabled={loading} className="flex-1 py-3 bg-red-100 text-red-700 rounded-xl font-medium">
                Tolak
              </button>
            </div>
          )}

          {doc?.rejection_comment && (
            <p className="text-sm text-red-600 bg-red-50 p-3 rounded-xl">{doc.rejection_comment}</p>
          )}
        </div>
      )}
    </div>
  );
}
