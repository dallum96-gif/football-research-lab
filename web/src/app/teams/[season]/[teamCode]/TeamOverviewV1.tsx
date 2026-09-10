import Link from "next/link";
import styles from "./TeamProfile.module.css";

export type ClubProfilePayload = {
  schema_version: string;
  persistent_team_code: string;
  canonical_name: string;
  status: "CURATED" | "PARTIAL" | "PENDING_CURATION";
  season: string | null;

  identity: {
    full_name: string | null;
    nickname: string | null;
    founded_year: number | null;
    origin: string | null;
    home: string | null;
    locality: string | null;
    colours: {
      name: string;
      hex: string;
    }[];
  };

  story: {
    text: string | null;
    milestones: {
      year: number;
      label: string;
    }[];
  };

  stadium: {
    name: string;
    capacity: number | null;
    since_year: number | null;
    previous_home: string | null;
  } | null;

  leadership: {
    manager: {
      name: string;
      detail: string | null;
    } | null;

    captain: {
      name: string;
      detail: string | null;
    } | null;
  } | null;

  honours: {
    as_of: string | null;
    note: string | null;
    categories: {
      key: string;
      label: string;
      wins: number;
      editions?: {
        season: string;
        competition: string | null;
      }[];
    }[];
  };

  visual: {
    hero_image: string | null;
    hero_image_credit: string | null;
    hero_image_licence: string | null;
    hero_image_licence_url: string | null;
    hero_image_source: string | null;
  };

  limitations: string[];
};

type Fixture = {
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

type EraSeason = {
  season: string;
  position: number;
  points: number;
  played: number;
};

type Props = {
  clubProfile: ClubProfilePayload | null;
  displayName: string;
  competition: string;
  season: string;
  position: number;
  played: number;
  points: number;
  wins: number;
  draws: number;
  losses: number;
  goalsFor: number;
  goalsAgainst: number;
  goalDifference: number;
  fixtures: Fixture[];
  eraSeasons: EraSeason[];
};

function ordinal(value: number): string {
  const mod100 = value % 100;

  if (mod100 >= 11 && mod100 <= 13) {
    return `${value}th`;
  }

  if (value % 10 === 1) return `${value}st`;
  if (value % 10 === 2) return `${value}nd`;
  if (value % 10 === 3) return `${value}rd`;

  return `${value}th`;
}

function shortDate(value: string | null): string {
  if (!value) return "Date unavailable";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Date unavailable";
  }

  return new Intl.DateTimeFormat("en-GB", {
    timeZone: "Europe/London",
    day: "numeric",
    month: "short",
  }).format(date);
}

function opponentName(
  fixture: Fixture,
  teamName: string,
): string {
  return fixture.home_team_name === teamName
    ? fixture.away_team_name
    : fixture.home_team_name;
}

function score(fixture: Fixture): string {
  if (
    fixture.home_score == null ||
    fixture.away_score == null
  ) {
    return "Score unavailable";
  }

  return `${fixture.home_score}–${fixture.away_score}`;
}

function chartY(position: number): number {
  const clamped = Math.max(1, Math.min(20, position));
  return 18 + ((clamped - 1) / 19) * 112;
}

export function TeamOverviewV1({
  clubProfile,
  displayName,
  competition,
  season,
  position,
  played,
  points,
  wins,
  draws,
  losses,
  goalsFor,
  goalsAgainst,
  goalDifference,
  fixtures,
  eraSeasons,
}: Props) {
  const bio =
    clubProfile?.status === "CURATED" ||
    clubProfile?.status === "PARTIAL"
      ? clubProfile
      : null;

  const completed = fixtures.filter(
    (fixture) =>
      fixture.result === "W" ||
      fixture.result === "D" ||
      fixture.result === "L",
  );

  const recentEra = [...eraSeasons]
    .sort((a, b) => a.season.localeCompare(b.season))
    .slice(-5);

  const pointsString = recentEra
    .map((item, index) => {
      const x =
        recentEra.length <= 1
          ? 160
          : 20 +
            (index / (recentEra.length - 1)) * 280;

      return `${x},${chartY(item.position)}`;
    })
    .join(" ");

  return (
    <div className={styles.overviewV1}>
      <section className={styles.whoGrid}>
        <article className={styles.whoPanel}>
          {bio ? (
            <>
              <div className={styles.whoHero}>
                <div className={styles.whoCopy}>
                  <p className={styles.sectionKicker}>
                    Club profile
                  </p>

                  <h2>Who are {displayName}?</h2>

                  {bio.identity.full_name && (
                    <strong className={styles.officialClubName}>
                      {bio.identity.full_name}
                    </strong>
                  )}

                  {bio.story.text && (
                    <p className={styles.originStory}>
                      {bio.story.text}
                    </p>
                  )}

                  <p className={styles.clubOriginLine}>
                    {bio.identity.founded_year != null && (
                      <>
                        Founded {bio.identity.founded_year}
                      </>
                    )}

                    {bio.identity.origin && (
                      <>
                        <span>·</span>
                        {bio.identity.origin}
                      </>
                    )}

                    {bio.identity.home && (
                      <>
                        <span>·</span>
                        {bio.identity.home}
                      </>
                    )}
                  </p>
                </div>

                {bio.visual.hero_image && (
                  <div className={styles.clubHeroVisual}>
                    <div
                      className={styles.clubHeroImage}
                      style={{
                        backgroundImage:
                          `url("${bio.visual.hero_image}")`,
                      }}
                      role="img"
                      aria-label={
                        bio.stadium?.name ??
                        `${displayName} club image`
                      }
                    />

                    {bio.visual.hero_image_credit && (
                      <div className={styles.heroCredit}>
                        {bio.visual.hero_image_source ? (
                          <a
                            href={bio.visual.hero_image_source}
                            target="_blank"
                            rel="noreferrer"
                          >
                            {bio.visual.hero_image_credit}
                          </a>
                        ) : (
                          <span>
                            {bio.visual.hero_image_credit}
                          </span>
                        )}

                        {bio.visual.hero_image_licence &&
                          bio.visual.hero_image_licence_url && (
                            <a
                              href={
                                bio.visual
                                  .hero_image_licence_url
                              }
                              target="_blank"
                              rel="noreferrer"
                            >
                              {
                                bio.visual
                                  .hero_image_licence
                              }
                            </a>
                          )}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {bio.honours.categories.length > 0 && (
                <div
                  className={styles.honoursRail}
                  title={bio.honours.note ?? undefined}
                >
                  <span className={styles.honoursTitle}>
                    Honours
                  </span>

                  {bio.honours.categories.map((honour) => (
                    <div
                      className={styles.honourItem}
                      key={honour.key}
                      tabIndex={0}
                    >
                      <strong>{honour.wins}</strong>
                      <small>{honour.label}</small>

                      {(honour.editions?.length ?? 0) > 0 && (
                        <span
                          className={styles.honourTooltip}
                          role="tooltip"
                        >
                          <b>{honour.label}</b>

                          <span
                            className={styles.honourTooltipEditions}
                          >
                            {(honour.editions ?? []).map(
                              (edition, index) => (
                                <span
                                  key={`${honour.key}-${edition.season}-${index}`}
                                >
                                  {edition.competition ? (
                                    <>
                                      <strong>
                                        {edition.competition}
                                      </strong>
                                      {" - "}
                                      {edition.season}
                                    </>
                                  ) : (
                                    edition.season
                                  )}
                                </span>
                              ),
                            )}
                          </span>
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              )}

              <div className={styles.profileFactRail}>
                <div>
                  <span>Home</span>

                  <strong>
                    {bio.stadium?.name ?? "—"}
                  </strong>

                  <small>
                    {bio.stadium?.capacity != null
                      ? `${bio.stadium.capacity.toLocaleString(
                          "en-GB",
                        )} capacity`
                      : "Capacity unavailable"}
                  </small>
                </div>

                <div>
                  <span>Location</span>

                  <strong>
                    {bio.identity.home ?? "—"}
                  </strong>

                  <small>
                    {bio.identity.locality ?? ""}
                  </small>
                </div>

                <div>
                  <span>Colours</span>

                  <div className={styles.factColours}>
                    {bio.identity.colours.map((colour) => (
                      <i
                        key={colour.name}
                        title={colour.name}
                        style={{
                          backgroundColor: colour.hex,
                        }}
                      />
                    ))}
                  </div>

                  <small>
                    {bio.identity.colours
                      .map((colour) => colour.name)
                      .join(" & ")}
                  </small>
                </div>

                <div>
                  <span>Manager</span>

                  <strong>
                    {bio.leadership?.manager?.name ??
                      "Not curated for this season"}
                  </strong>

                  <small>
                    {bio.leadership?.manager?.detail ?? ""}
                  </small>
                </div>

                <div>
                  <span>Captain</span>

                  <strong>
                    {bio.leadership?.captain?.name ??
                      "Not curated for this season"}
                  </strong>

                  <small>
                    {bio.identity.nickname ?? ""}
                  </small>
                </div>
              </div>
            </>
          ) : (
            <div className={styles.whoCopy}>
              <p className={styles.sectionKicker}>
                Club profile
              </p>

              <h2>{displayName}</h2>

              <p className={styles.clubOriginLine}>
                Biographical profile pending curation.
              </p>
            </div>
          )}
        </article>

        <aside className={styles.fiveYearPanel}>
          <header>
            <div>
              <p className={styles.sectionKicker}>
                Recent history
              </p>

              <h2>Last five seasons</h2>
            </div>

            <span>League finish</span>
          </header>

          {recentEra.length > 0 ? (
            <>
              <div className={styles.miniEraChart}>
                <span
                  className={styles.miniRank}
                  data-rank="1"
                >
                  1
                </span>

                <span
                  className={styles.miniRank}
                  data-rank="10"
                >
                  10
                </span>

                <span
                  className={styles.miniRank}
                  data-rank="20"
                >
                  20
                </span>

                <svg
                  viewBox="0 0 320 148"
                  role="img"
                  aria-label={`${displayName} league positions over the last five captured seasons`}
                >
                  <line
                    className={styles.miniGuide}
                    x1="20"
                    x2="300"
                    y1="18"
                    y2="18"
                  />
                  <line
                    className={styles.miniGuide}
                    x1="20"
                    x2="300"
                    y1="71"
                    y2="71"
                  />
                  <line
                    className={styles.miniGuide}
                    x1="20"
                    x2="300"
                    y1="130"
                    y2="130"
                  />

                  {recentEra.length > 1 && (
                    <polyline
                      className={styles.miniPath}
                      points={pointsString}
                    />
                  )}

                  {recentEra.map((item, index) => {
                    const x =
                      recentEra.length <= 1
                        ? 160
                        : 20 +
                          (index /
                            (recentEra.length - 1)) *
                            280;

                    const y = chartY(item.position);

                    return (
                      <g key={item.season}>
                        <circle
                          className={styles.miniPointHalo}
                          cx={x}
                          cy={y}
                          r="8"
                        />

                        <circle
                          className={styles.miniPoint}
                          data-active={
                            item.season === season
                              ? "true"
                              : "false"
                          }
                          cx={x}
                          cy={y}
                          r="4"
                        >
                        </circle>
                      </g>
                    );
                  })}
                </svg>
              </div>

              <div
                className={styles.miniEraLabels}
                style={{
                  gridTemplateColumns:
                    `repeat(${recentEra.length}, minmax(0, 1fr))`,
                }}
              >
                {recentEra.map((item) => (
                  <div
                    key={item.season}
                    data-active={
                      item.season === season
                        ? "true"
                        : "false"
                    }
                  >
                    <span>{item.season.slice(2)}</span>
                    <strong>
                      {ordinal(item.position)}
                    </strong>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <p className={styles.unavailable}>
              Recent league history unavailable.
            </p>
          )}

          <div className={styles.fiveYearFoot}>
            <span>Selected season</span>
            <strong>
              {season} · {ordinal(position)}
            </strong>
          </div>
        </aside>
      </section>

      <section className={styles.currentChapter}>
        <header className={styles.currentChapterHeader}>
          <div>
            <p className={styles.sectionKicker}>
              {season} · Season fingerprint
            </p>

            <h2>The shape of the season</h2>

            <p>Every league result in sequence.</p>
          </div>

          <div className={styles.currentSeasonReading}>
            <strong>{ordinal(position)}</strong>

            <span>
              {points} pts · {wins}W {draws}D {losses}L
              {" · "}
              {goalDifference > 0
                ? `+${goalDifference}`
                : goalDifference}
            </span>
          </div>
        </header>

        {completed.length > 0 ? (
          <>
            <div
              className={styles.formRibbon}
              style={{
                gridTemplateColumns:
                  `repeat(${completed.length}, minmax(0, 1fr))`,
              }}
              aria-label={`${competition} ${season} results`}
            >
              {completed.map((fixture) => (
                <Link
                  key={fixture.fixture_id}
                  href={`/fixtures/${encodeURIComponent(
                    fixture.season,
                  )}/${encodeURIComponent(
                    fixture.fixture_id,
                  )}`}
                  className={styles.formResult}
                  data-result={fixture.result}
                >
                  <span className={styles.resultLetter}>
                    {fixture.result}
                  </span>

                  <span className={styles.fixtureTooltip}>
                    <em>
                      GW {fixture.gameweek ?? "—"}
                    </em>

                    <strong>
                      {opponentName(
                        fixture,
                        displayName,
                      )}
                    </strong>

                    <small>
                      {shortDate(
                        fixture.kickoff_time,
                      )}
                      {" · "}
                      {fixture.venue ??
                        "Venue unavailable"}
                    </small>

                    <b>{score(fixture)}</b>
                  </span>
                </Link>
              ))}
            </div>

            <div className={styles.ribbonAxis}>
              <span>
                {shortDate(
                  completed[0]?.kickoff_time ??
                    null,
                )}
              </span>

              <span>
                {played} league matches
              </span>

              <span>
                {shortDate(
                  completed[
                    completed.length - 1
                  ]?.kickoff_time ?? null,
                )}
              </span>
            </div>
          </>
        ) : (
          <p className={styles.unavailable}>
            Season result sequence unavailable.
          </p>
        )}

        <div className={styles.profileRoutes}>
          <Link href="?view=records">
            <span>Record book</span>
            <b>Explore club history →</b>
          </Link>

          <Link href="?view=xi">
            <span>XI</span>
            <b>See the team →</b>
          </Link>

          <Link href="?view=fixtures">
            <span>Fixtures</span>
            <b>Browse every match →</b>
          </Link>

          <Link href="?view=form">
            <span>Form</span>
            <b>Follow the run →</b>
          </Link>
        </div>
      </section>
    </div>
  );
}