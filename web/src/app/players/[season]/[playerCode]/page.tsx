import Link from "next/link";
import { notFound } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { TeamCrest } from "@/components/TeamCrest";
import { PlayerPortrait } from "./PlayerPortrait";
import { MidfielderRadar, type PlayerProfileRadarData } from "./MidfielderRadar";
import { PlayerSeasonSelect } from "./PlayerSeasonSelect";
import styles from "./PlayerProfile.module.css";

type PlayerBiography = {
  available: boolean;
  identity_status: string;
  first_name: string | null;
  last_name: string | null;
  display_name: string | null;
  nationality: string | null;
  nationality_code: string | null;
  birth_date: string | null;
  birth_country: string | null;
  preferred_foot: string | null;
  height_cm: number | null;
  weight_kg: number | null;
  shirt_number: number | null;
  join_date: string | null;
  on_loan: boolean | null;
  evidence: Record<string, unknown>;
  limitations: string[];
};

type PlayerProfile = {
  season: string;
  player_code: string;
  player_name: string;
  position: string;
  clubs: string[];
  competition: string;
  appearances: number;
  starts: number;
  minutes: number;
  biography?: PlayerBiography;
  evidence: Record<string, unknown>;
  limitations: string[];
};

type PlayerSeasonOption = {
  season: string;
  player_code: string;
  player_name: string;
  position: string;
  clubs: string[];
};

type Fact = {
  label: string;
  value: string;
  flag?: string | null;
  crestTeam?: string;
};

const API_BASE = (
  process.env.NEXT_PUBLIC_FRL_API_URL ?? "http://127.0.0.1:8000"
).replace(/\/$/, "");

async function getJson<T>(
  path: string
): Promise<{ ok: boolean; status: number; data?: T }> {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      cache: "no-store",
    });

    if (!response.ok) {
      return { ok: false, status: response.status };
    }

    return {
      ok: true,
      status: response.status,
      data: (await response.json()) as T,
    };
  } catch {
    return { ok: false, status: 503 };
  }
}

function positionLabel(position: string) {
  const labels: Record<string, string> = {
    GKP: "Goalkeeper",
    GK: "Goalkeeper",
    DEF: "Defender",
    MID: "Midfielder",
    FWD: "Forward",
  };

  return labels[position] ?? position;
}

function formatDate(value: string | null) {
  if (!value) return "—";

  const parsed = new Date(`${value}T00:00:00Z`);

  if (Number.isNaN(parsed.getTime())) return value;

  return new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(parsed);
}

function formatHeight(value: number | null) {
  return value == null ? "—" : `${Math.round(value)} cm`;
}

function formatWeight(value: number | null) {
  return value == null ? "—" : `${Math.round(value)} kg`;
}

function countryFlag(code: string | null) {
  if (!code || code.length !== 2) return null;

  return String.fromCodePoint(
    ...code
      .toUpperCase()
      .split("")
      .map((letter) => 127397 + letter.charCodeAt(0))
  );
}

function profileNarrative(
  profile: PlayerProfile,
  biography: PlayerBiography,
  club: string,
  radar: PlayerProfileRadarData | null
) {
  const role =
    positionLabel(profile.position).toLowerCase();

  const article =
    /^[aeiou]/i.test(club) ? "an" : "a";

  const nationality =
    biography.nationality
      ? ` from ${biography.nationality}`
      : "";

  const sentences = [
    `${profile.player_name} is ${article} ${club} ${role}${nationality}.`,
  ];

  const facts: string[] = [];

  if (biography.birth_date) {
    facts.push(
      `Born ${formatDate(biography.birth_date)}`
    );
  }

  if (biography.preferred_foot) {
    facts.push(
      `${biography.preferred_foot.toLowerCase()}-footed`
    );
  }

  if (biography.height_cm != null) {
    facts.push(
      `listed at ${formatHeight(biography.height_cm)}`
    );
  }

  if (facts.length > 0) {
    sentences.push(`${facts.join(", ")}.`);
  }

  if (radar?.summary) {
    sentences.push(radar.summary);
  }

  return sentences.join(" ");
}

function FactGrid({ facts }: { facts: Fact[] }) {
  return (
    <dl className={styles.factGrid}>
      {facts.map((fact) => (
        <div key={fact.label}>
          <dt>{fact.label}</dt>
          <dd className={styles.factValue}>
            {fact.crestTeam ? (
              <TeamCrest teamName={fact.crestTeam} size={24} />
            ) : null}

            {fact.flag ? (
              <span className={styles.flag} aria-hidden="true">
                {fact.flag}
              </span>
            ) : null}

            <span>{fact.value}</span>
          </dd>
        </div>
      ))}
    </dl>
  );
}

export const dynamic = "force-dynamic";

export default async function PlayerProfilePage({
  params,
  searchParams,
}: {
  params: Promise<{ season: string; playerCode: string }>;
  searchParams: Promise<{ view?: string | string[] }>;
}) {
  const [{ season, playerCode }, query] = await Promise.all([
    params,
    searchParams,
  ]);

  const [
    profileResult,
    seasonsResult,
    radarResult,
  ] = await Promise.all([
    getJson<PlayerProfile>(
      `/api/v1/players/${encodeURIComponent(
        season
      )}/${encodeURIComponent(playerCode)}`
    ),
    getJson<PlayerSeasonOption[]>(
      `/api/v1/player-seasons/${encodeURIComponent(playerCode)}`
    ),
    getJson<PlayerProfileRadarData>(
      `/api/v1/player-profile-radar/${encodeURIComponent(
        season
      )}/${encodeURIComponent(playerCode)}`
    ),
  ]);

  if (!profileResult.ok || !profileResult.data) {
    if (profileResult.status === 404) notFound();

    throw new Error(
      `FRL Player Profile request failed: ${profileResult.status}`
    );
  }

  const profile = profileResult.data;

  const seasonOptions =
    seasonsResult.ok && seasonsResult.data
      ? seasonsResult.data
      : [
          {
            season,
            player_code: playerCode,
            player_name: profile.player_name,
            position: profile.position,
            clubs: profile.clubs,
          },
        ];

  const biography: PlayerBiography =
    profile.biography ?? {
      available: false,
      identity_status: "UNAVAILABLE",
      first_name: null,
      last_name: null,
      display_name: null,
      nationality: null,
      nationality_code: null,
      birth_date: null,
      birth_country: null,
      preferred_foot: null,
      height_cm: null,
      weight_kg: null,
      shirt_number: null,
      join_date: null,
      on_loan: null,
      evidence: {},
      limitations: [
        "Player biography was not returned by the current API contract.",
      ],
    };

  const club = profile.clubs[0] ?? "Club unavailable";
  const role = positionLabel(profile.position);

  const radar =
    radarResult.ok &&
    radarResult.data?.available
      ? radarResult.data
      : null;

  const viewValue = Array.isArray(query.view) ? query.view[0] : query.view;
  const historyActive = viewValue === "history";

  const identityFacts: Fact[] = [
    {
      label: "Nationality",
      value: biography.nationality ?? "—",
      flag: countryFlag(biography.nationality_code),
    },
    {
      label: "Born",
      value: formatDate(biography.birth_date),
    },
    {
      label: "Birth country",
      value: biography.birth_country ?? "—",
    },
    {
      label: "Preferred foot",
      value: biography.preferred_foot ?? "—",
    },
    {
      label: "Height",
      value: formatHeight(biography.height_cm),
    },
    {
      label: "Weight",
      value: formatWeight(biography.weight_kg),
    },
  ];

  const contextFacts: Fact[] = [
    {
      label: "Club",
      value: club,
      crestTeam: club,
    },
    {
      label: "Position",
      value: profile.position,
    },
    {
      label: "Competition",
      value: profile.competition,
    },
    {
      label: "Season",
      value: profile.season,
    },
    {
      label: "Squad no.",
      value:
        biography.shirt_number == null
          ? "—"
          : String(biography.shirt_number),
    },
    {
      label: "Joined",
      value: formatDate(biography.join_date),
    },
  ];

  const railItems = [
    club,
    role,
    biography.preferred_foot
      ? `${biography.preferred_foot}-footed`
      : null,
    biography.nationality,
  ].filter((item): item is string => Boolean(item));

  const sourceSeason =
    typeof biography.evidence?.source_season === "string"
      ? biography.evidence.source_season
      : null;

  const historicalFallback =
    biography.evidence?.historical_fallback === true;

  const provenance = biography.available
    ? sourceSeason
      ? `Biographical details use verified squad evidence from ${sourceSeason}${
          historicalFallback
            ? " because no matching current-season squad record is available."
            : "."
        }`
      : "Biographical details use verified preserved squad evidence."
    : biography.limitations[0] ??
      "Verified biographical evidence is currently unavailable.";

  return (
    <AppShell>
      <div className={styles.page}>
        <div className={styles.inner}>
          <header className={styles.hero}>
            <section className={styles.heroCopy}>
              <p className={styles.eyebrow}>Player profile</p>

              <h1>{profile.player_name}</h1>

              <p className={styles.contextLine}>
                <span>{club}</span>
                <i>·</i>
                <span>{profile.position}</span>

                {biography.nationality && (
                  <>
                    <i>·</i>
                    <span>{biography.nationality}</span>
                  </>
                )}
              </p>

              <p className={styles.heroBiography}>
                {profileNarrative(profile, biography, club, radar)}
              </p>
            </section>

            <section
              className={styles.portraitStage}
              aria-label={`${profile.player_name} visual identity`}
            >
              <PlayerPortrait
                playerCode={profile.player_code}
                playerName={profile.player_name}
                club={club}
              />
            </section>

            <aside className={styles.heroRail}>
              <PlayerSeasonSelect
                currentSeason={season}
                playerCode={playerCode}
                seasons={seasonOptions}
              />

              {radar ? (
                <MidfielderRadar
                  radar={radar}
                  playerName={profile.player_name}
                />
              ) : (
                <>
                  <p className={styles.railStatement}>
                    Football identity
                  </p>
              
                  <ul className={styles.identityList}>
                    {railItems.map((item) => (
                      <li key={item}>
                        <span
                          className={styles.identityMark}
                          aria-hidden="true"
                        >
                          ?
                        </span>
                        <strong>{item}</strong>
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </aside>

            <nav
              className={styles.tabs}
              aria-label="Player profile views"
            >
              <Link
                href={`/players/${encodeURIComponent(
                  season
                )}/${encodeURIComponent(playerCode)}`}
                className={
                  historyActive ? styles.tabLink : styles.activeTab
                }
              >
                Overview
              </Link>

              <Link
                href={`/players/${encodeURIComponent(
                  season
                )}/${encodeURIComponent(playerCode)}?view=history`}
                className={
                  historyActive ? styles.activeTab : styles.tabLink
                }
              >
                History
              </Link>

              <Link
                className={styles.tabLink}
                href={`/player-stats?season=${encodeURIComponent(
                  season
                )}&player=${encodeURIComponent(playerCode)}`}
              >
                Stats →
              </Link>
            </nav>
          </header>

          <main className={styles.workspace}>
            {historyActive ? (
              <section className={styles.historyView}>
                <header className={styles.historyHeader}>
                  <div>
                    <p className={styles.eyebrow}>Career record</p>
                    <h2>Captured seasons</h2>
                  </div>

                  <span>
                    {seasonOptions.length} FRL season
                    {seasonOptions.length === 1 ? "" : "s"}
                  </span>
                </header>

                <div className={styles.timeline}>
                  {seasonOptions.map((option, index) => {
                    const current = option.season === season;

                    return (
                      <Link
                        key={`${option.season}-${option.player_code}`}
                        href={`/players/${encodeURIComponent(
                          option.season
                        )}/${encodeURIComponent(option.player_code)}?view=history`}
                        className={styles.timelineRow}
                        data-current={current}
                      >
                        <span className={styles.timelineIndex}>
                          {String(index + 1).padStart(2, "0")}
                        </span>

                        <strong>{option.season}</strong>

                        <div>
                          <b>
                            {option.clubs.join(" · ") ||
                              "Club unavailable"}
                          </b>
                          <span>
                            {positionLabel(option.position)}
                          </span>
                        </div>

                        <i>{current ? "Current" : "View"}</i>
                      </Link>
                    );
                  })}
                </div>

                <footer className={styles.historyFooter}>
                  <Link
                    href={`/players/${encodeURIComponent(
                      season
                    )}/${encodeURIComponent(playerCode)}`}
                  >
                    ← Overview
                  </Link>

                  <Link
                    href={`/player-stats?season=${encodeURIComponent(
                      season
                    )}&player=${encodeURIComponent(playerCode)}`}
                  >
                    Open Player Stats →
                  </Link>
                </footer>
              </section>
            ) : (
              <>
                <section className={styles.profileRow}>
                  <div className={styles.rowHeading}>
                    <span>01</span>
                    <h2>Identity</h2>
                  </div>

                  <FactGrid facts={identityFacts} />
                </section>

                <section className={styles.profileRow}>
                  <div className={styles.rowHeading}>
                    <span>02</span>
                    <h2>Current context</h2>
                  </div>

                  <FactGrid facts={contextFacts} />
                </section>

                <section className={styles.profileRow}>
                  <div className={styles.rowHeading}>
                    <span>03</span>
                    <h2>Participation</h2>
                  </div>

                  <div className={styles.participation}>
                    <div>
                      <strong>{profile.appearances}</strong>
                      <span>Appearances</span>
                    </div>

                    <div>
                      <strong>{profile.starts}</strong>
                      <span>Starts</span>
                    </div>

                    <div>
                      <strong>{profile.minutes}</strong>
                      <span>Minutes</span>
                    </div>
                  </div>
                </section>

                <footer className={styles.profileFooter}>
                  <div className={styles.footerActions}>
                    <Link
                      className={styles.primaryAction}
                      href={`/players/${encodeURIComponent(
                        season
                      )}/${encodeURIComponent(playerCode)}?view=history`}
                    >
                      View career history →
                    </Link>

                    <Link
                      className={styles.secondaryAction}
                      href={`/player-stats?season=${encodeURIComponent(
                        season
                      )}&player=${encodeURIComponent(playerCode)}`}
                    >
                      Open Player Stats →
                    </Link>
                  </div>

                  <p className={styles.provenance}>
                    <span>ⓘ</span>
                    {provenance}
                  </p>
                </footer>
              </>
            )}
          </main>
        </div>
      </div>
    </AppShell>
  );
}

