import { BarChart3, BookOpen, Gauge, Wind } from "lucide-react";
import type { ViewKey } from "../../App";

const NAV_ITEMS: { key: ViewKey; label: string; icon: typeof Gauge }[] = [
  { key: "overview", label: "Overview", icon: Gauge },
  { key: "forecast-analysis", label: "Forecast Analysis", icon: BarChart3 },
  { key: "accuracy", label: "Accuracy & Backtesting", icon: BarChart3 },
  { key: "methodology", label: "Data & Methodology", icon: BookOpen },
];

interface SidebarProps {
  activeView: ViewKey;
  onSelectView: (view: ViewKey) => void;
}

export function Sidebar({ activeView, onSelectView }: SidebarProps) {
  return (
    <nav
      aria-label="Primary"
      className="flex h-full w-64 flex-shrink-0 flex-col gap-6 bg-navy-950 px-4 py-6 text-slate-200"
    >
      <div className="flex items-center gap-2 px-2">
        <Wind className="h-6 w-6 text-teal-500" aria-hidden="true" />
        <div>
          <p className="text-base font-semibold text-white">WindLens</p>
          <p className="text-[11px] uppercase tracking-wide text-slate-400">Wind Forecast Analytics</p>
        </div>
      </div>

      <ul className="flex flex-col gap-1">
        {NAV_ITEMS.map(({ key, label, icon: Icon }) => {
          const isActive = key === activeView;
          return (
            <li key={key}>
              <button
                type="button"
                onClick={() => onSelectView(key)}
                aria-current={isActive ? "page" : undefined}
                className={`flex w-full items-center gap-3 rounded-md px-3 py-2 text-left text-sm font-medium transition ${
                  isActive
                    ? "bg-navy-700 text-white"
                    : "text-slate-300 hover:bg-navy-800 hover:text-white"
                }`}
              >
                <Icon className="h-4 w-4" aria-hidden="true" />
                {label}
              </button>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
