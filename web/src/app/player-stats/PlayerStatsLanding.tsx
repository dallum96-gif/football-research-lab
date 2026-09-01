import Link from "next/link";
import { ClubKit } from "@/components/ClubKit";
import type { RankingMetric } from "./PlayerVisuals";
import { PlayerStatsSearch } from "./PlayerStatsSearch";
import styles from "./PlayerStatsDiscovery.module.css";

type PlayerOption = {
  player_code: string;
  player_name: string;
  position: string;
  clubs: string[];
  minutes: number;
  appearances: number;
  starts: number;
};

type PositionRanking = {
  position: string;
  metrics: RankingMetric[];
};

const CARD_SIGNALS: Array<{
  position: string;
  metricKey: string;
  label: string;
}> = [
  { position: "FWD", metricKey: "goals_per_90", label: "Scoring output" },
  { position: "MID", metricKey: "xgi_per_90", label: "Attacking involvement" },
  { position: "DEF", metricKey: "defensive_contribution_per_90", label: "Defensive contribution" },
  { position: "GKP", metricKey: "saves_per_90", label: "Save workload" },
];

function trim(value: number, decimals = 2) {
  const fixed = value.toFixed(decimals);
  return fixed.includes(".")
    ? fixed.replace(/0+$/, "").replace(/\.$/, "")
    : fixed;
}

function formatMetric(metric: RankingMetric, value: number | null) {
  if (value == null) return "—";
  if (metric.unit === "%") return `${trim(value, 1)}%`;
  return trim(value, Number.isInteger(value) ? 0 : 2);
}

function discoveryCard(
  rankingsByPosition: Record<string, PositionRanking | null>,
  position: string,
  metricKey: string
) {
  const ranking = rankingsByPosition[position];
  const metric = ranking?.metrics.find((candidate) => candidate.key === metricKey);
  if (!metric) return null;

  const entry = metric.entries
    .filter((candidate) => candidate.value != null && candidate.minutes >= 60)
    .sort((a, b) => {
      const left = a.percentile ?? -1;
      const right = b.percentile ?? -1;
      return right - left || b.minutes - a.minutes;
    })[0];

  return entry ? { metric, entry } : null;
}

export function PlayerStatsLanding({
  season,
  players,
  rankingsByPosition,
}: {
  season: string;
  players: PlayerOption[];
  rankingsByPosition: Record<string, PositionRanking | null>;
}) {
  const cards = CARD_SIGNALS.map((signal) => ({
    ...signal,
    result: discoveryCard(rankingsByPosition, signal.position, signal.metricKey),
  })).filter((card) => card.result);

  return (
    <main className={styles.landing}>
      <section className={styles.searchHero}>
        <div className={styles.heroCopy}>
          <p>Player discovery</p>
          <h2>Start with a name, a club, or someone worth exploring.</h2>
          <span>
            Search the governed Premier League player database directly. Nothing is pre-selected, so Player View now starts as a discovery surface rather than dropping you into an arbitrary player.
          </span>
        </div>
        <PlayerStatsSearch season={season} players={players} />
      </section>

      <section className={styles.discoverySection}>
        <header className={styles.sectionHeading}>
          <div>
            <p>Worth a look</p>
            <h2>Players to explore</h2>
          </div>
          <span>
            Four position-specific governed signals. These are discovery prompts, not a single cross-position ranking.
          </span>
        </header>

        <div className={styles.cardGrid}>
          {cards.map((card) => {
            const result = card.result!;
            const club = result.entry.clubs[0] ?? "Premier League";

            return (
              <Link
                key={`${card.position}-${result.entry.player_code}`}
                href={`/player-stats?season=${encodeURIComponent(season)}&player=${encodeURIComponent(result.entry.player_code)}`}
                className={styles.playerCard}
              >
                <div className={styles.cardTop}>
                  <div className={styles.shirtStage}>
                    <ClubKit club={club} size="large" />
                  </div>
                  <span className={styles.positionBadge}>{card.position}</span>
                </div>

                <div className={styles.cardBody}>
                  <h3>{result.entry.player_name}</h3>
                  <p className={styles.cardClub}>{club}</p>

                  <div className={styles.primaryStat}>
                    <span>{card.label}</span>
                    <strong>{formatMetric(result.metric, result.entry.value)}</strong>
                  </div>

                  <div className={styles.cardStats}>
                    <div>
                      <strong>{result.entry.minutes}</strong>
                      <span>Minutes</span>
                    </div>
                    <div>
                      <strong>
                        {result.entry.rank != null ? `${result.entry.rank}/${result.entry.out_of}` : "—"}
                      </strong>
                      <span>League rank</span>
                    </div>
                  </div>
                </div>

                <footer className={styles.cardFooter}>
                  <span>{result.metric.label}</span>
                  <span>Open Player Stats →</span>
                </footer>
              </Link>
            );
          })}
        </div>
      </section>

      <section className={styles.discoverySection}>
        <header className={styles.sectionHeading}>
          <div>
            <p>Browse</p>
            <h2>Prefer the curated player board?</h2>
          </div>
          <Link className={styles.directoryLink} href={`/players?season=${encodeURIComponent(season)}`}>
            Open Players →
          </Link>
        </header>
      </section>
    </main>
  );
}
