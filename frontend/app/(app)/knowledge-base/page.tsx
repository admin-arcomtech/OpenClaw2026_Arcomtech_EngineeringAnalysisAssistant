"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/useAuth";
import { api, type KnowledgeItem } from "@/lib/api";

export default function KnowledgeBasePage() {
  const { token, ready } = useAuth();
  const [q, setQ] = useState("");
  const [model, setModel] = useState("");
  const [items, setItems] = useState<KnowledgeItem[]>([]);
  const [mode, setMode] = useState("");
  const [loading, setLoading] = useState(false);

  const search = async () => {
    if (!token) return;
    setLoading(true);
    try {
      const res = await api.searchKnowledge(token, { q, model: model || undefined, limit: 30 });
      setItems(res.items);
      setMode(res.mode);
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  if (!ready) return null;

  return (
    <div className="p-4 pt-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Knowledge Base</h1>
      <p className="text-sm text-gray-500 mb-4">Cari kasus terarsip, root cause, dan Why-Why</p>

      <div className="space-y-2 mb-4">
        <input
          className="w-full border rounded-xl px-4 py-3 text-sm"
          placeholder="Cari symptom, fatal error, root cause..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && search()}
        />
        <input
          className="w-full border rounded-xl px-4 py-2 text-sm"
          placeholder="Filter model (opsional)"
          value={model}
          onChange={(e) => setModel(e.target.value)}
        />
        <button
          type="button"
          onClick={search}
          disabled={loading}
          className="w-full py-3 bg-brand text-white rounded-xl font-medium disabled:opacity-50"
        >
          {loading ? "Mencari..." : "Cari"}
        </button>
      </div>

      {mode && <p className="text-xs text-gray-400 mb-2">Mode: {mode} · {items.length} hasil</p>}

      <div className="space-y-2.5">
        {items.map((item) => (
          <Link
            key={item.id}
            href={`/cases/${item.id}`}
            className="block bg-white border border-gray-200 rounded-xl p-4 hover:border-brand/40"
          >
            <div className="flex justify-between items-start gap-2">
              <span className="font-mono text-xs text-gray-400">{item.case_id}</span>
              {item.similarity_pct != null && (
                <span className="text-xs text-brand font-medium">{item.similarity_pct}%</span>
              )}
            </div>
            <p className="font-medium text-gray-800 text-sm mt-1">{item.title}</p>
            {item.root_cause && (
              <p className="text-xs text-gray-500 mt-1 line-clamp-2">RC: {item.root_cause}</p>
            )}
            <div className="flex gap-2 mt-2 text-xs text-gray-400">
              <span>{item.model}</span>
              <span>·</span>
              <span>{item.process}</span>
              {item.has_why_why && <span className="text-green-600">✓ Why-Why</span>}
            </div>
          </Link>
        ))}
        {items.length === 0 && !loading && (
          <p className="text-center text-gray-400 text-sm py-8">Ketik kata kunci lalu tekan Cari</p>
        )}
      </div>
    </div>
  );
}
