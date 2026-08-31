import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { PlayerDirectorySelect } from "./PlayerDirectorySelect";
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

const POSITION_LABELS: Record<string, string> = {
  GKP: "Goalkeepers",
  DEF: "Defenders",
  MID: "Midfielders",
  FWD: "Forwards",
};

const POSITION_ORDER = ["GKP", "DEF", "MID", "FWD"];

async function getJson<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
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

  const groups = POSITION_ORDER.map((position) => ({
    position,
    label: POSITION_LABELS[position],
    players: players
      .filter((player) => player.position === position)
      .sort((a, b) => a.player_name.localeCompare(b.player_name)),
  })).filter((group) => group.players.length > 0);

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
          {groups.length > 0 ? (
            <div className={styles.groups}>
              {groups.map((group) => (
                <section className={styles.group} key={group.position}>
                  <header className={styles.sectionHeading}>
                    <div>
                      <p className={styles.sectionKicker}>{group.position}</p>
                      <h2>{group.label}</h2>
                    </div>
                    <span>{group.players.length} players</span>
                  </header>

                  <div className={styles.playerGrid}>
                    {group.players.map((player) => (
                      <Link
                        key={player.player_code}
                        href={`/players/${encodeURIComponent(
                          season ?? ""
                        )}/${encodeURIComponent(player.player_code)}`}
                        className={styles.playerLink}
                      >
                        <span className={styles.avatar}>
                          {initials(player.player_name)}
                        </span>
                        <span className={styles.playerIdentity}>
                          <strong>{player.player_name}</strong>
                          <small>
                            {player.clubs.join(" · ") || "Club unavailable"}
                          </small>
                        </span>
                        <span className={styles.playerMeta}>
                          <strong>{player.appearances}</strong>
                          <small>apps</small>
                        </span>
                        <span className={styles.action}>Profile →</span>
                      </Link>
                    ))}
                  </div>
                </section>
              ))}
            </div>
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
