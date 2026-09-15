"use client";

import { useState } from "react";
import { ClubKit } from "@/components/ClubKit";
import styles from "./PlayerProfile.module.css";

type PortraitStage = "remote" | "local" | "fallback";

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

export function PlayerPortrait({
  portraitPlayerCode,
  playerName,
  club,
}: {
  portraitPlayerCode: string | null;
  playerName: string;
  club: string | null;
}) {
  const [stage, setStage] = useState<PortraitStage>(
    portraitPlayerCode ? "remote" : "fallback"
  );

  if (!portraitPlayerCode || stage === "fallback") {
    return (
      <div
        className={styles.portraitFallback}
        aria-label={`${playerName} portrait unavailable`}
      >
        {club ? (
          <ClubKit club={club} size="large" />
        ) : (
          <span
            aria-hidden="true"
            style={{
              color: "#d8d1c7",
              fontFamily: 'Georgia, "Times New Roman", serif',
              fontSize: "4rem",
              letterSpacing: "-.06em",
            }}
          >
            {initials(playerName)}
          </span>
        )}
      </div>
    );
  }

  const remoteSrc =
    `https://resources.premierleague.com/premierleague25/photos/players/500x500/${portraitPlayerCode}.png`;
  const localSrc = `/player-portraits/${portraitPlayerCode}.png`;
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
        alt={playerName}
        onError={() =>
          setStage((current) =>
            current === "remote" ? "local" : "fallback"
          )
        }
      />
    </div>
  );
}
