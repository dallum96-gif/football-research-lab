import type { ResearchResult } from "@/lib/research-result";

export type FixtureApiRow = {
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
  venue: "Home" | "Away" | null;
  result: "W" | "D" | "L" | "UNPLAYED" | null;
};

export type FixtureResearchResult = {
  result_id: string;
  title: string;
  description: string;
  data: FixtureApiRow[];
  population: {
    label: string;
    sample_size: number;
    filters: Record<string, string | number | boolean>;
    exclusions?: string[];
  };
  scope: {
    competition?: string;
    season?: string;
    as_of?: string | null;
  };
  references: {
    fixtures?: Array<{ season: string; fixture_id: string }>;
  };
  provenance: {
    source: string;
    transformation_version: string;
  };
  methodology: {
    metric_version: string;
    notes: string[];
  };
  limitations: string[];
};

const API_BASE = process.env.NEXT_PUBLIC_FRL_API_URL ?? "http://127.0.0.1:8000";

export async function fetchFixtureResearchResult(
  season: string,
  team: string,
  signal?: AbortSignal,
): Promise<FixtureResearchResult> {
  const params = new URLSearchParams({ team });
  const response = await fetch(
    `${API_BASE}/api/v1/fixtures/${encodeURIComponent(season)}?${params.toString()}`,
    { signal, cache: "no-store" },
  );

  if (!response.ok) {
    let detail = `FRL API returned ${response.status}`;
    try {
      const body = await response.json();
      if (typeof body?.detail === "string") detail = body.detail;
    } catch {
      // Keep the HTTP status error when the response is not JSON.
    }
    throw new Error(detail);
  }

  return response.json() as Promise<FixtureResearchResult>;
}
