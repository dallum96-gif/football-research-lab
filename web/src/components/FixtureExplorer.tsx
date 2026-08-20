"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import {
  fetchFixtureResearchResult,
  fetchSeasons,
  fetchTeams,
  type FixtureApiRow,
  type FixtureResearchResult,
  type TeamOption,
} from "@/lib/api";

type FixtureViewRow = {
  fixtureId: string;
  season: string;
  date: string;
  opponent: string;
  venue: "Home" | "Away";
  score: string;
  result: "W" | "D" | "L" | "UNPLAYED";
  kickoffTime: string;
  gameweek: number | null;
};

const DEFAULT_SEASON = "2025-26";
const DEFAULT_TEAM = "Arsenal";

type FixtureQuerySet = {
  rows: FixtureViewRow[];
  resultIds: string[];
  descriptions: string[];
  populations: string[];
  provenances: string[];
  includedSeasons: string[];
  excludedSeasons: string[];
};

function formatDate(value: string | null) {
  if (!value) return "—";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value.slice(0, 10);
  return parsed.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function monthLabel(value: string) {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "Fixtures";
  return parsed.toLocaleDateString("en-GB", {
    month: "long",
    year: "numeric",
  });
}

function toViewRow(row: FixtureApiRow, selectedTeam: string): FixtureViewRow {
  const score = row.home_score == null || row.away_score == null
    ? "—"
    : `${row.home_score}–${row.away_score}`;

  return {
    fixtureId: row.fixture_id,
    season: row.season,
    date: formatDate(row.kickoff_time),
    opponent: row.venue === "Home" ? row.away_team_name : row.home_team_name,
    venue: row.venue ?? (row.home_team_name === selectedTeam ? "Home" : "Away"),
    score,
    result: row.result ?? "UNPLAYED",
    kickoffTime: row.kickoff_time ?? "",
    gameweek: row.gameweek,
  };
}

function sortSeasonValue(a: string, b: string) {
  return a.localeCompare(b);
}

function seasonRange(seasons: string[], from: string, to: string) {
  if (!from || !to) return [];
  const low = sortSeasonValue(from, to) <= 0 ? from : to;
  const high = low === from ? to : from;
  return seasons.filter((value) => value >= low && value <= high).sort((a, b) => a.localeCompare(b));
}

async function loadFixtureQuerySet(
  seasonsToLoad: string[],
  selectedPersistentTeamCode: string | null,
  selectedTeam: string,
  filters: { opponent: string; venue: string; result: string },
  signal: AbortSignal,
): Promise<FixtureQuerySet> {
  const result: FixtureQuerySet = {
    rows: [],
    resultIds: [],
    descriptions: [],
    populations: [],
    provenances: [],
    includedSeasons: [],
    excludedSeasons: [],
  };

  const perSeason = await Promise.all(
    seasonsToLoad.map(async (targetSeason) => {
      const options = await fetchTeams(targetSeason, signal);
      const matchingTeam = selectedPersistentTeamCode
        ? options.find((option) => option.persistent_team_code === selectedPersistentTeamCode)
        : options.find((option) => option.display_name === selectedTeam);

      if (!matchingTeam) {
        return { targetSeason, excluded: true } as const;
      }

      const payload = await fetchFixtureResearchResult(
        targetSeason,
        matchingTeam.display_name,
        signal,
        filters,
      );

      return { targetSeason, matchingTeam, payload, excluded: false } as const;
    }),
  );

  for (const item of perSeason) {
    if (item.excluded) {
      result.excludedSeasons.push(item.targetSeason);
      continue;
    }

    result.includedSeasons.push(item.targetSeason);
    result.rows.push(...item.payload.data.map((row) => toViewRow(row, item.matchingTeam.display_name)));
    result.resultIds.push(item.payload.result_id);
    result.descriptions.push(item.payload.description);
    result.populations.push(item.payload.population.label);
    result.provenances.push(`${item.payload.provenance.source} · ${item.payload.provenance.transformation_version}`);
  }

  result.rows.sort((a, b) => {
    const time = a.kickoffTime.localeCompare(b.kickoffTime);
    if (time !== 0) return time;
    return `${a.season}-${a.fixtureId}`.localeCompare(`${b.season}-${b.fixtureId}`);
  });

  return result;
}

export function FixtureExplorer() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const season = searchParams.get("season") ?? DEFAULT_SEASON;
  const team = searchParams.get("team") ?? DEFAULT_TEAM;
  const opponent = searchParams.get("opponent") ?? "";
  const venue = searchParams.get("venue") ?? "";
  const resultFilter = searchParams.get("result") ?? "";
  const view = searchParams.get("view") === "multi" ? "multi" : "single";
  const fromSeason = searchParams.get("from") ?? season;
  const toSeason = searchParams.get("to") ?? season;

  const [seasons, setSeasons] = useState<string[]>([]);
  const [teams, setTeams] = useState<TeamOption[]>([]);
  const [rows, setRows] = useState<FixtureViewRow[]>([]);
  const [resultIds, setResultIds] = useState<string[]>([]);
  const [description, setDescription] = useState("");
  const [populationLabel, setPopulationLabel] = useState("");
  const [provenance, setProvenance] = useState("");
  const [includedSeasons, setIncludedSeasons] = useState<string[]>([]);
  const [excludedSeasons, setExcludedSeasons] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [contextLoading, setContextLoading] = useState(true);
  const [teamMenuOpen, setTeamMenuOpen] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    fetchSeasons(controller.signal)
      .then((payload) => setSeasons(payload.seasons))
      .catch((caught: unknown) => {
        if (caught instanceof DOMException && caught.name === "AbortError") return;
        setError(caught instanceof Error ? caught.message : "Unable to load seasons.");
      });

    return () => controller.abort();
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    setContextLoading(true);

    fetchTeams(season, controller.signal)
      .then((options) => {
        setTeams(options);

        const names = options.map((option) => option.display_name);
        if (names.length && !names.includes(team)) {
          const next = new URLSearchParams(searchParams.toString());
          next.set("team", names[0]);
          next.delete("opponent");
          next.delete("venue");
          next.delete("result");
          next.delete("view");
          next.delete("from");
          next.delete("to");
          router.replace(`${pathname}?${next.toString()}`, { scroll: false });
        }
      })
      .catch((caught: unknown) => {
        if (caught instanceof DOMException && caught.name === "AbortError") return;
        setError(caught instanceof Error ? caught.message : "Unable to load teams.");
        setTeams([]);
      })
      .finally(() => {
        if (!controller.signal.aborted) setContextLoading(false);
      });

    return () => controller.abort();
  }, [season, pathname, router, searchParams, team]);

  useEffect(() => {
    if (!seasons.length && season !== DEFAULT_SEASON) return;
    if (seasons.length && !seasons.includes(season)) {
      const fallback = seasons.includes(DEFAULT_SEASON) ? DEFAULT_SEASON : seasons[0];
      const next = new URLSearchParams(searchParams.toString());
      next.set("season", fallback);
      next.set("team", DEFAULT_TEAM);
      next.delete("opponent");
      next.delete("venue");
      next.delete("result");
      next.delete("view");
      next.delete("from");
      next.delete("to");
      router.replace(`${pathname}?${next.toString()}`, { scroll: false });
    }
  }, [pathname, router, searchParams, season, seasons]);

  useEffect(() => {
    if (!teams.length) return;

    const selectedTeam = teams.find((option) => option.display_name === team);
    const persistentCode = selectedTeam?.persistent_team_code ?? null;
    if (!selectedTeam && team) return;

    const selectedSeasons = view === "multi"
      ? seasonRange(seasons, fromSeason, toSeason)
      : [season];

    if (!selectedSeasons.length) return;

    const controller = new AbortController();
    setLoading(true);
    setError("");

    loadFixtureQuerySet(
      selectedSeasons,
      persistentCode,
      team,
      { opponent, venue, result: resultFilter },
      controller.signal,
    )
      .then((payload) => {
        if (!payload.includedSeasons.length) {
          throw new Error("No verified fixture history is available for that period.");
        }

        setRows(payload.rows);
        setResultIds(payload.resultIds);
        setDescription(
          view === "multi"
            ? `Composed fixture view from ${payload.includedSeasons.length} validated seasonal Research Results.`
            : payload.descriptions[0] ?? "",
        );
        setPopulationLabel(
          view === "multi"
            ? `${team} Premier League fixtures across ${payload.includedSeasons[0]} → ${payload.includedSeasons[payload.includedSeasons.length - 1]}`
            : payload.populations[0] ?? "",
        );
        setProvenance(
          view === "multi"
            ? [...new Set(payload.provenances)].join(" · ")
            : payload.provenances[0] ?? "",
        );
        setIncludedSeasons(payload.includedSeasons);
        setExcludedSeasons(payload.excludedSeasons);
      })
      .catch((caught: unknown) => {
        if (caught instanceof DOMException && caught.name === "AbortError") return;
        setRows([]);
        setResultIds([]);
        setIncludedSeasons([]);
        setExcludedSeasons([]);
        setError(caught instanceof Error ? caught.message : "Unable to load fixture research result.");
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });

    return () => controller.abort();
  }, [fromSeason, opponent, resultFilter, season, seasons, team, teams, toSeason, venue, view]);

  const opponents = useMemo(
    () => [...new Set(rows.map((row) => row.opponent))].sort((a, b) => a.localeCompare(b)),
    [rows],
  );

  const filtered = useMemo(
    () => rows.filter((row) => {
      if (opponent && row.opponent !== opponent) return false;
      if (venue && row.venue !== venue) return false;
      if (resultFilter && row.result !== resultFilter) return false;
      return true;
    }),
    [rows, opponent, venue, resultFilter],
  );

  const record = useMemo(
    () => ({
      wins: filtered.filter((row) => row.result === "W").length,
      draws: filtered.filter((row) => row.result === "D").length,
      losses: filtered.filter((row) => row.result === "L").length,
    }),
    [filtered],
  );

  const grouped = useMemo(() => {
    const groups = new Map<string, FixtureViewRow[]>();
    for (const row of filtered) {
      const group = view === "multi" ? `${row.season} · ${monthLabel(row.kickoffTime)}` : row.kickoffTime ? monthLabel(row.kickoffTime) : "Fixtures";
      const list = groups.get(group) ?? [];
      list.push(row);
      groups.set(group, list);
    }
    return [...groups.entries()];
  }, [filtered, view]);

  function updateContext(key: "season" | "team", value: string) {
    const next = new URLSearchParams(searchParams.toString());
    next.set(key, value);
    next.delete("opponent");
    next.delete("venue");
    next.delete("result");
    if (key === "team") {
      next.delete("view");
      next.delete("from");
      next.delete("to");
    }
    router.replace(`${pathname}?${next.toString()}`, { scroll: false });
    if (key === "team") setTeamMenuOpen(false);
  }

  function updateFilter(key: string, value: string) {
    const next = new URLSearchParams(searchParams.toString());
    if (value) next.set(key, value);
    else next.delete(key);
    const query = next.toString();
    router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }

  function updateView(value: string) {
    const next = new URLSearchParams(searchParams.toString());
    if (value === "multi") {
      next.set("view", "multi");
      next.set("from", fromSeason || season);
      next.set("to", toSeason || season);
    } else {
      next.delete("view");
      next.delete("from");
      next.delete("to");
    }
    next.delete("opponent");
    next.delete("venue");
    next.delete("result");
    router.replace(`${pathname}?${next.toString()}`, { scroll: false });
  }

  function updateRange(key: "from" | "to", value: string) {
    const next = new URLSearchParams(searchParams.toString());
    next.set("view", "multi");
    next.set(key, value);
    router.replace(`${pathname}?${next.toString()}`, { scroll: false });
  }

  function clearFilters() {
    const next = new URLSearchParams();
    next.set("season", season);
    next.set("team", team);
    if (view === "multi") {
      next.set("view", "multi");
      next.set("from", fromSeason);
      next.set("to", toSeason);
    }
    router.replace(`${pathname}?${next.toString()}`, { scroll: false });
  }

  const teamOptions = teams.length ? teams.map((option) => option.display_name) : [team];
  const seasonOptions = seasons.length ? seasons : [season];
  const hasFilters = Boolean(opponent || venue || resultFilter);
  const selectedTeamOption = teams.find((option) => option.display_name === team);
  const rangeOptions = seasonOptions;
  const range = view === "multi" ? seasonRange(seasons, fromSeason, toSeason) : [season];

  return (
    <>
      <section className="frl-page-heading">
        <div className="frl-heading-copy">
          <div className="frl-eyebrow">Fixtures</div>
          <div className="frl-heading-row">
            <div className="frl-team-title-control">
              <button
                type="button"
                className={`frl-team-title-button${teamMenuOpen ? " is-open" : ""}`}
                aria-label={`Change team from ${team}`}
                aria-expanded={teamMenuOpen}
                disabled={contextLoading || !!error}
                onClick={() => setTeamMenuOpen((open) => !open)}
              >
                <h1 className="frl-title">{team}</h1>
                <span className="frl-team-title-chevron" aria-hidden="true">⌄</span>
              </button>

              {teamMenuOpen && (
                <div className="frl-team-menu" role="menu" aria-label="Choose team">
                  {teamOptions.map((value) => (
                    <button
                      key={value}
                      type="button"
                      role="menuitem"
                      className={value === team ? "is-active" : ""}
                      onClick={() => updateContext("team", value)}
                    >
                      {value}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
          <div className="frl-context">Premier League · fixture history</div>
        </div>

        <div className="frl-context-actions">
          <div className="frl-context-control frl-context-control-season">
            <span>Season</span>
            <select
              id="fixture-season"
              value={season}
              onChange={(event) => updateContext("season", event.target.value)}
              disabled={contextLoading || !!error}
              aria-label="Season"
            >
              {seasonOptions.map((value) => <option key={value}>{value}</option>)}
            </select>
            <span className="frl-context-chevron" aria-hidden="true">⌄</span>
          </div>

          <div className="frl-record-chip" aria-label="Fixture record">
            <strong>{filtered.length}</strong>
            <span>matches</span>
            <span className="frl-record-positive">{record.wins} W</span>
            <span>{record.draws} D</span>
            <span className="frl-record-negative">{record.losses} L</span>
          </div>
        </div>
      </section>

      <div className="frl-rule" />

      <section className="frl-filter-bar" aria-label="Fixture exploration">
        <div className="frl-filter-heading">
          <span>Explore fixtures</span>
          <strong>{hasFilters ? "Filtered view" : view === "multi" ? `${range.length} seasons` : "All fixtures"}</strong>
        </div>

        <div className="frl-context-control">
          <span>View</span>
          <select value={view} onChange={(event) => updateView(event.target.value)} disabled={loading || !!error} aria-label="Fixture view">
            <option value="single">Single season</option>
            <option value="multi">Multiple seasons</option>
          </select>
          <span className="frl-context-chevron" aria-hidden="true">⌄</span>
        </div>

        {view === "multi" && (
          <>
            <div className="frl-context-control">
              <span>From</span>
              <select value={fromSeason} onChange={(event) => updateRange("from", event.target.value)} disabled={loading || !!error} aria-label="From season">
                {rangeOptions.map((value) => <option key={value}>{value}</option>)}
              </select>
              <span className="frl-context-chevron" aria-hidden="true">⌄</span>
            </div>

            <div className="frl-context-control">
              <span>To</span>
              <select value={toSeason} onChange={(event) => updateRange("to", event.target.value)} disabled={loading || !!error} aria-label="To season">
                {rangeOptions.map((value) => <option key={value}>{value}</option>)}
              </select>
              <span className="frl-context-chevron" aria-hidden="true">⌄</span>
            </div>
          </>
        )}

        <div className="frl-context-control">
          <span>Opponent</span>
          <select value={opponent} onChange={(event) => updateFilter("opponent", event.target.value)} disabled={loading || !!error} aria-label="Opponent">
            <option value="">All opponents</option>
            {opponents.map((value) => <option key={value}>{value}</option>)}
          </select>
          <span className="frl-context-chevron" aria-hidden="true">⌄</span>
        </div>

        <div className="frl-context-control">
          <span>Venue</span>
          <select value={venue} onChange={(event) => updateFilter("venue", event.target.value)} disabled={loading || !!error} aria-label="Venue">
            <option value="">Home + Away</option>
            <option>Home</option>
            <option>Away</option>
          </select>
          <span className="frl-context-chevron" aria-hidden="true">⌄</span>
        </div>

        <div className="frl-context-control">
          <span>Result</span>
          <select value={resultFilter} onChange={(event) => updateFilter("result", event.target.value)} disabled={loading || !!error} aria-label="Result">
            <option value="">All results</option>
            <option>W</option>
            <option>D</option>
            <option>L</option>
            <option>UNPLAYED</option>
          </select>
          <span className="frl-context-chevron" aria-hidden="true">⌄</span>
        </div>

        <div className="frl-filter-summary">
          <span>{loading ? "Loading research result…" : `${filtered.length} fixtures`}</span>
          {hasFilters && <button type="button" onClick={clearFilters}>Clear</button>}
        </div>
      </section>

      {excludedSeasons.length > 0 && !loading && (
        <div className="frl-research-note">
          <strong>Coverage note.</strong> No verified team identity is present for {excludedSeasons.length} selected season{excludedSeasons.length === 1 ? "" : "s"}; those seasons are excluded rather than inferred.
        </div>
      )}

      {error ? (
        <div className="frl-empty-state">
          <strong>Fixture research result unavailable.</strong>
          <div>{error}</div>
          <small>The page has failed closed rather than falling back to fabricated or stale fixture data.</small>
        </div>
      ) : loading ? (
        <div className="frl-empty-state">Loading the validated fixture research result…</div>
      ) : grouped.length === 0 ? (
        <div className="frl-empty-state">
          <strong>No fixtures match those filters.</strong>
          <button type="button" onClick={clearFilters}>Clear filters</button>
        </div>
      ) : (
        <section className="frl-fixture-list" aria-label="Fixture results">
          {grouped.map(([group, groupRows]) => (
            <div className="frl-fixture-month" key={group}>
              <div className="frl-month-heading"><span />{group}</div>
              <div className="frl-fixture-header">
                <span>Date</span>
                <span>Opponent</span>
                <span>Venue</span>
                <span>Score</span>
                <span>Result</span>
              </div>
              {groupRows.map((row) => (
                <Link
                  className="frl-fixture-row"
                  href={`/fixtures/${row.season}/${row.fixtureId}`}
                  key={`${row.season}-${row.fixtureId}`}
                >
                  <span className="frl-fixture-date">
                    {row.date}
                    {row.gameweek ? <small>GW {row.gameweek}</small> : null}
                  </span>
                  <span className="frl-fixture-opponent">
                    <i aria-hidden="true" />
                    {row.opponent}
                  </span>
                  <span className="frl-fixture-venue">{row.venue}</span>
                  <span className="frl-fixture-score">{row.score}</span>
                  <span className={`frl-fixture-result frl-result-${row.result.toLowerCase()}`}>{row.result}</span>
                </Link>
              ))}
            </div>
          ))}
        </section>
      )}

      <div className="frl-research-note">
        <strong>Research result.</strong> {description}
        <br />
        <span>{populationLabel}</span>
        <br />
        <span>Validated seasonal results: {resultIds.length}</span>
        <br />
        <span>Included seasons: {includedSeasons.length ? includedSeasons.join(", ") : "—"}</span>
        <br />
        <span>Provenance: {provenance}</span>
      </div>
    </>
  );
}
