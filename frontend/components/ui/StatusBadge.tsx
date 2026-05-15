import type { CaseStatus, Severity } from "@/lib/api";

const STATUS_CONFIG: Record<CaseStatus, { label: string; className: string }> = {
  OPEN:              { label: "Terbuka",       className: "bg-blue-100 text-blue-700" },
  INVESTIGATING:     { label: "Investigasi",   className: "bg-yellow-100 text-yellow-700" },
  SUSPECTED_CAUSE:   { label: "Tersangka",     className: "bg-orange-100 text-orange-700" },
  TRIAL_IN_PROGRESS: { label: "Trial",         className: "bg-purple-100 text-purple-700" },
  RESOLVED:          { label: "Selesai",       className: "bg-green-100 text-green-700" },
  CLOSED:            { label: "Ditutup",       className: "bg-gray-100 text-gray-600" },
  ARCHIVED:          { label: "Diarsipkan",    className: "bg-slate-100 text-slate-500" },
};

const SEVERITY_CONFIG: Record<Severity, { label: string; className: string }> = {
  LOW:      { label: "Rendah",   className: "bg-green-100 text-green-700" },
  MEDIUM:   { label: "Sedang",   className: "bg-yellow-100 text-yellow-700" },
  HIGH:     { label: "Tinggi",   className: "bg-red-100 text-red-700" },
  CRITICAL: { label: "Kritis",   className: "bg-red-200 text-red-800 font-bold" },
};

export function StatusBadge({ status }: { status: CaseStatus }) {
  const cfg = STATUS_CONFIG[status] ?? { label: status, className: "bg-gray-100 text-gray-500" };
  return (
    <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold ${cfg.className}`}>
      {cfg.label}
    </span>
  );
}

export function SeverityBadge({ severity }: { severity: Severity | null }) {
  if (!severity) return null;
  const cfg = SEVERITY_CONFIG[severity] ?? { label: severity, className: "bg-gray-100 text-gray-500" };
  return (
    <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold ${cfg.className}`}>
      {cfg.label}
    </span>
  );
}
