interface KpiCardProps {
  label: string;
  value: string;
  description: string;
  helpText?: string;
  unavailable?: boolean;
}

export function KpiCard({ label, value, description, helpText, unavailable }: KpiCardProps) {
  return (
    <div
      className="flex flex-col gap-1 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4 shadow-card"
      title={helpText}
    >
      <span className="text-xs font-medium uppercase tracking-wide text-[var(--color-text-secondary)]">
        {label}
      </span>
      <span className={`text-2xl font-semibold ${unavailable ? "text-slate-400" : "text-[var(--color-text-primary)]"}`}>
        {value}
      </span>
      <span className="text-xs text-[var(--color-text-secondary)]">{description}</span>
    </div>
  );
}
