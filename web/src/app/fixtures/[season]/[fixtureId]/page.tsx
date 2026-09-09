import type { CSSProperties } from "react";
import { notFound } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { TeamCrest } from "@/components/TeamCrest";
import { FixturePlayerPerformance } from "./FixturePlayerPerformance";
import styles from "./FixtureOverview.module.css";

type FixtureDetailProps = {
  params: Promise<{
    season: string;
    fixtureId: string;
  }>;
};

type Player = {
  name: string;
  role: string;
  number: string | null;
  x: number | null;
  y: number | null;
};

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

type FixtureEvidenceResponse = {
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

type FixtureDetailResponse = {
  fixture: {
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
  stats: {
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
};

const API_BASE = (process.env.NEXT_PUBLIC_FRL_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

type ApiResult<T> =
  | { ok: true; data: T }
  | { ok: false; status: number };

async function getJson<T>(path: string): Promise<ApiResult<T>> {
  const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!response.ok) return { ok: false, status: response.status };
  return { ok: true, data: await response.json() as T };
}

async function getOptionalJson<T>(path: string): Promise<T | null> {
  try {
    const result = await getJson<T>(path);
    return result.ok ? result.data : null;
  } catch {
    return null;
  }
}

function dateParts(kickoff: string | null): { date: string; time: string } {
  if (!kickoff) return { date: "Date unavailable", time: "Time unavailable" };
  const value = new Date(kickoff);
  if (Number.isNaN(value.getTime())) return { date: "Date unavailable", time: "Time unavailable" };

  const formatter = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Europe/London",
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
  const parts = formatter.formatToParts(value);
  const get = (type: string) => parts.find((part) => part.type === type)?.value ?? "";
  return {
    date: `${get("day")} ${get("month")} ${get("year")}`,
    time: `${get("hour")}:${get("minute")}`,
  };
}

function formatStat(value: number | null, suffix = ""): string {
  return value == null || Number.isNaN(value) ? "—" : `${Number.isInteger(value) ? value : value.toFixed(1)}${suffix}`;
}

function share(home: number | null, away: number | null): [number, number] {
  if (home == null || away == null) return [0, 0];
  const total = home + away;
  if (total <= 0) return [0, 0];
  return [(home / total) * 100, (away / total) * 100];
}

function managerName(evidence: FixtureEvidenceResponse | null, side: "home" | "away"): string {
  const manager = evidence?.managers.items.find((item) => item.side === side);
  if (!manager) return "Manager unavailable";
  return [manager.first_name, manager.last_name].filter(Boolean).join(" ") || "Manager unavailable";
}

function LineupSide({
  title,
  formation,
  manager,
  players,
  team,
  emptyLabel,
}: {
  title: string;
  formation: string | null;
  manager: string;
  players: Player[];
  team: "home" | "away";
  emptyLabel: string;
}) {
  const placedPlayers = players.filter((player) => player.x != null && player.y != null);

  return (
    <div className={`${styles.lineupSide} ${team === "home" ? styles.lineupHome : styles.lineupAway}`}>
      <div className={styles.lineupSideHeader}>
        <div>
          <span>{team === "home" ? "Home XI" : "Away XI"}</span>
          <strong>{title}</strong>
        </div>
        <div className={styles.lineupMeta}>
          <strong>{formation ?? "—"}</strong>
          <span>{manager}</span>
        </div>
      </div>
      <div className={styles.tacticalBoard}>
        <div className={styles.boardBox} />
        <div className={styles.boardHalfLine} />
        <div className={styles.boardCircle} />
        {placedPlayers.length ? placedPlayers.map((player) => (
          <div
            className={styles.playerNode}
            key={`${player.name}-${player.number ?? ""}`}
            style={{ left: `${player.x}%`, top: `${player.y}%` } as CSSProperties}
            title={`${player.name} · ${player.role}`}
          >
            <span className={styles.playerDot}>{player.number ?? ""}</span>
            <span className={styles.playerName}>{player.name}</span>
            <span className={styles.playerRole}>{player.role}</span>
          </div>
        )) : <span className={styles.lineupUnavailable}>{emptyLabel}</span>}
      </div>
    </div>
  );
}

function eventLabel(event: FixtureEvent): string {
  const primary = event.primary_player.name || "Player unavailable";
  if (event.type === "goal") {
    return event.assist?.name ? `${primary} · assist ${event.assist.name}` : primary;
  }
  return primary;
}

function EventCell({ event }: { event: FixtureEvent }) {
  const isGoal = event.type === "goal";
  const isRed = event.detail.card_type?.toUpperCase() === "RED";
  const className = isGoal ? styles.eventGoal : isRed ? styles.eventRed : styles.eventCard;

  return (
    <div className={`${styles.event} ${event.side === "home" ? styles.eventHome : styles.eventAway} ${className}`}>
      <span className={styles.eventSymbol} aria-hidden="true">{isGoal ? "●" : "■"}</span>
      <span>{eventLabel(event)}</span>
    </div>
  );
}

export const dynamic = "force-dynamic";

export default async function FixtureDetailPage({ params }: FixtureDetailProps) {
  const { season, fixtureId } = await params;
  const fixturePath = `/api/v1/fixtures/${encodeURIComponent(season)}/${encodeURIComponent(fixtureId)}`;
  const detailResult = await getJson<FixtureDetailResponse>(fixturePath);

  if (!detailResult.ok) {
    if (detailResult.status === 404) notFound();
    throw new Error(`FRL fixture detail request failed: ${detailResult.status}`);
  }

  const detail = detailResult.data;
  const evidence = await getOptionalJson<FixtureEvidenceResponse>(`${fixturePath}/evidence`);
  const fixture = detail.fixture;
  const stats = detail.stats;
  const { date, time } = dateParts(fixture.kickoff_time);
  const completed = fixture.home_score != null && fixture.away_score != null;

  const events = evidence?.events ?? [];
  const timelineEvents = events.filter((event) => event.type === "goal" || event.type === "card");
  const startingPlayers = (side: "home" | "away"): Player[] =>
    (evidence?.lineup ?? [])
      .filter((row) => row.side === side && row.participation === "starting")
      .map((row) => ({
        name: row.player.name || "Player unavailable",
        role: row.position || "—",
        number: row.shirt_number,
        x: row.placement?.x ?? null,
        y: row.placement?.y ?? null,
      }));

  const evidenceNotice = evidence?.status === "AVAILABLE"
    ? null
    : evidence?.status === "KNOWN_EXCEPTION"
      ? {
          title: "Fixture evidence partial",
          detail: "Some event, lineup, formation or manager evidence could not be verified.",
        }
      : {
          title: "Fixture evidence unavailable",
          detail: "Events, lineups, formations and managers could not be verified for this fixture.",
        };

  const statRows = [
    [stats?.home_possession, "Possession", stats?.away_possession, stats?.home_possession, stats?.away_possession, true],
    [stats?.home_shots_on_target, "Shots on target", stats?.away_shots_on_target, ...share(stats?.home_shots_on_target ?? null, stats?.away_shots_on_target ?? null), false],
    [stats?.home_shots, "Shots", stats?.away_shots, ...share(stats?.home_shots ?? null, stats?.away_shots ?? null), false],
    [stats?.home_corners, "Corners", stats?.away_corners, ...share(stats?.home_corners ?? null, stats?.away_corners ?? null), false],
    [stats?.home_fouls, "Fouls", stats?.away_fouls, ...share(stats?.home_fouls ?? null, stats?.away_fouls ?? null), false],
    [stats?.home_yellow_cards, "Yellow cards", stats?.away_yellow_cards, ...share(stats?.home_yellow_cards ?? null, stats?.away_yellow_cards ?? null), false],
  ] as Array<[number | null, string, number | null, number, number, boolean]>;

  const metadata = [
    ["Competition", "Premier League"],
    ["Matchweek", fixture.gameweek == null ? "Unavailable" : `GW ${fixture.gameweek}`],
    ["Date", date],
    ["Kick-off", time],
    ["Venue", evidence?.metadata?.ground || "Unavailable"],
    ["Attendance", evidence?.metadata?.attendance == null ? "Unavailable" : evidence.metadata.attendance.toLocaleString("en-GB")],
    ["Referee", evidence?.metadata?.referee || "Unavailable"],
  ];

  return (
    <AppShell>
      <article className={styles.dossier}>
        <header className={styles.fixtureHero}>
          <div className={styles.heroEyebrow}>
            <span>Premier League</span>
            <span>{fixture.gameweek == null ? season : `GW ${fixture.gameweek}`}</span>
            <span>{date}</span>
          </div>

          <h1 className={styles.visuallyHidden}>
            {fixture.home_team_name} {fixture.home_score ?? ""} {fixture.away_team_name} {fixture.away_score ?? ""}
          </h1>

          <div className={styles.fixtureStage}>
            <div className={`${styles.clubIdentity} ${styles.clubHome}`}>
              <TeamCrest teamName={fixture.home_team_name} size={72} />
              <div>
                <span>Home</span>
                <strong>{fixture.home_team_name}</strong>
              </div>
            </div>

            <div className={styles.scoreBlock}>
              <div className={styles.score} aria-label={`${fixture.home_team_name} ${fixture.home_score ?? ""} ${fixture.away_team_name} ${fixture.away_score ?? ""}`}>
                <span>{fixture.home_score ?? "—"}</span>
                <i>–</i>
                <span>{fixture.away_score ?? "—"}</span>
              </div>
              <small>{completed ? "Full time" : "Status unavailable"}</small>
            </div>

            <div className={`${styles.clubIdentity} ${styles.clubAway}`}>
              <TeamCrest teamName={fixture.away_team_name} size={72} />
              <div>
                <span>Away</span>
                <strong>{fixture.away_team_name}</strong>
              </div>
            </div>
          </div>

          <div className={styles.heroContext}>
            <span>{evidence?.metadata?.ground || "Venue unavailable"}</span>
            <i aria-hidden="true" />
            <span>{time}</span>
            {evidence?.metadata?.attendance != null ? <><i aria-hidden="true" /><span>{evidence.metadata.attendance.toLocaleString("en-GB")} attendance</span></> : null}
          </div>
        </header>

        <nav className={styles.dossierNav} aria-label="Match dossier sections">
          <a href="#overview">Overview</a>
          <a href="#timeline">Timeline</a>
          <a href="#lineups">Lineups</a>
          <a href="#players">Players</a>
          <a href="#statistics">Statistics</a>
        </nav>

        <div className={styles.dossierBody}>
          <section className={styles.overviewSection} id="overview">
            <div className={styles.sectionIntro}>
              <span>Match dossier</span>
              <h2>Verified fixture context</h2>
              <p>Match identity and available source evidence, presented without filling missing fields.</p>
            </div>

            {evidenceNotice ? (
              <div className={styles.evidenceNotice} role="status">
                <strong>{evidenceNotice.title}</strong>
                <span>{evidenceNotice.detail}</span>
              </div>
            ) : null}

            <div className={styles.metadata} aria-label="Match metadata">
              {metadata.map(([label, value]) => (
                <div className={styles.metadataItem} key={label}>
                  <span>{label}</span>
                  <strong>{value}</strong>
                </div>
              ))}
            </div>
          </section>

          <section className={styles.timelineSection} id="timeline">
            <div className={styles.sectionHeading}>
              <div><span>Chronology</span><h2>Goals & cards</h2></div>
              <small>{timelineEvents.length ? `${timelineEvents.length} verified events` : "No verified event sequence"}</small>
            </div>

            <div className={styles.timeline} aria-label="Goals and cards timeline">
              {timelineEvents.length ? timelineEvents.map((event) => (
                <div key={`${event.event_id ?? "event"}-${event.minute ?? ""}-${event.primary_player.source_player_id ?? ""}`} className={styles.timelineRow}>
                  {event.side === "home" ? <EventCell event={event} /> : <span className={styles.eventEmpty} />}
                  <div className={styles.minute}>{event.minute ?? "—"}</div>
                  {event.side === "away" ? <EventCell event={event} /> : <span className={styles.eventEmpty} />}
                </div>
              )) : (
                <div className={styles.timelineRow}>
                  <span className={styles.eventEmpty} />
                  <div className={styles.minute}>Unavailable</div>
                  <span className={styles.eventEmpty} />
                </div>
              )}
            </div>
          </section>

          <section className={styles.lineupsSection} id="lineups" aria-label="Starting lineups">
            <div className={styles.sectionHeading}>
              <div><span>Tactical view</span><h2>Starting lineups</h2></div>
              <small>Source placement where available · derived layout remains presentation-only</small>
            </div>
            <div className={styles.lineupBoard}>
              <LineupSide
                title={fixture.home_team_name}
                formation={evidence?.formation.home.status === "AVAILABLE" ? evidence.formation.home.value : null}
                manager={managerName(evidence, "home")}
                players={startingPlayers("home")}
                team="home"
                emptyLabel={(evidence?.lineup ?? []).some((row) => row.side === "home") ? "Formation & placement unavailable" : "Lineup & formation unavailable"}
              />
              <LineupSide
                title={fixture.away_team_name}
                formation={evidence?.formation.away.status === "AVAILABLE" ? evidence.formation.away.value : null}
                manager={managerName(evidence, "away")}
                players={startingPlayers("away")}
                team="away"
                emptyLabel={(evidence?.lineup ?? []).some((row) => row.side === "away") ? "Formation & placement unavailable" : "Lineup & formation unavailable"}
              />
            </div>
          </section>

          <section className={styles.playersSection} id="players">
            <div className={styles.sectionHeading}>
              <div><span>Individual output</span><h2>Player performance</h2></div>
              <small>Verified fixture leaders only</small>
            </div>
            <FixturePlayerPerformance season={season} fixtureId={fixtureId} />
          </section>

          <section className={styles.statsSection} id="statistics">
            <div className={styles.sectionHeading}>
              <div><span>Team comparison</span><h2>Match statistics</h2></div>
              <small>{fixture.home_team_name} · {fixture.away_team_name}</small>
            </div>
            <div className={styles.stats}>
              {statRows.map(([home, label, away, homeShare, awayShare, possession]) => (
                <div className={styles.statRow} key={label}>
                  <div className={`${styles.statValue} ${styles.statHome}`}>
                    <strong>{possession ? formatStat(home, "%") : formatStat(home)}</strong>
                    <span className={styles.statTrack} style={{ "--home-share": `${possession ? Number(home ?? 0) : homeShare}%` } as CSSProperties} />
                  </div>
                  <div className={styles.statLabel}>{label}</div>
                  <div className={`${styles.statValue} ${styles.statAway}`}>
                    <span className={styles.statTrack} style={{ "--away-share": `${possession ? Number(away ?? 0) : awayShare}%` } as CSSProperties} />
                    <strong>{possession ? formatStat(away, "%") : formatStat(away)}</strong>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <details className={styles.provenance}>
            <summary>Evidence & limitations</summary>
            <div>
              <p>Fixture ID {fixture.fixture_id} · season {fixture.season}</p>
              {evidence?.limitations?.length ? <ul>{evidence.limitations.map((note, index) => <li key={`${index}-${note}`}>{note}</li>)}</ul> : <p>No additional fixture-evidence limitations were returned.</p>}
            </div>
          </details>
        </div>
      </article>
    </AppShell>
  );
}
