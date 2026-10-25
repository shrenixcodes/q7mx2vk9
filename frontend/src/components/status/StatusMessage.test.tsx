import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { StatusMessage } from "./StatusMessage";

describe("StatusMessage", () => {
  it("renders a loading state with status role", () => {
    render(<StatusMessage kind="loading" message="Loading data…" />);
    expect(screen.getByRole("status")).toHaveTextContent("Loading data…");
  });

  it("renders an error state with alert role", () => {
    render(<StatusMessage kind="error" message="Something failed" />);
    expect(screen.getByRole("alert")).toHaveTextContent("Something failed");
  });

  it("invokes onRetry when the retry button is clicked", async () => {
    const onRetry = vi.fn();
    render(<StatusMessage kind="error" message="Failed" onRetry={onRetry} />);
    await userEvent.click(screen.getByRole("button", { name: "Retry" }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("does not render a retry button when onRetry is omitted", () => {
    render(<StatusMessage kind="empty" message="Nothing here" />);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });
});
