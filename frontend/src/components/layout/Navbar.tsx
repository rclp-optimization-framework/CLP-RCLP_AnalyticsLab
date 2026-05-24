import * as Tooltip from "@radix-ui/react-tooltip";
import {
  ActivitySquare,
  BarChart3,
  Cpu,
  LayoutDashboard,
  Menu,
  X,
  Box,
  TestTube2,
} from "lucide-react";
import { useState } from "react";
import { NavLink } from "react-router-dom";

const navItems = [
  { to: "/", label: "Home", icon: LayoutDashboard },
  { to: "/batteries", label: "Batteries", icon: Box },
  { to: "/tests", label: "Tests", icon: TestTube2 },
  { to: "/execution", label: "Execution", icon: Cpu },
  { to: "/cache", label: "Cache", icon: ActivitySquare },
  { to: "/statistics", label: "Statistics", icon: BarChart3 },
];

export function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-white/50 bg-white/70 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <NavLink to="/" className="flex items-center gap-3">
          <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-950 text-white shadow-glow">
            <span className="brand-type text-lg font-bold">R</span>
          </span>
          <div>
            <p className="brand-type text-sm font-semibold uppercase tracking-[0.35em] text-blue-700">
              R-CLP Analytics
            </p>
            <p className="text-xs text-slate-500">
              Research execution and statistics platform
            </p>
          </div>
        </NavLink>

        <nav className="hidden items-center gap-2 lg:flex">
          <Tooltip.Provider delayDuration={120}>
            {navItems.map(({ to, label, icon: Icon }) => (
              <Tooltip.Root key={to}>
                <Tooltip.Trigger asChild>
                  <NavLink
                    to={to}
                    className={({ isActive }) =>
                      `flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition ${
                        isActive
                          ? "bg-blue-600 text-gray-500 shadow-panel"
                          : "text-blue-700 hover:bg-blue-50 hover:text-blue-800"
                      }`
                    }
                    title={label}
                  >
                    <Icon className="h-4 w-4 text-current" />
                    {label}
                  </NavLink>
                </Tooltip.Trigger>
                <Tooltip.Portal>
                  <Tooltip.Content
                    sideOffset={8}
                    className="rounded-full bg-blue-700 px-3 py-1.5 text-xs text-white shadow-panel"
                  >
                    {label} section
                    <Tooltip.Arrow className="fill-blue-700" />
                  </Tooltip.Content>
                </Tooltip.Portal>
              </Tooltip.Root>
            ))}
          </Tooltip.Provider>
        </nav>

        <button
          type="button"
          className="inline-flex items-center justify-center rounded-full border border-slate-200 bg-white p-3 text-slate-950 shadow-sm transition hover:border-blue-300 hover:text-blue-700 lg:hidden"
          onClick={() => setOpen((value) => !value)}
          aria-label="Toggle navigation"
        >
          {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {open ? (
        <div className="border-t border-slate-200 bg-white/95 px-4 pb-4 pt-2 lg:hidden">
          <div className="mx-auto flex max-w-7xl flex-col gap-2">
            {navItems.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                onClick={() => setOpen(false)}
                className={({ isActive }) =>
                  `rounded-2xl px-4 py-3 text-sm font-semibold ${
                    isActive
                      ? "bg-blue-600 text-white"
                      : "bg-blue-50 text-blue-700"
                  }`
                }
                title={label}
              >
                {label}
              </NavLink>
            ))}
          </div>
        </div>
      ) : null}
    </header>
  );
}
