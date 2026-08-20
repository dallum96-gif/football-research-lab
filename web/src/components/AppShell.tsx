"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

type AppShellProps = {
  children: ReactNode;
};

const navGroups = [
  {
    label: "Explore",
    links: [
      { href: "/", label: "Overview" },
      { href: "/fixtures", label: "Fixtures" },
      { href: "/teams", label: "Teams" },
      { href: "/players", label: "Players" },
    ],
  },
  {
    label: "Analysis",
    links: [
      { href: "/research", label: "Research" },
      { href: "/visualisations", label: "Visualisation" },
    ],
  },
];

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();

  return (
    <div className="frl-shell">
      <aside className="frl-sidebar" aria-label="FRL navigation">
        <div className="frl-sidebar-brand">Football Research Laboratory</div>
        {navGroups.map((group) => (
          <div key={group.label} className="frl-sidebar-group">
            <p className="frl-sidebar-kicker">{group.label}</p>
            {group.links.map((link) => {
              const active = link.href === "/"
                ? pathname === "/"
                : pathname === link.href || pathname.startsWith(`${link.href}/`);

              return (
                <Link
                  key={link.href}
                  className="frl-sidebar-link"
                  data-active={active ? "true" : "false"}
                  href={link.href}
                >
                  {link.label}
                </Link>
              );
            })}
          </div>
        ))}
      </aside>

      <main className="frl-main">{children}</main>
    </div>
  );
}
