"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { TeamCrest } from "@/components/TeamCrest";
import {
  fetchFixtureResearchResult,
  fetchSeasons,
  fetchTeams,
  type FixtureApiRow,
  type TeamOption,
} from "@/lib/api";
import styles from "./FixturesExperience.module.css";

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

type FixtureQuerySet = {
  rows: FixtureViewRow[];
  resultIds: string[];
  descriptions: string[];
  populations: string[];
  provenances: string[];
  includedSeasons: string[];
  excludedSeasons: string[];
};

const DEFAULT_SEASON = "2025-26";
const DEFAULT_TEAM = "Arsenal";

function formatDate(value: string | null) {
  if (!value) return "—";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value.slice(0, 10);
  return parsed.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
}

function monthLabel(value: string) {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "Fixtures";
  return parsed.toLocaleDateString("en-GB", { month: "long", year: "numeric" });
}

function monthNavLabel(group: string) {
  const part = group.split(" · ").at(-1) ?? group;
  return part.split(" ")[0]?.slice(0, 3).toUpperCase() ?? part;
}

function groupId(group: string) {
  return `fixtures-${group.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")}`;
}

function toViewRow(row: FixtureApiRow, selectedTeam: string): FixtureViewRow {
  return {
    fixtureId: row.fixture_id,
    season: row.season,
    date: formatDate(row.kickoff_time),
    opponent: row.venue === "Home" ? row.away_team_name : row.home_team_name,
    venue: row.venue ?? (row.home_team_name === selectedTeam ? "Home" : "Away"),
    score: row.home_score == null || row.away_score == null ? "—" : `${row.home_score}–${row.away_score}`,
    result: row.result ?? "UNPLAYED",
    kickoffTime: row.kickoff_time ?? "",
    gameweek: row.gameweek,
  };
}

function seasonRange(seasons: string[], from: string, to: string) {
  if (!from || !to) return [];
  const low = from.localeCompare(to) <= 0 ? from : to;
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
    rows: [], resultIds: [], descriptions: [], populations: [], provenances: [], includedSeasons: [], excludedSeasons: [],
  };

  const perSeason = await Promise.all(seasonsToLoad.map(async (targetSeason) => {
    const options = await fetchTeams(targetSeason, signal);
    const matchingTeam = selectedPersistentTeamCode
      ? options.find((option) => option.persistent_team_code === selectedPersistentTeamCode)
      : options.find((option) => option.display_name === selectedTeam);
    if (!matchingTeam) return { targetSeason, excluded: true } as const;
    const payload = await fetchFixtureResearchResult(targetSeason, matchingTeam.display_name, signal, filters);
    return { targetSeason, matchingTeam, payload, excluded: false } as const;
  }));

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

  result.rows.sort((a, b) => b.kickoffTime.localeCompare(a.kickoffTime) || `${b.season}-${b.fixtureId}`.localeCompare(`${a.season}-${a.fixtureId}`));
  return result;
}

export function FixturesExperience() {
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
  const [refineOpen, setRefineOpen] = useState(false);

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
          next.delete("opponent"); next.delete("venue"); next.delete("result"); next.delete("view"); next.delete("from"); next.delete("to");
          router.replace(`${pathname}?${next.toString()}`, { scroll: false });
        }
      })
      .catch((caught: unknown) => {
        if (caught instanceof DOMException && caught.name === "AbortError") return;
        setError(caught instanceof Error ? caught.message : "Unable to load teams.");
        setTeams([]);
      })
      .finally(() => { if (!controller.signal.aborted) setContextLoading(false); });
    return () => controller.abort();
  }, [season, pathname, router, searchParams, team]);

  useEffect(() => {
    if (!seasons.length && season !== DEFAULT_SEASON) return;
    if (seasons.length && !seasons.includes(season)) {
      const fallback = seasons.includes(DEFAULT_SEASON) ? DEFAULT_SEASON : seasons[0];
      const next = new URLSearchParams(searchParams.toString());
      next.set("season", fallback); next.set("team", DEFAULT_TEAM);
      next.delete("opponent"); next.delete("venue"); next.delete("result"); next.delete("view"); next.delete("from"); next.delete("to");
      router.replace(`${pathname}?${next.toString()}`, { scroll: false });
    }
  }, [pathname, router, searchParams, season, seasons]);

  useEffect(() => {
    if (!teams.length) return;
    const selectedTeam = teams.find((option) => option.display_name === team);
    if (!selectedTeam && team) return;
    const selectedSeasons = view === "multi" ? seasonRange(seasons, fromSeason, toSeason) : [season];
    if (!selectedSeasons.length) return;

    const controller = new AbortController();
    setLoading(true); setError("");
    loadFixtureQuerySet(
      selectedSeasons,
      selectedTeam?.persistent_team_code ?? null,
      team,
      { opponent, venue, result: resultFilter },
      controller.signal,
    )
      .then((payload) => {
        if (!payload.includedSeasons.length) throw new Error("No verified fixture history is available for that period.");
        setRows(payload.rows); setResultIds(payload.resultIds);
        setDescription(view === "multi" ? `Composed fixture view from ${payload.includedSeasons.length} validated seasonal Research Results.` : payload.descriptions[0] ?? "");
        setPopulationLabel(view === "multi" ? `${team} Premier League fixtures across ${payload.includedSeasons[0]} → ${payload.includedSeasons[payload.includedSeasons.length - 1]}` : payload.populations[0] ?? "");
        setProvenance(view === "multi" ? [...new Set(payload.provenances)].join(" · ") : payload.provenances[0] ?? "");
        setIncludedSeasons(payload.includedSeasons); setExcludedSeasons(payload.excludedSeasons);
      })
      .catch((caught: unknown) => {
        if (caught instanceof DOMException && caught.name === "AbortError") return;
        setRows([]); setResultIds([]); setIncludedSeasons([]); setExcludedSeasons([]);
        setError(caught instanceof Error ? caught.message : "Unable to load fixture research result.");
      })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [fromSeason, opponent, resultFilter, season, seasons, team, teams, toSeason, venue, view]);

  useEffect(() => {
    if (!refineOpen) return;
    const onKey = (event: KeyboardEvent) => { if (event.key === "Escape") setRefineOpen(false); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [refineOpen]);

  const filtered = useMemo(() => rows.filter((row) => {
    if (opponent && row.opponent !== opponent) return false;
    if (venue && row.venue !== venue) return false;
    if (resultFilter && row.result !== resultFilter) return false;
    return true;
  }), [rows, opponent, venue, resultFilter]);

  const opponents = useMemo(() => [...new Set(rows.map((row) => row.opponent))].sort((a, b) => a.localeCompare(b)), [rows]);
  const record = useMemo(() => ({
    wins: filtered.filter((row) => row.result === "W").length,
    draws: filtered.filter((row) => row.result === "D").length,
    losses: filtered.filter((row) => row.result === "L").length,
  }), [filtered]);

  const grouped = useMemo(() => {
    const groups = new Map<string, FixtureViewRow[]>();
    for (const row of filtered) {
      const group = view === "multi" ? `${row.season} · ${monthLabel(row.kickoffTime)}` : row.kickoffTime ? monthLabel(row.kickoffTime) : "Fixtures";
      groups.set(group, [...(groups.get(group) ?? []), row]);
    }
    return [...groups.entries()];
  }, [filtered, view]);

  const seasonOptions = seasons.length ? seasons : [season];
  const teamOptions = teams.length ? teams.map((option) => option.display_name) : [team];
  const rangeOptions = seasonOptions;
  const hasFilters = Boolean(opponent || venue || resultFilter || view === "multi");

  function replaceParams(next: URLSearchParams) {
    const query = next.toString();
    router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }

  function updateContext(key: "season" | "team", value: string) {
    const next = new URLSearchParams(searchParams.toString());
    next.set(key, value);
    next.delete("opponent"); next.delete("venue"); next.delete("result");
    if (key === "team") { next.delete("view"); next.delete("from"); next.delete("to"); }
    replaceParams(next);
  }

  function updateFilter(key: string, value: string) {
    const next = new URLSearchParams(searchParams.toString());
    if (value) next.set(key, value); else next.delete(key);
    replaceParams(next);
  }

  function updateView(value: string) {
    const next = new URLSearchParams(searchParams.toString());
    if (value === "multi") {
      next.set("view", "multi"); next.set("from", fromSeason || season); next.set("to", toSeason || season);
    } else {
      next.delete("view"); next.delete("from"); next.delete("to");
    }
    next.delete("opponent"); next.delete("venue"); next.delete("result");
    replaceParams(next);
  }

  function updateRange(key: "from" | "to", value: string) {
    const next = new URLSearchParams(searchParams.toString());
    next.set("view", "multi"); next.set(key, value); replaceParams(next);
  }

  function clearFilters() {
    const next = new URLSearchParams();
    next.set("season", season); next.set("team", team);
    replaceParams(next);
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.kicker}>Fixture archive <span /> Premier League</div>
        <div className={styles.headerGrid}>
          <div className={styles.identity}>
            <div className={styles.teamMark} style={{ width: "3.9rem", height: "3.9rem" }} aria-hidden="true"><TeamCrest teamName={team} size={58} /></div>
            <div>
              <h1>{team}</h1>
              <p>{view === "multi" ? `${fromSeason} — ${toSeason}` : season}</p>
            </div>
          </div>

          <div className={styles.summary}>
            <div><strong>{filtered.length}</strong><span>fixtures</span></div>
            <div><strong>{record.wins}</strong><span>wins</span></div>
            <div><strong>{record.draws}</strong><span>draws</span></div>
            <div><strong>{record.losses}</strong><span>losses</span></div>
          </div>

          <button className={styles.refineButton} type="button" onClick={() => setRefineOpen(true)}>
            Refine <span>↗</span>{hasFilters ? <i aria-hidden="true" /> : null}
          </button>
        </div>
      </header>

      {grouped.length > 1 ? (
        <nav className={styles.monthNav} aria-label="Fixture months">
          {grouped.map(([group]) => <a key={group} href={`#${groupId(group)}`}>{monthNavLabel(group)}</a>)}
        </nav>
      ) : null}

      {excludedSeasons.length > 0 && !loading ? (
        <p className={styles.coverage}>Coverage excludes {excludedSeasons.length} season{excludedSeasons.length === 1 ? "" : "s"} without a verified team identity.</p>
      ) : null}

      {error ? (
        <div className={styles.state}><strong>Fixture archive unavailable.</strong><span>{error}</span></div>
      ) : loading ? (
        <div className={styles.state}>Loading validated fixture history…</div>
      ) : grouped.length === 0 ? (
        <div className={styles.state}><strong>No fixtures match this view.</strong><button type="button" onClick={clearFilters}>Clear filters</button></div>
      ) : (
        <main className={styles.archive}>
          {grouped.map(([group, groupRows]) => (
            <section className={styles.month} id={groupId(group)} key={group}>
              <div className={styles.monthHeading}>
                <h2>{group}</h2>
                <span>{groupRows.length.toString().padStart(2, "0")}</span>
              </div>

              <div className={styles.columnHead} aria-hidden="true">
                <span>Date</span><span>Match</span><span>Context</span><span />
              </div>

              {groupRows.map((row) => {
                const homeTeam = row.venue === "Home" ? team : row.opponent;
                const awayTeam = row.venue === "Home" ? row.opponent : team;
                return (
                  <Link className={styles.fixture} href={`/fixtures/${row.season}/${row.fixtureId}`} key={`${row.season}-${row.fixtureId}`}>
                    <div className={styles.date}>
                      <strong>{row.date}</strong>
                      <span>{row.gameweek ? `GW ${row.gameweek}` : row.season}</span>
                    </div>

                    <div className={styles.matchup}>
                      <div className={`${styles.side} ${homeTeam === team ? styles.selectedTeam : ""}`}>
                        <span className={styles.kit}><TeamCrest teamName={homeTeam} size={20} /></span>
                        <span>{homeTeam}</span>
                      </div>
                      <strong className={styles.score}>{row.score}</strong>
                      <div className={`${styles.side} ${styles.awaySide} ${awayTeam === team ? styles.selectedTeam : ""}`}>
                        <span>{awayTeam}</span>
                        <span className={styles.kit}><TeamCrest teamName={awayTeam} size={20} /></span>
                      </div>
                    </div>

                    <div className={styles.contextMeta}>
                      <span>{row.venue === "Home" ? "Home" : "Away"}</span>
                      <span>{row.result === "UNPLAYED" ? "Upcoming" : row.result === "W" ? "Win" : row.result === "D" ? "Draw" : "Loss"}</span>
                    </div>

                    <span className={styles.arrow} aria-hidden="true">↗</span>
                  </Link>
                );
              })}
            </section>
          ))}
        </main>
      )}

      <details className={styles.provenance}>
        <summary>Research provenance</summary>
        <div>
          <p>{description}</p>
          <p>{populationLabel}</p>
          <p>Validated seasonal results: {resultIds.length}</p>
          <p>Included seasons: {includedSeasons.length ? includedSeasons.join(", ") : "—"}</p>
          <p>{provenance}</p>
        </div>
      </details>

      {refineOpen ? (
        <div className={styles.drawerLayer}>
          <button className={styles.backdrop} type="button" aria-label="Close filters" onClick={() => setRefineOpen(false)} />
          <aside className={styles.drawer} role="dialog" aria-modal="true" aria-label="Refine fixture archive">
            <div className={styles.drawerHead}>
              <div><span>Fixture archive</span><h2>Refine</h2></div>
              <button type="button" onClick={() => setRefineOpen(false)}>Close</button>
            </div>

            <div className={styles.control}>
              <label htmlFor="fixtures-team">Club</label>
              <select id="fixtures-team" value={team} onChange={(event) => updateContext("team", event.target.value)} disabled={contextLoading || !!error}>
                {teamOptions.map((value) => <option key={value}>{value}</option>)}
              </select>
            </div>

            <div className={styles.control}>
              <label htmlFor="fixtures-season">Season</label>
              <select id="fixtures-season" value={season} onChange={(event) => updateContext("season", event.target.value)} disabled={contextLoading || !!error}>
                {seasonOptions.map((value) => <option key={value}>{value}</option>)}
              </select>
            </div>

            <div className={styles.control}>
              <label htmlFor="fixtures-view">Range</label>
              <select id="fixtures-view" value={view} onChange={(event) => updateView(event.target.value)} disabled={loading || !!error}>
                <option value="single">Single season</option><option value="multi">Multiple seasons</option>
              </select>
            </div>

            {view === "multi" ? (
              <div className={styles.rangeGrid}>
                <div className={styles.control}><label htmlFor="fixtures-from">From</label><select id="fixtures-from" value={fromSeason} onChange={(event) => updateRange("from", event.target.value)}>{rangeOptions.map((value) => <option key={value}>{value}</option>)}</select></div>
                <div className={styles.control}><label htmlFor="fixtures-to">To</label><select id="fixtures-to" value={toSeason} onChange={(event) => updateRange("to", event.target.value)}>{rangeOptions.map((value) => <option key={value}>{value}</option>)}</select></div>
              </div>
            ) : null}

            <div className={styles.control}>
              <label htmlFor="fixtures-opponent">Opponent</label>
              <select id="fixtures-opponent" value={opponent} onChange={(event) => updateFilter("opponent", event.target.value)}><option value="">All opponents</option>{opponents.map((value) => <option key={value}>{value}</option>)}</select>
            </div>

            <div className={styles.control}>
              <label htmlFor="fixtures-venue">Venue</label>
              <select id="fixtures-venue" value={venue} onChange={(event) => updateFilter("venue", event.target.value)}><option value="">Home + Away</option><option>Home</option><option>Away</option></select>
            </div>

            <div className={styles.control}>
              <label htmlFor="fixtures-result">Result</label>
              <select id="fixtures-result" value={resultFilter} onChange={(event) => updateFilter("result", event.target.value)}><option value="">All results</option><option>W</option><option>D</option><option>L</option><option>UNPLAYED</option></select>
            </div>

            <div className={styles.drawerFoot}>
              <span>{loading ? "Updating…" : `${filtered.length} fixtures`}</span>
              {hasFilters ? <button type="button" onClick={clearFilters}>Reset view</button> : null}
            </div>
          </aside>
        </div>
      ) : null}
    </div>
  );
}