from __future__ import annotations

from pathlib import Path
import re
import tempfile

import duckdb

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_PLAYER_SOURCE = ROOT / "_merged" / "players" / "2025-26_all_players_gw.csv"
DEFAULT_FIXTURE_SOURCE = ROOT / "data" / "fixture_match_stats.csv"
DEFAULT_FIXTURE_MASTER = ROOT / "fixtures_master_corrected.csv"
DEFAULT_IDENTITY_REGISTRY = ROOT / "player_identity_registry.csv"
DEFAULT_TEAM_REGISTRY = ROOT / "identity" / "team_seasons.csv"


def _escape(value: Path) -> str:
    return str(value.resolve()).replace("'", "''")


def _read_csv(path: Path) -> str:
    escaped = _escape(path)
    return f"read_csv_auto('{escaped}', SAMPLE_SIZE=-1, HEADER=TRUE)"


def _promote_to_parquet(
    con: duckdb.DuckDBPyConnection,
    source: Path,
    parquet: Path,
) -> None:
    csv = _escape(source)
    pq = _escape(parquet)
    con.execute(
        f"COPY (SELECT * FROM read_csv_auto('{csv}', SAMPLE_SIZE=-1, HEADER=TRUE)) "
        f"TO '{pq}' (FORMAT PARQUET, COMPRESSION ZSTD)"
    )


def _season_from_player_source(source: Path) -> str:
    """Derive the season context exactly as the existing loader does."""
    match = re.search(r"(\d{4}-\d{2})", source.name)
    if not match:
        raise ValueError(f"Cannot derive season from player source filename: {source.name}")
    return match.group(1)


def run_player_proof(source: Path = DEFAULT_PLAYER_SOURCE) -> dict[str, int | str]:
    """Round-trip a trusted player CSV and preserve core invariants."""
    source = source.resolve()
    if not source.exists():
        raise FileNotFoundError(source)

    with tempfile.TemporaryDirectory(prefix="frl-parquet-proof-") as tmp:
        parquet = Path(tmp) / f"{source.stem}.parquet"
        con = duckdb.connect(database=":memory:")
        try:
            _promote_to_parquet(con, source, parquet)
            csv = _read_csv(source)
            pq = f"read_parquet('{_escape(parquet)}')"

            csv_rows = int(con.execute(f"SELECT COUNT(*) FROM {csv}").fetchone()[0])
            parquet_rows = int(con.execute(f"SELECT COUNT(*) FROM {pq}").fetchone()[0])
            csv_columns = [row[0] for row in con.execute(f"DESCRIBE SELECT * FROM {csv}").fetchall()]
            parquet_columns = [row[0] for row in con.execute(f"DESCRIBE SELECT * FROM {pq}").fetchall()]

            if parquet_rows != csv_rows:
                raise AssertionError(f"player row-count mismatch: CSV={csv_rows}, Parquet={parquet_rows}")
            if csv_columns != parquet_columns:
                raise AssertionError("player column-order/name mismatch after Parquet promotion")

            return {"source": str(source), "rows": parquet_rows, "columns": len(csv_columns)}
        finally:
            con.close()


def run_fixture_proof(source: Path = DEFAULT_FIXTURE_SOURCE) -> dict[str, int | str]:
    """Round-trip canonical fixture stats and preserve season + fixture_id uniqueness."""
    source = source.resolve()
    if not source.exists():
        raise FileNotFoundError(source)

    with tempfile.TemporaryDirectory(prefix="frl-fixture-parquet-proof-") as tmp:
        parquet = Path(tmp) / f"{source.stem}.parquet"
        con = duckdb.connect(database=":memory:")
        try:
            _promote_to_parquet(con, source, parquet)
            csv = _read_csv(source)
            pq = f"read_parquet('{_escape(parquet)}')"

            csv_rows = int(con.execute(f"SELECT COUNT(*) FROM {csv}").fetchone()[0])
            parquet_rows = int(con.execute(f"SELECT COUNT(*) FROM {pq}").fetchone()[0])
            duplicate_keys = int(
                con.execute(
                    f"SELECT COUNT(*) FROM (SELECT season, fixture_id FROM {pq} GROUP BY season, fixture_id HAVING COUNT(*) > 1)"
                ).fetchone()[0]
            )
            missing_keys = int(
                con.execute(
                    f"SELECT COUNT(*) FROM {pq} WHERE season IS NULL OR fixture_id IS NULL"
                ).fetchone()[0]
            )

            if parquet_rows != csv_rows:
                raise AssertionError(f"fixture row-count mismatch: CSV={csv_rows}, Parquet={parquet_rows}")
            if duplicate_keys:
                raise AssertionError(f"duplicate season + fixture_id keys: {duplicate_keys}")
            if missing_keys:
                raise AssertionError(f"missing season + fixture_id keys: {missing_keys}")

            return {
                "source": str(source),
                "rows": parquet_rows,
                "duplicate_keys": duplicate_keys,
                "missing_keys": missing_keys,
            }
        finally:
            con.close()


def run_relationship_proof(
    fixture_stats: Path = DEFAULT_FIXTURE_SOURCE,
    fixture_master: Path = DEFAULT_FIXTURE_MASTER,
    identity_registry: Path = DEFAULT_IDENTITY_REGISTRY,
    team_registry: Path = DEFAULT_TEAM_REGISTRY,
    player_source: Path = DEFAULT_PLAYER_SOURCE,
) -> dict[str, int | str]:
    """Prove the principal FRL cross-layer relationships survive promotion."""
    paths = [fixture_stats, fixture_master, identity_registry, team_registry, player_source]
    for path in paths:
        if not path.resolve().exists():
            raise FileNotFoundError(path)

    player_season = _season_from_player_source(player_source)

    with tempfile.TemporaryDirectory(prefix="frl-relationship-proof-") as tmp:
        tmp_path = Path(tmp)
        promoted = {
            "fixture_stats": tmp_path / "fixture_stats.parquet",
            "fixture_master": tmp_path / "fixture_master.parquet",
            "identity": tmp_path / "player_identity_registry.parquet",
            "team_registry": tmp_path / "team_seasons.parquet",
            "players": tmp_path / "players.parquet",
        }

        con = duckdb.connect(database=":memory:")
        try:
            _promote_to_parquet(con, fixture_stats, promoted["fixture_stats"])
            _promote_to_parquet(con, fixture_master, promoted["fixture_master"])
            _promote_to_parquet(con, identity_registry, promoted["identity"])
            _promote_to_parquet(con, team_registry, promoted["team_registry"])
            _promote_to_parquet(con, player_source, promoted["players"])

            stats = f"read_parquet('{_escape(promoted['fixture_stats'])}')"
            master = f"read_parquet('{_escape(promoted['fixture_master'])}')"
            identity = f"read_parquet('{_escape(promoted['identity'])}')"
            teams = f"read_parquet('{_escape(promoted['team_registry'])}')"
            players = f"read_parquet('{_escape(promoted['players'])}')"

            orphan_fixture_stats = int(
                con.execute(
                    f"SELECT COUNT(*) FROM {stats} s LEFT JOIN {master} f ON s.season = f.season AND s.fixture_id = f.fixture_id WHERE f.fixture_id IS NULL"
                ).fetchone()[0]
            )
            fixture_stats_total = int(con.execute(f"SELECT COUNT(*) FROM {stats}").fetchone()[0])
            fixture_stats_master_matches = int(
                con.execute(
                    f"SELECT COUNT(*) FROM {stats} s JOIN {master} f ON s.season = f.season AND s.fixture_id = f.fixture_id"
                ).fetchone()[0]
            )

            fixture_count = int(con.execute(f"SELECT COUNT(*) FROM {master}").fetchone()[0])
            duplicate_team_registry_keys = int(
                con.execute(
                    f"SELECT COUNT(*) FROM (SELECT season, club_id FROM {teams} WHERE mapping_status = 'VERIFIED' GROUP BY season, club_id HAVING COUNT(*) > 1)"
                ).fetchone()[0]
            )
            orphan_fixture_home_teams = int(
                con.execute(
                    f"SELECT COUNT(*) FROM {master} f LEFT JOIN {teams} t ON f.season = t.season AND CAST(f.home_team_id AS VARCHAR) = CAST(t.club_id AS VARCHAR) AND t.mapping_status = 'VERIFIED' WHERE t.club_id IS NULL"
                ).fetchone()[0]
            )
            orphan_fixture_away_teams = int(
                con.execute(
                    f"SELECT COUNT(*) FROM {master} f LEFT JOIN {teams} t ON f.season = t.season AND CAST(f.away_team_id AS VARCHAR) = CAST(t.club_id AS VARCHAR) AND t.mapping_status = 'VERIFIED' WHERE t.club_id IS NULL"
                ).fetchone()[0]
            )

            duplicate_identity = int(
                con.execute(
                    f"SELECT COUNT(*) FROM (SELECT season, fpl_element FROM {identity} WHERE identity_status = 'VERIFIED' GROUP BY season, fpl_element HAVING COUNT(*) > 1)"
                ).fetchone()[0]
            )
            verified_identity_rows = int(
                con.execute(
                    f"SELECT COUNT(*) FROM {identity} WHERE identity_status = 'VERIFIED'"
                ).fetchone()[0]
            )
            player_records_with_verified_identity = int(
                con.execute(
                    f"SELECT COUNT(*) FROM {players} p JOIN {identity} i ON CAST('{player_season}' AS VARCHAR) = CAST(i.season AS VARCHAR) AND CAST(p.element AS VARCHAR) = CAST(i.fpl_element AS VARCHAR) WHERE i.identity_status = 'VERIFIED' AND i.season = '{player_season}'"
                ).fetchone()[0]
            )
            verified_identity_orphans = int(
                con.execute(
                    f"SELECT COUNT(*) FROM {identity} i LEFT JOIN {players} p ON CAST('{player_season}' AS VARCHAR) = CAST(i.season AS VARCHAR) AND CAST(p.element AS VARCHAR) = CAST(i.fpl_element AS VARCHAR) WHERE i.identity_status = 'VERIFIED' AND i.season = '{player_season}' AND p.element IS NULL"
                ).fetchone()[0]
            )

            if orphan_fixture_stats:
                raise AssertionError(f"fixture-stat rows without canonical fixture: {orphan_fixture_stats}")
            if fixture_stats_master_matches != fixture_stats_total:
                raise AssertionError(
                    f"fixture-stat join coverage mismatch: matched={fixture_stats_master_matches}, total={fixture_stats_total}"
                )
            if duplicate_team_registry_keys:
                raise AssertionError(f"duplicate verified team identity keys: {duplicate_team_registry_keys}")
            if orphan_fixture_home_teams:
                raise AssertionError(f"fixtures with unverified home-team mapping: {orphan_fixture_home_teams}")
            if orphan_fixture_away_teams:
                raise AssertionError(f"fixtures with unverified away-team mapping: {orphan_fixture_away_teams}")
            if duplicate_identity:
                raise AssertionError(f"duplicate verified player identity keys: {duplicate_identity}")
            if verified_identity_rows == 0:
                raise AssertionError("no verified player identity rows available")
            if player_records_with_verified_identity == 0:
                raise AssertionError("no player records join to verified identity registry")
            if verified_identity_orphans:
                raise AssertionError(f"verified identity rows without matching player source records: {verified_identity_orphans}")

            return {
                "fixture_stats_rows": fixture_stats_total,
                "fixture_count": fixture_count,
                "fixture_stat_orphans": orphan_fixture_stats,
                "home_team_orphans": orphan_fixture_home_teams,
                "away_team_orphans": orphan_fixture_away_teams,
                "identity_verified_rows": verified_identity_rows,
                "player_records_with_verified_identity": player_records_with_verified_identity,
                "verified_identity_orphans": verified_identity_orphans,
            }
        finally:
            con.close()


def run_proof(source: Path = DEFAULT_PLAYER_SOURCE) -> dict[str, int | str]:
    """Backward-compatible alias for the original player proof."""
    return run_player_proof(source)


if __name__ == "__main__":
    player = run_player_proof()
    fixture = run_fixture_proof()
    relationship = run_relationship_proof()
    print(
        "DATA PLATFORM PROOF PASS: "
        f"player {player['rows']:,} rows / {player['columns']} columns; "
        f"fixtures {fixture['rows']:,} rows / canonical-key checks passed; "
        f"relationships {relationship['fixture_stats_rows']:,} fixture-stat rows / "
        f"{relationship['identity_verified_rows']:,} verified player identities / "
        f"{relationship['player_records_with_verified_identity']:,} player records joined"
    )
