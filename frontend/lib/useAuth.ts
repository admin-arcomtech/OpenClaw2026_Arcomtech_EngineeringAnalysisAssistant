"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getToken, getUser, isLoggedIn } from "@/lib/auth";
import type { UserMe } from "@/lib/api";

export function useAuth() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserMe | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!isLoggedIn()) {
      router.replace("/");
      return;
    }
    setToken(getToken());
    setUser(getUser<UserMe>());
    setReady(true);
  }, [router]);

  return { token, user, ready };
}
