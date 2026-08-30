"use client";

import Link from "next/link";
import { useState } from "react";
import styles from "./TeamProfile.module.css";

export type TeamRecordSequenceItem = {
  result: "W" | "D" | "L";
  fixture_id: string;
  season: string;
  opponent: string;
  venue: "Home" | "Away";
  kickoff_time: string;
  score: string;
};

export type TeamRecordRankEntry = {
  rank: number;
  label: string;
  value: string;
  relative: number;
};

export type TeamRecordItem = {
  key: string;
  label: string;
  value: string;
  detail: string | null;
  fixture_id: string | null;
  fixture_season: string | null;
  percentage: number | null;
  comparison_rank: number | null;
  comparison_population: number | null;
  top_percent: number | null;
  comparison_basis: string | null;
  result_sequence: TeamRecordSequenceItem[];
  ranking?: TeamRecordRankEntry[];
};

export type TeamRecordCategory = {
  key: "results" | "runs" | "goals" | "players" | "matchday";
  label: string;
  status: "AVAILABLE" | "UNAVAILABLE";
  items: TeamRecordItem[];
  leaderboard?: Array<{
    rank: number;
    player_id: string;
    player_name: string;
    appearances: number;
    goals: number;
    assists: number;
    goal_involvements: number;
  }>;

  note: string | null;
};

export type TeamSeasonRecords = {
  persistent_team_code: string;
  display_name: string;
  season: string;
  scope: "season" | "overall";
  scope_label: string;
  seasons_included: string[];
  competition: string;
  categories: TeamRecordCategory[];
  limitations: string[];
};

function ResultSequence({
  sequence,
  season,
}: {
  sequence: TeamRecordSequenceItem[];
  season: string;
}) {
  if (!sequence.length) return null;

  return (
    <div className={styles.recordSequence} aria-label="Fixture sequence">
      {sequence.map((fixture) => (
        <Link
          key={fixture.fixture_id}
          href={`/fixtures/${encodeURIComponent(
            fixture.season
          )}/${encodeURIComponent(fixture.fixture_id)}`}
          className={styles.recordSequenceLink}
          data-result={fixture.result}
          aria-label={`${fixture.result}: ${fixture.opponent}, ${fixture.score}`}
        >
          <span className={styles.recordSequenceLetter}>
            {fixture.result}
          </span>

          <span className={styles.fixtureTooltip}>
            <strong>{fixture.opponent}</strong>
            <small>
              {fixture.kickoff_time} ? {fixture.venue}
            </small>
            <b>{fixture.score}</b>
          </span>
        </Link>
      ))}
    </div>
  );
}

function RecordComparison({
  record,
}: {
  record: TeamRecordItem;
}) {
  if (
    record.top_percent == null ||
    record.comparison_rank == null ||
    record.comparison_population == null
  ) {
    return null;
  }

  return (
    <div
      className={styles.recordComparison}
      title={record.comparison_basis ?? undefined}
    >
      <strong>TOP {record.top_percent}%</strong>
      <small>
        #{record.comparison_rank} of {record.comparison_population}
      </small>

      {record.comparison_basis && (
        <span className={styles.recordComparisonTooltip}>
          <b>Comparison rank</b>
          <small>{record.comparison_basis}</small>
          <em>
            #{record.comparison_rank} of{" "}
            {record.comparison_population}
          </em>
        </span>
      )}
    </div>
  );
}

function RecordPercentage({
  record,
}: {
  record: TeamRecordItem;
}) {
  if (record.percentage == null) return null;

  const percentage = Math.max(0, Math.min(100, record.percentage));
  const negative = record.key === "conceded-two-plus";

  const label = Number.isInteger(percentage)
    ? `${percentage}%`
    : `${percentage.toFixed(1)}%`;

  return (
    <div
      className={styles.recordPercentage}
      data-tone={negative ? "negative" : "positive"}
    >
      <div className={styles.recordPercentageTrack}>
        <span style={{ width: `${percentage}%` }} />
      </div>

      <b>{label}</b>
    </div>
  );
}

function RecordValue({
  record,
  season,
}: {
  record: TeamRecordItem;
  season: string;
}) {
  const content = (
    <>
      <strong>{record.value}</strong>
      {record.detail && <small>{record.detail}</small>}
      <RecordPercentage record={record} />
      <RecordComparison record={record} />
      <ResultSequence
        sequence={record.result_sequence}
        season={season}
      />
    </>
  );

  if (!record.fixture_id) {
    return <div className={styles.recordValue}>{content}</div>;
  }

  return (
    <Link
      href={`/fixtures/${encodeURIComponent(
        record.fixture_season ?? season
      )}/${encodeURIComponent(record.fixture_id)}`}
      className={`${styles.recordValue} ${styles.recordFixtureLink}`}
    >
      {content}
      <span className={styles.recordArrow}>?</span>
    </Link>
  );
}

function PlayerRanking({
  record,
}: {
  record: TeamRecordItem;
}) {
  const ranking = record.ranking ?? [];

  if (!ranking.length) {
    return null;
  }

  return (
    <div className={styles.playerRanking}>
      {ranking.map((entry) => (
        <div
          className={styles.playerRankRow}
          data-rank={entry.rank}
          key={`${record.key}-${entry.rank}-${entry.label}`}
        >
          <span className={styles.playerRankNumber}>
            {entry.rank}
          </span>

          <div className={styles.playerRankIdentity}>
            <strong>{entry.label}</strong>

            <div className={styles.playerRankTrack}>
              <span
                style={{
                  width: `${Math.max(
                    0,
                    Math.min(100, entry.relative)
                  )}%`,
                }}
              />
            </div>
          </div>

          <small>{entry.value}</small>
        </div>
      ))}
    </div>
  );
}


export function TeamRecordsView({
  records,
  teamCode,
}: {
  records: TeamSeasonRecords;
  teamCode: string;
}) {
  const [activeKey, setActiveKey] =
    useState<TeamRecordCategory["key"]>("results");

  const active =
    records.categories.find((category) => category.key === activeKey) ??
    records.categories[0];

  const feature =
    active.status === "AVAILABLE" ? active.items[0] ?? null : null;

  const ledger =
    active.status === "AVAILABLE" ? active.items.slice(1) : [];

  return (
    <div className={styles.recordsView}>
      <header className={styles.recordsIntro}>
        <div>
          <p className={styles.sectionKicker}>Season record book</p>
          <h2>What defined {records.display_name}?</h2>
        </div>

        <div className={styles.recordsScope}>
          <span className={styles.recordsCompetition}>
            {records.competition}
          </span>

          <div
            className={styles.scopeToggle}
            aria-label="Records scope"
          >
            <Link
              href={`/teams/${encodeURIComponent(
                records.season
              )}/${encodeURIComponent(
                teamCode
              )}?view=records&scope=season`}
              data-active={
                records.scope === "season" ? "true" : "false"
              }
            >
              Individual season
            </Link>

            <Link
              href={`/teams/${encodeURIComponent(
                records.season
              )}/${encodeURIComponent(
                teamCode
              )}?view=records&scope=overall`}
              data-active={
                records.scope === "overall" ? "true" : "false"
              }
            >
              Overall
            </Link>
          </div>

          <small>{records.scope_label}</small>
        </div>
      </header>

      <nav
        className={styles.recordCategoryTabs}
        aria-label="Record categories"
      >
        {records.categories.map((category) => (
          <button
            key={category.key}
            type="button"
            className={styles.recordCategoryTab}
            data-active={active.key === category.key ? "true" : "false"}
            onClick={() => setActiveKey(category.key)}
          >
            {category.label}
          </button>
        ))}
      </nav>
      {active.status === "AVAILABLE" && feature ? (
        active.key === "players" ? (
        <section className={styles.playersV5}>
          <article className={styles.playersV5Leaderboard}>
            <header className={styles.playersV5LeaderboardHeader}>
              <div>
                <span>GOAL INVOLVEMENTS</span>
                <h2>Top 20 players</h2>
              </div>

              <small>Goals + assists</small>
            </header>

            <div className={styles.playersV5Table}>
              <div
                className={`${styles.playersV5TableRow} ${styles.playersV5TableHead}`}
              >
                <span>#</span>
                <span>Player</span>
                <span>Apps</span>
                <span>Goals</span>
                <span>Assists</span>
                <span>Total</span>
              </div>

              {(active.leaderboard ?? []).map((player) => (
                <div
                  className={styles.playersV5TableRow}
                  data-rank={player.rank}
                  key={player.player_id}
                >
                  <span>{player.rank}</span>
                  <strong>{player.player_name}</strong>
                  <span>{player.appearances}</span>
                  <span>{player.goals}</span>
                  <span>{player.assists}</span>
                  <b>{player.goal_involvements}</b>
                </div>
              ))}
            </div>
          </article>

          <div className={styles.playersV5Records}>
            {active.items.map((record, index) => (
              <article
                className={styles.playersV5Tile}
                data-record={record.key}
                key={record.key}
              >
                <header className={styles.playersV5TileHeader}>
                  <span>
                    {String(index + 1).padStart(2, "0")}
                  </span>

                  <div>
                    <small>RECORD</small>
                    <h3>{record.label}</h3>
                  </div>
                </header>

                <div className={styles.playersV5Leader}>
                  <strong>{record.value}</strong>
                  {record.detail && <span>{record.detail}</span>}
                </div>
                <div className={styles.playersV5Percentile}>
                  <RecordComparison record={record} />
                </div>

                <PlayerRanking record={record} />
              </article>
            ))}
          </div>
        </section>
        ) : (
        <section
          className={styles.recordBook}
          data-category={active.key}
        >
          <article className={styles.featuredRecord}>
            <div className={styles.featuredRecordTopline}>
              <span>{active.label}</span>
              <span>01</span>
            </div>

            <div className={styles.featuredRecordBody}>
              <p>{feature.label}</p>

              {feature.fixture_id ? (
                <Link
                  href={`/fixtures/${encodeURIComponent(
                    feature.fixture_season ?? records.season
                  )}/${encodeURIComponent(feature.fixture_id)}`}
                  className={styles.featuredRecordLink}
                >
                  <strong>{feature.value}</strong>
                  <span>?</span>
                </Link>
              ) : (
                <strong>{feature.value}</strong>
              )}

              {feature.detail && <small>{feature.detail}</small>}

              <div className={styles.featuredRecordContext}>
                <RecordPercentage record={feature} />
                <RecordComparison record={feature} />
              </div>

              <ResultSequence
                sequence={feature.result_sequence}
                season={records.season}
              />
            </div>

            <div className={styles.featuredRecordFooter}>
              <span>
                {records.scope === "overall"
                  ? "FRL era record"
                  : "FRL season record"}
              </span>
              <span>{records.scope_label}</span>
            </div>
          </article>

          <div className={styles.recordLedger}>
            <header className={styles.recordLedgerHeading}>
              <span>Record</span>
              <span>Mark</span>
            </header>

            {ledger.map((record, index) => (
              <article className={styles.recordLedgerRow} key={record.key}>
                <div className={styles.recordLabel}>
                  <span>{String(index + 2).padStart(2, "0")}</span>
                  <p>{record.label}</p>
                </div>

                <RecordValue
                  record={record}
                  season={records.season}
                />
              </article>
            ))}
          </div>
        </section>
        )
      ) : (
        <section className={styles.recordUnavailable}>
          <div className={styles.recordUnavailableMark}>FRL</div>

          <div>
            <p className={styles.sectionKicker}>{active.label}</p>
            <h2>Evidence before decoration.</h2>
            <p>
              {active.note ??
                "This record category is not yet available through a governed FRL evidence seam."}
            </p>
          </div>

          <span className={styles.evidenceLabel}>
            Evidence boundary preserved
          </span>
        </section>
      )}

      <footer className={styles.recordsFooter}>
        <span>
          {records.scope === "overall"
            ? "Premier League FRL-era records"
            : "Premier League season records"}
          {" ? "}governed FRL fixtures
        </span>
        <span>
          {records.scope === "overall"
            ? `${records.seasons_included.length} represented seasons`
            : records.season}
        </span>
      </footer>
    </div>
  );
}
