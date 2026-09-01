import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { PlayerDirectorySelect } from "./PlayerDirectorySelect";
import { PlayersDirectoryGrid } from "./PlayersDirectoryGrid";
import styles from "./PlayersDirectory.module.css";

type SeasonResponse = {
  seasons: string[];
};

type PlayerOption = {
  player_code: string;
  player_name: string;
  position: string;
  clubs: string[];
  minutes: number;
  appearances: number;
};

const API_BASE =
  process.env.NEXT_PUBLIC_FRL_API_URL ?? "http://127.0.0.1:8000";

async function getJson<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export default async function PlayersPage({
  searchParams,
}: {
  searchParams: Promise<{ season?: string }>;
}) {
  const query = await searchParams;
  const seasonResponse = await getJson<SeasonResponse>("/api/v1/seasons");
  const seasons = seasonResponse?.seasons ?? [];
  const season =
    query.season && seasons.includes(query.season)
      ? query.season
      : seasons[0];

  const players = season
    ? (await getJson<PlayerOption[]>(
        `/api/v1/players/${encodeURIComponent(season)}`
      )) ?? []
    : [];

  return (
    <AppShell>
      <div className={styles.page}>
        <header className={styles.profileHeader}>
          <div className={styles.identity}>
            <span className={styles.monogram}>P</span>
            <div>
              <p className={styles.eyebrow}>Explore</p>
              <h1>Players</h1>
              <p className={styles.context}>
                Premier League · {season ?? "Season unavailable"}
              </p>
            </div>
          </div>

          {season && (
            <PlayerDirectorySelect
              currentSeason={season}
              seasons={seasons}
            />
          )}
        </header>

        <nav className={styles.tabs} aria-label="Player workspace">
          <span className={styles.activeTab}>Player profiles</span>
          {season && players.some((player) => player.minutes > 0) && (
            <Link
              href={`/player-stats?season=${encodeURIComponent(season)}`}
              className={styles.tabLink}
            >
              Player Stats →
            </Link>
          )}
        </nav>

        <main className={styles.workspace}>
          {season && players.length > 0 ? (
            <PlayersDirectoryGrid season={season} players={players} />
          ) : (
            <div className="frl-empty-state">
              No governed player profiles are available for this season.
            </div>
          )}
        </main>
      </div>
    </AppShell>
  );
}
