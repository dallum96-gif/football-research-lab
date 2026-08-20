"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { ResearchChart } from "@/components/ResearchChart";
import { AppShell } from "@/components/AppShell";
import { demoResearchResult, fixtureRowsFromResult } from "@/lib/research-result";

export default function HomePage() {
  const result = useMemo(() => demoResearchResult(), []);
  const rows = useMemo(() => fixtureRowsFromResult(result), [result]);
  const [selectedFixtureId, setSelectedFixtureId] = useState(rows[0]?.fixtureId ?? "");

  const selected = rows.find((row) => row.fixtureId === selectedFixtureId) ?? rows[0];

  return (
    <AppShell>
      <header>
        <div className="frl-eyebrow">Foundation spike</div>
        <h1 className="frl-title">Visual Research Platform</h1>
        <div className="frl-context">A typed Research Result driving coordinated table, chart and inspection views.</div>
      </header>

      <div className="frl-rule" />

      <section className="frl-result-grid" id="research-result">
        <div className="frl-panel" id="visualisation">
          <div className="frl-panel-title">Research Result</div>
          <div className="frl-panel-subtitle">{result.description}</div>
          <ResearchChart
            points={result.data}
            selectedFixtureId={selectedFixtureId}
            onSelect={setSelectedFixtureId}
          />

          <div className="frl-panel-link-row">
            <Link href="/fixtures">Open Fixture Explorer →</Link>
          </div>

          <table className="frl-table" id="fixtures">
            <thead>
              <tr>
                <th>Date</th>
                <th>Opponent</th>
                <th>Venue</th>
                <th>Score</th>
                <th>Result</th>
                <th>Pos.</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={`${result.scope.season}-${row.fixtureId}`} data-selected={row.fixtureId === selectedFixtureId}>
                  <td>{row.date}</td>
                  <td>
                    <button onClick={() => setSelectedFixtureId(row.fixtureId)} type="button">
                      {row.opponent}
                    </button>
                  </td>
                  <td>{row.venue}</td>
                  <td>{row.score}</td>
                  <td><strong>{row.result}</strong></td>
                  <td>{row.positionAfter}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <aside className="frl-panel">
          <div className="frl-panel-title">Exact Result Context</div>
          <span className="frl-badge">Demo result</span>

          <div className="frl-meta-list">
            <div className="frl-meta-row">
              <div className="frl-meta-label">Result ID</div>
              <div className="frl-meta-value">{result.resultId}</div>
            </div>
            <div className="frl-meta-row">
              <div className="frl-meta-label">Population</div>
              <div className="frl-meta-value">{result.population.label}</div>
            </div>
            <div className="frl-meta-row">
              <div className="frl-meta-label">Sample</div>
              <div className="frl-meta-value">{result.population.sampleSize}</div>
            </div>
            <div className="frl-meta-row">
              <div className="frl-meta-label">As of</div>
              <div className="frl-meta-value">{result.scope.asOf}</div>
            </div>
            <div className="frl-meta-row">
              <div className="frl-meta-label">Selected fixture</div>
              <div className="frl-meta-value">{result.scope.season} / {selected?.fixtureId}</div>
            </div>
            <div className="frl-meta-row">
              <div className="frl-meta-label">Opponent</div>
              <div className="frl-meta-value">{selected?.opponent}</div>
            </div>
            <div className="frl-meta-row">
              <div className="frl-meta-label">Position</div>
              <div className="frl-meta-value">{selected?.positionAfter}</div>
            </div>
          </div>

          <div className="frl-note" id="provenance">
            <strong>Provenance:</strong> {result.provenance.source} · {result.provenance.transformationVersion}.
            The demo is intentionally static; production data will arrive through the existing Python research/query layer.
          </div>
        </aside>
      </section>
    </AppShell>
  );
}
