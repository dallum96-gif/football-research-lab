"use client";

import { useState } from "react";
import { ClubKit } from "@/components/ClubKit";
import styles from "./PlayerProfile.module.css";

type PortraitStage = "remote" | "local" | "kit";

export function PlayerPortrait({
  playerCode,
  playerName,
  club,
}: {
  playerCode: string;
  playerName: string;
  club: string;
}) {
  const [stage, setStage] = useState<PortraitStage>("remote");

  const remoteSrc =
    `https://resources.premierleague.com/premierleague25/photos/players/500x500/${playerCode}.png`;

  const localSrc = `/player-portraits/${playerCode}.png`;

  if (stage === "kit") {
    return (
      <div
        className={styles.portraitFallback}
        aria-label={`${playerName} portrait unavailable`}
      >
        <ClubKit club={club} size="large" />
      </div>
    );
  }

  const src = stage === "remote" ? remoteSrc : localSrc;

  return (
    <div className={styles.portraitComposition}>
      <img
        className={styles.portraitBackdrop}
        src={src}
        alt=""
        aria-hidden="true"
      />

      <img
        className={styles.portraitImage}
        src={src}
        alt={`${playerName}`}
        onError={() =>
          setStage((current) => (current === "remote" ? "local" : "kit"))
        }
      />
    </div>
  );
}


