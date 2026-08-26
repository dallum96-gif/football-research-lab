export type CanonicalFixtureRef = {
  season: string;
  fixtureId: string;
};

export type CanonicalTeamRef = {
  persistentTeamCode: string;
  displayName: string;
  season?: string;
  localTeamId?: string;
};

export type ResearchResult<T> = {
  resultId: string;
  title: string;
  description?: string;
  data: T[];
  population: {
    label: string;
    sampleSize: number;
    filters: Record<string, string | number | boolean>;
    exclusions?: string[];
  };
  scope: {
    competition?: string;
    season?: string;
    asOf?: string;
  };
  references: {
    fixtures?: CanonicalFixtureRef[];
    teams?: CanonicalTeamRef[];
  };
  provenance: {
    source: string;
    transformationVersion: string;
  };
  methodology: {
    metricVersion: string;
    notes: string[];
  };
  limitations: string[];
};

export type PositionPoint = {
  fixtureId: string;
  date: string;
  opponent: string;
  position: number;
};

export type FixtureRow = {
  fixtureId: string;
  date: string;
  opponent: string;
  venue: "Home" | "Away";
  score: string;
  result: "W" | "D" | "L";
  positionAfter: number;
};

export function demoResearchResult(): ResearchResult<PositionPoint> {
  return {
    resultId: "demo-team-position-arsenal-2025-26",
    title: "Arsenal position trajectory",
    description: "Foundation-spike example of one Research Result powering multiple views.",
    data: [
      { fixtureId: "101", date: "16 Aug", opponent: "Wolves", position: 1 },
      { fixtureId: "102", date: "23 Aug", opponent: "Tottenham", position: 2 },
      { fixtureId: "103", date: "31 Aug", opponent: "Liverpool", position: 2 },
      { fixtureId: "104", date: "13 Sep", opponent: "Newcastle", position: 1 },
      { fixtureId: "105", date: "20 Sep", opponent: "Chelsea", position: 1 },
      { fixtureId: "106", date: "27 Sep", opponent: "Everton", position: 2 },
      { fixtureId: "107", date: "4 Oct", opponent: "Brighton", position: 1 },
    ],
    population: {
      label: "Arsenal Premier League fixtures through 4 October 2025",
      sampleSize: 7,
      filters: { team: "Arsenal", competition: "Premier League" },
    },
    scope: {
      competition: "Premier League",
      season: "2025-26",
      asOf: "2025-10-04T23:59:59Z",
    },
    references: {
      fixtures: [
        { season: "2025-26", fixtureId: "101" },
        { season: "2025-26", fixtureId: "102" },
        { season: "2025-26", fixtureId: "103" },
        { season: "2025-26", fixtureId: "104" },
        { season: "2025-26", fixtureId: "105" },
        { season: "2025-26", fixtureId: "106" },
        { season: "2025-26", fixtureId: "107" },
      ],
      teams: [{ persistentTeamCode: "ARS", displayName: "Arsenal" }],
    },
    provenance: {
      source: "demo research-result fixture feed",
      transformationVersion: "foundation-spike-v1",
    },
    methodology: {
      metricVersion: "position-after-fixture-v1",
      notes: ["Demo only; the production query seam will supply trusted results."],
    },
    limitations: ["This foundation spike intentionally uses static demo data."],
  };
}

export function fixtureRowsFromResult(result: ResearchResult<PositionPoint>): FixtureRow[] {
  return result.data.map((point, index) => ({
    fixtureId: point.fixtureId,
    date: point.date,
    opponent: point.opponent,
    venue: index % 2 === 0 ? "Away" : "Home",
    score: index % 3 === 0 ? "2–0" : index % 2 === 0 ? "1–1" : "2–1",
    result: point.position <= 1 ? "W" : index % 2 === 0 ? "D" : "L",
    positionAfter: point.position,
  }));
}
