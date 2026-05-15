"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/useAuth";
import { api, type ImportResult, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/Toast";

export default function AdminImportPage() {
  const { token, user, ready } = useAuth();
  const { showToast } = useToast();
  const [file, setFile] = useState<File | null>(null);
  const [dryRun, setDryRun] = useState(true);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [loading, setLoading] = useState(false);

  const run = async () => {
    if (!token || !file) return;
    setLoading(true);
    try {
      const res = await api.adminImport(token, file, dryRun);
      setResult(res);
      showToast(dryRun ? "Dry-run selesai" : `Import: ${res.imported_rows} baris`, "success");
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : "Import gagal", "error");
    } finally {
      setLoading(false);
    }
  };

  if (!ready || user?.role !== "ADMIN") return null;

  return (
    <div className="p-4 pt-6">
      <Link href="/admin" className="text-brand text-sm">← Admin</Link>
      <h1 className="text-xl font-bold mt-2 mb-2">Import Data Historis</h1>
      <p className="text-xs text-gray-500 mb-4">
        CSV kolom wajib: model, fatal_error, symptom, root_cause
      </p>

      <input
        type="file"
        accept=".csv"
        className="w-full text-sm mb-3"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
      />
      <label className="flex items-center gap-2 text-sm mb-4">
        <input type="checkbox" checked={dryRun} onChange={(e) => setDryRun(e.target.checked)} />
        Dry-run (validasi tanpa insert)
      </label>
      <button
        type="button"
        onClick={run}
        disabled={!file || loading}
        className="w-full py-3 bg-brand text-white rounded-xl font-medium disabled:opacity-50"
      >
        {loading ? "Memproses..." : dryRun ? "Validasi" : "Import"}
      </button>

      {result && (
        <div className="mt-4 bg-gray-50 border rounded-xl p-4 text-sm space-y-1">
          <p>Status: <strong>{result.status}</strong></p>
          <p>Total: {result.total_rows} · Import: {result.imported_rows} · Skip: {result.skipped_rows}</p>
          {result.errors && result.errors.length > 0 && (
            <div className="mt-2 max-h-40 overflow-y-auto">
              {result.errors.slice(0, 10).map((e, i) => (
                <p key={i} className="text-red-600 text-xs">Baris {e.row}: {e.error}</p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
