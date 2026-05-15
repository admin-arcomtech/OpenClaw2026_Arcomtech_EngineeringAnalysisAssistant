"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { isLoggedIn } from "@/lib/auth";

export default function CasesPage() {
  const router = useRouter();
  useEffect(() => {
    if (!isLoggedIn()) router.replace("/");
  }, [router]);

  return (
    <div className="p-4 pt-6">
      <h1 className="text-xl font-bold text-gray-900 mb-4">Daftar Kasus</h1>
      <div className="bg-white border border-gray-200 rounded-xl p-8 text-center text-gray-400">
        <svg className="w-12 h-12 mx-auto mb-3 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <p className="font-medium text-gray-500">Belum ada kasus</p>
        <p className="text-sm mt-1">Fitur Case Management tersedia di Sprint 2</p>
      </div>
    </div>
  );
}
