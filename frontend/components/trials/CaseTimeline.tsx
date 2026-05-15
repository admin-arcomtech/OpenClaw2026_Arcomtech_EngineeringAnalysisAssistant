"use client";

import { useEffect, useState } from "react";
import { api, type TimelineEvent } from "@/lib/api";

const ICON: Record<string, string> = {
  "case.created": "📋",
  "case.status_changed": "🔄",
  "trial.logged": "🔬",
  "case.root_cause_confirmed": "✅",
  "case.photo_uploaded": "📷",
  "trial_queue.approved": "✔️",
};

interface Props {
  token: string;
  caseId: string;
}

export function CaseTimeline({ token, caseId }: Props) {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getTimeline(token, caseId).then(setEvents).finally(() => setLoading(false));
  }, [token, caseId]);

  if (loading) {
    return <div className="h-24 bg-gray-100 rounded-xl animate-pulse" />;
  }

  return (
    <div className="bg-white border border-gray-200 rounded-2xl p-4">
      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">Timeline</p>
      {events.length === 0 ? (
        <p className="text-sm text-gray-400 text-center py-4">Belum ada aktivitas</p>
      ) : (
        <div className="relative pl-4 border-l-2 border-gray-100 space-y-4">
          {events.map((e) => (
            <div key={e.id} className="relative">
              <span className="absolute -left-[1.35rem] top-0.5 w-5 h-5 flex items-center justify-center text-xs bg-white">
                {ICON[e.event_type] ?? "•"}
              </span>
              <p className="text-sm font-medium text-gray-800">{e.title}</p>
              {e.detail && <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{e.detail}</p>}
              <p className="text-[10px] text-gray-400 mt-0.5">
                {e.actor && `${e.actor} · `}
                {new Date(e.created_at).toLocaleString("id-ID", { dateStyle: "short", timeStyle: "short" })}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
