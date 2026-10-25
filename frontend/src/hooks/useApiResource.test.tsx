import { act, renderHook, waitFor } from "@testing-library/react";
import { useApiResource } from "./useApiResource";

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((r) => {
    resolve = r;
  });
  return { promise, resolve };
}

describe("useApiResource", () => {
  it("ignores a stale response that resolves after deps change", async () => {
    const first = deferred<string>();
    const second = deferred<string>();
    let callCount = 0;
    const fetcher = vi.fn(() => {
      callCount += 1;
      return callCount === 1 ? first.promise : second.promise;
    });

    const { result, rerender } = renderHook(({ dep }) => useApiResource(fetcher, [dep]), {
      initialProps: { dep: 1 },
    });

    rerender({ dep: 2 });
    second.resolve("second-result");
    await waitFor(() => expect(result.current.status).toBe("success"));

    first.resolve("first-result");
    await new Promise((r) => setTimeout(r, 0));

    expect(result.current.data).toBe("second-result");
  });

  it("re-invokes the fetcher when retry is called", async () => {
    const fetcher = vi.fn().mockResolvedValue("ok");
    const { result } = renderHook(() => useApiResource(fetcher, []));
    await waitFor(() => expect(result.current.status).toBe("success"));
    expect(fetcher).toHaveBeenCalledTimes(1);

    act(() => result.current.retry());
    await waitFor(() => expect(fetcher).toHaveBeenCalledTimes(2));
  });

  it("surfaces a rejected promise as an error state", async () => {
    const fetcher = vi.fn().mockRejectedValue(new Error("boom"));
    const { result } = renderHook(() => useApiResource(fetcher, []));
    await waitFor(() => expect(result.current.status).toBe("error"));
    expect(result.current.error).toBe("boom");
  });
});
