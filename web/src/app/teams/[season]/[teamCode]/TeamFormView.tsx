import styles from "./TeamProfile.module.css";

type FormFixture = {
  fixture_id: string;
  season: string;
  gameweek: number | null;
  kickoff_time: string | null;
  home_team_name: string;
  away_team_name: string;
  home_score: number | null;
  away_score: number | null;
  venue: "Home" | "Away" | null;
  result: "W" | "D" | "L" | "UNPLAYED" | null;
};

type MatchNumbers = {
  matches: number;
  wins: number;
  draws: number;
  losses: number;
  pointsPerGame: number;
  goalsForPerGame: number;
  goalsAgainstPerGame: number;
  totalGoalsPerGame: number;
  scoredPct: number;
  failedToScorePct: number;
  cleanSheetPct: number;
  bttsPct: number;
  over25Pct: number;
};

function isPlayed(fixture: FormFixture) {
  return (
    fixture.result != null &&
    fixture.result !== "UNPLAYED" &&
    fixture.home_score != null &&
    fixture.away_score != null
  );
}

function goalsFor(fixture: FormFixture, teamName: string) {
  if (fixture.home_score == null || fixture.away_score == null) return 0;

  return fixture.home_team_name === teamName
    ? fixture.home_score
    : fixture.away_score;
}

function goalsAgainst(fixture: FormFixture, teamName: string) {
  if (fixture.home_score == null || fixture.away_score == null) return 0;

  return fixture.home_team_name === teamName
    ? fixture.away_score
    : fixture.home_score;
}

function numbers(
  fixtures: FormFixture[],
  teamName: string
): MatchNumbers {
  const played = fixtures.filter(isPlayed);

  if (!played.length) {
    return {
      matches: 0,
      wins: 0,
      draws: 0,
      losses: 0,
      pointsPerGame: 0,
      goalsForPerGame: 0,
      goalsAgainstPerGame: 0,
      totalGoalsPerGame: 0,
      scoredPct: 0,
      failedToScorePct: 0,
      cleanSheetPct: 0,
      bttsPct: 0,
      over25Pct: 0,
    };
  }

  let wins = 0;
  let draws = 0;
  let losses = 0;
  let gf = 0;
  let ga = 0;
  let scored = 0;
  let failedToScore = 0;
  let cleanSheets = 0;
  let btts = 0;
  let over25 = 0;

  for (const fixture of played) {
    if (fixture.result === "W") wins += 1;
    if (fixture.result === "D") draws += 1;
    if (fixture.result === "L") losses += 1;

    const teamGoals = goalsFor(fixture, teamName);
    const opponentGoals = goalsAgainst(fixture, teamName);

    gf += teamGoals;
    ga += opponentGoals;

    if (teamGoals > 0) scored += 1;
    else failedToScore += 1;

    if (opponentGoals === 0) cleanSheets += 1;
    if (teamGoals > 0 && opponentGoals > 0) btts += 1;
    if (teamGoals + opponentGoals > 2.5) over25 += 1;
  }

  const count = played.length;

  return {
    matches: count,
    wins,
    draws,
    losses,
    pointsPerGame: (wins * 3 + draws) / count,
    goalsForPerGame: gf / count,
    goalsAgainstPerGame: ga / count,
    totalGoalsPerGame: (gf + ga) / count,
    scoredPct: (scored / count) * 100,
    failedToScorePct: (failedToScore / count) * 100,
    cleanSheetPct: (cleanSheets / count) * 100,
    bttsPct: (btts / count) * 100,
    over25Pct: (over25 / count) * 100,
  };
}

function rate(value: number) {
  return value.toFixed(2);
}

function pct(value: number) {
  return `${Math.round(value)}%`;
}

function RecordLine({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className={styles.formStatLine}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

export function TeamFormView({
  fixtures,
  teamName,
  season,
}: {
  fixtures: FormFixture[];
  teamName: string;
  season: string;
}) {
  const completed = fixtures
    .filter(isPlayed)
    .sort((a, b) => {
      const aTime = a.kickoff_time
        ? new Date(a.kickoff_time).getTime()
        : 0;

      const bTime = b.kickoff_time
        ? new Date(b.kickoff_time).getTime()
        : 0;

      return aTime - bTime;
    });

  const last5Fixtures = completed.slice(-5);
  const last10Fixtures = completed.slice(-10);

  const seasonNumbers = numbers(completed, teamName);
  const last5 = numbers(last5Fixtures, teamName);
  const last10 = numbers(last10Fixtures, teamName);

  const home = numbers(
    completed.filter((fixture) => fixture.venue === "Home"),
    teamName
  );

  const away = numbers(
    completed.filter((fixture) => fixture.venue === "Away"),
    teamName
  );

  if (!completed.length) {
    return (
      <section className={styles.formSnapshot}>
        <div className={styles.fixtureLedgerEmpty}>
          Form evidence is not yet available for this team-season.
        </div>
      </section>
    );
  }

  return (
    <section className={styles.formSnapshot}>
      <header className={styles.formSnapshotHeader}>
        <div>
          <p className={styles.sectionKicker}>Form snapshot</p>
          <h2>{season} current state</h2>
          <p>
            Recent performance beside the season baseline ? useful context
            before deeper analysis or model interpretation.
          </p>
        </div>

        <div className={styles.formHeaderBadge}>
          <span>Last 5</span>
          <strong>
            {last5.wins}-{last5.draws}-{last5.losses}
          </strong>
        </div>
      </header>

      <div className={styles.formGrid}>
        <article className={`${styles.formCard} ${styles.formCardPrimary}`}>
          <div className={styles.formCardHeading}>
            <div>
              <span>01</span>
              <p>Recent form</p>
            </div>
            <small>Last 5 matches</small>
          </div>

          <div className={styles.formHeroValue}>
            <strong>{rate(last5.pointsPerGame)}</strong>
            <span>points / match</span>
          </div>

          <div className={styles.formMiniRibbon}>
            {last5Fixtures.map((fixture) => (
              <span
                key={fixture.fixture_id}
                data-result={fixture.result}
                title={`GW ${fixture.gameweek ?? "-"}`}
              >
                {fixture.result}
              </span>
            ))}
          </div>

          <div className={styles.formBaseline}>
            <span>Last 10</span>
            <strong>
              {last10.wins}-{last10.draws}-{last10.losses}
            </strong>
            <small>{rate(last10.pointsPerGame)} PPG</small>
          </div>
        </article>

        <article className={styles.formCard}>
          <div className={styles.formCardHeading}>
            <div>
              <span>02</span>
              <p>Attack</p>
            </div>
            <small>Scoring rate</small>
          </div>

          <div className={styles.formHeroValue}>
            <strong>{rate(last5.goalsForPerGame)}</strong>
            <span>goals / match</span>
          </div>

          <div className={styles.formComparison}>
            <RecordLine
              label="Last 10"
              value={rate(last10.goalsForPerGame)}
            />
            <RecordLine
              label="Season"
              value={rate(seasonNumbers.goalsForPerGame)}
            />
          </div>

          <p className={styles.formContext}>
            Recent attacking rate beside the longer-run scoring baseline.
          </p>
        </article>

        <article className={styles.formCard}>
          <div className={styles.formCardHeading}>
            <div>
              <span>03</span>
              <p>Defence</p>
            </div>
            <small>Concession rate</small>
          </div>

          <div className={styles.formHeroValue}>
            <strong>{rate(last5.goalsAgainstPerGame)}</strong>
            <span>conceded / match</span>
          </div>

          <div className={styles.formComparison}>
            <RecordLine
              label="Last 10"
              value={rate(last10.goalsAgainstPerGame)}
            />
            <RecordLine
              label="Season"
              value={rate(seasonNumbers.goalsAgainstPerGame)}
            />
          </div>

          <p className={styles.formContext}>
            A quick check on whether the season defensive rate still
            resembles recent results.
          </p>
        </article>

        <article className={styles.formCard}>
          <div className={styles.formCardHeading}>
            <div>
              <span>04</span>
              <p>Scoring reliability</p>
            </div>
            <small>Last 10</small>
          </div>

          <div className={styles.formPercentRows}>
            <div>
              <span>Scored</span>
              <strong>{pct(last10.scoredPct)}</strong>
              <i>
                <b style={{ width: `${last10.scoredPct}%` }} />
              </i>
            </div>

            <div>
              <span>Failed to score</span>
              <strong>{pct(last10.failedToScorePct)}</strong>
              <i>
                <b style={{ width: `${last10.failedToScorePct}%` }} />
              </i>
            </div>

            <div>
              <span>Clean sheet</span>
              <strong>{pct(last10.cleanSheetPct)}</strong>
              <i>
                <b style={{ width: `${last10.cleanSheetPct}%` }} />
              </i>
            </div>
          </div>

          <div className={styles.formBaseline}>
            <span>Season scoring rate</span>
            <strong>{pct(seasonNumbers.scoredPct)}</strong>
          </div>
        </article>

        <article className={styles.formCard}>
          <div className={styles.formCardHeading}>
            <div>
              <span>05</span>
              <p>Goal environment</p>
            </div>
            <small>Last 10</small>
          </div>

          <div className={styles.formHeroValue}>
            <strong>{rate(last10.totalGoalsPerGame)}</strong>
            <span>total goals / match</span>
          </div>

          <div className={styles.formComparison}>
            <RecordLine label="BTTS" value={pct(last10.bttsPct)} />
            <RecordLine label="Over 2.5" value={pct(last10.over25Pct)} />
            <RecordLine
              label="Season goals"
              value={rate(seasonNumbers.totalGoalsPerGame)}
            />
          </div>
        </article>

        <article className={styles.formCard}>
          <div className={styles.formCardHeading}>
            <div>
              <span>06</span>
              <p>Venue split</p>
            </div>
            <small>Season</small>
          </div>

          <div className={styles.formVenueSplit}>
            <div>
              <span>Home</span>
              <strong>{rate(home.pointsPerGame)}</strong>
              <small>PPG</small>
              <p>
                {rate(home.goalsForPerGame)} GF ?{" "}
                {rate(home.goalsAgainstPerGame)} GA
              </p>
            </div>

            <div>
              <span>Away</span>
              <strong>{rate(away.pointsPerGame)}</strong>
              <small>PPG</small>
              <p>
                {rate(away.goalsForPerGame)} GF ?{" "}
                {rate(away.goalsAgainstPerGame)} GA
              </p>
            </div>
          </div>
        </article>
      </div>

      <footer className={styles.formSnapshotFooter}>
        <span>Poisson context, not a replacement model</span>
        <small>
          Recent samples help interpret whether season-long rates still
          describe the team's current state.
        </small>
      </footer>
    </section>
  );
}
