"use client";

import type { ReactNode } from "react";
import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import styles from "./AppShell.module.css";

type AppShellProps = {
  children: ReactNode;
};

type NavLink = {
  href: string;
  label: string;
  activePrefix?: string;
};

type NavSection = {
  label: string;
  href: string;
  prefixes: string[];
  links: NavLink[];
};

const navSections: NavSection[] = [
  {
    label: "Explore",
    href: "/",
    prefixes: ["/fixtures", "/league-table", "/teams", "/players"],
    links: [
      { href: "/", label: "Overview" },
      { href: "/fixtures", label: "Fixtures" },
      { href: "/league-table", label: "League Table" },
      { href: "/teams", label: "Teams" },
      { href: "/players", label: "Players" },
    ],
  },
  {
    label: "Analyse",
    href: "/team-stats",
    prefixes: ["/team-stats", "/player-stats"],
    links: [
      { href: "/team-stats", label: "Team Stats", activePrefix: "/team-stats" },
      { href: "/player-stats", label: "Player Stats", activePrefix: "/player-stats" },
    ],
  },
  {
    label: "Bet",
    href: "/matchday",
    prefixes: ["/matchday", "/head-to-head"],
    links: [
      { href: "/matchday", label: "Matchday", activePrefix: "/matchday" },
      { href: "/fixtures", label: "Fixture List" },
    ],
  },
];

function linkIsActive(pathname: string, link: NavLink) {
  if (link.href === "/") return pathname === "/";
  const prefix = link.activePrefix ?? link.href;
  return pathname === prefix || pathname.startsWith(`${prefix}/`);
}

function sectionIsActive(pathname: string, section: NavSection) {
  if (section.label === "Explore" && pathname === "/") return true;
  return section.prefixes.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`),
  );
}

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);
  const activeSection =
    navSections.find((section) => sectionIsActive(pathname, section)) ?? navSections[0];
  const darkSurface = pathname === "/fixtures";

  return (
    <div className={styles.shell} data-tone={darkSurface ? "dark" : "light"}>
      <header className={styles.header}>
        <div className={styles.topRow}>
          <Link className={styles.brand} href="/" onClick={() => setMenuOpen(false)}>
            <span className={styles.monogram}>FRL.</span>
            <span className={styles.brandRule} aria-hidden="true" />
            <span className={styles.brandName}>Football Research Laboratory</span>
          </Link>

          <nav
            id="frl-primary-navigation"
            className={styles.primaryNav}
            data-open={menuOpen ? "true" : "false"}
            aria-label="Primary navigation"
          >
            {navSections.map((section) => {
              const active = sectionIsActive(pathname, section);
              return (
                <Link
                  key={section.label}
                  className={styles.primaryLink}
                  data-active={active ? "true" : "false"}
                  href={section.href}
                  onClick={() => setMenuOpen(false)}
                >
                  {section.label}
                </Link>
              );
            })}
          </nav>

          <div className={styles.scope} aria-label="Competition scope">
            <span className={styles.scopeDot} aria-hidden="true" />
            Premier League research
          </div>

          <button
            className={styles.menuButton}
            type="button"
            aria-expanded={menuOpen}
            aria-controls="frl-primary-navigation"
            onClick={() => setMenuOpen((open) => !open)}
          >
            {menuOpen ? "Close" : "Menu"}
          </button>
        </div>

        <div className={styles.contextBar}>
          <div className={styles.contextInner}>
            <span className={styles.contextLabel}>{activeSection.label}</span>
            <span className={styles.contextRule} aria-hidden="true" />
            <nav className={styles.contextNav} aria-label={`${activeSection.label} navigation`}>
              {activeSection.links.map((link) => {
                const active = linkIsActive(pathname, link);
                return (
                  <Link
                    key={`${activeSection.label}-${link.href}`}
                    className={styles.contextLink}
                    data-active={active ? "true" : "false"}
                    href={link.href}
                  >
                    {link.label}
                  </Link>
                );
              })}
            </nav>
          </div>
        </div>
      </header>

      <main className={styles.main}>{children}</main>
    </div>
  );
}
