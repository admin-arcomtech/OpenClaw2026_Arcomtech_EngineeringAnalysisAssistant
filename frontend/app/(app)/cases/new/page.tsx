"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { isLoggedIn } from "@/lib/auth";
import Link from "next/link";

export default function NewCasePage() {
  const router = useRouter();
  useEffect(() => {
    if (!isLoggedIn()) router.replace("/");
  }, [router]);

  return (
    <div className="p-4 pt-6">
      <div className="flex items-center gap-3 mb-6">
        <Link href="/cases" className="p-2 rounded-xl hover:bg-gray-100 min-h-touch min-w-touch flex items-center justify-center">
          <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </Link>
        <h1 className="text-xl font-bold text-gray-900">Kasus Baru</h1>
      </div>
      <div className="bg-white border border-gray-200 rounded-xl p-8 text-center text-gray-400">
        <p className="font-medium text-gray-500">Form akan tersedia di Sprint 2</p>
        <p className="text-sm mt-1">F-001 Case Management</p>
      </div>
    </div>
  );
}
