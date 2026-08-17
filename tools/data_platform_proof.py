from __future__ import annotations

from pathlib import Path
import tempfile

import duckdb

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_PLAYER_SOURCE = ROOT / "_merged" / "players" / "2025-26_all_players_gw.csv"
DEFAULT_FIXTURE_SOURCE = ROOT / "data" / "fixture_match_stats.csv"


def _escape(value: Path) -> str:
    return str(value.resolve()).replace("'", "''")


def run_player_proof(source: Path = DEFAULT_PLAYER_SOURCE) -> dict[str, int | str]:
    """Round-trip a trusted player CSV through Parquet and preserve core invariants."""
    source = source.resolve()
    if not source.exists():
        raise FileNotFoundError(source)

    with tempfile.TemporaryDirectory(prefix="frl-parquet-proof-") as tmp:
        parquet = Path(tmp) / f"{source.stem}.parquet"
        con = duckdb.connect(database=":memory:")
        try:
            csv = _escape(source)
            pq = _escape(parquet)
            con.execute(
                f"COPY (SELECT * FROM read_csv_auto('{csv}', SAMPLE_SIZE=-1)) "
                f"TO '{pq}' (FORMAT PARQUET, COMPRESSION ZSTD)"
            )
            rows = int(con.execute(f"SELECT COUNT(*) FROM read_parquet('{pq}')").fetchone()[0])
            csv_rows = int(
                con.execute(
                    f"SELECT COUNT(*) FROM read_csv_auto('{csv}', SAMPLE_SIZE=-1)"
                ).fetchone()[0]
            )
            csv_columns = [
                row[0]
                for row in con.execute(
                    f"DESCRIBE SELECT * FROM read_csv_auto('{csv}', SAMPLE_SIZE=-1)"
                ).fetchall()
            ]
            parquet_columns = [
                row[0]
                for row in con.execute(f"DESCRIBE SELECT * FROM read_parquet('{pq}')").fetchall()
            ]
            if rows != csv_rows:
                raise AssertionError(f"row-count mismatch: CSV={csv_rows}, Parquet={rows}")
            if csv_columns != parquet_columns:
                raise AssertionError("column-order/name mismatch after Parquet promotion")
            return {"source": str(source), "rows": rows, "columns": len(csv_columns)}
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
            csv = _escape(source)
            pq = _escape(parquet)
            con.execute(
                f"COPY (SELECT * FROM read_csv_auto('{csv}', SAMPLE_SIZE=-1)) "
                f"TO '{pq}' (FORMAT PARQUET, COMPRESSION ZSTD)"
            )

            csv_rows = int(
                con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{csv}', SAMPLE_SIZE=-1)")
                .fetchone()[0]
            )
            parquet_rows = int(
                con.execute(f"SELECT COUNT(*) FROM read_parquet('{pq}')").fetchone()[0]
            )
            duplicate_keys = int(
                con.execute(
                    f"SELECT COUNT(*) FROM ("
                    f"SELECT season, fixture_id FROM read_parquet('{pq}') "
                    f"GROUP BY season, fixture_id HAVING COUNT(*) > 1"
                    f")"
                ).fetchone()[0]
            )
            missing_keys = int(
                con.execute(
                    f"SELECT COUNT(*) FROM read_parquet('{pq}') "
                    f"WHERE season IS NULL OR fixture_id IS NULL"
                ).fetchone()[0]
            )

            if parquet_rows != csv_rows:
                raise AssertionError(
                    f"fixture row-count mismatch: CSV={csv_rows}, Parquet={parquet_rows}"
                )
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


def run_proof(source: Path = DEFAULT_PLAYER_SOURCE) -> dict[str, int | str]:
    """Backward-compatible alias for the original player proof."""
    return run_player_proof(source)


if __name__ == "__main__":
    player = run_player_proof()
    fixture = run_fixture_proof()
    print(
        "DATA PLATFORM PROOF PASS: "
        f"player {player['rows']:,} rows / {player['columns']} columns; "
        f"fixtures {fixture['rows']:,} rows / canonical-key checks passed"
    )
