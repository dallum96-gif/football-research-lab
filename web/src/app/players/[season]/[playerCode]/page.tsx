import Link from "next/link";
import { notFound } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { PlayerSeasonSelect } from "./PlayerSeasonSelect";
import styles from "./PlayerProfile.module.css";

type PlayerProfileMetric = {
  key: string;
  label: string;
  value: number | null;
  unit: string;
};

type PlayerProfile = {
  season: string;
  player_code: string;
  player_name: string;
  position: string;
  clubs: string[];
  competition: string;
  appearances: number;
  starts: number;
  minutes: number;
  metrics: PlayerProfileMetric[];
  evidence: Record<string, unknown>;
  limitations: string[];
};

type PlayerSeasonOption = {
  season: string;
  player_code: string;
  player_name: string;
  position: string;
  clubs: string[];
};

const API_BASE = (
  process.env.NEXT_PUBLIC_FRL_API_URL ?? "http://127.0.0.1:8000"
).replace(/\/$/, "");

async function getJson<T>(path: string): Promise<{ ok: boolean; status: number; data?: T }> {
  try {
    const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
    if (!response.ok) return { ok: false, status: response.status };
    return { ok: true, status: response.status, data: (await response.json()) as T };
  } catch {
    return { ok: false, status: 503 };
  }
}

function initials(name: string) {
  return (
    name
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase())
      .join("") || "P"
  );
}

function formatNumber(value: number | null, unit: string) {
  if (value == null) return "—";
  if (Number.isInteger(value)) return String(value);
  if (unit === "%") return `${value.toFixed(1)}%`;
  if (["xG", "xA", "xGI", "xGC"].includes(unit)) return value.toFixed(2);
  return value.toFixed(1).replace(/\.0$/, "");
}

export const dynamic = "force-dynamic";

export default async function PlayerProfilePage({
  params,
}: {
  params: Promise<{ season: string; playerCode: string }>;
}) {
  const { season, playerCode } = await params;

  const [profileResult, seasonsResult] = await Promise.all([
    getJson<PlayerProfile>(
      `/api/v1/players/${encodeURIComponent(season)}/${encodeURIComponent(playerCode)}`
    ),
    getJson<PlayerSeasonOption[]>(
      `/api/v1/player-seasons/${encodeURIComponent(playerCode)}`
    ),
  ]);

  if (!profileResult.ok || !profileResult.data) {
    if (profileResult.status === 404) notFound();
    throw new Error(`FRL Player Profile request failed: ${profileResult.status}`);
  }

  const profile = profileResult.data;
  const seasonOptions = seasonsResult.ok && seasonsResult.data
    ? seasonsResult.data
    : [
        {
          season,
          player_code: playerCode,
          player_name: profile.player_name,
          position: profile.position,
          clubs: profile.clubs,
        },
      ];

  const featured = profile.metrics.filter((metric) =>
    ["goals", "assists", "xg", "xa", "xgi", "saves", "tackles", "recoveries"].includes(
      metric.key
    )
  );

  return (
    <AppShell>
      <div className={styles.page}>
        <header className={styles.profileHeader}>
          <div className={styles.identity}>
            <span className={styles.avatar}>{initials(profile.player_name)}</span>
            <div>
              <p className={styles.eyebrow}>Player profile</p>
              <h1>{profile.player_name}</h1>
              <p className={styles.context}>
                {profile.clubs.join(" · ") || "Club unavailable"} · {profile.position} · {profile.season}
              </p>
            </div>
          </div>

          <PlayerSeasonSelect
            currentSeason={season}
            playerCode={playerCode}
            seasons={seasonOptions}
          />
        </header>

        <nav className={styles.tabs} aria-label="Player profile views">
          <span className={styles.activeTab}>Overview</span>
          {profile.minutes > 0 && (
            <Link
              className={styles.tabLink}
              href={`/player-stats?season=${encodeURIComponent(
                season
              )}&player=${encodeURIComponent(playerCode)}`}
            >
              View in Player Stats →
            </Link>
          )}
        </nav>

        <main className={styles.workspace}>
          <section className={styles.headlineStrip}>
            <div><strong>{profile.appearances}</strong><span>Appearances</span></div>
            <div><strong>{profile.starts}</strong><span>Starts</span></div>
            <div><strong>{profile.minutes}</strong><span>Minutes</span></div>
            <div><strong>{profile.position}</strong><span>Listed position</span></div>
          </section>

          <section className={styles.contentGrid}>
            <article className={styles.metricPanel}>
              <header className={styles.sectionHeading}>
                <div>
                  <p className={styles.kicker}>Season output</p>
                  <h2>What the source records</h2>
                </div>
                <span>{profile.metrics.length} available measures</span>
              </header>

              <div className={styles.metricGrid}>
                {featured.map((metric) => (
                  <div className={styles.metricCard} key={metric.key}>
                    <span>{metric.label}</span>
                    <strong>{formatNumber(metric.value, metric.unit)}</strong>
                  </div>
                ))}
              </div>
            </article>

            <article className={styles.readPanel}>
              <p className={styles.kicker}>Profile boundary</p>
              <h2>Identity and season story</h2>
              <p>
                This surface stays descriptive. Position-aware ranks, percentiles,
                league distributions and per-90 analysis live in Player Stats.
              </p>
              {profile.minutes > 0 ? (
                <Link
                  className={styles.primaryAction}
                  href={`/player-stats?season=${encodeURIComponent(
                    season
                  )}&player=${encodeURIComponent(playerCode)}`}
                >
                  Measure {profile.player_name.split(" ")[0]} →
                </Link>
              ) : (
                <span className={styles.unavailable}>No recorded minutes yet.</span>
              )}
            </article>
          </section>

          <section className={styles.sourcePanel}>
            <div>
              <p className={styles.kicker}>Evidence</p>
              <strong>Governed player-season aggregate</strong>
            </div>
            <p>
              {profile.limitations[0] ?? "Season player evidence retained with source provenance."}
            </p>
          </section>
        </main>
      </div>
    </AppShell>
  );
}
