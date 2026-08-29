import type { CSSProperties } from "react";
import { notFound } from "next/navigation";
import { AppShell } from "@/components/AppShell";
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
  if (!response.ok) {
    return { ok: false, status: response.status };
  }
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
  const managerStyle: CSSProperties = {
    position: "absolute",
    top: "-.35rem",
    [team === "home" ? "right" : "left"]: "15%",
    color: "var(--frl-muted-soft)",
    fontSize: ".5rem",
    fontWeight: 700,
    letterSpacing: ".1em",
    lineHeight: 1,
    textTransform: "uppercase",
    whiteSpace: "nowrap",
    zIndex: 2,
    textAlign: team === "home" ? "right" : "left",
  };

  return (
    <div className={`${styles.lineupSide} ${team === "home" ? styles.lineupHome : styles.lineupAway}`}>
      <div className={styles.lineupSideHeader}>
        <span>{title}</span>
        <span>{formation ?? "—"}</span>
      </div>
      <div className={styles.tacticalBoard}>
        <div className={styles.boardHalfLine} />
        <div className={styles.boardCenterLine} />
        <span style={managerStyle}>
          {manager}
          {formation ? ` · ${formation}` : ""}
        </span>
        {placedPlayers.length ? placedPlayers.map((player) => {
          return (
            <div
              className={styles.playerNode}
              key={`${player.name}-${player.number ?? ""}`}
              style={{ left: `${player.x}%`, top: `${player.y}%` } as CSSProperties}
              title={`${player.name} · ${player.role}`}
            >
              <span className={styles.playerDot} />
              <span className={styles.playerRole}>{player.role}</span>
              <span className={styles.playerName}>{player.name}</span>
            </div>
          );
        }) : <span className={styles.lineupUnavailable}>{emptyLabel}</span>}
      </div>
    </div>
  );
}

function eventLabel(event: FixtureEvent): string {
  const primary = event.primary_player.name || "Player unavailable";
  if (event.type === "goal") {
    return event.assist?.name ? `${primary} — ${event.assist.name} assist` : primary;
  }
  return primary;
}

function EventCell({ event }: { event: FixtureEvent }) {
  const isGoal = event.type === "goal";
  const isRed = event.detail.card_type?.toUpperCase() === "RED";
  const icon = isGoal ? "⚽" : "■";
  const className = isGoal ? styles.eventGoal : isRed ? styles.eventRed : styles.eventCard;

  return (
    <div className={`${styles.event} ${event.side === "home" ? styles.eventHome : styles.eventAway} ${className}`}>
      <span className={styles.icon}>{icon}</span>
      <span>{eventLabel(event)}</span>
    </div>
  );
}

function FrlBrand() {
  return (
    <div className={styles.frlBrand} aria-label="Football Research Laboratory">
      <svg className={styles.frlMascot} viewBox="0 0 84 52" role="img" aria-hidden="true">
        <circle cx="42" cy="29" r="22" fill="var(--frl-surface)" stroke="currentColor" strokeWidth="3" />
        <path d="M25 16 31 11M59 16 53 11M20 34 11 39M64 34 73 39" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
        <path d="M32 23 38 19 42 22 46 18 52 23 47 30 42 33 36 30Z" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" opacity=".38" />
        <circle cx="31.5" cy="25" r="4.2" fill="var(--frl-surface)" stroke="currentColor" strokeWidth="1.9" />
        <circle cx="31.5" cy="25" r="1.55" fill="currentColor" />
        <circle cx="52.5" cy="25" r="4.2" fill="var(--frl-surface)" stroke="currentColor" strokeWidth="1.9" />
        <circle cx="52.5" cy="25" r="1.55" fill="currentColor" />
        <path d="M35.7 25H48.3" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" />
        <path d="M34 38Q42 44 50 38" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
      </svg>
      <div className={styles.frlWordmark}>FRL</div>
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

  const [possessionHome, possessionAway] = stats
    ? [stats.home_possession, stats.away_possession]
    : [null, null];

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
    ["Matchweek", fixture.gameweek == null ? "Unavailable" : String(fixture.gameweek)],
    ["Date", date],
    ["Kick-off", time],
    ["Venue", evidence?.metadata?.ground || "Unavailable"],
    ["Attendance", evidence?.metadata?.attendance == null ? "Unavailable" : evidence.metadata.attendance.toLocaleString("en-GB")],
    ["Referee", evidence?.metadata?.referee || "Unavailable"],
  ];

  return (
    <AppShell>
      <div className={styles.overview}>
        <header className={styles.pageHeader}>
          <div className={styles.pageHeaderCompetition}>Premier League</div>
          <div className={styles.pageHeaderDate}>{date}</div>
          <FrlBrand />
        </header>

        <section className={styles.matchHeader} aria-label="Match result">
          <div className={styles.teams}>
            <div className={`${styles.team} ${styles.teamHome}`}>
              <span className={styles.teamName}>{fixture.home_team_name}</span>
              <span className={styles.kit} aria-hidden="true">
                <span className={styles.kitSleeve} />
                <span className={styles.kitSleeveRight} />
                <span className={styles.kitBody} />
              </span>
            </div>

            <div className={styles.scoreBlock}>
              <div className={styles.score} aria-label={`${fixture.home_team_name} ${fixture.home_score ?? ""} ${fixture.away_team_name} ${fixture.away_score ?? ""}`}>
                <span className={styles.scoreNumber}>{fixture.home_score ?? "—"}</span>
                <span className={styles.scoreDash}>–</span>
                <span className={styles.scoreNumber}>{fixture.away_score ?? "—"}</span>
              </div>
              <div className={styles.status}>
                {fixture.home_score != null && fixture.away_score != null ? "Full time" : "Fixture status unavailable"}
              </div>
            </div>

            <div className={`${styles.team} ${styles.teamAway}`}>
              <span className={styles.kit} aria-hidden="true">
                <span className={styles.kitSleeve} />
                <span className={styles.kitSleeveRight} />
                <span className={styles.kitBody} />
              </span>
              <span className={styles.teamName}>{fixture.away_team_name}</span>
            </div>
          </div>

          {evidenceNotice ? (
            <div className={styles.evidenceNotice} role="status">
              <span className={styles.evidenceNoticeTitle}>{evidenceNotice.title}</span>
              <span>{evidenceNotice.detail}</span>
            </div>
          ) : null}

          <div className={styles.timelineWrap}>
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
                  <div className={styles.minute}>Events unavailable</div>
                  <span className={styles.eventEmpty} />
                </div>
              )}
            </div>
          </div>
        </section>

        <section className={styles.lineupSection} aria-label="Starting lineups">
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
        </section>

        <FixturePlayerPerformance season={season} fixtureId={fixtureId} />

        <section className={styles.statsSection}>
          <div className={styles.sectionTitle}>
            <span className={styles.sectionArrow} aria-hidden="true">←</span>
            <h2>Match statistics</h2>
            <span className={styles.sectionArrow} aria-hidden="true">→</span>
          </div>
          <div className={styles.stats}>
            {statRows.map(([home, label, away, homeShare, awayShare, possession]) => (
              <div className={styles.statRow} key={label}>
                <div className={`${styles.statValue} ${styles.statHome}`}>
                  <span>{possession ? formatStat(home, "%") : formatStat(home)}</span>
                  <span className={styles.statTrack} style={{ "--home-share": `${possession ? Number(home ?? 0) : homeShare}%` } as CSSProperties} />
                </div>
                <div className={styles.statLabel}>{label}</div>
                <div className={`${styles.statValue} ${styles.statAway}`}>
                  <span className={styles.statTrack} style={{ "--away-share": `${possession ? Number(away ?? 0) : awayShare}%` } as CSSProperties} />
                  <span>{possession ? formatStat(away, "%") : formatStat(away)}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className={styles.metadata} aria-label="Match metadata">
          {metadata.map(([label, value]) => (
            <div className={styles.metadataItem} key={label}>
              <span className={styles.metadataLabel}>{label}</span>
              <span className={styles.metadataValue}>{value}</span>
            </div>
          ))}
        </section>
      </div>
    </AppShell>
  );
}
