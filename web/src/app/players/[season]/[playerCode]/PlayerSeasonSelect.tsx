type PlayerSeasonOption = {
  season: string;
  player_code: string;
  player_name: string;
  position: string;
  clubs: string[];
};

/**
 * Player Profile is intentionally a current-state surface.
 *
 * Career/previous-season navigation remains available through the History view,
 * which retains the governed season-specific route identities. Keep this seam as
 * a no-op while the approved Profile composition still imports it; a later
 * structural cleanup can remove the import without changing the page design.
 */
export function PlayerSeasonSelect(_props: {
  currentSeason: string;
  playerCode: string;
  seasons: PlayerSeasonOption[];
}) {
  return null;
}
