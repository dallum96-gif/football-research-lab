from __future__ import annotations

import argparse
from pathlib import Path
import tempfile

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURES = ROOT / "fixtures_master_corrected.csv"
DEFAULT_TEAM_REGISTRY = ROOT / "identity" / "team_seasons.csv"
DEFAULT_FIXTURE_STATS = ROOT / "data" / "fixture_match_stats.csv"


def _escape(path: Path) -> str:
    return str(path.resolve()).replace("'", "''")


def materialize(output_dir: Path) -> dict[str, int | str]:
    """Build additive analytical Parquet datasets from trusted canonical inputs."""
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    for path in (DEFAULT_FIXTURES, DEFAULT_TEAM_REGISTRY, DEFAULT_FIXTURE_STATS):
        if not path.exists():
            raise FileNotFoundError(path)

    con = duckdb.connect(database=":memory:")
    try:
        fixtures = f"read_csv_auto('{_escape(DEFAULT_FIXTURES)}', SAMPLE_SIZE=-1, HEADER=TRUE)"
        teams = f"read_csv_auto('{_escape(DEFAULT_TEAM_REGISTRY)}', SAMPLE_SIZE=-1, HEADER=TRUE)"
        stats = f"read_csv_auto('{_escape(DEFAULT_FIXTURE_STATS)}', SAMPLE_SIZE=-1, HEADER=TRUE)"

        fixture_out = output_dir / "fixtures.parquet"
        team_fixture_out = output_dir / "team_fixtures.parquet"

        # Canonical fixture grain. Persistent team identity is reached through
        # the season-local team registry, never through a direct numeric join.
        fixture_sql = f"""
            SELECT
                f.season,
                CAST(f.fixture_id AS BIGINT) AS fixture_id,
                f.fixture_code,
                f.kickoff_time,
                CAST(f.gameweek AS INTEGER) AS gameweek,
                CAST(f.home_team_id AS INTEGER) AS home_local_team_id,
                CAST(f.away_team_id AS INTEGER) AS away_local_team_id,
                CAST(ht.persistent_team_code AS INTEGER) AS home_persistent_team_code,
                CAST(at.persistent_team_code AS INTEGER) AS away_persistent_team_code,
                f.home_score,
                f.away_score,
                CASE
                    WHEN f.home_score IS NULL OR f.away_score IS NULL THEN NULL
                    WHEN f.home_score > f.away_score THEN 'H'
                    WHEN f.home_score < f.away_score THEN 'A'
                    ELSE 'D'
                END AS result
            FROM {fixtures} f
            LEFT JOIN {teams} ht
              ON f.season = ht.season
             AND CAST(f.home_team_id AS VARCHAR) = CAST(ht.local_team_id AS VARCHAR)
             AND ht.mapping_status = 'VERIFIED'
            LEFT JOIN {teams} at
              ON f.season = at.season
             AND CAST(f.away_team_id AS VARCHAR) = CAST(at.local_team_id AS VARCHAR)
             AND at.mapping_status = 'VERIFIED'
        """
        con.execute(f"COPY ({fixture_sql}) TO '{_escape(fixture_out)}' (FORMAT PARQUET, COMPRESSION ZSTD)")

        # Team-fixture grain. Core fixture facts plus the applicable home/away
        # match-stat namespace are reshaped into one symmetrical team row.
        team_fixture_sql = f"""
            WITH base AS ({fixture_sql}),
            team_rows AS (
                SELECT
                    season, fixture_id, home_persistent_team_code AS persistent_team_code,
                    home_local_team_id AS local_team_id, 'HOME' AS venue_role,
                    away_persistent_team_code AS opponent_persistent_team_code,
                    CASE WHEN result = 'H' THEN 'W' WHEN result = 'A' THEN 'L' WHEN result = 'D' THEN 'D' END AS result,
                    CASE WHEN result = 'H' THEN 3 WHEN result = 'D' THEN 1 WHEN result = 'A' THEN 0 END AS points,
                    home_score AS for_goals, away_score AS against_goals
                FROM base
                UNION ALL
                SELECT
                    season, fixture_id, away_persistent_team_code AS persistent_team_code,
                    away_local_team_id AS local_team_id, 'AWAY' AS venue_role,
                    home_persistent_team_code AS opponent_persistent_team_code,
                    CASE WHEN result = 'A' THEN 'W' WHEN result = 'H' THEN 'L' WHEN result = 'D' THEN 'D' END AS result,
                    CASE WHEN result = 'A' THEN 3 WHEN result = 'D' THEN 1 WHEN result = 'H' THEN 0 END AS points,
                    away_score AS for_goals, home_score AS against_goals
                FROM base
            )
            SELECT * FROM team_rows
        """
        con.execute(f"COPY ({team_fixture_sql}) TO '{_escape(team_fixture_out)}' (FORMAT PARQUET, COMPRESSION ZSTD)")

        fixture_count = int(con.execute(f"SELECT COUNT(*) FROM '{_escape(fixture_out)}'").fetchone()[0])
        team_fixture_count = int(con.execute(f"SELECT COUNT(*) FROM '{_escape(team_fixture_out)}'").fetchone()[0])
        duplicate_fixture_keys = int(
            con.execute(
                f"SELECT COUNT(*) FROM (SELECT season, fixture_id FROM read_parquet('{_escape(fixture_out)}') GROUP BY season, fixture_id HAVING COUNT(*) > 1)"
            ).fetchone()[0]
        )
        duplicate_team_fixture_keys = int(
            con.execute(
                f"SELECT COUNT(*) FROM (SELECT season, fixture_id, persistent_team_code FROM read_parquet('{_escape(team_fixture_out)}') GROUP BY season, fixture_id, persistent_team_code HAVING COUNT(*) > 1)"
            ).fetchone()[0]
        )

        if duplicate_fixture_keys:
            raise AssertionError(f"duplicate fixture keys after materialisation: {duplicate_fixture_keys}")
        if duplicate_team_fixture_keys:
            raise AssertionError(f"duplicate team-fixture keys after materialisation: {duplicate_team_fixture_keys}")
        if team_fixture_count != fixture_count * 2:
            raise AssertionError(
                f"team-fixture cardinality mismatch: fixtures={fixture_count}, team_fixtures={team_fixture_count}"
            )

        return {
            "fixtures": fixture_count,
            "team_fixtures": team_fixture_count,
            "fixture_output": str(fixture_out),
            "team_fixture_output": str(team_fixture_out),
        }
    finally:
        con.close()


def _main() -> None:
    parser = argparse.ArgumentParser(description="Build additive FRL analytical Parquet datasets")
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    if args.output_dir is None:
        with tempfile.TemporaryDirectory(prefix="frl-analytical-materialisation-") as tmp:
            result = materialize(Path(tmp))
            print(
                "ANALYTICAL MATERIALISATION PASS: "
                f"{result['fixtures']:,} fixtures / {result['team_fixtures']:,} team-fixtures"
            )
    else:
        result = materialize(args.output_dir)
        print(
            "ANALYTICAL MATERIALISATION PASS: "
            f"{result['fixtures']:,} fixtures / {result['team_fixtures']:,} team-fixtures"
        )


if __name__ == "__main__":
    _main()
