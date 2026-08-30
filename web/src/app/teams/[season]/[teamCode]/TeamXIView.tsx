import Link from "next/link";
import styles from "./TeamProfile.module.css";

export type TeamXIPlayer = {
  player_id: string;
  player_name: string;
  position: string | null;
  appearances: number;
  starts: number;
  minutes: number;
  goals: number;
  assists: number;
  season_count: number;
};

export type TeamXISlot = {
  slot_id: string;
  line_index: number;
  slot_index: number;
  line_size: number;
  x: number;
  y: number;
  role: "GK" | "DEF" | "MID" | "FWD";
  player_id: string | null;
  player_name: string | null;
  position: string | null;
  role_starts: number;
  appearances: number;
};

export type TeamXIResult = {
  persistent_team_code: string;
  display_name: string;
  season: string;
  scope: "season" | "overall";
  scope_label: string;
  seasons_included: string[];
  competition: string;
  formation: string | null;
  formation_uses: number;
  formation_sample: number;
  squad: TeamXIPlayer[];
  xi: TeamXISlot[];
  limitations: string[];
};

function initials(name: string): string {
  const parts = name.trim().split(/\s+/);

  if (parts.length === 1) {
    return parts[0].slice(0, 2).toUpperCase();
  }

  return `${parts[0][0] ?? ""}${parts[parts.length - 1][0] ?? ""}`.toUpperCase();
}

function shortPosition(position: string | null): string {
  const value = (position ?? "").toLowerCase();

  if (value.includes("goal")) return "GK";
  if (value.includes("def")) return "DEF";
  if (value.includes("mid")) return "MID";
  if (value.includes("forward") || value.includes("striker")) return "FWD";

  return position?.slice(0, 3).toUpperCase() ?? "?";
}

export function TeamXIView({
  data,
  season,
  teamCode,
}: {
  data: TeamXIResult;
  season: string;
  teamCode: string;
}) {
  const isOverall = data.scope === "overall";

  const seasonHref =
    `/teams/${encodeURIComponent(season)}/${encodeURIComponent(teamCode)}?view=xi`;

  const overallHref =
    `/teams/${encodeURIComponent(season)}/${encodeURIComponent(teamCode)}?view=xi&scope=overall`;

  return (
    <section className={styles.xiWorkspace}>
      <header className={styles.xiHeader}>
        <div>
          <p className={styles.sectionKicker}>
            {isOverall ? "Across the FRL era" : "Squad & shape"}
          </p>

          <div className={styles.xiTitleLine}>
            <h2>
              {isOverall
                ? `${data.display_name} era XI`
                : `${data.season} XI`}
            </h2>

            {data.formation && (
              <span className={styles.xiFormationChip}>
                {data.formation}
              </span>
            )}
          </div>

          <p className={styles.xiIntro}>
            {isOverall
              ? "The most-used player in every exact position of the club's most-used formation across represented FRL seasons."
              : "The players who most often occupied each exact position when the club used its most common shape."}
          </p>
        </div>

        <div className={styles.xiScopeSwitch} aria-label="XI scope">
          <Link
            href={seasonHref}
            data-active={!isOverall ? "true" : "false"}
          >
            {season}
          </Link>

          <Link
            href={overallHref}
            data-active={isOverall ? "true" : "false"}
          >
            Overall
          </Link>
        </div>
      </header>

      <div className={styles.xiBody}>
        <aside className={styles.xiSquadPanel}>
          <header className={styles.xiPanelHeading}>
            <div>
              <span>{isOverall ? "Era players" : "Season squad"}</span>
              <small>
                {data.squad.length} represented players
              </small>
            </div>

            <span className={styles.xiAppearancesLabel}>Apps</span>
          </header>

          <div className={styles.xiSquadTableWrap}>
            <table className={styles.xiSquadTable}>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Player</th>
                  <th>Pos</th>
                  <th>Apps</th>
                  <th>Starts</th>
                  <th>G</th>
                  <th>A</th>
                </tr>
              </thead>

              <tbody>
                {data.squad.map((player, index) => (
                  <tr key={player.player_id}>
                    <td className={styles.xiRank}>{index + 1}</td>

                    <td>
                      <strong>{player.player_name}</strong>

                      {isOverall && player.season_count > 1 && (
                        <small>
                          {player.season_count} seasons
                        </small>
                      )}
                    </td>

                    <td className={styles.xiPosition}>
                      {shortPosition(player.position)}
                    </td>

                    <td className={styles.xiNumeric}>
                      {player.appearances}
                    </td>

                    <td className={styles.xiNumeric}>
                      {player.starts}
                    </td>

                    <td className={styles.xiNumeric}>
                      {player.goals}
                    </td>

                    <td className={styles.xiNumeric}>
                      {player.assists}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </aside>

        <article className={styles.xiPitchPanel}>
          <header className={styles.xiPitchHeader}>
            <div>
              <span>
                {isOverall ? "Era formation" : "Most-used formation"}
              </span>

              <strong>{data.formation ?? "Formation unavailable"}</strong>
            </div>

            <div className={styles.xiFormationEvidence}>
              <strong>{data.formation_uses}</strong>
              <span>of {data.formation_sample}</span>
              <small>
                {isOverall
                  ? "represented matches used this shape"
                  : "matches used this shape"}
              </small>
            </div>
          </header>

          {data.formation && data.xi.length === 11 ? (
            <div
              className={styles.xiPitch}
              aria-label={`${data.display_name} ${data.scope_label} ${data.formation} XI`}
            >
              <span className={styles.xiHalfwayLine} />
              <span className={styles.xiCentreCircle} />
              <span className={styles.xiCentreSpot} />

              <span
                className={`${styles.xiPenaltyBox} ${styles.xiPenaltyBoxTop}`}
              />
              <span
                className={`${styles.xiPenaltyBox} ${styles.xiPenaltyBoxBottom}`}
              />

              <span
                className={`${styles.xiGoalBox} ${styles.xiGoalBoxTop}`}
              />
              <span
                className={`${styles.xiGoalBox} ${styles.xiGoalBoxBottom}`}
              />

              {data.xi.map((slot, index) => {
                if (!slot.player_name) return null;

                return (
                  <div
                    key={slot.slot_id}
                    className={styles.xiPlayer}
                    style={{
                      left: `${slot.x}%`,
                      top: `${100 - slot.y}%`,
                    }}
                    title={`${slot.player_name} ? ${slot.role_starts} starts in this exact ${data.formation} slot ? ${slot.appearances} total appearances`}
                  >
                    <span className={styles.xiPlayerToken}>
                      <small>{index + 1}</small>
                      <strong>{initials(slot.player_name)}</strong>
                    </span>

                    <span className={styles.xiPlayerName}>
                      {slot.player_name}
                    </span>

                    <span className={styles.xiPlayerMeta}>
                      {slot.role_starts} slot starts
                    </span>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className={styles.xiUnavailable}>
              <strong>Formation XI unavailable</strong>
              <p>
                FRL will not infer tactical positions where the governed
                formation evidence is incomplete.
              </p>
            </div>
          )}

          <footer className={styles.xiPitchFooter}>
            <span>
              <i />
              Source-backed formation slot
            </span>

            <small>
              Presentation geometry only ? not tracking coordinates
            </small>
          </footer>
        </article>
      </div>
    </section>
  );
}
