"use client";

import Link from "next/link";
import { useAuth } from "@/lib/useAuth";

export default function AdminSettingsPage() {
  const { user, ready } = useAuth();
  if (!ready || (user?.role !== "ADMIN" && user?.role !== "MANAGER")) return null;

  return (
    <div className="p-4 pt-6">
      <Link href="/admin" className="text-brand text-sm">← Admin</Link>
      <h1 className="text-xl font-bold mt-2 mb-4">Pengaturan AI</h1>
      <div className="bg-white border rounded-xl p-4 text-sm text-gray-600 space-y-3">
        <p>Konfigurasi AI dikelola via environment variables di server:</p>
        <ul className="list-disc pl-5 space-y-1 text-xs font-mono">
          <li>AI_ENABLED</li>
          <li>OPENCLAW_BASE_URL</li>
          <li>OPENCLAW_TOKEN</li>
          <li>EMBEDDING_DIM</li>
        </ul>
        <p className="text-xs text-gray-400">Similarity threshold default: 0.5 (dapat diubah per-request di API)</p>
      </div>
    </div>
  );
}
