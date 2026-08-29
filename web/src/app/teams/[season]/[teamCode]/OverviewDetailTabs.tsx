"use client";

import { useState } from "react";
import Link from "next/link";
import styles from "./TeamProfile.module.css";

type ClosingFixture = {
  href: string;
  result: string;
  opponent: string;
  score: string;
  venue: string;
  date: string;
};

type Props = {
  position: string;
  played: number;
  points: number;
  wins: number;
  draws: number;
  losses: number;
  goalsFor: number;
  goalsAgainst: number;
  goalDifference: number;
  closingFixtures: ClosingFixture[];
};

const tabs = ["closing", "goals", "record"] as const;
type Tab = typeof tabs[number];

export function OverviewDetailTabs({
  position,
  played,
  points,
  wins,
  draws,
  losses,
  goalsFor,
  goalsAgainst,
  goalDifference,
  closingFixtures,
}: Props) {
  const [active, setActive] = useState<Tab>("closing");

  return (
    <section className={styles.detailStrip}>
      <nav className={styles.detailTabs} aria-label="Season overview details">
        <button data-active={active === "closing"} onClick={() => setActive("closing")}>
          Closing form
        </button>
        <button data-active={active === "goals"} onClick={() => setActive("goals")}>
          Goals
        </button>
        <button data-active={active === "record"} onClick={() => setActive("record")}>
          League record
        </button>
      </nav>

      <div className={styles.detailPanel}>
        {active === "closing" && (
          <div className={styles.closingForm}>
            {closingFixtures.map((fixture) => (
              <Link href={fixture.href} key={fixture.href} className={styles.closingFixture}>
                <span className={styles.closingResult} data-result={fixture.result}>
                  {fixture.result}
                </span>
                <span className={styles.closingFixtureCopy}>
                  <strong>{fixture.opponent}</strong>
                  <small>{fixture.date} · {fixture.venue}</small>
                </span>
                <b>{fixture.score}</b>
              </Link>
            ))}
          </div>
        )}

        {active === "goals" && (
          <div className={styles.detailNumbers}>
            <div>
              <strong>{goalsFor}</strong>
              <span>Scored</span>
            </div>
            <div>
              <strong>{goalsAgainst}</strong>
              <span>Conceded</span>
            </div>
            <div>
              <strong>{goalDifference > 0 ? `+${goalDifference}` : goalDifference}</strong>
              <span>Goal difference</span>
            </div>
          </div>
        )}

        {active === "record" && (
          <div className={styles.detailNumbers}>
            <div>
              <strong>{position}</strong>
              <span>League finish</span>
            </div>
            <div>
              <strong>{points}</strong>
              <span>Points</span>
            </div>
            <div>
              <strong>{wins}–{draws}–{losses}</strong>
              <span>W–D–L · {played} played</span>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
