import { useCallback, useEffect, useState } from "react";

export interface ApiResourceState<T> {
  status: "loading" | "success" | "error";
  data: T | null;
  error: string | null;
}

/**
 * Shared fetch-with-abort state machine used by every dashboard data hook.
 * Aborting the in-flight request on dependency change (not just on
 * unmount) is what stops a slow, stale response from overwriting a result
 * for a filter selection the user already moved away from.
 */
export function useApiResource<T>(
  fetcher: (signal: AbortSignal) => Promise<T>,
  deps: unknown[]
): ApiResourceState<T> & { retry: () => void } {
  const [state, setState] = useState<ApiResourceState<T>>({
    status: "loading",
    data: null,
    error: null,
  });
  const [retryCount, setRetryCount] = useState(0);
  const retry = useCallback(() => setRetryCount((count) => count + 1), []);

  useEffect(() => {
    const controller = new AbortController();
    setState((prev) => ({ ...prev, status: "loading", error: null }));

    fetcher(controller.signal)
      .then((data) => {
        if (!controller.signal.aborted) {
          setState({ status: "success", data, error: null });
        }
      })
      .catch((error: unknown) => {
        if (!controller.signal.aborted) {
          const message = error instanceof Error ? error.message : "Unknown error";
          setState({ status: "error", data: null, error: message });
        }
      });

    return () => controller.abort();
    // deps is intentionally spread by the caller; retryCount forces a refetch.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, retryCount]);

  return { ...state, retry };
}
