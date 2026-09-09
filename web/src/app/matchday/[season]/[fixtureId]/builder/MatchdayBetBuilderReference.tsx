"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { TeamKit } from "@/app/teams/TeamKit";
import styles from "./MatchdayBetBuilderReference.module.css";

type FormResult = "W" | "D" | "L";

type TeamSide = {
  team_name: string;
  form?: FormResult[];
};

type MatchdayPack = {
  fixture: {
    season: string;
    fixture_id: string;
    gameweek: number | null;
    kickoff_time: string | null;
    home_team_name: string;
    away_team_name: string;
  };
  teams?: {
    home?: TeamSide;
    away?: TeamSide;
  };
};

type ThresholdSummary = {
  hits?: number;
  observed_matches?: number;
};

type BetBuilderEntry = {
  id?: string;
  family?: string;
  team_name?: string;
  opponent_name?: string;
  market_label?: string;
  metric_label?: string;
  evidence_label?: string;
  evidence_index?: number | null;
  team_recent?: ThresholdSummary;
  opponent_allowance?: ThresholdSummary;
};

type PlayerMarketPlayer = {
  player_code?: string;
  player_name?: string;
  hits?: number;
  observed_appearances?: number;
};

type PlayerMarketSide = {
  team_name?: string;
  players?: PlayerMarketPlayer[];
};

type PlayerMarket = {
  key?: string;
  family?: string;
  label?: string;
  home?: PlayerMarketSide;
  away?: PlayerMarketSide;
};

type HeadToHeadPack = {
  betbuilder?: {
    entries?: BetBuilderEntry[];
  };
  player_markets?: PlayerMarket[];
};

type Candidate = {
  id: string;
  kind: "team" | "player";
  family: string;
  subject: string;
  market: string;
  estimate: number;
  evidence: string[];
  observations: number;
  smallSample: boolean;
};

type Props = {
  pack: Record<string, unknown>;
  marketPack: Record<string, unknown> | null;
};

const COMMON_FRACTIONAL_ODDS: Array<readonly [number, number]> = [
  [1, 100], [1, 66], [1, 50], [1, 40], [1, 33], [1, 25], [1, 20], [1, 16], [1, 14], [1, 12],
  [1, 10], [1, 9], [1, 8], [1, 7], [1, 6], [1, 5], [2, 9], [1, 4], [2, 7], [3, 10], [1, 3],
  [4, 11], [2, 5], [4, 9], [1, 2], [8, 15], [4, 7], [8, 13], [2, 3], [8, 11], [4, 5], [5, 6],
  [8, 9], [10, 11], [1, 1], [11, 10], [6, 5], [5, 4], [11, 8], [6, 4], [13, 8], [7, 4], [15, 8],
  [2, 1], [9, 4], [5, 2], [11, 4], [3, 1], [10, 3], [7, 2], [4, 1], [9, 2], [5, 1], [6, 1],
  [7, 1], [8, 1], [9, 1], [10, 1], [12, 1], [14, 1], [16, 1], [20, 1], [25, 1], [33, 1], [40, 1],
  [50, 1], [66, 1], [100, 1],
];

function asMatchdayPack(pack: Record<string, unknown>) {
  return pack as unknown as MatchdayPack;
}

function asHeadToHeadPack(pack: Record<string, unknown> | null) {
  return pack as unknown as HeadToHeadPack | null;
}

function clampProbability(value: number) {
  return Math.max(0.01, Math.min(0.99, value));
}

function smoothedEstimate(hits: number, observations: number) {
  if (observations <= 0) return 0.5;
  return clampProbability((hits + 1) / (observations + 2));
}

function percent(value: number) {
  return `${Math.round(value * 100)}%`;
}

function fairFractionalOdds(probability: number) {
  if (!Number.isFinite(probability) || probability <= 0 || probability >= 1) return "—";
  const target = (1 - probability) / probability;
  let best = COMMON_FRACTIONAL_ODDS[0];
  let bestDistance = Math.abs(best[0] / best[1] - target);

  for (const candidate of COMMON_FRACTIONAL_ODDS.slice(1)) {
    const distance = Math.abs(candidate[0] / candidate[1] - target);
    if (distance < bestDistance) {
      best = candidate;
      bestDistance = distance;
    }
  }

  return best[0] === best[1] ? "EVS" : `${best[0]}/${best[1]}`;
}

function fixtureDate(value: string | null) {
  if (!value) return "Date TBC";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Date TBC";
  return date.toLocaleDateString("en-GB", {
    timeZone: "Europe/London",
    weekday: "short",
    day: "numeric",
    month: "short",
  });
}

function fixtureTime(value: string | null) {
  if (!value) return "TBC";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "TBC";
  return date.toLocaleTimeString("en-GB", {
    timeZone: "Europe/London",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function normaliseFamily(family: string) {
  const value = family.toLowerCase();
  if (value.includes("foul")) return "PLAYER MARKET";
  if (value.includes("card")) return "PLAYER MARKET";
  if (value.includes("shot")) return "TEAM MARKET";
  return "TEAM MARKET";
}

function buildCandidates(marketPack: HeadToHeadPack | null): Candidate[] {
  if (!marketPack) return [];
  const candidates: Candidate[] = [];

  for (const [index, entry] of (marketPack.betbuilder?.entries ?? []).entries()) {
    const teamHits = Number(entry.team_recent?.hits ?? 0);
    const teamObserved = Number(entry.team_recent?.observed_matches ?? 0);
    const opponentHits = Number(entry.opponent_allowance?.hits ?? 0);
    const opponentObserved = Number(entry.opponent_allowance?.observed_matches ?? 0);
    const observations = teamObserved + opponentObserved;
    const hits = teamHits + opponentHits;
    const estimate = observations > 0
      ? smoothedEstimate(hits, observations)
      : clampProbability(Number(entry.evidence_index ?? 0.5));

    const subject = entry.team_name ?? "Team";
    const market = entry.market_label ?? entry.metric_label ?? entry.family ?? "Market";

    candidates.push({
      id: entry.id ?? `team-${index}-${subject}-${market}`,
      kind: "team",
      family: entry.family ?? "Team",
      subject,
      market,
      estimate,
      evidence: [
        `Team ${teamHits}/${teamObserved || "—"}`,
        `Opponent ${opponentHits}/${opponentObserved || "—"}`,
      ],
      observations,
      smallSample: observations > 0 && observations <= 6,
    });
  }

  for (const [marketIndex, market] of (marketPack.player_markets ?? []).entries()) {
    for (const side of [market.home, market.away]) {
      const teamName = side?.team_name ?? "Team";
      for (const [playerIndex, player] of (side?.players ?? []).entries()) {
        const observed = Number(player.observed_appearances ?? 0);
        const hits = Number(player.hits ?? 0);
        if (observed <= 0 || hits <= 0) continue;

        candidates.push({
          id: `player-${market.key ?? marketIndex}-${player.player_code ?? playerIndex}`,
          kind: "player",
          family: market.family ?? "Player",
          subject: player.player_name ?? "Player",
          market: market.label ?? market.family ?? "Player market",
          estimate: smoothedEstimate(hits, observed),
          evidence: [`Recent ${hits}/${observed}`],
          observations: observed,
          smallSample: observed <= 5,
        });
      }
    }
  }

  const deduped = new Map<string, Candidate>();
  for (const candidate of candidates) {
    const existing = deduped.get(candidate.id);
    if (!existing || candidate.estimate > existing.estimate) deduped.set(candidate.id, candidate);
  }

  return [...deduped.values()].sort((a, b) =>
    b.estimate - a.estimate
    || b.observations - a.observations
    || a.subject.localeCompare(b.subject)
  );
}

function initialSelection(candidates: Candidate[]) {
  const selected: Candidate[] = [];
  const team = candidates.find((candidate) => candidate.kind === "team");
  if (team) selected.push(team);

  const foulPlayers = candidates.filter((candidate) => candidate.kind === "player" && candidate.family.toLowerCase().includes("foul"));
  for (const candidate of foulPlayers) {
    if (selected.length >= 3) break;
    if (!selected.some((item) => item.subject === candidate.subject)) selected.push(candidate);
  }

  for (const candidate of candidates) {
    if (selected.length >= 3) break;
    if (!selected.some((item) => item.id === candidate.id)) selected.push(candidate);
  }

  return selected.map((candidate) => candidate.id);
}

function FormStrip({ results }: { results: FormResult[] }) {
  return (
    <div className={styles.formStrip} aria-label="Recent form">
      {results.slice(0, 5).map((result, index) => (
        <span key={`${result}-${index}`} data-result={result}>{result}</span>
      ))}
    </div>
  );
}

export function MatchdayBetBuilderReference({ pack, marketPack }: Props) {
  const data = asMatchdayPack(pack);
  const markets = asHeadToHeadPack(marketPack);
  const candidates = useMemo(() => buildCandidates(markets), [markets]);
  const [selectedIds, setSelectedIds] = useState<string[]>(() => initialSelection(candidates));
  const [howOpen, setHowOpen] = useState(false);
  const [saved, setSaved] = useState(false);

  const selected = selectedIds
    .map((id) => candidates.find((candidate) => candidate.id === id))
    .filter((candidate): candidate is Candidate => Boolean(candidate));
  const selectedSet = new Set(selectedIds);
  const alternatives = candidates.filter((candidate) => !selectedSet.has(candidate.id)).slice(0, 6);
  const combined = selected.length > 0
    ? selected.reduce((value, candidate) => value * candidate.estimate, 1)
    : null;
  const smallSamples = selected.filter((candidate) => candidate.smallSample).length;

  const fixture = data.fixture;
  const homeForm = data.teams?.home?.form ?? [];
  const awayForm = data.teams?.away?.form ?? [];
  const baseHref = `/matchday/${encodeURIComponent(fixture.season)}/${encodeURIComponent(fixture.fixture_id)}`;

  function replaceSelection(index: number) {
    const current = selected[index];
    if (!current) return;
    const replacement = candidates.find((candidate) =>
      !selectedSet.has(candidate.id) && candidate.kind === current.kind
    ) ?? candidates.find((candidate) => !selectedSet.has(candidate.id));
    if (!replacement) return;
    setSelectedIds((ids) => ids.map((id, itemIndex) => itemIndex === index ? replacement.id : id));
    setSaved(false);
  }

  function removeSelection(index: number) {
    setSelectedIds((ids) => ids.filter((_, itemIndex) => itemIndex !== index));
    setSaved(false);
  }

  function addSelection(candidateId?: string) {
    const next = candidateId
      ? candidates.find((candidate) => candidate.id === candidateId)
      : candidates.find((candidate) => !selectedSet.has(candidate.id));
    if (!next || selectedSet.has(next.id)) return;
    setSelectedIds((ids) => [...ids, next.id].slice(0, 5));
    setSaved(false);
  }

  function compareCandidate(candidate: Candidate) {
    if (selected.length < 5) {
      addSelection(candidate.id);
      return;
    }
    setSelectedIds((ids) => [...ids.slice(0, -1), candidate.id]);
    setSaved(false);
  }

  function saveBuilder() {
    try {
      window.localStorage.setItem(`frl-builder:${fixture.season}:${fixture.fixture_id}`, JSON.stringify({
        selectedIds,
        savedAt: new Date().toISOString(),
      }));
    } catch {
      // Local persistence is a convenience only; the builder remains usable without it.
    }
    setSaved(true);
  }

  return (
    <main className={styles.page}>
      <section className={styles.fixtureCard}>
        <div className={styles.teamSide}>
          <TeamKit teamName={fixture.home_team_name} />
          <div>
            <strong>{fixture.home_team_name}</strong>
            <FormStrip results={homeForm} />
          </div>
        </div>

        <div className={styles.fixtureMeta}>
          <span>{fixtureDate(fixture.kickoff_time)} · <b>{fixtureTime(fixture.kickoff_time)}</b></span>
          <small>{fixture.gameweek != null ? `GW ${fixture.gameweek}` : "Premier League"}</small>
        </div>

        <div className={`${styles.teamSide} ${styles.teamSideAway}`}>
          <div>
            <strong>{fixture.away_team_name}</strong>
            <FormStrip results={awayForm} />
          </div>
          <TeamKit teamName={fixture.away_team_name} />
        </div>
      </section>

      <nav className={styles.marketTabs} aria-label="Matchday analysis sections">
        <Link href={baseHref}>Team markets</Link>
        <Link href={baseHref}>Player markets</Link>
        <Link href={baseHref}>Foul matchups</Link>
        <span aria-current="page">Bet builder</span>
      </nav>

      <section className={styles.headingRow}>
        <div className={styles.headingCopy}>
          <h1>Build your bet</h1>
          <span>FRL suggested</span>
        </div>
        <button className={styles.howButton} type="button" onClick={() => setHowOpen((value) => !value)}>
          <span>{howOpen ? "⌃" : "⌄"}</span> How it works
        </button>
      </section>

      {howOpen && (
        <aside className={styles.howPanel}>
          <strong>Evidence first, price second.</strong>
          <p>FRL ranks the evidence available before kickoff, suggests a compact set of legs and shows an indicative combined likelihood. Individual estimates use small-sample smoothing; the whole-builder number is still indicative because same-game correlation can remain.</p>
        </aside>
      )}

      <section className={styles.builderGrid}>
        <div className={styles.selectionColumn}>
          {selected.length > 0 ? selected.map((candidate, index) => (
            <article className={styles.selectionCard} key={candidate.id}>
              <span className={styles.selectionNumber}>{index + 1}</span>

              <div className={styles.selectionIdentity}>
                <small data-kind={candidate.kind}>{normaliseFamily(candidate.family)}</small>
                <strong>{candidate.subject}<br /><span>{candidate.market}</span></strong>
              </div>

              <div className={styles.selectionEvidence}>
                <small>{candidate.kind === "team" ? "Evidence (first leg)" : "Evidence (recent)"}</small>
                <div>
                  {candidate.evidence.map((item) => <span key={item}>{item}</span>)}
                  {candidate.smallSample && <em>Small sample</em>}
                </div>
              </div>

              <div className={styles.selectionEstimate}>
                <strong>{percent(candidate.estimate)}</strong>
                <small>est.</small>
              </div>

              <button className={styles.swapButton} type="button" onClick={() => replaceSelection(index)}>
                ⇄ <span>Swap</span>
              </button>
              <button className={styles.removeButton} type="button" aria-label={`Remove ${candidate.subject} ${candidate.market}`} onClick={() => removeSelection(index)}>×</button>
            </article>
          )) : (
            <div className={styles.emptyState}>
              <strong>No selections yet.</strong>
              <span>Add one of FRL&apos;s evidence-backed options below.</span>
            </div>
          )}

          <button className={styles.addButton} type="button" onClick={() => addSelection()} disabled={alternatives.length === 0 || selected.length >= 5}>
            <span>＋</span> Add selection
          </button>
        </div>

        <aside className={styles.summaryCard}>
          <div className={styles.summaryHeader}>
            <div>
              <h2>Your builder</h2>
              <strong>{selected.length} {selected.length === 1 ? "selection" : "selections"}</strong>
            </div>
            <span>FRL suggested</span>
          </div>

          <div className={styles.summaryMetrics}>
            <div>
              <strong>{combined == null ? "—" : percent(combined)}</strong>
              <span>Est. likelihood ⓘ</span>
            </div>
            <div>
              <strong>{combined == null ? "—" : fairFractionalOdds(combined)}</strong>
              <span>Est. fair odds ⓘ</span>
            </div>
          </div>

          {smallSamples > 0 && (
            <div className={styles.warningRow}>
              <span>!</span>
              <strong>{smallSamples} small {smallSamples === 1 ? "sample" : "samples"}</strong>
              <b>⌄</b>
            </div>
          )}

          <p className={styles.correlationNote}>ⓘ <span>Indicative · Correlation may remain</span></p>

          <button className={styles.saveButton} type="button" onClick={saveBuilder}>
            <span>♡</span> {saved ? "Builder saved" : "Save builder"}
          </button>
        </aside>
      </section>

      <section className={styles.alternativesSection}>
        <header>
          <strong>Other options to consider</strong>
          <span>Show more »</span>
        </header>
        <div className={styles.alternativeGrid}>
          {alternatives.slice(0, 3).map((candidate) => (
            <article className={styles.alternativeCard} key={candidate.id}>
              <span className={styles.playerDot}>{candidate.kind === "player" ? "●" : "◆"}</span>
              <div>
                <strong>{candidate.subject}</strong>
                <span>{candidate.market}</span>
              </div>
              <div className={styles.alternativeEstimate}>
                <strong>{percent(candidate.estimate)}</strong>
                <small>est.</small>
              </div>
              <button type="button" onClick={() => compareCandidate(candidate)}>Compare</button>
            </article>
          ))}
          {alternatives.length === 0 && <p className={styles.noAlternatives}>No additional governed candidates are available for this fixture yet.</p>}
        </div>
      </section>
    </main>
  );
}
