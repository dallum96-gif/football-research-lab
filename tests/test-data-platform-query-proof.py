from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.data_platform_query_proof import run_query_proof


def test_csv_and_duckdb_queries_are_equivalent() -> None:
    result = run_query_proof(season="2025-26", team="Arsenal")

    assert result["league_table_rows"] > 0
    assert result["fixture_results"] > 0
    assert result["duckdb_fixture_rows"] >= result["fixture_results"]
