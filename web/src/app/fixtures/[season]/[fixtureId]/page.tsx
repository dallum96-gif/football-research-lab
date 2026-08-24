import type { CSSProperties } from "react";
import { AppShell } from "@/components/AppShell";
import styles from "./FixtureOverview.module.css";

type FixtureDetailProps = {
  params: Promise<{
    season: string;
    fixtureId: string;
  }>;
};

type Event = {
  minute: string;
  side: "home" | "away";
  kind: "goal" | "card";
  player: string;
  assist?: string;
  card?: "yellow" | "red";
};

type Player = {
  name: string;
  role: string;
  x: number;
  y: number;
};

const events: Event[] = [
  { minute: "26'", side: "away", kind: "card", player: "Adam Lallana", card: "yellow" },
  { minute: "29'", side: "away", kind: "card", player: "Alberto Moreno", card: "yellow" },
  { minute: "31'", side: "home", kind: "goal", player: "Theo Walcott", assist: "Alex Iwobi" },
  { minute: "37'", side: "home", kind: "card", player: "Francis Coquelin", card: "yellow" },
  { minute: "41'", side: "away", kind: "card", player: "Dejan Lovren", card: "yellow" },
  { minute: "45+1'", side: "away", kind: "goal", player: "Philippe Coutinho" },
  { minute: "49'", side: "away", kind: "goal", player: "Adam Lallana", assist: "Georginio Wijnaldum" },
  { minute: "56'", side: "away", kind: "goal", player: "Philippe Coutinho", assist: "Nathaniel Clyne" },
  { minute: "57'", side: "home", kind: "card", player: "Alex Iwobi", card: "yellow" },
  { minute: "63'", side: "away", kind: "goal", player: "Sadio Mané", assist: "Adam Lallana" },
  { minute: "64'", side: "home", kind: "goal", player: "Alex Oxlade-Chamberlain", assist: "Santi Cazorla" },
  { minute: "75'", side: "home", kind: "goal", player: "Calum Chambers", assist: "Santi Cazorla" },
  { minute: "86'", side: "home", kind: "card", player: "Granit Xhaka", card: "yellow" },
];

const stats: [string, string, string, number, number][] = [
  ["50%", "Possession", "50%", 50, 50],
  ["5", "Shots on target", "7", 42, 58],
  ["9", "Shots", "16", 36, 64],
  ["5", "Corners", "4", 56, 44],
  ["3", "Yellow cards", "3", 50, 50],
];

const metadata = [
  ["Competition", "Premier League"],
  ["Matchweek", "1"],
  ["Date", "14 August 2016"],
  ["Kick-off", "16:00"],
  ["Venue", "Emirates Stadium"],
  ["Attendance", "60,033"],
  ["Referee", "Michael Oliver"],
];

const arsenalPlayers: Player[] = [
  { name: "Čech", role: "GK", x: 50, y: 8 },
  { name: "Bellerín", role: "RB", x: 20, y: 28.75 },
  { name: "Koscielny", role: "CB", x: 40, y: 28.75 },
  { name: "Holding", role: "CB", x: 60, y: 28.75 },
  { name: "Monreal", role: "LB", x: 80, y: 28.75 },
  { name: "Coquelin", role: "DM", x: 38, y: 49.5 },
  { name: "Cazorla", role: "DM", x: 62, y: 49.5 },
  { name: "Iwobi", role: "LW", x: 22, y: 70.25 },
  { name: "Özil", role: "AM", x: 50, y: 70.25 },
  { name: "Walcott", role: "RW", x: 78, y: 70.25 },
  { name: "Giroud", role: "ST", x: 50, y: 91 },
];

const liverpoolPlayers: Player[] = [
  { name: "Mignolet", role: "GK", x: 50, y: 8 },
  { name: "Clyne", role: "RB", x: 20, y: 35.67 },
  { name: "Lovren", role: "CB", x: 40, y: 35.67 },
  { name: "Klavan", role: "CB", x: 60, y: 35.67 },
  { name: "Moreno", role: "LB", x: 80, y: 35.67 },
  { name: "Wijnaldum", role: "CM", x: 25, y: 63.33 },
  { name: "Henderson", role: "CM", x: 50, y: 63.33 },
  { name: "Lallana", role: "CM", x: 75, y: 63.33 },
  { name: "Mané", role: "RW", x: 20, y: 91 },
  { name: "Firmino", role: "ST", x: 50, y: 91 },
  { name: "Coutinho", role: "LW", x: 80, y: 91 },
];

function Kit({ team }: { team: "arsenal" | "liverpool" }) {
  return (
    <span className={`${styles.kit} ${team === "arsenal" ? styles.arsenal : styles.liverpool}`} aria-hidden="true">
      <span className={styles.kitSleeve} />
      <span className={styles.kitSleeveRight} />
      <span className={styles.kitBody} />
    </span>
  );
}

function EventCell({ event }: { event: Event }) {
  const isGoal = event.kind === "goal";
  const isRed = event.card === "red";
  const icon = isGoal ? "⚽" : isRed ? "■" : "■";
  const className = isGoal
    ? styles.eventGoal
    : isRed
      ? styles.eventRed
      : styles.eventCard;

  return (
    <div className={`${styles.event} ${event.side === "home" ? styles.eventHome : styles.eventAway} ${className}`}>
      <span className={styles.icon}>{icon}</span>
      <span>
        {event.player}
        {event.assist ? <span className={styles.eventAssist}> — {event.assist} assist</span> : null}
      </span>
    </div>
  );
}

function LineupSide({
  title,
  formation,
  players,
  team,
}: {
  title: string;
  formation: string;
  players: Player[];
  team: "home" | "away";
}) {
  return (
    <div className={`${styles.lineupSide} ${team === "home" ? styles.lineupHome : styles.lineupAway}`}>
      <div className={styles.lineupSideHeader}>
        <span>{title}</span>
        <span>{formation}</span>
      </div>
      <div className={styles.tacticalBoard}>
        <div className={styles.boardHalfLine} />
        <div className={styles.boardCenterLine} />
        {players.map((player) => (
          <div
            className={styles.playerNode}
            key={player.name}
            style={{ left: `${player.x}%`, top: `${player.y}%` } as CSSProperties}
          >
            <span className={styles.playerDot} />
            <span className={styles.playerRole}>{player.role}</span>
            <span className={styles.playerName}>{player.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default async function FixtureDetailPage({ params }: FixtureDetailProps) {
  await params;

  return (
    <AppShell>
      <div className={styles.overview}>
        <header className={styles.pageHeader}>
          <div className={styles.pageHeaderCompetition}>Premier League</div>
          <div className={styles.pageHeaderDate}>14 August 2016</div>
        </header>

        <section className={styles.matchHeader} aria-label="Match result">
          <div className={styles.teams}>
            <div className={`${styles.team} ${styles.teamHome}`}>
              <span className={styles.teamName}>Arsenal</span>
              <Kit team="arsenal" />
            </div>

            <div className={styles.scoreBlock}>
              <div className={styles.score} aria-label="Arsenal 3 Liverpool 4">
                <span className={styles.scoreNumber}>3</span>
                <span className={styles.scoreDash}>–</span>
                <span className={styles.scoreNumber}>4</span>
              </div>
              <div className={styles.status}>Full time</div>
            </div>

            <div className={`${styles.team} ${styles.teamAway}`}>
              <Kit team="liverpool" />
              <span className={styles.teamName}>Liverpool</span>
            </div>
          </div>

          <div className={styles.timelineWrap}>
            <div className={styles.timeline} aria-label="Goals and cards timeline">
              {events.map((event) => (
                <div key={`${event.minute}-${event.player}`} className={styles.timelineRow}>
                  {event.side === "home" ? <EventCell event={event} /> : <span className={styles.eventEmpty} />}
                  <div className={styles.minute}>{event.minute}</div>
                  {event.side === "away" ? <EventCell event={event} /> : <span className={styles.eventEmpty} />}
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className={styles.lineupSection} aria-label="Starting lineups">
          <LineupSide title="Arsenal" formation="4–2–3–1" players={arsenalPlayers} team="home" />
          <LineupSide title="Liverpool" formation="4–3–3" players={liverpoolPlayers} team="away" />
        </section>

        <section>
          <div className={styles.sectionTitle}>
            <h2>Match statistics</h2>
            <span>Arsenal · Liverpool</span>
          </div>
          <div className={styles.stats}>
            {stats.map(([home, label, away, homeShare, awayShare]) => (
              <div className={styles.statRow} key={label}>
                <div className={`${styles.statValue} ${styles.statHome}`}>
                  <span>{home}</span>
                  <span className={styles.statTrack} style={{ "--home-share": `${homeShare}%` } as CSSProperties} />
                </div>
                <div className={styles.statLabel}>{label}</div>
                <div className={`${styles.statValue} ${styles.statAway}`}>
                  <span className={styles.statTrack} style={{ "--away-share": `${awayShare}%` } as CSSProperties} />
                  <span>{away}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className={styles.metadata} aria-label="Match metadata">
          {metadata.map(([label, value]) => (
            <div className={styles.metadataItem} key={label}>
              <span className={styles.metadataLabel}>{label}</span>
              <span className={styles.metadataValue}>{value}</span>
            </div>
          ))}
        </section>
      </div>
    </AppShell>
  );
}
