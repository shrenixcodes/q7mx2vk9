import { ApiError } from "./types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL;

function buildUrl(path: string, params?: Record<string, string | number | undefined>): string {
  if (!BASE_URL) {
    throw new ApiError(
      0,
      "VITE_API_BASE_URL is not configured for this build. Set it as an environment " +
        "variable (e.g. in Vercel project settings) and redeploy."
    );
  }
  const url = new URL(path, BASE_URL);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined) {
        url.searchParams.set(key, String(value));
      }
    }
  }
  return url.toString();
}

async function request<T>(
  path: string,
  options: { params?: Record<string, string | number | undefined>; method?: string; signal?: AbortSignal } = {}
): Promise<T> {
  const response = await fetch(buildUrl(path, options.params), {
    method: options.method ?? "GET",
    signal: options.signal,
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = typeof body?.detail === "string" ? body.detail : JSON.stringify(body?.detail ?? body);
    } catch {
      // Response had no JSON body; fall back to statusText.
    }
    throw new ApiError(response.status, detail);
  }

  try {
    return (await response.json()) as T;
  } catch {
    throw new ApiError(response.status, "Received an invalid response payload from the server.");
  }
}

export const apiClient = { request };
