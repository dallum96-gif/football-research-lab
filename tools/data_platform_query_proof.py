from __future__ import annotations

import json
from pathlib import Path
import tempfile

import duckdb

import query_api

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_FILE = ROOT / "fixtures_master_corrected.csv"
TEAM_REGISTRY = ROOT / "identity" / "team_seasons.csv"


def _escape(path: Path) -> str:
    return str(path.resolve()).replace("'", "''")


def _promote(con: duckdb.DuckDBPyConnection, source: Path, target: Path) -> None:
    con.execute(
        f"COPY (SELECT * FROM read_csv_auto('{_escape(source)}', SAMPLE_SIZE=-1, HEADER=TRUE)) "
        f"TO '{_escape(target)}' (FORMAT PARQUET, COMPRESSION ZSTD)"
    )


def _duckdb_fixture_rows(con: duckdb.DuckDBPyConnection, fixture_pq: Path, team_pq: Path, season: str):
    fixtures = f"read_parquet('{_escape(fixture_pq)}')"
    teams = f"read_parquet('{_escape(team_pq)}')"
    query = f"""
        SELECT
            f.season,
            f.fixture_id,
            f.kickoff_time,
            f.gameweek,
            f.home_team_id,
            f.away_team_id,
            f.home_score,
            f.away_score,
            th.canonical_name AS home_team_name,
            away_team.canonical_name AS away_team_name
        FROM {fixtures} f
        LEFT JOIN {teams} th
          ON f.season = th.season
         AND CAST(f.home_team_id AS VARCHAR) = CAST(th.local_team_id AS VARCHAR)
         AND th.mapping_status = 'VERIFIED'
        LEFT JOIN {teams} away_team
          ON f.season = away_team.season
         AND CAST(f.away_team_id AS VARCHAR) = CAST(away_team.local_team_id AS VARCHAR)
         AND away_team.mapping_status = 'VERIFIED'
        WHERE f.season = ?
        ORDER BY CAST(f.kickoff_time AS VARCHAR), CAST(f.fixture_id AS BIGINT)
    """
    return con.execute(query, [season]).fetchall(), [x[0] for x in con.description]


def _canonical_league_table(rows):
    stats = {}
    for row in rows:
        home_id = str(row["home_team_id"]).strip()
        away_id = str(row["away_team_id"]).strip()
        home_name = str(row["home_team_name"])
        away_name = str(row["away_team_name"])
        home_score = row["home_score"]
        away_score = row["away_score"]
        stats.setdefault(home_id, {"team": home_name, "played": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "points": 0})
        stats.setdefault(away_id, {"team": away_name, "played": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "points": 0})
        if home_score in (None, "") or away_score in (None, ""):
            continue
        hs, aw = int(home_score), int(away_score)
        h, a = stats[home_id], stats[away_id]
        h["played"] += 1
        a["played"] += 1
        h["goals_for"] += hs
        h["goals_against"] += aw
        a["goals_for"] += aw
        a["goals_against"] += hs
        if hs > aw:
            h["wins"] += 1
            a["losses"] += 1
            h["points"] += 3
        elif aw > hs:
            a["wins"] += 1
            h["losses"] += 1
            a["points"] += 3
        else:
            h["draws"] += 1
            a["draws"] += 1
            h["points"] += 1
            a["points"] += 1

    output = []
    for item in stats.values():
        item = dict(item)
        item["goal_difference"] = item["goals_for"] - item["goals_against"]
        output.append(item)
    output.sort(key=lambda x: (-x["points"], -x["goal_difference"], -x["goals_for"], x["team"].casefold()))
    for position, item in enumerate(output, start=1):
        item["position"] = position
    return output


def run_query_proof(season: str = "2025-26", team: str = "Arsenal") -> dict[str, int | str]:
    if not FIXTURE_FILE.exists() or not TEAM_REGISTRY.exists():
        raise FileNotFoundError("Required canonical fixture/team files are missing")

    with tempfile.TemporaryDirectory(prefix="frl-query-proof-") as tmp:
        tmp_path = Path(tmp)
        fixture_pq = tmp_path / "fixtures.parquet"
        team_pq = tmp_path / "team_registry.parquet"
        con = duckdb.connect(database=":memory:")
        try:
            _promote(con, FIXTURE_FILE, fixture_pq)
            _promote(con, TEAM_REGISTRY, team_pq)

            csv_table = query_api.league_table(season)
            csv_fixtures = query_api.fixtures(season=season, team=team, limit=100)

            fixture_rows, cols = _duckdb_fixture_rows(con, fixture_pq, team_pq, season)
            normalised = [{name: row[i] for i, name in enumerate(cols)} for row in fixture_rows]
            duck_table = _canonical_league_table(normalised)

            if csv_table["teams"] != duck_table:
                raise AssertionError("league table mismatch between CSV-backed query and DuckDB analytical representation")

            csv_arsenal = {int(row["fixture_id"]): row for row in csv_fixtures["results"]}
            duck_arsenal = {
                int(row["fixture_id"]): row
                for row in normalised
                if team.casefold() in {str(row["home_team_name"]).casefold(), str(row["away_team_name"]).casefold()}
            }

            if set(csv_arsenal) != set(duck_arsenal):
                raise AssertionError("fixture result key set mismatch for team-filtered query")

            contract_fields = [
                "season", "fixture_id", "kickoff_time", "gameweek",
                "home_team_id", "away_team_id", "home_score", "away_score",
                "home_team_name", "away_team_name",
            ]
            for fixture_id, csv_row in csv_arsenal.items():
                duck_row = duck_arsenal[fixture_id]
                for field in contract_fields:
                    if str(csv_row.get(field, "")) != str(duck_row.get(field, "")):
                        raise AssertionError(
                            f"fixture query mismatch fixture={fixture_id} field={field}: "
                            f"csv={csv_row.get(field)!r} duckdb={duck_row.get(field)!r}"
                        )

            return {
                "season": season,
                "team": team,
                "league_table_rows": len(csv_table["teams"]),
                "fixture_results": len(csv_fixtures["results"]),
                "duckdb_fixture_rows": len(normalised),
            }
        finally:
            con.close()


if __name__ == "__main__":
    print(json.dumps(run_query_proof(), indent=2))
