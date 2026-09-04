from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import research_access
from scripts.reconcile_pulselive_team_stat_capability import (
    DEFAULT_RAW_CATALOGUE,
    build_reconciliation,
)
from source_family_adapters import team_match_source_rows_for_season
from variable_resolver import resolve_variable, variable_definition

DEFAULT_OUTPUT_DIR = ROOT / "data" / "audits" / "team_match_generic_access"


def _safe_value(value: object) -> bool:
    return value not in (None, "", "null", "None")


@lru_cache(maxsize=16)
def _season_rows(season: str) -> tuple[dict, ...]:
    return tuple(team_match_source_rows_for_season(season))


def _season_order(first_seen: str, last_seen: str) -> tuple[str, ...]:
    seasons = (
        "2016-17", "2017-18", "2018-19", "2019-20", "2020-21",
        "2021-22", "2022-23", "2023-24", "2024-25", "2025-26",
    )
    if first_seen in seasons and last_seen in seasons:
        lo = seasons.index(first_seen)
        hi = seasons.index(last_seen)
        return tuple(reversed(seasons[lo : hi + 1]))
    if last_seen in seasons:
        return tuple(reversed(seasons[: seasons.index(last_seen) + 1]))
    return tuple(reversed(seasons))


def _observed_fixture(field: str, *, first_seen: str, last_seen: str) -> tuple[str, str] | None:
    for season in _season_order(first_seen, last_seen):
        for row in _season_rows(season):
            if _safe_value(row.get(field)):
                fixture_id = str(row.get("frl_fixture_id") or "").strip()
                if fixture_id:
                    return season, fixture_id
    return None


def audit_rows(raw_catalogue: Path = DEFAULT_RAW_CATALOGUE) -> tuple[dict[str, object], ...]:
    reconciliation = build_reconciliation(raw_catalogue)
    exposed = [
        row
        for row in reconciliation["rows"]
        if str(row.get("reconciliation_status") or "") == "EXISTING_EXPOSED"
    ]

    discovery = research_access.discover(family="team_match")
    discovered = {
        str(row.get("variable") or ""): row
        for row in discovery.get("results", [])
    }

    audited: list[dict[str, object]] = []
    for source in exposed:
        field = str(source.get("source_field") or "").strip()
        first_seen = str(source.get("existing_first_seen_season") or "")
        last_seen = str(source.get("existing_last_seen_season") or "")
        sample = _observed_fixture(field, first_seen=first_seen, last_seen=last_seen)

        definition_status = "ERROR"
        definition_error = ""
        discovery_status = str(discovered.get(field, {}).get("status") or "")
        query_status = "NOT_RUN"
        query_error = ""
        sample_season = ""
        sample_fixture_id = ""
        result_rows = 0
        observed_values = 0
        source_field_consistent = False

        if sample is not None:
            sample_season, sample_fixture_id = sample

        try:
            definition = variable_definition(
                field,
                family="team_match",
                season=sample_season or last_seen or "2025-26",
            )
            definition_status = definition.status
        except Exception as exc:  # audit surface: retain exact failure text
            definition_error = f"{type(exc).__name__}: {exc}"

        if sample is None:
            query_status = "NO_NONEMPTY_SOURCE_SAMPLE"
        else:
            try:
                result = resolve_variable(
                    field,
                    family="team_match",
                    season=sample_season,
                    fixture_id=sample_fixture_id,
                )
                values = list(result.get("results", []))
                result_rows = len(values)
                observed_values = sum(1 for row in values if _safe_value(row.get("value")))
                source_field_consistent = bool(values) and all(
                    str(row.get("source_field") or "") == field for row in values
                )
                query_status = "PASS" if result_rows > 0 and source_field_consistent else "FAIL"
            except Exception as exc:  # audit surface: retain exact failure text
                query_status = "ERROR"
                query_error = f"{type(exc).__name__}: {exc}"

        discoverable = field in discovered and discovery_status == "exposed"
        passed = (
            definition_status == "exposed"
            and discoverable
            and query_status == "PASS"
        )

        audited.append({
            "source_field": field,
            "raw_path": str(source.get("raw_path") or ""),
            "raw_logical_family": str(source.get("raw_logical_family") or ""),
            "first_seen_season": first_seen,
            "last_seen_season": last_seen,
            "coverage_class": str(source.get("existing_coverage_class") or ""),
            "definition_status": definition_status,
            "discoverable_as_exposed": discoverable,
            "discovery_status": discovery_status,
            "sample_season": sample_season,
            "sample_fixture_id": sample_fixture_id,
            "query_status": query_status,
            "result_rows": result_rows,
            "observed_values": observed_values,
            "source_field_consistent": source_field_consistent,
            "generic_access_status": "PASS" if passed else "FAIL",
            "definition_error": definition_error,
            "query_error": query_error,
        })

    audited.sort(key=lambda row: str(row["source_field"]).casefold())
    return tuple(audited)


OUTPUT_FIELDS = (
    "source_field",
    "raw_path",
    "raw_logical_family",
    "first_seen_season",
    "last_seen_season",
    "coverage_class",
    "definition_status",
    "discoverable_as_exposed",
    "discovery_status",
    "sample_season",
    "sample_fixture_id",
    "query_status",
    "result_rows",
    "observed_values",
    "source_field_consistent",
    "generic_access_status",
    "definition_error",
    "query_error",
)


def build_audit(raw_catalogue: Path = DEFAULT_RAW_CATALOGUE) -> dict[str, object]:
    rows = audit_rows(raw_catalogue)
    return {
        "schema_version": "1.0.0",
        "exposed_team_match_stat_fields": len(rows),
        "generic_access_status_counts": dict(
            sorted(Counter(str(row["generic_access_status"]) for row in rows).items())
        ),
        "query_status_counts": dict(
            sorted(Counter(str(row["query_status"]) for row in rows).items())
        ),
        "all_exposed_fields_pass_generic_access": bool(rows)
        and all(row["generic_access_status"] == "PASS" for row in rows),
        "rows": list(rows),
        "interpretation": (
            "This audit verifies that raw team-match statistical fields already marked exposed "
            "are discoverable, resolve as exposed definitions, and execute through the shared "
            "team-match generic query route against an observed historical fixture. It does not "
            "establish aggregation, comparability or product-visualisation semantics beyond the "
            "governed exposure decision."
        ),
    }


def write_audit(result: Mapping[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "exposed_team_match_generic_access.csv"
    json_path = output_dir / "exposed_team_match_generic_access.json"

    rows = list(result.get("rows") or [])
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in OUTPUT_FIELDS})

    json_path.write_text(
        json.dumps(dict(result), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return csv_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify all exposed PulseLive team-match statistics through generic FRL access."
    )
    parser.add_argument("--raw-catalogue", type=Path, default=DEFAULT_RAW_CATALOGUE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    raw_catalogue = args.raw_catalogue.expanduser().resolve()
    if not raw_catalogue.is_file():
        raise SystemExit(
            f"Raw catalogue not found: {raw_catalogue}. Run the raw PulseLive catalogue first."
        )

    result = build_audit(raw_catalogue)
    csv_path, json_path = write_audit(result, args.output_dir.expanduser().resolve())
    summary = {
        "exposed_team_match_stat_fields": result["exposed_team_match_stat_fields"],
        "generic_access_status_counts": result["generic_access_status_counts"],
        "query_status_counts": result["query_status_counts"],
        "all_exposed_fields_pass_generic_access": result[
            "all_exposed_fields_pass_generic_access"
        ],
        "failures": [
            {
                "source_field": row["source_field"],
                "definition_status": row["definition_status"],
                "discovery_status": row["discovery_status"],
                "query_status": row["query_status"],
                "definition_error": row["definition_error"],
                "query_error": row["query_error"],
            }
            for row in result["rows"]
            if row["generic_access_status"] != "PASS"
        ],
        "csv_output": str(csv_path),
        "json_output": str(json_path),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if result["all_exposed_fields_pass_generic_access"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
