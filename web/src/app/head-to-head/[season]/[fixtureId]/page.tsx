import Link from "next/link";
import { notFound } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import HeadToHeadWorkspace from "./HeadToHeadWorkspace";

type RateSummary = {
  hits: number;
  observed_matches: number;
  eligible_matches: number;
  hit_rate: number | null;
  coverage_status: string;
};

type BetBuilderEntry = {
  id: string;
  side: "home" | "away";
  team_name: string;
  opponent_name: string;
  market_label: string;
  evidence_label: string;
  evidence_index: number | null;
  team_recent: RateSummary;
  opponent_allowance: RateSummary;
};

type Metric = {
  key: string;
  label: string;
  unit: string;
  value: number | null;
  observed_matches: number;
  eligible_matches: number;
};

type TeamProfile = {
  team_name: string;
  persistent_team_code: string;
  sample_size: number;
  current_season_sample_size: number;
  form: Array<"W" | "D" | "L">;
  points: number;
  metrics: Metric[];
};

type PlayerRow = {
  rank: number;
  player_code: string;
  player_name: string;
  position: string;
  appearances: number;
  minutes: number;
  value: number;
};

type Leaderboard = {
  key: string;
  label: string;
  unit: string;
  players: PlayerRow[];
};

type PlayerSide = {
  team_name: string;
  player_count: number;
  fixture_evidence_count: number;
  leaderboards: Leaderboard[];
};

export type H2HPack = {
  pack_version: string;
  fixture: {
    season: string;
    fixture_id: string;
    gameweek: number | null;
    kickoff_time: string | null;
    home_team_name: string;
    away_team_name: string;
  };
  forecast: {
    status: string;
    model?: string;
    control_status?: string;
    training_fixtures?: number;
    expected_goals?: { home: number; away: number };
    probabilities?: Record<string, number>;
    correct_scores?: Array<{ home: number; away: number; probability: number }>;
  };
  profiles: { home: TeamProfile; away: TeamProfile };
  players: { home: PlayerSide; away: PlayerSide };
  betbuilder: {
    status: string;
    threshold_policy: string;
    index_definition: string;
    entries: BetBuilderEntry[];
  };
  data_maturity?: {
    status: string;
    note: string;
  };
  limitations: string[];
};


export const dynamic = "force-dynamic";
const API_BASE = (process.env.NEXT_PUBLIC_FRL_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");
export default async function HeadToHeadPage({ params }: { params: Promise<{ season: string; fixtureId: string }> }) {
  const { season, fixtureId } = await params;
  let response: Response;
  try {
    response = await fetch(`${API_BASE}/api/v1/head-to-head/${encodeURIComponent(season)}/${encodeURIComponent(fixtureId)}`, { cache: "no-store" });
  } catch {
    return <AppShell><h1>Matchup temporarily unavailable</h1><p>The evidence service could not be reached.</p><Link href={`/head-to-head/${season}/${fixtureId}`}>Try again →</Link></AppShell>;
  }
  if (response.status === 404) notFound();
  if (!response.ok) return <AppShell><h1>Evidence temporarily unavailable</h1><p>The fixture has not been classified as missing.</p><Link href={`/head-to-head/${season}/${fixtureId}`}>Try again →</Link></AppShell>;
  const data = await response.json() as H2HPack;
  return <AppShell><HeadToHeadWorkspace data={data} /></AppShell>;
}
