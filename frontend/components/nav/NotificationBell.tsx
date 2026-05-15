"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type NotificationItem } from "@/lib/api";
import { getToken } from "@/lib/auth";

export function NotificationBell() {
  const [unread, setUnread] = useState(0);
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState<NotificationItem[]>([]);

  const load = () => {
    const token = getToken();
    if (!token) return;
    api.listNotifications(token).then((r) => {
      setUnread(r.unread_count);
      setItems(r.items);
    }).catch(() => {});
  };

  useEffect(() => {
    load();
    const t = setInterval(load, 60000);
    return () => clearInterval(t);
  }, []);

  const markRead = async (id: string) => {
    const token = getToken();
    if (!token) return;
    await api.markNotificationRead(token, id);
    load();
  };

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => { setOpen(!open); load(); }}
        className="relative p-2 rounded-full hover:bg-gray-100"
        aria-label="Notifikasi"
      >
        <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        {unread > 0 && (
          <span className="absolute top-0.5 right-0.5 min-w-[18px] h-[18px] px-1 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
            {unread > 9 ? "9+" : unread}
          </span>
        )}
      </button>
      {open && (
        <div className="absolute right-0 top-full mt-1 w-80 max-h-96 overflow-y-auto bg-white border border-gray-200 rounded-xl shadow-lg z-50">
          <div className="p-3 border-b font-semibold text-sm text-gray-800">Notifikasi</div>
          {items.length === 0 ? (
            <p className="p-4 text-sm text-gray-400 text-center">Tidak ada notifikasi</p>
          ) : (
            items.map((n) => (
              <div key={n.id} className={`p-3 border-b text-sm ${n.is_read ? "bg-white" : "bg-blue-50"}`}>
                <p className="text-gray-800">{n.message}</p>
                <div className="flex gap-2 mt-2">
                  {n.case_id && (
                    <Link href={`/cases/${n.case_id}`} className="text-brand text-xs font-medium" onClick={() => setOpen(false)}>
                      Lihat kasus
                    </Link>
                  )}
                  {!n.is_read && (
                    <button type="button" onClick={() => markRead(n.id)} className="text-xs text-gray-500">
                      Tandai dibaca
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
