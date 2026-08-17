from __future__ import annotations

from pathlib import Path
import shutil
import tempfile

import duckdb

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_SOURCE = ROOT / "_merged" / "players" / "2025-26_all_players_gw.csv"


def run_proof(source: Path = DEFAULT_SOURCE) -> dict[str, int | str]:
    """Round-trip a trusted CSV through Parquet and compare core invariants.

    This is an architectural proof only. It never changes the source CSV and
    writes the temporary Parquet representation outside the repository's
    tracked data paths.
    """
    source = source.resolve()
    if not source.exists():
        raise FileNotFoundError(source)

    with tempfile.TemporaryDirectory(prefix="frl-parquet-proof-") as tmp:
        parquet = Path(tmp) / f"{source.stem}.parquet"
        con = duckdb.connect(database=":memory:")
        try:
            escaped_csv = str(source).replace("'", "''")
            escaped_parquet = str(parquet).replace("'", "''")

            con.execute(
                f"COPY (SELECT * FROM read_csv_auto('{escaped_csv}', SAMPLE_SIZE=-1)) "
                f"TO '{escaped_parquet}' (FORMAT PARQUET, COMPRESSION ZSTD)"
            )

            csv_row_count = int(
                con.execute(
                    f"SELECT COUNT(*) FROM read_csv_auto('{escaped_csv}', SAMPLE_SIZE=-1)"
                ).fetchone()[0]
            )
            parquet_row_count = int(
                con.execute(f"SELECT COUNT(*) FROM read_parquet('{escaped_parquet}')")
                .fetchone()[0]
            )

            csv_columns = [
                row[0]
                for row in con.execute(
                    f"DESCRIBE SELECT * FROM read_csv_auto('{escaped_csv}', SAMPLE_SIZE=-1)"
                ).fetchall()
            ]
            parquet_columns = [
                row[0]
                for row in con.execute(
                    f"DESCRIBE SELECT * FROM read_parquet('{escaped_parquet}')"
                ).fetchall()
            ]

            if csv_row_count != parquet_row_count:
                raise AssertionError(
                    f"row-count mismatch: CSV={csv_row_count}, Parquet={parquet_row_count}"
                )
            if csv_columns != parquet_columns:
                raise AssertionError("column-order/name mismatch after Parquet promotion")

            return {
                "source": str(source),
                "rows": csv_row_count,
                "columns": len(csv_columns),
            }
        finally:
            con.close()


if __name__ == "__main__":
    result = run_proof()
    print(
        "DATA PLATFORM PROOF PASS: "
        f"{result['rows']:,} rows / {result['columns']} columns -> Parquet -> DuckDB"
    )
