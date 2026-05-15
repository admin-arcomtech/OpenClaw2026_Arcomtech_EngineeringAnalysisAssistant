"use client";

import Link from "next/link";
import { useAuth } from "@/lib/useAuth";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

const LINKS = [
  { href: "/admin/users", label: "Manajemen User", desc: "CRUD pengguna sistem" },
  { href: "/admin/import", label: "Import Data", desc: "Upload CSV historis Why-Why" },
  { href: "/admin/audit", label: "Audit Log", desc: "Riwayat aktivitas sistem" },
  { href: "/admin/settings", label: "Pengaturan AI", desc: "Threshold & konfigurasi" },
];

export default function AdminPage() {
  const { user, ready } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (ready && user && user.role !== "ADMIN" && user.role !== "MANAGER") {
      router.replace("/dashboard");
    }
  }, [ready, user, router]);

  if (!ready || !user) return null;

  return (
    <div className="p-4 pt-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Admin Panel</h1>
      <p className="text-sm text-gray-500 mb-6">Konfigurasi sistem — tidak mengubah konten investigasi</p>
      <div className="space-y-3">
        {LINKS.map((l) => (
          <Link
            key={l.href}
            href={l.href}
            className="block bg-white border border-gray-200 rounded-xl p-4 hover:border-brand/40"
          >
            <p className="font-semibold text-gray-800">{l.label}</p>
            <p className="text-xs text-gray-400 mt-0.5">{l.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
