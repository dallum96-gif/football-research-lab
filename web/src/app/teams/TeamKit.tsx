import styles from "./TeamsDirectory.module.css";

const kits: Record<string, [string, string, string?]> = {
  "Arsenal": ["#d71920", "#ffffff"],
  "Aston Villa": ["#7a263a", "#95bfe5"],
  "Bournemouth": ["#d71920", "#111111", "#111111"],
  "Brentford": ["#ffffff", "#e30613", "#e30613"],
  "Brighton and Hove Albion": ["#ffffff", "#0057b8", "#0057b8"],
  "Burnley": ["#6c1d45", "#8fd2ee"],
  "Chelsea": ["#034694", "#034694"],
  "Crystal Palace": ["#1b458f", "#c4122e", "#c4122e"],
  "Everton": ["#003399", "#003399"],
  "Fulham": ["#ffffff", "#111111"],
  "Leeds United": ["#ffffff", "#1d428a"],
  "Leicester City": ["#003090", "#003090"],
  "Liverpool": ["#c8102e", "#c8102e"],
  "Manchester City": ["#6cabdd", "#6cabdd"],
  "Manchester United": ["#da291c", "#da291c"],
  "Newcastle United": ["#ffffff", "#111111", "#111111"],
  "Nottingham Forest": ["#dd0000", "#dd0000"],
  "Southampton": ["#ffffff", "#d71920", "#d71920"],
  "Sunderland": ["#ffffff", "#eb172b", "#eb172b"],
  "Tottenham Hotspur": ["#ffffff", "#132257"],
  "West Ham United": ["#7a263a", "#1bb1e7"],
  "Wolverhampton Wanderers": ["#fdb913", "#111111"],
  "Sheffield United": ["#ffffff", "#ee2737", "#ee2737"],
  "West Bromwich Albion": ["#ffffff", "#122f67", "#122f67"],
  "Watford": ["#fbee23", "#111111"],
  "Norwich City": ["#fff200", "#00a650"],
  "Ipswich Town": ["#0044aa", "#0044aa"],
  "Luton Town": ["#f78f1e", "#f78f1e"],
  "Stoke City": ["#ffffff", "#e03a3e", "#e03a3e"],
  "Swansea City": ["#ffffff", "#111111"],
};

export function TeamKit({ teamName }: { teamName: string }) {
  const [body, sleeve, stripe] =
    kits[teamName] ?? ["#d8d2c7", "#b4ada2"];

  return (
    <span
      className={styles.kit}
      aria-label={`${teamName} home colours`}
      role="img"
    >
      <svg viewBox="0 0 64 64" aria-hidden="true">
        <path
          d="M18 11 26 7c1.7 3 3.7 4.5 6 4.5S36.3 10 38 7l8 4 10 11-8 7-5-5v31H21V24l-5 5-8-7 10-11Z"
          fill={body}
          stroke="rgba(23,23,20,.28)"
          strokeWidth="1.2"
          strokeLinejoin="round"
        />

        {stripe && (
          <>
            <path d="M26 11h5v44h-5Z" fill={stripe} />
            <path d="M36 11h5v44h-5Z" fill={stripe} />
          </>
        )}

        <path d="M18 11 8 22l8 7 5-5V13Z" fill={sleeve} />
        <path d="m46 11 10 11-8 7-5-5V13Z" fill={sleeve} />

        <path
          d="M27 8c.8 4 2.5 6 5 6s4.2-2 5-6"
          fill="none"
          stroke="rgba(23,23,20,.35)"
          strokeWidth="1.4"
          strokeLinecap="round"
        />
      </svg>
    </span>
  );
}
