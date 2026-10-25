import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Sidebar } from "./Sidebar";

describe("Sidebar", () => {
  it("marks the active view with aria-current", () => {
    render(<Sidebar activeView="overview" onSelectView={vi.fn()} />);
    expect(screen.getByRole("button", { name: "Overview" })).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("button", { name: "Data & Methodology" })).not.toHaveAttribute("aria-current");
  });

  it("calls onSelectView with the clicked view key", async () => {
    const onSelectView = vi.fn();
    render(<Sidebar activeView="overview" onSelectView={onSelectView} />);
    await userEvent.click(screen.getByRole("button", { name: "Accuracy & Backtesting" }));
    expect(onSelectView).toHaveBeenCalledWith("accuracy");
  });
});
