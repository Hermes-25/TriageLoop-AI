"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, ClipboardClock, FlaskConical, Gauge, Info, RotateCcw, UsersRound } from "lucide-react";
import { useProduct } from "@/app/components/ProductProvider";

const NAV_ITEMS = [
  { href: "/board", label: "Live board", icon: UsersRound },
  { href: "/surge", label: "Capacity", icon: Gauge },
  { href: "/evaluation", label: "Evidence", icon: FlaskConical },
  { href: "/audit", label: "Audit", icon: ClipboardClock },
  { href: "/about", label: "About", icon: Info },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { state, pending, degraded, resetDemo } = useProduct();

  return (
    <div className="app-frame">
      <a className="skip-link" href="#main-content">Skip to clinical workspace</a>
      <aside className="nav-rail" aria-label="Primary navigation">
        <Link href="/board" className="brand-lockup" aria-label="TriageLoop live board">
          <span className="loop-mark" aria-hidden="true"><span /></span>
          <span className="brand-word">TriageLoop</span>
        </Link>
        <nav className="nav-items">
          {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
            const active = pathname === href || pathname.startsWith(`${href}/`);
            return (
              <Link key={href} href={href} className="nav-link" aria-label={label} aria-current={active ? "page" : undefined}>
                <Icon size={19} strokeWidth={1.8} aria-hidden="true" />
                <span aria-hidden="true">{label}</span>
              </Link>
            );
          })}
        </nav>
        <div className="nav-foot">
          <button className="nav-reset" type="button" onClick={resetDemo} disabled={pending || degraded} aria-label="Reset demo">
            <RotateCcw size={17} aria-hidden="true" />
            <span>Reset demo</span>
          </button>
          <div className="prototype-chip"><Activity size={14} aria-hidden="true" /> Synthetic</div>
        </div>
      </aside>
      <div className="app-column" id="main-content" tabIndex={-1}>
        <header className="context-bar">
          <div className="context-place">
            <span className={`live-dot ${degraded ? "degraded" : ""}`} aria-label={degraded ? "Decision service degraded" : "Decision service live"} />
            <strong>Regional ED</strong>
            <span>{degraded ? "Degraded mode" : "Waiting room"}</span>
          </div>
          <div className="context-meta">
            <span>{pending ? "Recalculating…" : state?.scenario_label ?? "Loading scenario"}</span>
            <span className="context-time">22 Aug · 10:42 IST</span>
            <span className="role-chip">RN · A. Mehta</span>
          </div>
        </header>
        {children}
      </div>
    </div>
  );
}
