import type { CSSProperties } from "react";
import styles from "./ClubKit.module.css";

type KitDefinition = {
  body: string;
  sleeves: string;
  trim: string;
  pattern?: string;
  mark?: string;
};

const SOLID = (colour: string) => colour;
const STRIPES = (first: string, second: string) =>
  `repeating-linear-gradient(90deg, ${first} 0 14px, ${second} 14px 28px)`;
const HOOPS = (first: string, second: string) =>
  `repeating-linear-gradient(180deg, ${first} 0 12px, ${second} 12px 24px)`;
const HALVES = (first: string, second: string) =>
  `linear-gradient(90deg, ${first} 0 50%, ${second} 50% 100%)`;

const KITS: Array<[RegExp, KitDefinition]> = [
  [/arsenal/i, { body: "#d71920", sleeves: "#f6f4ef", trim: "#14264a", mark: "ARS" }],
  [/aston villa|villa/i, { body: "#6a1638", sleeves: "#95cbea", trim: "#f5d44b", mark: "AVL" }],
  [/bournemouth/i, { body: "#d71920", sleeves: "#111111", trim: "#d71920", pattern: STRIPES("#d71920", "#111111"), mark: "BOU" }],
  [/brentford/i, { body: "#d71920", sleeves: "#d71920", trim: "#111111", pattern: STRIPES("#ffffff", "#d71920"), mark: "BRE" }],
  [/brighton/i, { body: "#0057b8", sleeves: "#0057b8", trim: "#f2d13d", pattern: STRIPES("#ffffff", "#0057b8"), mark: "BHA" }],
  [/burnley/i, { body: "#6c1d45", sleeves: "#8ccce8", trim: "#f3cf57", mark: "BUR" }],
  [/chelsea/i, { body: "#034694", sleeves: "#034694", trim: "#ffffff", mark: "CHE" }],
  [/crystal palace|palace/i, { body: "#1b458f", sleeves: "#1b458f", trim: "#f7c843", pattern: STRIPES("#d71920", "#1b458f"), mark: "CRY" }],
  [/everton/i, { body: "#003399", sleeves: "#003399", trim: "#ffffff", mark: "EVE" }],
  [/fulham/i, { body: "#ffffff", sleeves: "#101010", trim: "#d71920", mark: "FUL" }],
  [/leeds/i, { body: "#ffffff", sleeves: "#ffffff", trim: "#1d428a", mark: "LEE" }],
  [/leicester/i, { body: "#003090", sleeves: "#003090", trim: "#e0b84c", mark: "LEI" }],
  [/liverpool/i, { body: "#c8102e", sleeves: "#c8102e", trim: "#f3e8c8", mark: "LIV" }],
  [/manchester city|man city/i, { body: "#6cabdd", sleeves: "#6cabdd", trim: "#ffffff", mark: "MCI" }],
  [/manchester united|man united/i, { body: "#da291c", sleeves: "#da291c", trim: "#111111", mark: "MUN" }],
  [/newcastle/i, { body: "#ffffff", sleeves: "#111111", trim: "#41b6e6", pattern: STRIPES("#ffffff", "#111111"), mark: "NEW" }],
  [/nottingham forest|nott'?m forest|forest/i, { body: "#dd0000", sleeves: "#dd0000", trim: "#ffffff", mark: "NFO" }],
  [/southampton/i, { body: "#d71920", sleeves: "#d71920", trim: "#111111", pattern: STRIPES("#ffffff", "#d71920"), mark: "SOU" }],
  [/sunderland/i, { body: "#d71920", sleeves: "#d71920", trim: "#111111", pattern: STRIPES("#ffffff", "#d71920"), mark: "SUN" }],
  [/tottenham|spurs/i, { body: "#ffffff", sleeves: "#ffffff", trim: "#132257", mark: "TOT" }],
  [/west ham/i, { body: "#7a263a", sleeves: "#80c7df", trim: "#f1d36b", mark: "WHU" }],
  [/wolves|wolverhampton/i, { body: "#fdb913", sleeves: "#fdb913", trim: "#111111", mark: "WOL" }],
  [/ipswich/i, { body: "#0057b8", sleeves: "#0057b8", trim: "#ffffff", mark: "IPS" }],
  [/sheffield united/i, { body: "#d71920", sleeves: "#d71920", trim: "#111111", pattern: STRIPES("#ffffff", "#d71920"), mark: "SHU" }],
  [/middlesbrough/i, { body: "#d71920", sleeves: "#d71920", trim: "#ffffff", pattern: HOOPS("#d71920", "#ffffff"), mark: "MID" }],
  [/coventry/i, { body: "#78bde8", sleeves: "#78bde8", trim: "#ffffff", mark: "COV" }],
  [/norwich/i, { body: "#fff200", sleeves: "#fff200", trim: "#009a44", mark: "NOR" }],
  [/watford/i, { body: "#fbee23", sleeves: "#fbee23", trim: "#111111", mark: "WAT" }],
  [/west brom/i, { body: "#ffffff", sleeves: "#132257", trim: "#132257", pattern: STRIPES("#ffffff", "#132257"), mark: "WBA" }],
  [/blackburn/i, { body: "#ffffff", sleeves: "#0067b1", trim: "#d71920", pattern: HALVES("#ffffff", "#0067b1"), mark: "BBR" }],
  [/birmingham/i, { body: "#0057b8", sleeves: "#0057b8", trim: "#ffffff", mark: "BIR" }],
  [/swansea/i, { body: "#ffffff", sleeves: "#ffffff", trim: "#111111", mark: "SWA" }],
  [/hull/i, { body: "#f5a623", sleeves: "#111111", trim: "#111111", pattern: STRIPES("#f5a623", "#111111"), mark: "HUL" }],
  [/qpr|queens park rangers/i, { body: "#ffffff", sleeves: "#ffffff", trim: "#0057b8", pattern: HOOPS("#ffffff", "#0057b8"), mark: "QPR" }],
  [/stoke/i, { body: "#d71920", sleeves: "#d71920", trim: "#111111", pattern: STRIPES("#ffffff", "#d71920"), mark: "STK" }],
];

const FALLBACK: KitDefinition = {
  body: "#5f6b7a",
  sleeves: "#5f6b7a",
  trim: "#ffffff",
  pattern: SOLID("#5f6b7a"),
  mark: "PL",
};

function kitForClub(club: string) {
  return KITS.find(([pattern]) => pattern.test(club))?.[1] ?? FALLBACK;
}

export function ClubKit({ club, size = "medium" }: { club: string; size?: "small" | "medium" | "large" }) {
  const kit = kitForClub(club);
  const style = {
    "--kit-body": kit.body,
    "--kit-sleeves": kit.sleeves,
    "--kit-trim": kit.trim,
    "--kit-pattern": kit.pattern ?? kit.body,
  } as CSSProperties;

  return (
    <span className={styles.kit} data-size={size} style={style} aria-label={`${club} home kit visual`}>
      <span className={styles.body}>
        <span className={styles.collar} />
        <span className={styles.mark}>{kit.mark}</span>
      </span>
    </span>
  );
}
