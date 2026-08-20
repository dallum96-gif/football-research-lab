"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import {
  fetchFixtureResearchResult,
  fetchSeasons,
  fetchTeams,
  type FixtureApiRow,
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

function toViewRow(row: FixtureApiRow): FixtureViewRow {
  const score = row.home_score == null || row.away_score == null
    ? "—"
    : `${row.home_score}–${row.away_score}`;

  return {
    fixtureId: row.fixture_id,
    season: row.season,
    date: formatDate(row.kickoff_time),
    opponent: row.venue === "Home" ? row.away_team_name : row.home_team_name,
    venue: row.venue ?? (row.home_team_name === DEFAULT_TEAM ? "Home" : "Away"),
    score,
    result: row.result ?? "UNPLAYED",
    kickoffTime: row.kickoff_time ?? "",
    gameweek: row.gameweek,
  };
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

  const [seasons, setSeasons] = useState<string[]>([]);
  const [teams, setTeams] = useState<string[]>([]);
  const [rows, setRows] = useState<FixtureViewRow[]>([]);
  const [resultId, setResultId] = useState("");
  const [description, setDescription] = useState("");
  const [populationLabel, setPopulationLabel] = useState("");
  const [provenance, setProvenance] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [contextLoading, setContextLoading] = useState(true);

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
        const names = options.map((option) => option.display_name);
        setTeams(names);

        if (names.length && !names.includes(team)) {
          const next = new URLSearchParams(searchParams.toString());
          next.set("team", names[0]);
          next.delete("opponent");
          next.delete("venue");
          next.delete("result");
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
      router.replace(`${pathname}?${next.toString()}`, { scroll: false });
    }
  }, [pathname, router, searchParams, season, seasons]);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError("");

    fetchFixtureResearchResult(season, team, controller.signal)
      .then((payload) => {
        setRows(payload.data.map(toViewRow));
        setResultId(payload.result_id);
        setDescription(payload.description);
        setPopulationLabel(payload.population.label);
        setProvenance(`${payload.provenance.source} · ${payload.provenance.transformation_version}`);
      })
      .catch((caught: unknown) => {
        if (caught instanceof DOMException && caught.name === "AbortError") return;
        setRows([]);
        setError(caught instanceof Error ? caught.message : "Unable to load fixture research result.");
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });

    return () => controller.abort();
  }, [season, team]);

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
      const group = row.kickoffTime ? monthLabel(row.kickoffTime) : "Fixtures";
      const list = groups.get(group) ?? [];
      list.push(row);
      groups.set(group, list);
    }
    return [...groups.entries()];
  }, [filtered]);

  function updateContext(key: "season" | "team", value: string) {
    const next = new URLSearchParams(searchParams.toString());
    next.set(key, value);
    next.delete("opponent");
    next.delete("venue");
    next.delete("result");
    router.replace(`${pathname}?${next.toString()}`, { scroll: false });
  }

  function updateFilter(key: string, value: string) {
    const next = new URLSearchParams(searchParams.toString());
    if (value) next.set(key, value);
    else next.delete(key);
    const query = next.toString();
    router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }

  function clearFilters() {
    const next = new URLSearchParams();
    next.set("season", season);
    next.set("team", team);
    router.replace(`${pathname}?${next.toString()}`, { scroll: false });
  }

  const teamOptions = teams.length ? teams : [team];
  const seasonOptions = seasons.length ? seasons : [season];
  const hasFilters = Boolean(opponent || venue || resultFilter);

  return (
    <>
      <section className="frl-page-heading">
        <div>
          <div className="frl-eyebrow">Fixtures</div>
          <h1 className="frl-title">{team}</h1>
          <div className="frl-context">Premier League · {season}</div>
        </div>

        <div className="frl-context-actions">
          <div className="frl-context-control">
            <label htmlFor="fixture-team">Team</label>
            <select
              id="fixture-team"
              value={team}
              onChange={(event) => updateContext("team", event.target.value)}
              disabled={contextLoading || !!error}
            >
              {teamOptions.map((value) => <option key={value}>{value}</option>)}
            </select>
          </div>

          <div className="frl-context-control frl-context-control-season">
            <label htmlFor="fixture-season">Season</label>
            <select
              id="fixture-season"
              value={season}
              onChange={(event) => updateContext("season", event.target.value)}
              disabled={contextLoading || !!error}
            >
              {seasonOptions.map((value) => <option key={value}>{value}</option>)}
            </select>
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

      <section className="frl-filter-bar" aria-label="Fixture filters">
        <div className="frl-filter-heading">
          <span>Explore</span>
          <strong>{hasFilters ? "Filtered fixtures" : "All fixtures"}</strong>
        </div>

        <label>
          <span>Opponent</span>
          <select value={opponent} onChange={(event) => updateFilter("opponent", event.target.value)} disabled={loading || !!error}>
            <option value="">All opponents</option>
            {opponents.map((value) => <option key={value}>{value}</option>)}
          </select>
        </label>

        <label>
          <span>Venue</span>
          <select value={venue} onChange={(event) => updateFilter("venue", event.target.value)} disabled={loading || !!error}>
            <option value="">All venues</option>
            <option>Home</option>
            <option>Away</option>
          </select>
        </label>

        <label>
          <span>Result</span>
          <select value={resultFilter} onChange={(event) => updateFilter("result", event.target.value)} disabled={loading || !!error}>
            <option value="">All results</option>
            <option>W</option>
            <option>D</option>
            <option>L</option>
            <option>UNPLAYED</option>
          </select>
        </label>

        <div className="frl-filter-summary">
          <span>{loading ? "Loading research result…" : `${filtered.length} of ${rows.length} fixtures`}</span>
          {hasFilters && (
            <button type="button" onClick={clearFilters}>Clear</button>
          )}
        </div>
      </section>

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
        <span>Result: {resultId}</span>
        <br />
        <span>Provenance: {provenance}</span>
      </div>
    </>
  );
}
