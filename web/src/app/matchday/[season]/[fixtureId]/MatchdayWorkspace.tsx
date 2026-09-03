"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { TeamKit } from "@/app/teams/TeamKit";
import styles from "./MatchdayWorkspace.module.css";

type Metric = {
  key: string;
  label: string;
  unit: string;
  value: number | null;
  observed_matches: number;
  eligible_matches: number;
};

type RecentMatch = {
  season: string;
  fixture_id: string;
  kickoff_time: string | null;
  opponent: string;
  venue: "Home" | "Away";
  goals_for: number;
  goals_against: number;
  result: "W" | "D" | "L";
};

type TeamSide = {
  team_name: string;
  persistent_team_code: string;
  sample_size: number;
  form: Array<"W" | "D" | "L">;
  points: number;
  matches: RecentMatch[];
  metrics: Metric[];
};

type PlayerLeaderboard = {
  key: string;
  label: string;
  unit: string;
  players: Array<{
    rank: number;
    player_code: string;
    player_name: string;
    position: string;
    appearances: number;
    minutes: number;
    value: number;
  }>;
};

type PlayerSide = {
  team_name: string;
  sample_definition: string;
  player_count: number;
  leaderboards: PlayerLeaderboard[];
};

type Prediction = {
  status: string;
  model?: string;
  reason?: string;
  expected_goals?: { home: number; away: number };
  probabilities?: Record<string, number>;
  fair_odds?: Record<string, number | null>;
  inputs?: {
    home_strength?: Record<string, number | string | null>;
    away_strength?: Record<string, number | string | null>;
    home_representation?: string;
    away_representation?: string;
  };
  correct_scores?: Array<{
    home: number;
    away: number;
    probability: number;
    fair_odds: number | null;
  }>;
  limitations?: string[];
};

type MatchdayPack = {
  pack_version: string;
  as_of: string | null;
  fixture: {
    season: string;
    fixture_id: string;
    gameweek: number | null;
    kickoff_time: string | null;
    home_team_name: string;
    away_team_name: string;
    home_score: number | null;
    away_score: number | null;
  };
  prediction: Prediction;
  teams: { home: TeamSide; away: TeamSide };
  players: { home: PlayerSide; away: PlayerSide };
  matchups: {
    cards: {
      status: string;
      available_now: string[];
      withheld: string[];
      note: string;
    };
  };
  market: { status: string; note: string };
  limitations: string[];
};

type FixtureOption = {
  season?: string;
  fixture_id?: string;
  gameweek?: number | null;
  kickoff_time?: string | null;
  home_team_name?: string;
  away_team_name?: string;
  completed?: boolean;
};

type Props = {
  pack: Record<string, unknown>;
  fixtureOptions: Array<Record<string, unknown>>;
};

const PRIMARY_TABS = ["Overview", "Teams", "Players", "Matchups", "Markets", "Model"] as const;
const DEFAULT_PLAYER_METRICS = ["xg", "xa", "cards", "tackles"];

function percent(value: number | undefined) {
  return value == null ? "—" : `${(value * 100).toFixed(1)}%`;
}

function decimal(value: number | null | undefined, digits = 2) {
  return value == null || Number.isNaN(value) ? "—" : value.toFixed(digits);
}

function metricValue(metric: Metric) {
  if (metric.value == null) return "—";
  const digits = Math.abs(metric.value) >= 10 ? 1 : 2;
  return metric.value.toFixed(digits);
}

function fixtureDate(value: string | null | undefined) {
  if (!value) return "Date TBC";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "Date TBC";
  return parsed.toLocaleDateString("en-GB", {
    timeZone: "Europe/London",
    weekday: "short",
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function fixtureTime(value: string | null | undefined) {
  if (!value) return "Time TBC";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "Time TBC";
  return parsed.toLocaleTimeString("en-GB", {
    timeZone: "Europe/London",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function FormStrip({ form }: { form: TeamSide["form"] }) {
  if (!form.length) return <span className={styles.muted}>No prior league matches</span>;
  return (
    <div className={styles.formStrip} aria-label={`Form ${form.join(" ")}`}>
      {form.map((result, index) => (
        <span key={`${result}-${index}`} data-result={result}>{result}</span>
      ))}
    </div>
  );
}

function TeamRecentCard({ side }: { side: TeamSide }) {
  const headline = side.metrics.slice(0, 4);
  return (
    <section className={styles.teamRecentCard}>
      <div className={styles.cardHeader}>
        <div>
          <span className={styles.kicker}>Last {side.sample_size}</span>
          <h3>{side.team_name}</h3>
        </div>
        <FormStrip form={side.form} />
      </div>
      <div className={styles.miniMetricGrid}>
        {headline.map((metric) => (
          <div className={styles.miniMetric} key={metric.key}>
            <span>{metric.label}</span>
            <strong>{metricValue(metric)}</strong>
            <small>{metric.observed_matches}/{metric.eligible_matches} observed</small>
          </div>
        ))}
      </div>
    </section>
  );
}

function TeamPanel({ side }: { side: TeamSide }) {
  return (
    <section className={styles.sidePanel}>
      <div className={styles.sidePanelHeader}>
        <div>
          <span className={styles.kicker}>As-of form</span>
          <h2>{side.team_name}</h2>
        </div>
        <div className={styles.pointsBlock}>
          <strong>{side.points}</strong>
          <span>points from {side.sample_size}</span>
        </div>
      </div>
      <FormStrip form={side.form} />
      <div className={styles.teamMetrics}>
        {side.metrics.map((metric) => (
          <article className={styles.metricTile} key={metric.key}>
            <span>{metric.label}</span>
            <strong>{metricValue(metric)}</strong>
            <small>
              per observed match · {metric.observed_matches}/{metric.eligible_matches}
            </small>
          </article>
        ))}
      </div>
      <div className={styles.recentMatches}>
        {side.matches.map((match) => (
          <Link
            href={`/fixtures/${match.season}/${match.fixture_id}`}
            className={styles.recentMatch}
            key={`${match.season}-${match.fixture_id}`}
          >
            <span data-result={match.result}>{match.result}</span>
            <strong>{match.opponent}</strong>
            <small>{match.venue}</small>
            <b>{match.goals_for}–{match.goals_against}</b>
          </Link>
        ))}
      </div>
    </section>
  );
}

function PlayerTile({ leaderboard }: { leaderboard: PlayerLeaderboard }) {
  return (
    <article className={styles.leaderTile}>
      <div className={styles.leaderTileHeader}>
        <span>{leaderboard.label}</span>
        <small>Last 5 apps max</small>
      </div>
      <div className={styles.leaderList}>
        {leaderboard.players.length ? leaderboard.players.map((player) => (
          <div className={styles.leaderRow} key={`${leaderboard.key}-${player.player_code}-${player.rank}`}>
            <span className={styles.rank}>{player.rank}</span>
            <div>
              <strong>{player.player_name}</strong>
              <small>{player.position || "—"} · {player.appearances} apps</small>
            </div>
            <b>{player.value.toFixed(player.value % 1 === 0 ? 0 : 2)}</b>
          </div>
        )) : <div className={styles.emptyTile}>No observed player data yet.</div>}
      </div>
    </article>
  );
}

function MarketCard({
  label,
  probability,
  fairOdds,
  value,
  onChange,
}: {
  label: string;
  probability: number | undefined;
  fairOdds: number | null | undefined;
  value: string;
  onChange: (value: string) => void;
}) {
  const entered = Number(value);
  const valid = Number.isFinite(entered) && entered > 1 && probability != null;
  const ev = valid ? probability * entered - 1 : null;
  return (
    <article className={styles.marketCard}>
      <div>
        <span>{label}</span>
        <strong>{percent(probability)}</strong>
      </div>
      <div className={styles.marketFair}>
        <span>FRL fair</span>
        <b>{decimal(fairOdds)}</b>
      </div>
      <label>
        <span>Bookmaker</span>
        <input
          inputMode="decimal"
          placeholder="e.g. 2.40"
          value={value}
          onChange={(event) => onChange(event.target.value)}
        />
      </label>
      <div className={styles.marketEdge} data-positive={ev != null && ev > 0 ? "true" : "false"}>
        <span>Model EV</span>
        <b>{ev == null ? "—" : `${ev >= 0 ? "+" : ""}${(ev * 100).toFixed(1)}%`}</b>
      </div>
    </article>
  );
}

export function MatchdayWorkspace({ pack, fixtureOptions }: Props) {
  const data = pack as unknown as MatchdayPack;
  const fixtures = fixtureOptions as unknown as FixtureOption[];
  const router = useRouter();
  const [tab, setTab] = useState<(typeof PRIMARY_TABS)[number]>("Overview");
  const [playerSide, setPlayerSide] = useState<"home" | "away">("home");
  const [playerMetrics, setPlayerMetrics] = useState<string[]>(DEFAULT_PLAYER_METRICS);
  const [odds, setOdds] = useState<Record<string, string>>({});

  const prediction = data.prediction;
  const probabilities = prediction.probabilities ?? {};
  const fairOdds = prediction.fair_odds ?? {};
  const selectedPlayers = data.players[playerSide];
  const allPlayerMetrics = selectedPlayers.leaderboards;
  const visiblePlayerMetrics = allPlayerMetrics.filter((metric) => playerMetrics.includes(metric.key));

  const fixtureLabel = `${data.fixture.home_team_name} v ${data.fixture.away_team_name}`;
  const currentFixtureValue = data.fixture.fixture_id;
  const sortedFixtures = useMemo(
    () => [...fixtures].sort((a, b) => String(a.kickoff_time ?? "").localeCompare(String(b.kickoff_time ?? ""))),
    [fixtures],
  );

  function togglePlayerMetric(key: string) {
    setPlayerMetrics((current) => {
      if (current.includes(key)) return current.length === 1 ? current : current.filter((item) => item !== key);
      if (current.length >= 4) return current;
      return [...current, key];
    });
  }

  function selectFixture(fixtureId: string) {
    router.push(`/matchday/${data.fixture.season}/${fixtureId}`);
  }

  return (
    <div className={styles.workspace}>
      <header className={styles.hero}>
        <div className={styles.heroMeta}>
          <span className={styles.kicker}>Matchday Stat Pack · {data.pack_version}</span>
          <strong>Premier League · {data.fixture.season}{data.fixture.gameweek ? ` · GW ${data.fixture.gameweek}` : ""}</strong>
          <small>{fixtureDate(data.fixture.kickoff_time)} · {fixtureTime(data.fixture.kickoff_time)}</small>
        </div>

        <div className={styles.fixtureHero}>
          <div className={styles.heroTeam}>
            <span className={styles.heroKit}><TeamKit teamName={data.fixture.home_team_name} /></span>
            <strong>{data.fixture.home_team_name}</strong>
          </div>
          <div className={styles.vsBlock}>
            <span>FRL</span>
            <b>v</b>
            <small>{prediction.status === "AVAILABLE" ? prediction.model : "Research pack"}</small>
          </div>
          <div className={`${styles.heroTeam} ${styles.heroTeamAway}`}>
            <span className={styles.heroKit}><TeamKit teamName={data.fixture.away_team_name} /></span>
            <strong>{data.fixture.away_team_name}</strong>
          </div>
        </div>

        <div className={styles.heroActions}>
          <label className={styles.fixtureSelect}>
            <span>Fixture</span>
            <select value={currentFixtureValue} onChange={(event) => selectFixture(event.target.value)}>
              {sortedFixtures.map((fixture) => (
                <option key={String(fixture.fixture_id)} value={String(fixture.fixture_id)}>
                  {fixture.gameweek ? `GW${fixture.gameweek} · ` : ""}{fixture.home_team_name} v {fixture.away_team_name}
                </option>
              ))}
            </select>
          </label>
          <Link className={styles.reportLink} href={`/fixtures/${data.fixture.season}/${data.fixture.fixture_id}`}>
            Match report ↗
          </Link>
        </div>
      </header>

      <nav className={styles.primaryTabs} aria-label="Matchday research sections">
        {PRIMARY_TABS.map((item) => (
          <button
            type="button"
            key={item}
            data-active={tab === item ? "true" : "false"}
            onClick={() => setTab(item)}
          >
            {item}
          </button>
        ))}
      </nav>

      <main className={styles.panel}>
        {tab === "Overview" && (
          <div className={styles.overviewGrid}>
            <section className={`${styles.featureCard} ${styles.forecastCard}`}>
              <div className={styles.sectionHeading}>
                <div>
                  <span className={styles.kicker}>FRL forecast</span>
                  <h2>{fixtureLabel}</h2>
                </div>
                <small>Proof-of-concept model · research use</small>
              </div>
              {prediction.status === "AVAILABLE" ? (
                <div className={styles.outcomeGrid}>
                  <article>
                    <span>{data.fixture.home_team_name}</span>
                    <strong>{percent(probabilities.home_win)}</strong>
                    <small>fair {decimal(fairOdds.home_win)}</small>
                  </article>
                  <article>
                    <span>Draw</span>
                    <strong>{percent(probabilities.draw)}</strong>
                    <small>fair {decimal(fairOdds.draw)}</small>
                  </article>
                  <article>
                    <span>{data.fixture.away_team_name}</span>
                    <strong>{percent(probabilities.away_win)}</strong>
                    <small>fair {decimal(fairOdds.away_win)}</small>
                  </article>
                </div>
              ) : (
                <div className={styles.notice}>{prediction.reason ?? "Prediction unavailable."}</div>
              )}
            </section>

            <section className={styles.featureCard}>
              <div className={styles.sectionHeading}>
                <div>
                  <span className={styles.kicker}>Goal picture</span>
                  <h2>What the model expects</h2>
                </div>
              </div>
              <div className={styles.goalGrid}>
                <article><span>Home λ</span><strong>{decimal(prediction.expected_goals?.home)}</strong></article>
                <article><span>Away λ</span><strong>{decimal(prediction.expected_goals?.away)}</strong></article>
                <article><span>Over 2.5</span><strong>{percent(probabilities.over_2_5)}</strong></article>
                <article><span>BTTS</span><strong>{percent(probabilities.btts)}</strong></article>
              </div>
            </section>

            <TeamRecentCard side={data.teams.home} />
            <TeamRecentCard side={data.teams.away} />
          </div>
        )}

        {tab === "Teams" && (
          <div className={styles.twoColumn}>
            <TeamPanel side={data.teams.home} />
            <TeamPanel side={data.teams.away} />
          </div>
        )}

        {tab === "Players" && (
          <div>
            <div className={styles.subnavRow}>
              <div className={styles.segmented}>
                {(["home", "away"] as const).map((side) => (
                  <button type="button" key={side} data-active={playerSide === side ? "true" : "false"} onClick={() => setPlayerSide(side)}>
                    {data.players[side].team_name}
                  </button>
                ))}
              </div>
              <div className={styles.metricToggles} aria-label="Choose up to four player metrics">
                {allPlayerMetrics.map((metric) => {
                  const active = playerMetrics.includes(metric.key);
                  const disabled = !active && playerMetrics.length >= 4;
                  return (
                    <button
                      type="button"
                      key={metric.key}
                      data-active={active ? "true" : "false"}
                      disabled={disabled}
                      onClick={() => togglePlayerMetric(metric.key)}
                    >
                      {metric.label}
                    </button>
                  );
                })}
              </div>
            </div>
            <div className={styles.playerTileGrid}>
              {visiblePlayerMetrics.map((leaderboard) => <PlayerTile key={leaderboard.key} leaderboard={leaderboard} />)}
            </div>
            <p className={styles.footnote}>{selectedPlayers.sample_definition}. Four metrics can be active at once.</p>
          </div>
        )}

        {tab === "Matchups" && (
          <div className={styles.matchupGrid}>
            <section className={styles.featureCard}>
              <span className={styles.kicker}>Cards watch · V1</span>
              <h2>Card context we can defend now</h2>
              <div className={styles.matchupColumns}>
                {(["home", "away"] as const).map((side) => {
                  const cardBoard = data.players[side].leaderboards.find((item) => item.key === "cards");
                  const tackleBoard = data.players[side].leaderboards.find((item) => item.key === "tackles");
                  return (
                    <div key={side}>
                      <h3>{data.players[side].team_name}</h3>
                      <strong>Cards</strong>
                      {(cardBoard?.players ?? []).slice(0, 3).map((player) => (
                        <p key={`card-${player.player_code}`}>{player.player_name}<b>{player.value.toFixed(0)}</b></p>
                      ))}
                      <strong>Tackles</strong>
                      {(tackleBoard?.players ?? []).slice(0, 3).map((player) => (
                        <p key={`tackle-${player.player_code}`}>{player.player_name}<b>{player.value.toFixed(0)}</b></p>
                      ))}
                    </div>
                  );
                })}
              </div>
            </section>
            <section className={`${styles.featureCard} ${styles.researchBoundary}`}>
              <span className={styles.kicker}>Research boundary</span>
              <h2>Next matchup layer</h2>
              <p>{data.matchups.cards.note}</p>
              <div>
                {data.matchups.cards.withheld.map((item) => <span key={item}>○ {item}</span>)}
              </div>
              <small>We’ll add this when foul-drawn/foul-committed player-match evidence is packaged at runtime rather than inferred.</small>
            </section>
          </div>
        )}

        {tab === "Markets" && (
          <div>
            <div className={styles.sectionHeading}>
              <div>
                <span className={styles.kicker}>Private market notebook</span>
                <h2>FRL price vs the price you can actually get</h2>
              </div>
              <small>Enter decimal odds manually · no bookmaker feed in V1</small>
            </div>
            <div className={styles.marketGrid}>
              <MarketCard label={data.fixture.home_team_name} probability={probabilities.home_win} fairOdds={fairOdds.home_win} value={odds.home_win ?? ""} onChange={(value) => setOdds((current) => ({ ...current, home_win: value }))} />
              <MarketCard label="Draw" probability={probabilities.draw} fairOdds={fairOdds.draw} value={odds.draw ?? ""} onChange={(value) => setOdds((current) => ({ ...current, draw: value }))} />
              <MarketCard label={data.fixture.away_team_name} probability={probabilities.away_win} fairOdds={fairOdds.away_win} value={odds.away_win ?? ""} onChange={(value) => setOdds((current) => ({ ...current, away_win: value }))} />
              <MarketCard label="Over 2.5" probability={probabilities.over_2_5} fairOdds={fairOdds.over_2_5} value={odds.over_2_5 ?? ""} onChange={(value) => setOdds((current) => ({ ...current, over_2_5: value }))} />
              <MarketCard label="BTTS yes" probability={probabilities.btts} fairOdds={fairOdds.btts} value={odds.btts ?? ""} onChange={(value) => setOdds((current) => ({ ...current, btts: value }))} />
            </div>
            <p className={styles.footnote}>Positive model EV means the entered price is longer than FRL’s fair price. It is a model disagreement to investigate, not a betting instruction.</p>
          </div>
        )}

        {tab === "Model" && (
          <div className={styles.modelGrid}>
            <section className={styles.featureCard}>
              <span className={styles.kicker}>Transparent inputs</span>
              <h2>Why these λ values?</h2>
              <div className={styles.inputGrid}>
                {[
                  ["Home attack", prediction.inputs?.home_strength?.home_attack],
                  ["Home defence", prediction.inputs?.home_strength?.home_defence],
                  ["Away attack", prediction.inputs?.away_strength?.away_attack],
                  ["Away defence", prediction.inputs?.away_strength?.away_defence],
                ].map(([label, value]) => (
                  <article key={String(label)}>
                    <span>{label}</span>
                    <strong>{typeof value === "number" ? `${value.toFixed(2)}×` : "—"}</strong>
                    <small>league rate</small>
                  </article>
                ))}
              </div>
              <p className={styles.explainer}>Above 1.00 means more than the relevant league scoring/conceding average; below 1.00 means less. FRL combines the two teams’ strengths with the league home/away scoring environment to create the expected-goal rates.</p>
            </section>
            <section className={styles.featureCard}>
              <span className={styles.kicker}>Correct score</span>
              <h2>Most likely scorelines</h2>
              <div className={styles.scoreGrid}>
                {(prediction.correct_scores ?? []).slice(0, 8).map((score) => (
                  <article key={`${score.home}-${score.away}`}>
                    <strong>{score.home}–{score.away}</strong>
                    <span>{percent(score.probability)}</span>
                    <small>fair {decimal(score.fair_odds)}</small>
                  </article>
                ))}
              </div>
            </section>
          </div>
        )}
      </main>

      <footer className={styles.footerNote}>
        <strong>As-of discipline:</strong> this pack only uses completed fixture evidence before the selected kickoff for recent-form views. {data.limitations[2]}
      </footer>
    </div>
  );
}
