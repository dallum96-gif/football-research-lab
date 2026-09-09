const FOOTBALL_DATA_TEAM_IDS: Record<string, number> = {
  "Arsenal": 57,
  "Aston Villa": 58,
  "Chelsea": 61,
  "Everton": 62,
  "Fulham": 63,
  "Liverpool": 64,
  "Manchester City": 65,
  "Manchester United": 66,
  "Newcastle United": 67,
  "Norwich City": 68,
  "Queens Park Rangers": 69,
  "Stoke City": 70,
  "Sunderland": 71,
  "Swansea City": 72,
  "Tottenham Hotspur": 73,
  "West Bromwich Albion": 74,
  "Wolverhampton Wanderers": 76,
  "Burnley": 328,
  "Leicester City": 338,
  "Southampton": 340,
  "Leeds United": 341,
  "Watford": 346,
  "Ipswich Town": 349,
  "Nottingham Forest": 351,
  "Crystal Palace": 354,
  "Sheffield United": 356,
  "Luton Town": 389,
  "Brighton and Hove Albion": 397,
  "Brentford": 402,
  "West Ham United": 563,
  "Bournemouth": 1044,
  "AFC Bournemouth": 1044,
};

function fallbackMark(teamName: string) {
  const words = teamName.split(/\s+/).filter(Boolean);
  if (words.length === 1) return words[0].slice(0, 3).toUpperCase();
  return words.slice(0, 3).map((word) => word[0]).join("").toUpperCase();
}

export function TeamCrest({ teamName, size = 24 }: { teamName: string; size?: number }) {
  const teamId = FOOTBALL_DATA_TEAM_IDS[teamName];
  const dimension = `${size}px`;

  return (
    <span
      role="img"
      aria-label={`${teamName} crest`}
      style={{
        position: "relative",
        display: "inline-flex",
        width: dimension,
        height: dimension,
        flex: "0 0 auto",
        alignItems: "center",
        justifyContent: "center",
        color: "currentColor",
        fontSize: `${Math.max(7, Math.round(size * 0.22))}px`,
        fontWeight: 760,
        letterSpacing: ".04em",
      }}
    >
      <span aria-hidden="true" style={{ opacity: teamId ? 0 : 0.58 }}>{fallbackMark(teamName)}</span>
      {teamId ? (
        <img
          src={`https://crests.football-data.org/${teamId}.png`}
          alt=""
          aria-hidden="true"
          loading="lazy"
          decoding="async"
          onError={(event) => { event.currentTarget.style.display = "none"; }}
          style={{
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
            objectFit: "contain",
            objectPosition: "center",
          }}
        />
      ) : null}
    </span>
  );
}
