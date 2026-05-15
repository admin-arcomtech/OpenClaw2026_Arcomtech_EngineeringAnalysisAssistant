"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/useAuth";
import { api, type AuditEntry } from "@/lib/api";

export default function AdminAuditPage() {
  const { token, user, ready } = useAuth();
  const [logs, setLogs] = useState<AuditEntry[]>([]);

  useEffect(() => {
    if (!token) return;
    api.adminAuditLog(token, 200).then((r) => setLogs(r.items)).catch(() => {});
  }, [token]);

  if (!ready || user?.role !== "ADMIN") return null;

  return (
    <div className="p-4 pt-6">
      <Link href="/admin" className="text-brand text-sm">← Admin</Link>
      <h1 className="text-xl font-bold mt-2 mb-4">Audit Log</h1>
      <div className="space-y-2 max-h-[70vh] overflow-y-auto">
        {logs.map((l) => (
          <div key={l.id} className="bg-white border rounded-lg p-3 text-xs">
            <p className="font-mono text-brand">{l.event}</p>
            <p className="text-gray-400 mt-0.5">{l.created_at}</p>
            {l.detail && (
              <pre className="mt-1 text-gray-600 whitespace-pre-wrap">{JSON.stringify(l.detail, null, 0)}</pre>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
