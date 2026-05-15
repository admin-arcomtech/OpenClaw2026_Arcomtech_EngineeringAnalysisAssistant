/** Offline trial log draft — localStorage key: trial-draft-{caseId} */
import type { TrialCreatePayload } from "@/lib/api";

const PREFIX = "trial-draft-";

export function saveTrialDraft(caseId: string, data: Partial<TrialCreatePayload>) {
  if (typeof window === "undefined") return;
  localStorage.setItem(PREFIX + caseId, JSON.stringify({ ...data, savedAt: Date.now() }));
}

export function loadTrialDraft(caseId: string): Partial<TrialCreatePayload> | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(PREFIX + caseId);
  if (!raw) return null;
  try {
    const { savedAt, ...rest } = JSON.parse(raw);
    return rest;
  } catch {
    return null;
  }
}

export function clearTrialDraft(caseId: string) {
  if (typeof window === "undefined") return;
  localStorage.removeItem(PREFIX + caseId);
}
