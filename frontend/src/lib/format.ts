const LONDON_TZ = "Europe/London";

export function formatMW(value: number | null, fractionDigits = 0): string {
  if (value === null) return "—";
  return `${value.toLocaleString("en-GB", { maximumFractionDigits: fractionDigits })} MW`;
}

export function formatSignedMW(value: number | null): string {
  if (value === null) return "—";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toLocaleString("en-GB", { maximumFractionDigits: 0 })} MW`;
}

export function formatPercent(value: number | null, fractionDigits = 1): string {
  if (value === null) return "—";
  return `${value.toFixed(fractionDigits)}%`;
}

export function formatLondonDateTime(isoUtc: string | null): string {
  if (!isoUtc) return "—";
  return new Intl.DateTimeFormat("en-GB", {
    timeZone: LONDON_TZ,
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(isoUtc));
}

export function formatLondonTime(isoUtc: string | null): string {
  if (!isoUtc) return "—";
  return new Intl.DateTimeFormat("en-GB", {
    timeZone: LONDON_TZ,
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(isoUtc));
}

export function formatLondonDate(isoUtc: string): string {
  return new Intl.DateTimeFormat("en-GB", {
    timeZone: LONDON_TZ,
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(isoUtc));
}
