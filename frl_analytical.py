from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb

ROOT = Path(__file__).resolve().parent
FIXTURE_FILE = ROOT / "fixtures_master_corrected.csv"
TEAM_REGISTRY = ROOT / "identity" / "team_seasons.csv"
QUERY_VERSION = "1.0.0"


@dataclass(frozen=True)
class ResearchResult:
    query_type: str
    parameters: dict[str, Any]
    columns: list[str]
    rows: list[dict[str, Any]]
    population: dict[str, Any]
    provenance: dict[str, Any]
    temporal_context: dict[str, Any]
    limitations: list[str] = field(default_factory=list)
    query_version: str = QUERY_VERSION
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_type": self.query_type,
            "query_version": self.query_version,
            "parameters": self.parameters,
            "columns": self.columns,
            "rows": self.rows,
            "population": self.population,
            "provenance": self.provenance,
            "temporal_context": self.temporal_context,
            "limitations": self.limitations,
            "generated_at": self.generated_at,
        }


def _escape(path: Path) -> str:
    return str(path.resolve()).replace("'", "''")


def _connection() -> duckdb.DuckDBPyConnection:
    if not FIXTURE_FILE.exists():
        raise FileNotFoundError(f"Canonical fixture file not found: {FIXTURE_FILE}")
    if not TEAM_REGISTRY.exists():
        raise FileNotFoundError(f"Team identity registry not found: {TEAM_REGISTRY}")
    return duckdb.connect(database=":memory:")


def _register_sources(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(
        f"CREATE OR REPLACE VIEW fixtures AS SELECT * FROM read_csv_auto('{_escape(FIXTURE_FILE)}', SAMPLE_SIZE=-1, HEADER=TRUE)"
    )
    con.execute(
        f"CREATE OR REPLACE VIEW team_seasons AS SELECT * FROM read_csv_auto('{_escape(TEAM_REGISTRY)}', SAMPLE_SIZE=-1, HEADER=TRUE)"
    )

    duplicates = con.execute(
        """
        SELECT season, local_team_id, COUNT(*) AS row_count
        FROM team_seasons
        WHERE mapping_status = 'VERIFIED'
        GROUP BY 1, 2
        HAVING COUNT(*) <> 1
        """
    ).fetchall()
    if duplicates:
        raise ValueError(
            "Verified team identity registry is not unique at (season, local_team_id): "
            + repr(duplicates)
        )


def league_table(season: str) -> ResearchResult:
    con = _connection()
    try:
        _register_sources(con)
        rows = con.execute(
            """
            WITH completed AS (
                SELECT
                    f.season,
                    CAST(f.fixture_id AS BIGINT) AS fixture_id,
                    CAST(f.home_team_id AS VARCHAR) AS home_team_id,
                    CAST(f.away_team_id AS VARCHAR) AS away_team_id,
                    TRY_CAST(f.home_score AS INTEGER) AS home_score,
                    TRY_CAST(f.away_score AS INTEGER) AS away_score
                FROM fixtures f
                WHERE f.season = ?
                  AND TRY_CAST(f.home_score AS INTEGER) IS NOT NULL
                  AND TRY_CAST(f.away_score AS INTEGER) IS NOT NULL
            ),
            teams AS (
                SELECT DISTINCT
                    CAST(local_team_id AS VARCHAR) AS local_team_id,
                    REPLACE(canonical_name, '_', ' ') AS team
                FROM team_seasons
                WHERE season = ?
                  AND mapping_status = 'VERIFIED'
            ),
            team_results AS (
                SELECT
                    t.local_team_id,
                    t.team,
                    COUNT(c.fixture_id) AS played,
                    COALESCE(SUM(CASE WHEN c.home_team_id = t.local_team_id AND c.home_score > c.away_score THEN 1 WHEN c.away_team_id = t.local_team_id AND c.away_score > c.home_score THEN 1 ELSE 0 END), 0) AS wins,
                    COALESCE(SUM(CASE WHEN c.home_score = c.away_score THEN 1 ELSE 0 END), 0) AS draws,
                    COALESCE(SUM(CASE WHEN c.home_team_id = t.local_team_id AND c.home_score < c.away_score THEN 1 WHEN c.away_team_id = t.local_team_id AND c.away_score < c.home_score THEN 1 ELSE 0 END), 0) AS losses,
                    COALESCE(SUM(CASE WHEN c.home_team_id = t.local_team_id THEN c.home_score ELSE c.away_score END), 0) AS goals_for,
                    COALESCE(SUM(CASE WHEN c.home_team_id = t.local_team_id THEN c.away_score ELSE c.home_score END), 0) AS goals_against,
                    COALESCE(SUM(CASE WHEN c.home_score > c.away_score AND c.home_team_id = t.local_team_id THEN 3 WHEN c.away_score > c.home_score AND c.away_team_id = t.local_team_id THEN 3 WHEN c.home_score = c.away_score THEN 1 ELSE 0 END), 0) AS points
                FROM teams t
                LEFT JOIN completed c
                  ON c.home_team_id = t.local_team_id
                  OR c.away_team_id = t.local_team_id
                GROUP BY 1, 2
            )
            SELECT
                team,
                played,
                wins,
                draws,
                losses,
                goals_for,
                goals_against,
                goals_for - goals_against AS goal_difference,
                points,
                ROW_NUMBER() OVER (ORDER BY points DESC, goal_difference DESC, goals_for DESC, LOWER(team)) AS position
            FROM team_results
            ORDER BY position
            """,
            [season, season],
        ).fetchall()
        columns = [x[0] for x in con.description]
        result_rows = [dict(zip(columns, row)) for row in rows]
        return ResearchResult(
            query_type="league_table",
            parameters={"season": season},
            columns=columns,
            rows=result_rows,
            population={"season": season, "team_rows": len(result_rows)},
            provenance={
                "fixture_source": str(FIXTURE_FILE),
                "team_identity_source": str(TEAM_REGISTRY),
                "query_version": QUERY_VERSION,
            },
            temporal_context={"season": season, "as_of": "season_end_for_completed_fixtures"},
        )
    finally:
        con.close()


def team_fixtures(season: str, team: str, limit: int = 100) -> ResearchResult:
    con = _connection()
    try:
        _register_sources(con)
        rows = con.execute(
            """
            WITH selected AS (
                SELECT CAST(local_team_id AS VARCHAR) AS local_team_id,
                       REPLACE(canonical_name, '_', ' ') AS team
                FROM team_seasons
                WHERE season = ?
                  AND mapping_status = 'VERIFIED'
                  AND LOWER(REPLACE(canonical_name, '_', ' ')) = LOWER(?)
            )
            SELECT
                f.season,
                CAST(f.fixture_id AS BIGINT) AS fixture_id,
                f.kickoff_time,
                f.gameweek,
                s.team AS team,
                CASE WHEN CAST(f.home_team_id AS VARCHAR) = s.local_team_id THEN 'home' ELSE 'away' END AS venue,
                CASE WHEN CAST(f.home_team_id AS VARCHAR) = s.local_team_id THEN REPLACE(away_team.canonical_name, '_', ' ') ELSE REPLACE(home_team.canonical_name, '_', ' ') END AS opponent,
                f.home_score,
                f.away_score
            FROM fixtures f
            JOIN selected s
              ON CAST(f.home_team_id AS VARCHAR) = s.local_team_id
              OR CAST(f.away_team_id AS VARCHAR) = s.local_team_id
            LEFT JOIN team_seasons home_team
              ON home_team.season = f.season
             AND CAST(home_team.local_team_id AS VARCHAR) = CAST(f.home_team_id AS VARCHAR)
             AND home_team.mapping_status = 'VERIFIED'
            LEFT JOIN team_seasons away_team
              ON away_team.season = f.season
             AND CAST(away_team.local_team_id AS VARCHAR) = CAST(f.away_team_id AS VARCHAR)
             AND away_team.mapping_status = 'VERIFIED'
            WHERE f.season = ?
            ORDER BY f.kickoff_time, fixture_id
            LIMIT ?
            """,
            [season, team, season, limit],
        ).fetchall()
        columns = [x[0] for x in con.description]
        result_rows = [dict(zip(columns, row)) for row in rows]
        return ResearchResult(
            query_type="team_fixtures",
            parameters={"season": season, "team": team, "limit": limit},
            columns=columns,
            rows=result_rows,
            population={"season": season, "requested_team": team, "rows_returned": len(result_rows)},
            provenance={
                "fixture_source": str(FIXTURE_FILE),
                "team_identity_source": str(TEAM_REGISTRY),
                "query_version": QUERY_VERSION,
            },
            temporal_context={"season": season, "ordering": "kickoff_time"},
        )
    finally:
        con.close()
