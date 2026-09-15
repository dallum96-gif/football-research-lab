"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ClubKit } from "@/components/ClubKit";
import styles from "./PlayerStatsRedesign.module.css";

type PlayerOption = {
  player_code: string;
  player_name: string;
  position: string;
  clubs: string[];
  minutes: number;
  appearances: number;
  starts: number;
};

export function PlayerStatsV2Controls({
  seasons,
  players,
  season,
  playerCode,
  view,
}: {
  seasons: string[];
  players: PlayerOption[];
  season: string;
  playerCode: string;
  view: string;
}) {
  const router = useRouter();
  const [query, setQuery] = useState("");

  const results = useMemo(() => {
    const needle = query.trim().toLocaleLowerCase("en-GB");
    if (!needle) return [];
    return players
      .filter((player) => [player.player_name, player.position, ...player.clubs].join(" ").toLocaleLowerCase("en-GB").includes(needle))
      .sort((a, b) => {
        const aName = a.player_name.toLocaleLowerCase("en-GB");
        const bName = b.player_name.toLocaleLowerCase("en-GB");
        return Number(!aName.startsWith(needle)) - Number(!bName.startsWith(needle)) || b.minutes - a.minutes || a.player_name.localeCompare(b.player_name);
      })
      .slice(0, 7);
  }, [players, query]);

  return (
    <div className={styles.controls}>
      <label className={styles.seasonControl}>
        <span>Season</span>
        <select
          value={season}
          onChange={(event) => router.push(`/player-stats/redesign?season=${encodeURIComponent(event.target.value)}`)}
        >
          {seasons.map((value) => <option key={value} value={value}>{value}</option>)}
        </select>
      </label>

      <div className={styles.searchControl}>
        <label>
          <span>Search player</span>
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search player or club…" autoComplete="off" />
        </label>
        {results.length > 0 ? (
          <div className={styles.searchResults}>
            {results.map((player) => {
              const params = new URLSearchParams({ season, player: player.player_code, view });
              return (
                <Link key={player.player_code} href={`/player-stats/redesign?${params.toString()}`} onClick={() => setQuery("")}>
                  <span><strong>{player.player_name}</strong><small>{player.clubs[0] ?? "Club unavailable"} · {player.position}</small></span>
                  <em>{player.minutes} min</em>
                </Link>
              );
            })}
          </div>
        ) : null}
      </div>

      <Link className={styles.currentPlayerLink} href={`/player-stats/redesign?season=${encodeURIComponent(season)}&player=${encodeURIComponent(playerCode)}&view=${encodeURIComponent(view)}`} aria-label="Keep current player selected">Selected</Link>
    </div>
  );
}

type PortraitStage = "remote" | "local" | "kit";

export function PlayerStatsV2Portrait({
  playerCode,
  playerName,
  club,
}: {
  playerCode: string;
  playerName: string;
  club: string;
}) {
  const [stage, setStage] = useState<PortraitStage>("remote");
  const remoteSrc = `https://resources.premierleague.com/premierleague25/photos/players/500x500/${playerCode}.png`;
  const localSrc = `/player-portraits/${playerCode}.png`;

  if (stage === "kit") {
    return <div className={styles.portraitFallback} aria-label={`${playerName} portrait unavailable`}><ClubKit club={club} size="large" /></div>;
  }

  const src = stage === "remote" ? remoteSrc : localSrc;
  return (
    <div className={styles.portraitComposition}>
      <img className={styles.portraitGlow} src={src} alt="" aria-hidden="true" />
      <img className={styles.portraitImage} src={src} alt={playerName} onError={() => setStage((current) => current === "remote" ? "local" : "kit")} />
    </div>
  );
}
