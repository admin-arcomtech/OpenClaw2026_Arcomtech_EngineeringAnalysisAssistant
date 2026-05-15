"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getUser, isLoggedIn } from "@/lib/auth";
import type { UserMe } from "@/lib/api";

const ROLE_LABEL: Record<string, string> = {
  JUNIOR: "Junior Engineer",
  SENIOR: "Senior Engineer",
  MANAGER: "Engineering Manager",
  ADMIN: "Administrator",
};

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserMe | null>(null);

  useEffect(() => {
    if (!isLoggedIn()) {
      router.replace("/");
      return;
    }
    setUser(getUser<UserMe>());
  }, [router]);

  if (!user) return null;

  return (
    <div className="p-4 pt-6">
      {/* Header */}
      <div className="mb-6">
        <p className="text-sm text-gray-500">Selamat datang,</p>
        <h1 className="text-2xl font-bold text-gray-900">{user.full_name}</h1>
        <span className="inline-block mt-1 px-2.5 py-0.5 bg-brand-light text-brand text-xs font-semibold rounded-full">
          {ROLE_LABEL[user.role] ?? user.role}
        </span>
      </div>

      {/* Quick stats placeholder */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        {[
          { label: "Kasus Aktif", value: "—", color: "bg-blue-50 border-blue-100" },
          { label: "Kasus Selesai", value: "—", color: "bg-green-50 border-green-100" },
          { label: "Trial Hari Ini", value: "—", color: "bg-orange-50 border-orange-100" },
          { label: "Rekomendasi AI", value: "—", color: "bg-purple-50 border-purple-100" },
        ].map((stat) => (
          <div key={stat.label} className={`${stat.color} border rounded-xl p-4`}>
            <p className="text-2xl font-bold text-gray-800">{stat.value}</p>
            <p className="text-xs text-gray-500 mt-0.5">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Coming soon banner */}
      <div className="bg-brand-light border border-blue-200 rounded-xl p-4 text-center">
        <p className="text-brand font-semibold text-sm">Arcom Engineering Intelligence</p>
        <p className="text-gray-500 text-xs mt-1">
          Fitur investigasi akan tersedia mulai Sprint 2
        </p>
      </div>
    </div>
  );
}
