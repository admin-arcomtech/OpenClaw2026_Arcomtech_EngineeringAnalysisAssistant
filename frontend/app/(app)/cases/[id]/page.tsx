"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useAuth } from "@/lib/useAuth";
import { api, type CaseOut, type CaseStatus, ApiError } from "@/lib/api";
import { StatusBadge, SeverityBadge } from "@/components/ui/StatusBadge";
import { useToast } from "@/components/ui/Toast";
import { SimilarCasesPanel } from "@/components/ai/SimilarCasesPanel";
import { AIRecommendationsPanel } from "@/components/ai/AIRecommendationsPanel";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const VALID_NEXT: Record<CaseStatus, CaseStatus[]> = {
  OPEN:              ["INVESTIGATING"],
  INVESTIGATING:     ["SUSPECTED_CAUSE", "OPEN"],
  SUSPECTED_CAUSE:   ["TRIAL_IN_PROGRESS", "INVESTIGATING"],
  TRIAL_IN_PROGRESS: ["RESOLVED", "INVESTIGATING"],
  RESOLVED:          ["CLOSED"],
  CLOSED:            ["ARCHIVED"],
  ARCHIVED:          [],
};

const STATUS_LABEL: Record<CaseStatus, string> = {
  OPEN: "Terbuka", INVESTIGATING: "Investigasi", SUSPECTED_CAUSE: "Tersangka Penyebab",
  TRIAL_IN_PROGRESS: "Trial Berlangsung", RESOLVED: "Selesai", CLOSED: "Ditutup", ARCHIVED: "Diarsipkan",
};

function InfoRow({ label, value }: { label: string; value?: string | null }) {
  if (!value) return null;
  return (
    <div>
      <p className="text-xs text-gray-400">{label}</p>
      <p className="text-sm text-gray-800 font-medium">{value}</p>
    </div>
  );
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString("id-ID", { dateStyle: "medium", timeStyle: "short" });
}

export default function CaseDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { token, user, ready } = useAuth();
  const { showToast } = useToast();
  const [caseData, setCaseData] = useState<CaseOut | null>(null);
  const [statusLoading, setStatusLoading] = useState(false);

  useEffect(() => {
    if (!token || !id) return;
    api.getCase(token, id).then(setCaseData).catch(() => showToast("Gagal memuat kasus", "error"));
  }, [token, id]);

  const advanceStatus = async (nextStatus: CaseStatus) => {
    if (!token || !caseData) return;
    setStatusLoading(true);
    try {
      const updated = await api.updateStatus(token, caseData.id, nextStatus);
      setCaseData(updated);
      showToast(`Status diubah ke ${STATUS_LABEL[nextStatus]}`, "success");
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : "Gagal ubah status", "error");
    } finally {
      setStatusLoading(false);
    }
  };

  if (!ready || !caseData) {
    return (
      <div className="p-4 pt-6 space-y-4 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3" />
        <div className="h-4 bg-gray-100 rounded w-2/3" />
        <div className="h-32 bg-gray-100 rounded-2xl" />
      </div>
    );
  }

  const nextStatuses = VALID_NEXT[caseData.status] ?? [];

  return (
    <div className="p-4 pt-6 pb-8 space-y-4">
      {/* Header */}
      <div className="flex items-start gap-3">
        <Link href="/cases" className="mt-1 p-2 rounded-xl hover:bg-gray-100 min-h-touch min-w-touch flex items-center justify-center flex-shrink-0">
          <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </Link>
        <div className="flex-1 min-w-0">
          <p className="font-mono text-xs text-gray-400 mb-1">{caseData.case_id}</p>
          <h1 className="text-lg font-bold text-gray-900 leading-snug">{caseData.title}</h1>
          <div className="flex flex-wrap gap-1.5 mt-2">
            <StatusBadge status={caseData.status} />
            {caseData.severity && <SeverityBadge severity={caseData.severity} />}
            {caseData.shift && (
              <span className="px-2.5 py-0.5 bg-gray-100 text-gray-600 text-xs font-medium rounded-full">
                {caseData.shift}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Status Transition */}
      {nextStatuses.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-2xl p-4">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Ubah Status</p>
          <div className="flex gap-2 flex-wrap">
            {nextStatuses.map((s) => (
              <button
                key={s}
                onClick={() => advanceStatus(s)}
                disabled={statusLoading}
                className="px-3.5 py-2 text-sm font-medium bg-brand text-white rounded-xl hover:bg-brand-dark disabled:opacity-50 min-h-touch transition"
              >
                → {STATUS_LABEL[s]}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Core Info */}
      <div className="bg-white border border-gray-200 rounded-2xl p-4 space-y-3">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Detail Kasus</p>
        <div className="grid grid-cols-2 gap-3">
          <InfoRow label="Model" value={caseData.model} />
          <InfoRow label="Proses" value={caseData.process} />
          <InfoRow label="Lini Produksi" value={caseData.line} />
          <InfoRow label="Fatal Error" value={caseData.fatal_error} />
          <InfoRow label="Shift" value={caseData.shift} />
          <InfoRow label="Operator ID" value={caseData.operator_id} />
        </div>
        {caseData.symptom && (
          <div>
            <p className="text-xs text-gray-400 mb-0.5">Symptom</p>
            <p className="text-sm text-gray-800 bg-gray-50 rounded-xl p-3 leading-relaxed">{caseData.symptom}</p>
          </div>
        )}
        {caseData.description && (
          <div>
            <p className="text-xs text-gray-400 mb-0.5">Deskripsi</p>
            <p className="text-sm text-gray-700">{caseData.description}</p>
          </div>
        )}
        {caseData.temporary_action && (
          <div>
            <p className="text-xs text-gray-400 mb-0.5">Tindakan Sementara</p>
            <p className="text-sm text-gray-700">{caseData.temporary_action}</p>
          </div>
        )}
        {caseData.spc_reference && <InfoRow label="Referensi SPC" value={caseData.spc_reference} />}
      </div>

      {/* People */}
      <div className="bg-white border border-gray-200 rounded-2xl p-4">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Tim</p>
        <div className="grid grid-cols-2 gap-3">
          {caseData.reporter && (
            <div>
              <p className="text-xs text-gray-400">Dibuat oleh</p>
              <p className="text-sm font-medium text-gray-800">{caseData.reporter.full_name}</p>
              <p className="text-xs text-gray-400">{caseData.reporter.role}</p>
            </div>
          )}
          {caseData.assigned_to && (
            <div>
              <p className="text-xs text-gray-400">Investigator</p>
              <p className="text-sm font-medium text-gray-800">{caseData.assigned_to.full_name}</p>
              <p className="text-xs text-gray-400">{caseData.assigned_to.role}</p>
            </div>
          )}
        </div>
        <div className="mt-3 pt-3 border-t border-gray-100 flex gap-4 text-xs text-gray-400">
          <span>Dibuat: {formatDate(caseData.created_at)}</span>
          <span>Diperbarui: {formatDate(caseData.updated_at)}</span>
        </div>
      </div>

      {/* Photos */}
      <div className="bg-white border border-gray-200 rounded-2xl p-4">
        <div className="flex items-center justify-between mb-3">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Foto ({caseData.photos.length}/5)</p>
          {caseData.photos.length < 5 && (
            <label className="cursor-pointer text-xs text-brand font-semibold min-h-touch flex items-center">
              + Upload
              <UploadPhotoInput caseId={caseData.id} token={token!} onUploaded={(updated) => setCaseData(updated)} />
            </label>
          )}
        </div>
        {caseData.photos.length === 0 ? (
          <p className="text-sm text-gray-400 text-center py-4">Belum ada foto</p>
        ) : (
          <div className="grid grid-cols-3 gap-2">
            {caseData.photos.map((photo) => (
              <a key={photo.id} href={`${BASE}${photo.storage_path}`} target="_blank" rel="noopener noreferrer">
                <div className="aspect-square bg-gray-100 rounded-xl overflow-hidden">
                  <img
                    src={`${BASE}${photo.storage_path}`}
                    alt={photo.filename}
                    className="w-full h-full object-cover"
                    onError={(e) => { (e.target as HTMLImageElement).src = ""; }}
                  />
                </div>
                {photo.caption && <p className="text-xs text-gray-400 mt-1 truncate">{photo.caption}</p>}
              </a>
            ))}
          </div>
        )}
      </div>

      {/* Sprint 3 — F-002 Similar Cases */}
      {token && <SimilarCasesPanel token={token} caseId={caseData.id} />}

      {/* Sprint 3 — F-003 AI Recommendations */}
      {token && <AIRecommendationsPanel token={token} caseId={caseData.id} />}
    </div>
  );
}

// Photo upload sub-component
function UploadPhotoInput({
  caseId, token, onUploaded,
}: {
  caseId: string;
  token: string;
  onUploaded: (updated: CaseOut) => void;
}) {
  const { showToast } = useToast();
  const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  const handleChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const form = new FormData();
    form.append("file", file);

    try {
      const res = await fetch(`${BASE_URL}/api/cases/${caseId}/photos`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: form,
      });
      if (!res.ok) {
        const body = await res.json();
        throw new Error(body.detail ?? "Upload gagal");
      }
      const updated = await api.getCase(token, caseId);
      onUploaded(updated);
      showToast("Foto berhasil diupload", "success");
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : "Upload gagal", "error");
    }
    e.target.value = "";
  };

  return (
    <input
      type="file"
      accept="image/jpeg,image/png,image/webp"
      className="hidden"
      onChange={handleChange}
    />
  );
}
