import { AlertTriangle, Loader2, Inbox } from "lucide-react";

interface StatusMessageProps {
  kind: "loading" | "empty" | "error";
  message: string;
  onRetry?: () => void;
}

export function StatusMessage({ kind, message, onRetry }: StatusMessageProps) {
  const icon =
    kind === "loading" ? (
      <Loader2 className="h-5 w-5 animate-spin text-teal-600" aria-hidden="true" />
    ) : kind === "error" ? (
      <AlertTriangle className="h-5 w-5 text-amber-600" aria-hidden="true" />
    ) : (
      <Inbox className="h-5 w-5 text-slate-400" aria-hidden="true" />
    );

  return (
    <div
      role={kind === "error" ? "alert" : "status"}
      className="flex min-h-[160px] flex-col items-center justify-center gap-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-8 text-center"
    >
      {icon}
      <p className="max-w-sm text-sm text-[var(--color-text-secondary)]">{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="rounded-md border border-teal-600 px-3 py-1.5 text-sm font-medium text-teal-700 transition hover:bg-teal-50 focus-visible:outline-teal-600"
        >
          Retry
        </button>
      )}
    </div>
  );
}
