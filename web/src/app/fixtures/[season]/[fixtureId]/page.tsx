import { notFound } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { MatchResultExperience } from "./MatchResultExperience";

type FixtureDetailProps = {
  params: Promise<{
    season: string;
    fixtureId: string;
  }>;
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
  const { date, time } = dateParts(detail.fixture.kickoff_time);

  return (
    <AppShell>
      <MatchResultExperience
        season={season}
        fixtureId={fixtureId}
        fixture={detail.fixture}
        stats={detail.stats}
        evidence={evidence}
        date={date}
        time={time}
      />
    </AppShell>
  );
}
