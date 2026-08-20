"use client";

import { useMemo } from "react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { demoResearchResult, fixtureRowsFromResult, type FixtureRow } from "@/lib/research-result";

export function FixtureExplorer() {
  const result = useMemo(() => demoResearchResult(), []);
  const rows = useMemo(() => fixtureRowsFromResult(result), [result]);
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const opponent = searchParams.get("opponent") ?? "";
  const venue = searchParams.get("venue") ?? "";
  const resultFilter = searchParams.get("result") ?? "";

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
    const groups = new Map<string, FixtureRow[]>();
    for (const row of filtered) {
      const group = row.date.split(" ").slice(-1)[0] || "Fixtures";
      const list = groups.get(group) ?? [];
      list.push(row);
      groups.set(group, list);
    }
    return [...groups.entries()];
  }, [filtered]);

  function updateFilter(key: string, value: string) {
    const next = new URLSearchParams(searchParams.toString());
    if (value) next.set(key, value);
    else next.delete(key);
    const query = next.toString();
    router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }

  function clearFilters() {
    router.replace(pathname, { scroll: false });
  }

  return (
    <>
      <section className="frl-page-heading">
        <div>
          <div className="frl-eyebrow">Fixtures</div>
          <h1 className="frl-title">Arsenal</h1>
          <div className="frl-context">Premier League · {result.scope.season}</div>
        </div>
        <div className="frl-context-actions">
          <label>
            <span>Season</span>
            <select defaultValue={result.scope.season} disabled aria-label="Season">
              <option>{result.scope.season}</option>
            </select>
          </label>
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
        <label>
          <span>Opponent</span>
          <select value={opponent} onChange={(event) => updateFilter("opponent", event.target.value)}>
            <option value="">All opponents</option>
            {opponents.map((value) => <option key={value}>{value}</option>)}
          </select>
        </label>
        <label>
          <span>Venue</span>
          <select value={venue} onChange={(event) => updateFilter("venue", event.target.value)}>
            <option value="">All venues</option>
            <option>Home</option>
            <option>Away</option>
          </select>
        </label>
        <label>
          <span>Result</span>
          <select value={resultFilter} onChange={(event) => updateFilter("result", event.target.value)}>
            <option value="">All results</option>
            <option>W</option>
            <option>D</option>
            <option>L</option>
          </select>
        </label>
        <div className="frl-filter-summary">
          <span>{filtered.length} of {rows.length} fixtures</span>
          {(opponent || venue || resultFilter) && (
            <button type="button" onClick={clearFilters}>Clear filters</button>
          )}
        </div>
      </section>

      {grouped.length === 0 ? (
        <div className="frl-empty-state">No fixtures match the selected filters.</div>
      ) : (
        <section className="frl-fixture-list" aria-label="Fixture results">
          {grouped.map(([group, groupRows]) => (
            <div className="frl-fixture-month" key={group}>
              <div className="frl-month-heading">{group}</div>
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
                  href={`/fixtures/${result.scope.season}/${row.fixtureId}`}
                  key={`${result.scope.season}-${row.fixtureId}`}
                >
                  <span className="frl-fixture-date">{row.date}</span>
                  <span className="frl-fixture-opponent">{row.opponent}</span>
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
        <strong>Research result.</strong> This workspace currently demonstrates the presentation contract using the foundation-spike result object. The production version will receive the validated fixture result from the Python research/query layer without changing the interaction model.
      </div>
    </>
  );
}
