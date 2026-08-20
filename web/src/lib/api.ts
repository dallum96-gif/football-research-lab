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

export type TeamOption = {
  persistent_team_code: string | null;
  display_name: string;
  season: string;
  local_team_id: string;
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

async function getJson<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    signal,
    cache: "no-store",
  });

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

  return response.json() as Promise<T>;
}

export function fetchSeasons(signal?: AbortSignal): Promise<{ seasons: string[] }> {
  return getJson<{ seasons: string[] }>("/api/v1/seasons", signal);
}

export function fetchTeams(season: string, signal?: AbortSignal): Promise<TeamOption[]> {
  return getJson<TeamOption[]>(`/api/v1/teams/${encodeURIComponent(season)}`, signal);
}

export async function fetchFixtureResearchResult(
  season: string,
  team: string,
  signal?: AbortSignal,
  filters?: { opponent?: string; venue?: string; result?: string },
): Promise<FixtureResearchResult> {
  const params = new URLSearchParams({ team });
  if (filters?.opponent) params.set("opponent", filters.opponent);
  if (filters?.venue) params.set("venue", filters.venue.toLowerCase());
  if (filters?.result) params.set("result", filters.result);

  return getJson<FixtureResearchResult>(
    `/api/v1/fixtures/${encodeURIComponent(season)}?${params.toString()}`,
    signal,
  );
}
