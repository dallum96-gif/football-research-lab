"use client";

import type { CSSProperties } from "react";
import { useMemo, useState } from "react";
import { TeamCrest } from "@/components/TeamCrest";
import { FixturePlayerPerformance } from "./FixturePlayerPerformance";
import styles from "./MatchResultExperience.module.css";

type View = "match" | "lineups" | "players" | "statistics";

type FixtureEventPlayer = {
  source_player_id: string | null;
  name: string | null;
  identity_status: string;
};

type FixtureEvent = {
  event_id: string | null;
  type: "goal" | "card" | "substitution" | string;
  side: "home" | "away";
  minute: string | null;
  seconds: number | null;
  primary_player: FixtureEventPlayer;
  secondary_player: FixtureEventPlayer;
  assist: FixtureEventPlayer | null;
  detail: {
    goal_type: string | null;
    card_type: string | null;
    period: string | null;
    timestamp: string | null;
  };
};

type FixtureEvidence = {
  status: string;
  season: string;
  fixture_id: string;
  fixture: {
    home_team_id?: string;
    away_team_id?: string;
    source_match_id?: string;
  };
  metadata?: {
    source_match_id?: string | null;
    ground?: string | null;
    attendance?: number | null;
    referee?: string | null;
    source_kickoff?: string | null;
  };
  events: FixtureEvent[];
  lineup: Array<{
    player: {
      source_player_id: string | null;
      name: string | null;
      identity_status: string;
    };
    side: "home" | "away" | null;
    position: string | null;
    shirt_number: string | null;
    placement: {
      source_player_id: string;
      x: number;
      y: number;
      status: "SOURCE_EXPLICIT" | "DERIVED_FORMATION_LAYOUT" | string;
      provenance: {
        classification: "SOURCE_EVIDENCE" | "PRESENTATION_ONLY" | string;
        explicit_source_coordinates: boolean;
      };
    } | null;
    participation: "starting" | "sub_in" | "bench" | "unknown";
    minutes: number | null;
  }>;
  formation: {
    home: { status: string; value: string | null };
    away: { status: string; value: string | null };
  };
  managers: {
    status: string;
    items: Array<{
      side: "home" | "away";
      source_manager_id: string | null;
      first_name: string | null;
      last_name: string | null;
      type: string | null;
    }>;
  };
  limitations: string[];
};

type Fixture = {
  fixture_id: string;
  season: string;
  gameweek: number | null;
  kickoff_time: string | null;
  home_team_id: string;
  away_team_id: string;
  home_team_name: string;
  away_team_name: string;
  home_score: number | null;
  away_score: number | null;
};

type MatchStats = {
  home_possession: number | null;
  away_possession: number | null;
  home_shots_on_target: number | null;
  away_shots_on_target: number | null;
  home_shots: number | null;
  away_shots: number | null;
  home_corners: number | null;
  away_corners: number | null;
  home_fouls: number | null;
  away_fouls: number | null;
  home_yellow_cards: number | null;
  away_yellow_cards: number | null;
  attendance: number | null;
} | null;

type Props = {
  season: string;
  fixtureId: string;
  fixture: Fixture;
  stats: MatchStats;
  evidence: FixtureEvidence | null;
  date: string;
  time: string;
};

type Metric = {
  label: string;
  home: number | null;
  away: number | null;
  suffix?: string;
};

function numberLabel(value: number | null, suffix = "") {
  if (value == null || Number.isNaN(value)) return "—";
  return `${Number.isInteger(value) ? value : value.toFixed(1)}${suffix}`;
}

function metricShares(home: number | null, away: number | null, isPercentage = false) {
  if (home == null || away == null) return [0, 0] as const;
  if (isPercentage) return [Math.max(0, home), Math.max(0, away)] as const;
  const total = home + away;
  if (total <= 0) return [0, 0] as const;
  return [(home / total) * 100, (away / total) * 100] as const;
}

function minuteNumber(value: string | null) {
  if (!value) return null;
  const [baseRaw, addedRaw] = value.split("+");
  const base = Number.parseInt(baseRaw, 10);
  const added = Number.parseInt(addedRaw ?? "0", 10);
  if (!Number.isFinite(base)) return null;
  return Math.max(0, base + (Number.isFinite(added) ? added : 0));
}

function eventName(event: FixtureEvent) {
  return event.primary_player.name || "Player unavailable";
}

function eventSecondary(event: FixtureEvent) {
  if (event.type === "goal" && event.assist?.name) return `Assist · ${event.assist.name}`;
  const card = event.detail.card_type?.trim();
  return card ? card.replaceAll("_", " ") : null;
}

function managerName(evidence: FixtureEvidence | null, side: "home" | "away") {
  const manager = evidence?.managers.items.find((item) => item.side === side);
  if (!manager) return "Manager unavailable";
  return [manager.first_name, manager.last_name].filter(Boolean).join(" ") || "Manager unavailable";
}

function resultLabel(fixture: Fixture) {
  const home = fixture.home_score;
  const away = fixture.away_score;
  if (home == null || away == null) return "Result unavailable";
  if (home === away) return `Drawn ${home}–${away}`;
  const winner = home > away ? fixture.home_team_name : fixture.away_team_name;
  return `${winner} won ${home}–${away}`;
}

function EventFlow({ events }: { events: FixtureEvent[] }) {
  const ordered = useMemo(() => {
    let homeIndex = 0;
    let awayIndex = 0;
    const maxMinute = Math.max(90, ...events.map((event) => minuteNumber(event.minute) ?? 0));
    const scale = maxMinute > 95 ? maxMinute : 95;

    return events
      .map((event) => {
        const minute = minuteNumber(event.minute);
        const sideIndex = event.side === "home" ? homeIndex++ : awayIndex++;
        const lane = sideIndex % 2;
        const position = minute == null ? 50 : Math.min(98, Math.max(2, (minute / scale) * 100));
        const align = position > 84 ? "right" : position < 16 ? "left" : "center";
        return { event, minute, lane, position, align };
      })
      .sort((a, b) => (a.minute ?? 999) - (b.minute ?? 999));
  }, [events]);

  if (!ordered.length) {
    return <div className={styles.flowUnavailable}>Verified event sequence unavailable</div>;
  }

  return (
    <div className={styles.flowCanvas} aria-label="Match event flow">
      <div className={styles.flowTrack} />
      {[0, 45, 90].map((tick) => (
        <div key={tick} className={styles.flowTick} style={{ left: `${(tick / 90) * 100}%` }}>
          <i />
          <span>{tick}′</span>
        </div>
      ))}

      {ordered.map(({ event, lane, position, align }, index) => {
        const isGoal = event.type === "goal";
        const isRed = event.detail.card_type?.toUpperCase().includes("RED") ?? false;
        const style = {
          left: `${position}%`,
          "--lane-offset": `${lane * 46}px`,
        } as CSSProperties;

        return (
          <div
            key={`${event.event_id ?? "event"}-${event.minute ?? index}-${index}`}
            className={`${styles.flowEvent} ${event.side === "home" ? styles.flowHome : styles.flowAway}`}
            data-align={align}
            data-kind={isGoal ? "goal" : isRed ? "red" : "card"}
            style={style}
          >
            <span className={styles.flowMinute}>{event.minute ?? "—"}</span>
            <strong>{eventName(event)}</strong>
            {eventSecondary(event) ? <small>{eventSecondary(event)}</small> : null}
          </div>
        );
      })}
    </div>
  );
}

function MetricRow({ metric }: { metric: Metric }) {
  const isPercentage = metric.suffix === "%";
  const [homeShare, awayShare] = metricShares(metric.home, metric.away, isPercentage);
  return (
    <div className={styles.metricRow}>
      <div className={styles.metricValues}>
        <strong>{numberLabel(metric.home, metric.suffix)}</strong>
        <span>{metric.label}</span>
        <strong>{numberLabel(metric.away, metric.suffix)}</strong>
      </div>
      <div className={styles.metricScale} aria-hidden="true">
        <span className={styles.metricHomeScale} style={{ width: `${homeShare}%` }} />
        <span className={styles.metricAwayScale} style={{ width: `${awayShare}%` }} />
      </div>
    </div>
  );
}

function MatchView({ fixture, stats, evidence }: { fixture: Fixture; stats: MatchStats; evidence: FixtureEvidence | null }) {
  const events = (evidence?.events ?? []).filter((event) => event.type === "goal" || event.type === "card");
  const metrics: Metric[] = [
    { label: "Possession", home: stats?.home_possession ?? null, away: stats?.away_possession ?? null, suffix: "%" },
    { label: "Shots", home: stats?.home_shots ?? null, away: stats?.away_shots ?? null },
    { label: "On target", home: stats?.home_shots_on_target ?? null, away: stats?.away_shots_on_target ?? null },
    { label: "Corners", home: stats?.home_corners ?? null, away: stats?.away_corners ?? null },
    { label: "Fouls", home: stats?.home_fouls ?? null, away: stats?.away_fouls ?? null },
    { label: "Yellow cards", home: stats?.home_yellow_cards ?? null, away: stats?.away_yellow_cards ?? null },
  ];

  return (
    <div className={`${styles.view} ${styles.matchView}`}>
      <section className={styles.flowPanel}>
        <div className={styles.viewHeading}>
          <div>
            <span>Match flow</span>
            <strong>{events.length ? `${events.length} verified events` : "Event evidence unavailable"}</strong>
          </div>
          <small>0′ — 90′</small>
        </div>
        <EventFlow events={events} />
      </section>

      <aside className={styles.profilePanel}>
        <div className={styles.profileHeading}>
          <span>Match profile</span>
          <strong>{resultLabel(fixture)}</strong>
          <small>{fixture.home_team_name} · {fixture.away_team_name}</small>
        </div>
        <div className={styles.metricList}>
          {metrics.map((metric) => <MetricRow key={metric.label} metric={metric} />)}
        </div>
      </aside>
    </div>
  );
}

function LineupPanel({
  side,
  fixture,
  evidence,
}: {
  side: "home" | "away";
  fixture: Fixture;
  evidence: FixtureEvidence | null;
}) {
  const teamName = side === "home" ? fixture.home_team_name : fixture.away_team_name;
  const formation = evidence?.formation[side].status === "AVAILABLE" ? evidence.formation[side].value : null;
  const players = (evidence?.lineup ?? [])
    .filter((row) => row.side === side && row.participation === "starting")
    .filter((row) => row.placement != null);

  return (
    <section className={styles.lineupPanel}>
      <div className={styles.lineupHeader}>
        <div className={styles.lineupIdentity}>
          <TeamCrest teamName={teamName} size={32} />
          <div>
            <span>{side === "home" ? "Home XI" : "Away XI"}</span>
            <strong>{teamName}</strong>
          </div>
        </div>
        <div className={styles.lineupContext}>
          <strong>{formation ?? "—"}</strong>
          <span>{managerName(evidence, side)}</span>
        </div>
      </div>

      <div className={styles.pitch}>
        <div className={styles.pitchHalf} />
        <div className={styles.pitchCircle} />
        <div className={`${styles.penaltyArea} ${styles.penaltyTop}`} />
        <div className={`${styles.penaltyArea} ${styles.penaltyBottom}`} />
        <div className={`${styles.goalBox} ${styles.goalTop}`} />
        <div className={`${styles.goalBox} ${styles.goalBottom}`} />

        {players.length ? players.map((row) => (
          <div
            key={`${side}-${row.player.source_player_id ?? row.player.name}`}
            className={styles.playerNode}
            style={{ left: `${row.placement?.x ?? 50}%`, top: `${row.placement?.y ?? 50}%` }}
          >
            <span className={styles.playerNumber}>{row.shirt_number ?? ""}</span>
            <strong>{row.player.name || "Player unavailable"}</strong>
            <small>{row.position || ""}</small>
          </div>
        )) : (
          <div className={styles.lineupUnavailable}>Verified starting XI placement unavailable</div>
        )}
      </div>
    </section>
  );
}

function LineupsView({ fixture, evidence }: { fixture: Fixture; evidence: FixtureEvidence | null }) {
  return (
    <div className={`${styles.view} ${styles.lineupsView}`}>
      <LineupPanel side="home" fixture={fixture} evidence={evidence} />
      <LineupPanel side="away" fixture={fixture} evidence={evidence} />
    </div>
  );
}

function PlayersView({ season, fixtureId }: { season: string; fixtureId: string }) {
  return (
    <div className={`${styles.view} ${styles.playersView}`}>
      <div className={styles.viewHeading}>
        <div>
          <span>Individual output</span>
          <strong>Verified fixture leaders</strong>
        </div>
        <small>Source-backed match performance</small>
      </div>
      <div className={styles.playersSurface}>
        <FixturePlayerPerformance season={season} fixtureId={fixtureId} />
      </div>
    </div>
  );
}

function StatisticsView({ fixture, stats }: { fixture: Fixture; stats: MatchStats }) {
  const metrics: Metric[] = [
    { label: "Possession", home: stats?.home_possession ?? null, away: stats?.away_possession ?? null, suffix: "%" },
    { label: "Shots", home: stats?.home_shots ?? null, away: stats?.away_shots ?? null },
    { label: "Shots on target", home: stats?.home_shots_on_target ?? null, away: stats?.away_shots_on_target ?? null },
    { label: "Corners", home: stats?.home_corners ?? null, away: stats?.away_corners ?? null },
    { label: "Fouls", home: stats?.home_fouls ?? null, away: stats?.away_fouls ?? null },
    { label: "Yellow cards", home: stats?.home_yellow_cards ?? null, away: stats?.away_yellow_cards ?? null },
  ];

  return (
    <div className={`${styles.view} ${styles.statisticsView}`}>
      <div className={styles.statsTeams}>
        <div>
          <TeamCrest teamName={fixture.home_team_name} size={30} />
          <strong>{fixture.home_team_name}</strong>
        </div>
        <span>Match statistics</span>
        <div>
          <strong>{fixture.away_team_name}</strong>
          <TeamCrest teamName={fixture.away_team_name} size={30} />
        </div>
      </div>
      <div className={styles.fullStats}>
        {metrics.map((metric) => <MetricRow key={metric.label} metric={metric} />)}
      </div>
    </div>
  );
}

export function MatchResultExperience({ season, fixtureId, fixture, stats, evidence, date, time }: Props) {
  const [view, setView] = useState<View>("match");
  const goalEvents = (evidence?.events ?? []).filter((event) => event.type === "goal");
  const homeGoals = goalEvents.filter((event) => event.side === "home");
  const awayGoals = goalEvents.filter((event) => event.side === "away");
  const completed = fixture.home_score != null && fixture.away_score != null;

  const metadata = [
    ["Competition", "Premier League"],
    ["Matchweek", fixture.gameweek == null ? "Unavailable" : `GW ${fixture.gameweek}`],
    ["Date", date],
    ["Kick-off", time],
    ["Venue", evidence?.metadata?.ground || "Unavailable"],
    ["Attendance", evidence?.metadata?.attendance == null ? "Unavailable" : evidence.metadata.attendance.toLocaleString("en-GB")],
    ["Referee", evidence?.metadata?.referee || "Unavailable"],
  ];

  const tabs: Array<[View, string]> = [
    ["match", "Match"],
    ["lineups", "Lineups"],
    ["players", "Players"],
    ["statistics", "Statistics"],
  ];

  return (
    <article className={styles.experience} data-match-result>
      <header className={styles.hero}>
        <div className={styles.eyebrow}>
          <span>Premier League</span>
          <span>{fixture.gameweek == null ? season : `GW ${fixture.gameweek}`}</span>
          <span>{date}</span>
        </div>

        <h1 className={styles.visuallyHidden}>
          {fixture.home_team_name} {fixture.home_score ?? ""} {fixture.away_team_name} {fixture.away_score ?? ""}
        </h1>

        <div className={styles.heroStage}>
          <div className={`${styles.club} ${styles.clubHome}`}>
            <TeamCrest teamName={fixture.home_team_name} size={58} />
            <strong>{fixture.home_team_name}</strong>
          </div>

          <div className={styles.scoreBlock}>
            <div className={styles.score}>
              <span>{fixture.home_score ?? "—"}</span>
              <i>–</i>
              <span>{fixture.away_score ?? "—"}</span>
            </div>
            <small>{completed ? "Full time" : "Status unavailable"}</small>
          </div>

          <div className={`${styles.club} ${styles.clubAway}`}>
            <strong>{fixture.away_team_name}</strong>
            <TeamCrest teamName={fixture.away_team_name} size={58} />
          </div>
        </div>

        {goalEvents.length ? (
          <div className={styles.scorers} aria-label="Goalscorers">
            <div className={styles.scorersHome}>
              {homeGoals.map((event, index) => (
                <div key={`${event.event_id ?? "home"}-${index}`}>
                  <strong>{eventName(event)}</strong><span>{event.minute ?? "—"}</span>
                </div>
              ))}
            </div>
            <div className={styles.scorersAway}>
              {awayGoals.map((event, index) => (
                <div key={`${event.event_id ?? "away"}-${index}`}>
                  <strong>{eventName(event)}</strong><span>{event.minute ?? "—"}</span>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </header>

      <nav className={styles.viewRail} aria-label="Match result views">
        {tabs.map(([key, label]) => (
          <button
            key={key}
            type="button"
            data-active={view === key ? "true" : "false"}
            aria-pressed={view === key}
            onClick={() => setView(key)}
          >
            {label}
          </button>
        ))}
      </nav>

      <main className={styles.workspace}>
        {view === "match" ? <MatchView fixture={fixture} stats={stats} evidence={evidence} /> : null}
        {view === "lineups" ? <LineupsView fixture={fixture} evidence={evidence} /> : null}
        {view === "players" ? <PlayersView season={season} fixtureId={fixtureId} /> : null}
        {view === "statistics" ? <StatisticsView fixture={fixture} stats={stats} /> : null}
      </main>

      <footer className={styles.recordFooter} aria-label="Match record">
        {metadata.map(([label, value]) => (
          <div key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </footer>
    </article>
  );
}
