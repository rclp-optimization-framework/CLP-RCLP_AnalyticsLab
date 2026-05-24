import { Github, MapPinned, Mail } from "lucide-react";
import { NavLink } from "react-router-dom";

const sitemap = [
  { to: "/", label: "Home" },
  { to: "/execution", label: "Execution" },
  { to: "/cache", label: "Cache" },
  { to: "/statistics", label: "Statistics" },
];

export function Footer() {
  return (
    <footer className="mt-20 border-t border-slate-200/80 bg-slate-950 text-white">
      <div className="mx-auto grid max-w-7xl gap-10 px-4 py-12 sm:px-6 lg:grid-cols-[1.3fr_1fr_1fr] lg:px-8">
        <div>
          <p className="brand-type text-sm uppercase tracking-[0.4em] text-blue-300">
            R-CLP Analytics
          </p>
          <p className="mt-4 max-w-xl text-sm leading-7 text-slate-300">
            A research-first platform for battery execution, result storage, and
            statistical analysis for the AVISPA group.
          </p>
        </div>

        <div>
          <p className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.25em] text-slate-200">
            <MapPinned className="h-4 w-4 text-blue-300" />
            Sitemap
          </p>
          <ul className="mt-4 space-y-3 text-sm text-slate-300">
            {sitemap.map((item) => (
              <li key={item.to}>
                <NavLink className="transition hover:text-white" to={item.to}>
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-slate-200">
            Project links
          </p>
          <div className="mt-4 space-y-3 text-sm text-slate-300">
            <p className="flex items-center gap-2">
              <Github className="h-4 w-4 text-blue-300" />
              Front and backend containers are designed to run in a single
              network.
            </p>
            <p className="flex items-center gap-2">
              <Mail className="h-4 w-4 text-blue-300" />
              Documentation lives in the root docs directory.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
