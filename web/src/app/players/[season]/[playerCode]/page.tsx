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
  first_name?: string | null;
  last_name?: string | null;
  display_name?: string | null;
  nationality?: string | null;
  nationality_code?: string | null;
  birth_date?: string | null;
  birth_country?: string | null;
  preferred_foot?: string | null;
  height_cm?: number | null;
  weight_kg?: number | null;
  shirt_number?: string | null;
  join_date?: string | null;
  on_loan?: string | null;
  evidence?: Record<string, unknown>;
  limitations?: string[];
};

type PlayerProfile = {
  season: string;
  player_code: string;
  player_name: string;
  position: string;
  competition: string;
  appearances: number;
  starts: number;
  minutes: number;
  clubs: string[];
  primary_club: string | null;
  club_context_status: string;
  portrait_player_code: string | null;
  player_identity_key: string | null;
  identity_status: string;
  biography: PlayerBiography;
};

type PlayerSeasonOption = {
  season: string;
  player_code: string;
  player_name: string;
  position: string;
  clubs: string[];
  identity_status?: string;
};

type Foundation = {
  milestone: string;
  profile: PlayerProfile;
  seasons: PlayerSeasonOption[];
  comparison: PlayerProfileRadarData;
  evidence: Record<string, unknown>;
  limitations: string[];
};

type Fact = {
  label: string;
  value: string;
  flag?: string | null;
  crestTeam?: string | null;
};

const API_BASE = (
  process.env.NEXT_PUBLIC_FRL_API_URL ?? "http://127.0.0.1:8000"
).replace(/\/$/, "");

async function getJson<T>(path: string): Promise<{ ok: boolean; status: number; data?: T }> {
  try {
    const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
    if (!response.ok) return { ok: false, status: response.status };
    return { ok: true, status: response.status, data: (await response.json()) as T };
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

function formatDate(value?: string | null) {
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

function formatHeight(value?: number | null) {
  return value == null ? "—" : `${Math.round(value)} cm`;
}

function formatWeight(value?: number | null) {
  return value == null ? "—" : `${Math.round(value)} kg`;
}

function countryFlag(code?: string | null) {
  if (!code) return null;
  const alpha2 = code.length === 2 ? code : code.startsWith("GB-") ? "GB" : null;
  if (!alpha2) return null;
  return String.fromCodePoint(
    ...alpha2.toUpperCase().split("").map((letter) => 127397 + letter.charCodeAt(0))
  );
}

function clubLabel(profile: PlayerProfile) {
  return profile.primary_club ?? (profile.clubs.join(" · ") || "Club unavailable");
}

function profileNarrative(
  profile: PlayerProfile,
  biography: PlayerBiography,
  radar: PlayerProfileRadarData | null
) {
  const role = positionLabel(profile.position).toLowerCase();
  const nationality = biography.nationality ? ` from ${biography.nationality}` : "";
  const sentences: string[] = [];

  if (profile.primary_club) {
    const article = /^[aeiou]/i.test(profile.primary_club) ? "an" : "a";
    sentences.push(
      `${profile.player_name} is ${article} ${profile.primary_club} ${role}${nationality}.`
    );
  } else if (profile.clubs.length > 0) {
    sentences.push(
      `${profile.player_name} is a Premier League ${role}${nationality} who represented ${profile.clubs.join(
        " and "
      )} in ${profile.season}.`
    );
  } else {
    sentences.push(`${profile.player_name} is a Premier League ${role}${nationality}.`);
  }

  const facts: string[] = [];
  if (biography.birth_date) facts.push(`Born ${formatDate(biography.birth_date)}`);
  if (biography.preferred_foot) facts.push(`${biography.preferred_foot.toLowerCase()}-footed`);
  if (biography.height_cm != null) facts.push(`listed at ${formatHeight(biography.height_cm)}`);
  if (facts.length > 0) sentences.push(`${facts.join(", ")}.`);
  if (radar?.summary) sentences.push(radar.summary);
  return sentences.join(" ");
}

function FactGrid({ facts }: { facts: Fact[] }) {
  return (
    <dl className={styles.factGrid}>
      {facts.map((fact) => (
        <div key={fact.label}>
          <dt>{fact.label}</dt>
          <dd className={styles.factValue}>
            {fact.crestTeam ? <TeamCrest teamName={fact.crestTeam} size={24} /> : null}
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
  const [{ season, playerCode }, query] = await Promise.all([params, searchParams]);
  const result = await getJson<Foundation>(
    `/api/v1/player-profile-foundation/${encodeURIComponent(season)}/${encodeURIComponent(
      playerCode
    )}`
  );

  if (!result.ok || !result.data) {
    if (result.status === 404) notFound();
    throw new Error(`FRL Player Profile foundation request failed: ${result.status}`);
  }

  const foundation = result.data;
  const profile = foundation.profile;
  const biography = profile.biography ?? {
    available: false,
    identity_status: "UNAVAILABLE",
    limitations: ["Packaged biography evidence is unavailable."],
  };
  const seasons = foundation.seasons.length
    ? foundation.seasons
    : [
        {
          season,
          player_code: profile.player_code,
          player_name: profile.player_name,
          position: profile.position,
          clubs: profile.clubs,
          identity_status: profile.identity_status,
        },
      ];
  const radar = foundation.comparison?.available ? foundation.comparison : null;
  const viewValue = Array.isArray(query.view) ? query.view[0] : query.view;
  const historyActive = viewValue === "history";
  const club = clubLabel(profile);

  const identityFacts: Fact[] = [
    {
      label: "Nationality",
      value: biography.nationality ?? "—",
      flag: countryFlag(biography.nationality_code),
    },
    { label: "Born", value: formatDate(biography.birth_date) },
    { label: "Birth country", value: biography.birth_country ?? "—" },
    { label: "Preferred foot", value: biography.preferred_foot ?? "—" },
    { label: "Height", value: formatHeight(biography.height_cm) },
    { label: "Weight", value: formatWeight(biography.weight_kg) },
  ];

  const contextFacts: Fact[] = [
    {
      label: profile.clubs.length > 1 ? "Primary club" : "Club",
      value: club,
      crestTeam: profile.primary_club,
    },
    { label: "Position", value: profile.position },
    { label: "Competition", value: profile.competition },
    { label: "Season", value: profile.season },
    { label: "Squad no.", value: biography.shirt_number ?? "—" },
    { label: "Joined", value: formatDate(biography.join_date) },
  ];

  const railItems = [
    club !== "Club unavailable" ? club : null,
    positionLabel(profile.position),
    biography.preferred_foot ? `${biography.preferred_foot}-footed` : null,
    biography.nationality,
  ].filter((item): item is string => Boolean(item));

  const sourceSeason =
    typeof biography.evidence?.source_season === "string"
      ? biography.evidence.source_season
      : null;
  const historicalFallback = biography.evidence?.historical_fallback === true;
  const provenance = biography.available
    ? sourceSeason
      ? `Biographical details use packaged verified squad evidence from ${sourceSeason}${
          historicalFallback ? " because no matching selected-season row is available." : "."
        }`
      : "Biographical details use packaged verified squad evidence."
    : biography.limitations?.[0] ?? "Verified packaged biographical evidence is unavailable.";

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
                {biography.nationality ? (
                  <>
                    <i>·</i>
                    <span>{biography.nationality}</span>
                  </>
                ) : null}
              </p>
              <p className={styles.heroBiography}>
                {profileNarrative(profile, biography, radar)}
              </p>
            </section>

            <section
              className={styles.portraitStage}
              aria-label={`${profile.player_name} visual identity`}
            >
              <PlayerPortrait
                portraitPlayerCode={profile.portrait_player_code}
                playerName={profile.player_name}
                club={profile.primary_club}
              />
            </section>

            <aside className={styles.heroRail}>
              <PlayerSeasonSelect currentSeason={season} seasons={seasons} />
              {radar ? (
                <MidfielderRadar radar={radar} playerName={profile.player_name} />
              ) : (
                <>
                  <p className={styles.railStatement}>
                    {profile.position === "MID"
                      ? "Comparative profile unavailable"
                      : "Football identity"}
                  </p>
                  <ul className={styles.identityList}>
                    {railItems.map((item) => (
                      <li key={item}>
                        <span className={styles.identityMark} aria-hidden="true">
                          ·
                        </span>
                        <strong>{item}</strong>
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </aside>

            <nav className={styles.tabs} aria-label="Player profile views">
              <Link
                href={`/players/${encodeURIComponent(season)}/${encodeURIComponent(
                  profile.player_code
                )}`}
                className={historyActive ? styles.tabLink : styles.activeTab}
              >
                Overview
              </Link>
              <Link
                href={`/players/${encodeURIComponent(season)}/${encodeURIComponent(
                  profile.player_code
                )}?view=history`}
                className={historyActive ? styles.activeTab : styles.tabLink}
              >
                History
              </Link>
              <Link
                className={styles.tabLink}
                href={`/player-stats?season=${encodeURIComponent(season)}&player=${encodeURIComponent(
                  profile.player_code
                )}`}
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
                    {seasons.length} FRL season{seasons.length === 1 ? "" : "s"}
                  </span>
                </header>

                <div className={styles.timeline}>
                  {seasons.map((option, index) => {
                    const current = option.season === season;
                    return (
                      <Link
                        key={`${option.season}-${option.player_code}`}
                        href={`/players/${encodeURIComponent(option.season)}/${encodeURIComponent(
                          option.player_code
                        )}?view=history`}
                        className={styles.timelineRow}
                        data-current={current}
                      >
                        <span className={styles.timelineIndex}>
                          {String(index + 1).padStart(2, "0")}
                        </span>
                        <strong>{option.season}</strong>
                        <div>
                          <b>{option.clubs.join(" · ") || "Club unavailable"}</b>
                          <span>{positionLabel(option.position)}</span>
                        </div>
                        <i>{current ? "Current" : "View"}</i>
                      </Link>
                    );
                  })}
                </div>

                <footer className={styles.historyFooter}>
                  <Link
                    href={`/players/${encodeURIComponent(season)}/${encodeURIComponent(
                      profile.player_code
                    )}`}
                  >
                    ← Overview
                  </Link>
                  <Link
                    href={`/player-stats?season=${encodeURIComponent(
                      season
                    )}&player=${encodeURIComponent(profile.player_code)}`}
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
                      href={`/players/${encodeURIComponent(season)}/${encodeURIComponent(
                        profile.player_code
                      )}?view=history`}
                    >
                      View career history →
                    </Link>
                    <Link
                      className={styles.secondaryAction}
                      href={`/player-stats?season=${encodeURIComponent(
                        season
                      )}&player=${encodeURIComponent(profile.player_code)}`}
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
