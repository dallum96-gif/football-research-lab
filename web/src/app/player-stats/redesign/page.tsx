import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { TeamCrest } from "@/components/TeamCrest";
import { PlayerStatsV2Controls, PlayerStatsV2Portrait } from "./PlayerStatsV2Client";
import styles from "./PlayerStatsRedesign.module.css";

type SeasonResponse = { seasons: string[] };

type PlayerOption = {
  player_code: string;
  player_name: string;
  position: string;
  clubs: string[];
  minutes: number;
  appearances: number;
  starts: number;
};

type PlayerBiography = {
  nationality?: string | null;
  nationality_code?: string | null;
  birth_date?: string | null;
  preferred_foot?: string | null;
  height_cm?: number | null;
  weight_kg?: number | null;
  shirt_number?: string | number | null;
  join_date?: string | null;
};

type PlayerProfile = {
  season: string;
  player_code: string;
  player_name: string;
  position: string;
  clubs: string[];
  primary_club?: string | null;
  portrait_player_code?: string | null;
  competition: string;
  appearances: number;
  starts: number;
  minutes: number;
  biography?: PlayerBiography;
};

type PlayerStatsMetric = {
  key: string;
  label: string;
  unit: string;
  family: string;
  higher_is_better: boolean;
  representation: string;
  value: number | null;
  rank: number | null;
  out_of: number;
  percentile: number | null;
  availability: string;
  observed_players: number;
  eligible_players: number;
};

type PlayerStatsResult = {
  analysis_version: string;
  season: string;
  player: PlayerOption;
  cohort: {
    competition: string;
    season: string;
    position: string;
    minimum_minutes: number;
    description: string;
  };
  overview_keys: string[];
  metrics: PlayerStatsMetric[];
  limitations: string[];
};

type RankingEntry = PlayerOption & {
  value: number | null;
  rank: number | null;
  out_of: number;
  percentile: number | null;
};

type RankingMetric = {
  key: string;
  label: string;
  unit: string;
  family: string;
  higher_is_better: boolean;
  entries: RankingEntry[];
};

type PlayerRankingsResult = {
  season: string;
  position: string;
  population_size: number;
  cohort: PlayerStatsResult["cohort"];
  metrics: RankingMetric[];
};

type RadarAxis = {
  key: string;
  label: string;
  metric_label: string;
  value: number | null;
  unit: string;
  percentile: number | null;
  average_percentile: number | null;
  rank: number | null;
  out_of: number;
  availability: "AVAILABLE" | "PARTIAL" | "UNAVAILABLE";
};

type RadarResult = {
  available: boolean;
  complete?: boolean;
  position: string;
  axes: RadarAxis[];
  summary: string;
  cohort: {
    description: string;
    minimum_minutes: number;
    population_size?: number;
  } | null;
  sample_status?: "QUALIFIED" | "PROVISIONAL" | "INSUFFICIENT_SAMPLE";
  sample_minutes?: number;
  qualification_minutes?: number;
  qualification_progress?: number;
  sample_message?: string;
};

type SearchQuery = {
  season?: string;
  player?: string;
  view?: string;
  family?: string;
  compare?: string;
};

const API_BASE = (process.env.NEXT_PUBLIC_FRL_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

const FAMILY_LABELS: Record<string, string> = {
  shooting: "Shooting",
  creation: "Creation",
  possession: "Possession",
  defending: "Defending",
  discipline: "Discipline",
  goalkeeping: "Goalkeeping",
  fpl: "FPL",
};

const KEY_METRICS_BY_POSITION: Record<string, string[]> = {
  GKP: [
    "saves_per_90",
    "saves_inside_box_per_90",
    "high_claims_per_90",
    "goals_conceded_per_90",
    "xgc_per_90",
    "clean_sheets_per_90",
    "keeper_sweeper_actions_per_90",
    "long_ball_accuracy",
  ],
  DEF: [
    "forward_passes_per_90",
    "recoveries_per_90",
    "tackles_per_90",
    "interceptions_won_per_90",
    "clearances_per_90",
    "aerial_duels_won_per_90",
    "duels_won_per_90",
    "key_passes_per_90",
    "assists_per_90",
    "goals_per_90",
  ],
  MID: [
    "forward_passes_per_90",
    "recoveries_per_90",
    "key_passes_per_90",
    "xa_per_90",
    "tackles_per_90",
    "interceptions_won_per_90",
    "successful_dribbles_per_90",
    "shots_per_90",
    "xg_per_90",
    "goals_per_90",
    "assists_per_90",
    "duels_won_per_90",
  ],
  FWD: [
    "xg_per_90",
    "goals_per_90",
    "shots_per_90",
    "shots_on_target_per_90",
    "key_passes_per_90",
    "xa_per_90",
    "assists_per_90",
    "successful_dribbles_per_90",
    "progressive_carries_per_90",
    "touches_per_90",
  ],
};

const SCATTER_KEYS_BY_POSITION: Record<string, [string, string]> = {
  GKP: ["saves_per_90", "high_claims_per_90"],
  DEF: ["forward_passes_per_90", "interceptions_won_per_90"],
  MID: ["forward_passes_per_90", "recoveries_per_90"],
  FWD: ["xg_per_90", "goals_per_90"],
};

async function getJson<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

function positionLabel(position: string) {
  return ({ GKP: "Goalkeeper", DEF: "Defender", MID: "Midfielder", FWD: "Forward" } as Record<string, string>)[position] ?? position;
}

function formatDate(value?: string | null) {
  if (!value) return "—";
  const parsed = new Date(`${value}T00:00:00Z`);
  if (Number.isNaN(parsed.getTime())) return value;
  return new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" }).format(parsed);
}

function trim(value: number, decimals = 2) {
  return value.toFixed(decimals).replace(/\.0+$|(?<=\.[0-9]*?)0+$/g, "").replace(/\.$/, "");
}

function formatMetric(metric: { unit: string; label?: string }, value: number | null) {
  if (value == null) return "—";
  if (metric.unit === "%") return `${trim(value, 1)}%`;
  if (Number.isInteger(value)) return String(value);
  return trim(value, 2);
}

function percentileLabel(value: number | null) {
  return value == null ? "—" : `P${Math.round(value)}`;
}

function viewHref(season: string, player: string, view: string, family?: string) {
  const params = new URLSearchParams({ season, player, view });
  if (family) params.set("family", family);
  return `/player-stats/redesign?${params.toString()}`;
}

function polarPoint(index: number, count: number, percent: number, radius: number, cx: number, cy: number) {
  const angle = -Math.PI / 2 + (Math.PI * 2 * index) / count;
  const ratio = Math.max(0, Math.min(100, percent)) / 100;
  return `${cx + Math.cos(angle) * radius * ratio},${cy + Math.sin(angle) * radius * ratio}`;
}

function radarPolygon(values: number[], radius = 92, cx = 130, cy = 118) {
  return values.map((value, index) => polarPoint(index, values.length, value, radius, cx, cy)).join(" ");
}

function Fingerprint({ radar }: { radar: RadarResult }) {
  const axes = radar.axes.filter((axis) => axis.percentile != null);
  if (!radar.available || axes.length !== 6) {
    return (
      <div className={styles.pendingPanel}>
        <span>Statistical fingerprint pending</span>
        <p>{radar.sample_message ?? "Comparable Player-Season evidence is not available yet."}</p>
      </div>
    );
  }

  const rings = [25, 50, 75, 100];
  const values = axes.map((axis) => axis.percentile ?? 0);
  return (
    <svg className={styles.radar} viewBox="0 0 260 250" role="img" aria-label="Position percentile fingerprint">
      {rings.map((ring) => (
        <polygon key={ring} points={radarPolygon(Array(axes.length).fill(ring))} className={styles.radarRing} />
      ))}
      {axes.map((axis, index) => {
        const outer = polarPoint(index, axes.length, 100, 92, 130, 118).split(",").map(Number);
        const label = polarPoint(index, axes.length, 124, 92, 130, 118).split(",").map(Number);
        return (
          <g key={axis.key}>
            <line x1="130" y1="118" x2={outer[0]} y2={outer[1]} className={styles.radarAxis} />
            <text x={label[0]} y={label[1]} textAnchor="middle" className={styles.radarLabel}>{axis.label}</text>
            <text x={label[0]} y={label[1] + 13} textAnchor="middle" className={styles.radarValue}>{percentileLabel(axis.percentile)}</text>
          </g>
        );
      })}
      <polygon points={radarPolygon(values)} className={styles.radarShape} />
      {values.map((value, index) => {
        const [x, y] = polarPoint(index, values.length, value, 92, 130, 118).split(",").map(Number);
        return <circle key={`${axes[index].key}-dot`} cx={x} cy={y} r="3.2" className={styles.radarDot} />;
      })}
    </svg>
  );
}

function MetricRows({ metrics, compact = false }: { metrics: PlayerStatsMetric[]; compact?: boolean }) {
  return (
    <div className={compact ? styles.metricRowsCompact : styles.metricRows}>
      {metrics.map((metric) => (
        <div className={styles.metricRow} key={metric.key}>
          <div className={styles.metricName}>
            <span>{metric.label}</span>
            <small>{formatMetric(metric, metric.value)}</small>
          </div>
          <div className={styles.metricBar} aria-label={`${metric.label} ${percentileLabel(metric.percentile)}`}>
            <span style={{ width: `${Math.max(0, Math.min(100, metric.percentile ?? 0))}%` }} />
          </div>
          <strong>{percentileLabel(metric.percentile)}</strong>
        </div>
      ))}
    </div>
  );
}

function ScatterPlot({
  rankings,
  xKey,
  yKey,
  playerCode,
  compareCode,
}: {
  rankings: PlayerRankingsResult;
  xKey: string;
  yKey: string;
  playerCode: string;
  compareCode?: string;
}) {
  const xMetric = rankings.metrics.find((metric) => metric.key === xKey);
  const yMetric = rankings.metrics.find((metric) => metric.key === yKey);
  if (!xMetric || !yMetric) return <div className={styles.pendingPanel}>Relationship plot unavailable for this cohort.</div>;

  const yByPlayer = new Map(yMetric.entries.map((entry) => [entry.player_code, entry]));
  const points = xMetric.entries
    .map((entry) => ({ x: entry, y: yByPlayer.get(entry.player_code) }))
    .filter((pair): pair is { x: RankingEntry; y: RankingEntry } => pair.x.value != null && pair.y?.value != null);

  if (points.length < 2) return <div className={styles.pendingPanel}>Not enough observed evidence for this relationship plot.</div>;

  const xValues = points.map((point) => point.x.value as number);
  const yValues = points.map((point) => point.y.value as number);
  const xMin = Math.min(...xValues);
  const xMax = Math.max(...xValues);
  const yMin = Math.min(...yValues);
  const yMax = Math.max(...yValues);
  const width = 620;
  const height = 330;
  const pad = 42;
  const xScale = (value: number) => pad + ((value - xMin) / Math.max(0.0001, xMax - xMin)) * (width - pad * 2);
  const yScale = (value: number) => height - pad - ((value - yMin) / Math.max(0.0001, yMax - yMin)) * (height - pad * 2);

  return (
    <div className={styles.scatterWrap}>
      <svg className={styles.scatter} viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`${xMetric.label} against ${yMetric.label}`}>
        {[0.25, 0.5, 0.75].map((ratio) => (
          <g key={ratio}>
            <line x1={pad} x2={width - pad} y1={pad + (height - pad * 2) * ratio} y2={pad + (height - pad * 2) * ratio} className={styles.scatterGrid} />
            <line y1={pad} y2={height - pad} x1={pad + (width - pad * 2) * ratio} x2={pad + (width - pad * 2) * ratio} className={styles.scatterGrid} />
          </g>
        ))}
        <line x1={pad} x2={width - pad} y1={height - pad} y2={height - pad} className={styles.scatterAxis} />
        <line x1={pad} x2={pad} y1={pad} y2={height - pad} className={styles.scatterAxis} />
        {points.map(({ x, y }) => {
          const highlighted = x.player_code === playerCode;
          const compared = compareCode && x.player_code === compareCode;
          return (
            <circle
              key={x.player_code}
              cx={xScale(x.value as number)}
              cy={yScale(y.value as number)}
              r={highlighted || compared ? 6.5 : 3.2}
              className={highlighted ? styles.scatterPrimary : compared ? styles.scatterCompare : styles.scatterPoint}
            >
              <title>{`${x.player_name}: ${xMetric.label} ${formatMetric(xMetric, x.value)}, ${yMetric.label} ${formatMetric(yMetric, y.value)}`}</title>
            </circle>
          );
        })}
        <text x={width / 2} y={height - 8} textAnchor="middle" className={styles.scatterLabel}>{xMetric.label}</text>
        <text x="14" y={height / 2} textAnchor="middle" transform={`rotate(-90 14 ${height / 2})`} className={styles.scatterLabel}>{yMetric.label}</text>
      </svg>
      <div className={styles.scatterLegend}>
        <span><i className={styles.legendPrimary} /> Selected player</span>
        {compareCode ? <span><i className={styles.legendCompare} /> Comparison player</span> : null}
        <span><i /> Same-position cohort</span>
      </div>
    </div>
  );
}

export const dynamic = "force-dynamic";

export default async function PlayerStatsRedesignPage({ searchParams }: { searchParams: Promise<SearchQuery> }) {
  const query = await searchParams;
  const seasonResponse = await getJson<SeasonResponse>("/api/v1/seasons");
  const seasons = seasonResponse?.seasons ?? [];
  const season = query.season && seasons.includes(query.season) ? query.season : seasons[0];

  if (!season) {
    return <AppShell><div className={styles.empty}>No governed Player Stats season is available.</div></AppShell>;
  }

  const players = (await getJson<PlayerOption[]>(`/api/v1/players/${encodeURIComponent(season)}`)) ?? [];
  const eligiblePlayers = players.filter((player) => player.minutes > 0);
  const requested = query.player && eligiblePlayers.find((player) => player.player_code === query.player);
  const fallback = eligiblePlayers.find((player) => player.player_name === "Declan Rice") ?? eligiblePlayers[0];
  const selected = requested ?? fallback;

  if (!selected) {
    return <AppShell><div className={styles.empty}>No player with recorded minutes is available for {season}.</div></AppShell>;
  }

  const playerCode = selected.player_code;
  const [stats, profile, radar, rankings] = await Promise.all([
    getJson<PlayerStatsResult>(`/api/v1/player-stats/${encodeURIComponent(season)}/${encodeURIComponent(playerCode)}`),
    getJson<PlayerProfile>(`/api/v1/players/${encodeURIComponent(season)}/${encodeURIComponent(playerCode)}`),
    getJson<RadarResult>(`/api/v1/player-profile-radar/${encodeURIComponent(season)}/${encodeURIComponent(playerCode)}`),
    getJson<PlayerRankingsResult>(`/api/v1/player-stats/${encodeURIComponent(season)}/rankings/${encodeURIComponent(selected.position)}`),
  ]);

  if (!stats || !profile || !radar || !rankings) {
    return <AppShell><div className={styles.empty}>The governed Player Stats workspace could not be assembled for this player.</div></AppShell>;
  }

  const club = profile.primary_club ?? profile.clubs[0] ?? "Club unavailable";
  const biography = profile.biography ?? {};
  const activeView = query.view === "explore" || query.view === "compare" ? query.view : "overview";
  const availableFamilies = Array.from(new Set(stats.metrics.map((metric) => metric.family))).filter((family) => family !== "overview");
  const activeFamily = query.family && availableFamilies.includes(query.family) ? query.family : availableFamilies[0] ?? "shooting";

  const metricByKey = new Map(stats.metrics.map((metric) => [metric.key, metric]));
  const preferredKeys = KEY_METRICS_BY_POSITION[selected.position] ?? stats.overview_keys;
  const keyMetrics = preferredKeys
    .map((key) => metricByKey.get(key))
    .filter((metric): metric is PlayerStatsMetric => Boolean(metric && metric.percentile != null))
    .slice(0, 12);

  const headlineAxes = [...radar.axes]
    .filter((axis) => axis.percentile != null)
    .sort((a, b) => (b.percentile ?? -1) - (a.percentile ?? -1))
    .slice(0, 4);
  const rankedAxes = [...radar.axes].filter((axis) => axis.percentile != null).sort((a, b) => (b.percentile ?? 0) - (a.percentile ?? 0));
  const strongest = rankedAxes.slice(0, 3);
  const lower = [...rankedAxes].sort((a, b) => (a.percentile ?? 0) - (b.percentile ?? 0)).slice(0, 3);

  const samePositionPlayers = eligiblePlayers
    .filter((player) => player.position === selected.position && player.player_code !== playerCode)
    .sort((a, b) => b.minutes - a.minutes || a.player_name.localeCompare(b.player_name));
  const requestedCompare = query.compare && samePositionPlayers.find((player) => player.player_code === query.compare);
  const comparePlayer = requestedCompare ?? (activeView === "compare" ? samePositionPlayers[0] : undefined);
  const compareStats = comparePlayer
    ? await getJson<PlayerStatsResult>(`/api/v1/player-stats/${encodeURIComponent(season)}/${encodeURIComponent(comparePlayer.player_code)}`)
    : null;

  const compareMetricMap = new Map((compareStats?.metrics ?? []).map((metric) => [metric.key, metric]));
  const familyMetrics = stats.metrics.filter((metric) => metric.family === activeFamily && metric.percentile != null);
  const [scatterX, scatterY] = SCATTER_KEYS_BY_POSITION[selected.position] ?? [stats.overview_keys[0], stats.overview_keys[1]];
  const sampleStatus = radar.sample_status ?? "INSUFFICIENT_SAMPLE";
  const qualificationMinutes = radar.qualification_minutes ?? radar.cohort?.minimum_minutes ?? 0;
  const qualificationProgress = Math.round(Math.max(0, Math.min(1, radar.qualification_progress ?? 0)) * 100);

  return (
    <AppShell>
      <div className={styles.page}>
        <div className={styles.inner}>
          <header className={styles.hero}>
            <section className={styles.heroCopy}>
              <p className={styles.eyebrow}>Player Stats</p>
              <h1>{profile.player_name}</h1>
              <p className={styles.identityLine}>{club} <span>·</span> {profile.position} <span>·</span> {biography.nationality ?? profile.competition}</p>
              <p className={styles.heroSummary}>{radar.summary || `Current-season analytical profile for ${profile.player_name}.`}</p>
              <div className={styles.heroActions}>
                <Link className={styles.primaryAction} href={`/players/${encodeURIComponent(season)}/${encodeURIComponent(playerCode)}`}>View Player Profile →</Link>
                <Link className={styles.secondaryAction} href={viewHref(season, playerCode, "compare")}>Add to Compare +</Link>
              </div>
            </section>

            <div className={styles.portraitStage}>
              <PlayerStatsV2Portrait playerCode={profile.portrait_player_code ?? playerCode} playerName={profile.player_name} club={club} />
            </div>

            <aside className={styles.identityRail}>
              <div className={styles.railHeading}>
                <span>{positionLabel(profile.position)} · {biography.shirt_number ?? "—"}</span>
                <strong>{radar.cohort?.population_size ?? "—"} qualified peers</strong>
              </div>
              <dl>
                <div><dt>Born</dt><dd>{formatDate(biography.birth_date)}</dd></div>
                <div><dt>Nationality</dt><dd>{biography.nationality ?? "—"}</dd></div>
                <div><dt>Height</dt><dd>{biography.height_cm ? `${Math.round(biography.height_cm)} cm` : "—"}</dd></div>
                <div><dt>Preferred foot</dt><dd>{biography.preferred_foot ?? "—"}</dd></div>
                <div><dt>Joined</dt><dd>{formatDate(biography.join_date)}</dd></div>
              </dl>
              <div className={styles.crestLine}><TeamCrest teamName={club} size={54} /><span>{club}</span></div>
            </aside>
          </header>

          <section className={styles.controlBar}>
            <nav className={styles.modeTabs} aria-label="Player Stats modes">
              {(["overview", "explore", "compare"] as const).map((view) => (
                <Link key={view} className={activeView === view ? styles.modeActive : styles.modeLink} href={viewHref(season, playerCode, view)}>{view[0].toUpperCase() + view.slice(1)}</Link>
              ))}
            </nav>
            <PlayerStatsV2Controls seasons={seasons} players={eligiblePlayers} season={season} playerCode={playerCode} view={activeView} />
            <div className={styles.sampleState} data-status={sampleStatus}>
              <i />
              <span>{radar.sample_minutes ?? profile.minutes} minutes · {sampleStatus.toLowerCase().replaceAll("_", " ")}</span>
            </div>
          </section>

          {activeView === "overview" ? (
            <main className={styles.workspace}>
              <section className={styles.headlineGrid}>
                {headlineAxes.map((axis, index) => (
                  <article className={styles.headlineCard} data-tone={index} key={axis.key}>
                    <span className={styles.headlineLabel}>{axis.label}</span>
                    <div><strong>{percentileLabel(axis.percentile)}</strong><span className={styles.headlineBar}><i style={{ width: `${axis.percentile ?? 0}%` }} /></span></div>
                    <small>{axis.metric_label}</small>
                  </article>
                ))}
              </section>

              <section className={styles.overviewGrid}>
                <article className={styles.fingerprintPanel}>
                  <header className={styles.panelHeading}>
                    <div><p>Player fingerprint</p><h2>Position percentile profile</h2></div>
                    <span>{sampleStatus === "PROVISIONAL" ? "Indicative" : "Qualified cohort"}</span>
                  </header>
                  <Fingerprint radar={radar} />
                  <p className={styles.panelNote}>{radar.cohort?.description ?? radar.sample_message}</p>
                </article>

                <article className={styles.metricsPanel}>
                  <header className={styles.panelHeading}>
                    <div><p>Key metrics</p><h2>Performance evidence</h2></div>
                    <Link href={viewHref(season, playerCode, "explore", activeFamily)}>View full breakdown →</Link>
                  </header>
                  <MetricRows metrics={keyMetrics} />
                  <p className={styles.panelNote}>Exploratory Player Stats percentiles use the current same-position Player Stats cohort: {stats.cohort.description}.</p>
                </article>

                <aside className={styles.contextStack}>
                  <section className={styles.contextPanel}>
                    <header><p>Player context</p><h2>Current sample</h2></header>
                    <dl>
                      <div><dt>Minutes</dt><dd>{profile.minutes}</dd></div>
                      <div><dt>Appearances</dt><dd>{profile.appearances}</dd></div>
                      <div><dt>Starts</dt><dd>{profile.starts}</dd></div>
                      <div><dt>Position</dt><dd>{positionLabel(profile.position)}</dd></div>
                      <div><dt>Qualification</dt><dd>{qualificationMinutes ? `${qualificationMinutes} min` : "—"}</dd></div>
                      <div><dt>Progress</dt><dd>{qualificationMinutes ? `${qualificationProgress}%` : "—"}</dd></div>
                    </dl>
                  </section>

                  <section className={styles.signalPanel}>
                    <header><p>Profile signals</p><h2>Relative markers</h2></header>
                    <h3>Highest percentiles</h3>
                    {strongest.map((axis) => <div className={styles.signalRow} key={`high-${axis.key}`}><span>{axis.label}</span><strong>{percentileLabel(axis.percentile)}</strong></div>)}
                    <h3>Lower percentiles</h3>
                    {lower.map((axis) => <div className={styles.signalRow} key={`low-${axis.key}`}><span>{axis.label}</span><strong>{percentileLabel(axis.percentile)}</strong></div>)}
                    <small>Descriptive ranking markers, not causal strengths or weaknesses.</small>
                  </section>
                </aside>
              </section>

              <section className={styles.bottomGrid}>
                <article className={styles.compareDoorway}>
                  <header className={styles.panelHeading}><div><p>Compare players</p><h2>Put the profile in context</h2></div><Link href={viewHref(season, playerCode, "compare")}>Open Compare →</Link></header>
                  <div className={styles.compareCandidates}>
                    <div className={styles.selectedChip}><strong>{profile.player_name}</strong><span>{club}</span></div>
                    {samePositionPlayers.slice(0, 3).map((player) => (
                      <Link key={player.player_code} href={`${viewHref(season, playerCode, "compare")}&compare=${encodeURIComponent(player.player_code)}`}><strong>{player.player_name}</strong><span>{player.clubs[0] ?? "Club unavailable"} · {player.minutes} min</span></Link>
                    ))}
                  </div>
                </article>
                <aside className={styles.methodStrip}>
                  <span>Evidence status</span>
                  <strong>{sampleStatus.replaceAll("_", " ")}</strong>
                  <p>{radar.sample_message ?? `Position-profile threshold: ${qualificationMinutes} minutes.`}</p>
                </aside>
              </section>
            </main>
          ) : null}

          {activeView === "explore" ? (
            <main className={styles.workspace}>
              <section className={styles.exploreHeader}>
                <div><p className={styles.eyebrow}>Explore evidence</p><h2>Every governed Player Stats family</h2><p>Move through the metric library without changing the selected player or comparison context.</p></div>
                <nav aria-label="Metric families">
                  {availableFamilies.map((family) => <Link key={family} className={activeFamily === family ? styles.familyActive : styles.familyLink} href={viewHref(season, playerCode, "explore", family)}>{FAMILY_LABELS[family] ?? family}</Link>)}
                </nav>
              </section>
              <section className={styles.exploreLedger}>
                <header className={styles.panelHeading}><div><p>{FAMILY_LABELS[activeFamily] ?? activeFamily}</p><h2>Metric ledger</h2></div><span>{familyMetrics.length} observed metrics</span></header>
                <MetricRows metrics={familyMetrics} />
              </section>
              <section className={styles.methodPanel}>
                <strong>Comparison population</strong>
                <p>{stats.cohort.description}. This existing Player Stats cohort is deliberately shown as exploratory; the stricter Profile sample-state contract remains separate until the broader Player Stats cohort semantics are governed.</p>
              </section>
            </main>
          ) : null}

          {activeView === "compare" ? (
            <main className={styles.workspace}>
              <section className={styles.compareHeader}>
                <div><p className={styles.eyebrow}>Compare</p><h2>{profile.player_name} against another {positionLabel(profile.position).toLowerCase()}</h2><p>Direct metric evidence plus a curated relationship plot. The plot uses observed values from the existing same-position Player Stats cohort.</p></div>
                <form className={styles.compareForm} method="get" action="/player-stats/redesign">
                  <input type="hidden" name="season" value={season} />
                  <input type="hidden" name="player" value={playerCode} />
                  <input type="hidden" name="view" value="compare" />
                  <label><span>Comparison player</span><select name="compare" defaultValue={comparePlayer?.player_code ?? ""}>{samePositionPlayers.map((player) => <option key={player.player_code} value={player.player_code}>{player.player_name} · {player.clubs[0] ?? "Club"}</option>)}</select></label>
                  <button type="submit">Compare →</button>
                </form>
              </section>

              <section className={styles.compareGrid}>
                <article className={styles.scatterPanel}>
                  <header className={styles.panelHeading}><div><p>Relationship plot</p><h2>{rankings.metrics.find((metric) => metric.key === scatterX)?.label ?? scatterX} × {rankings.metrics.find((metric) => metric.key === scatterY)?.label ?? scatterY}</h2></div><span>{rankings.population_size} players</span></header>
                  <ScatterPlot rankings={rankings} xKey={scatterX} yKey={scatterY} playerCode={playerCode} compareCode={comparePlayer?.player_code} />
                </article>
                <article className={styles.directComparePanel}>
                  <header className={styles.panelHeading}><div><p>Direct comparison</p><h2>{comparePlayer ? `${profile.player_name} vs ${comparePlayer.player_name}` : profile.player_name}</h2></div></header>
                  {comparePlayer && compareStats ? (
                    <div className={styles.compareTable}>
                      <div className={styles.compareTableHead}><span>Metric</span><strong>{profile.player_name.split(" ").slice(-1)[0]}</strong><strong>{comparePlayer.player_name.split(" ").slice(-1)[0]}</strong></div>
                      {keyMetrics.slice(0, 8).map((metric) => {
                        const other = compareMetricMap.get(metric.key);
                        return <div className={styles.compareTableRow} key={metric.key}><span>{metric.label}</span><strong>{formatMetric(metric, metric.value)} <small>{percentileLabel(metric.percentile)}</small></strong><strong>{other ? formatMetric(other, other.value) : "—"} <small>{other ? percentileLabel(other.percentile) : "—"}</small></strong></div>;
                      })}
                    </div>
                  ) : <div className={styles.pendingPanel}>Select a comparison player to open the direct evidence view.</div>}
                </article>
              </section>

              <section className={styles.methodPanel}><strong>Compare semantics</strong><p>This V2 preview visualises governed values already returned by Player Stats. It does not yet claim role similarity, causal strengths or a bespoke similarity score.</p></section>
            </main>
          ) : null}
        </div>
      </div>
    </AppShell>
  );
}
