from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_football_capability_ledger import build_ledger

DEFAULT_RAW_CATALOGUE = (
    ROOT / "data" / "audits" / "pulselive_raw_variables" / "pulselive_raw_variable_catalogue.csv"
)
DEFAULT_OUTPUT_DIR = ROOT / "data" / "audits" / "remaining_football_capability_triage"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _text(row: Mapping[str, object]) -> str:
    return " ".join(
        str(row.get(key) or "").casefold()
        for key in ("path", "leaf_name", "logical_family", "workstream")
    )


def _subworkstream(row: Mapping[str, object]) -> str:
    workstream = str(row.get("workstream") or "")
    text = _text(row)

    if workstream == "EVENTS":
        if any(token in text for token in ("goal", "score")):
            return "EVENT_GOALS_AND_ASSISTS"
        if any(token in text for token in ("card", "yellow", "red", "booking")):
            return "EVENT_DISCIPLINE"
        if any(token in text for token in ("substitut", "substitution", "subbed")):
            return "EVENT_SUBSTITUTIONS"
        if any(token in text for token in ("minute", "second", "clock", "time")):
            return "EVENT_TIMING"
        if any(token in text for token in ("playerid", "teamid", ".id", " id")):
            return "EVENT_IDENTITY_RELATIONSHIPS"
        return "EVENT_OTHER_REVIEW"

    if workstream == "PLAYER_LINEUP_CONTEXT":
        if any(token in text for token in ("position", "role")):
            return "PLAYER_LINEUP_ROLE_POSITION"
        if any(token in text for token in ("substitute", "starter", "starting")):
            return "PLAYER_LINEUP_SELECTION_STATUS"
        if any(token in text for token in ("playerid", ".id", " name", "name")):
            return "PLAYER_LINEUP_IDENTITY"
        return "PLAYER_LINEUP_OTHER_CONTEXT"

    if workstream == "TEAM_LINEUP_CONTEXT":
        if "formation" in text:
            return "TEAM_FORMATION"
        if any(token in text for token in ("teamid", ".id", "name")):
            return "TEAM_LINEUP_IDENTITY"
        return "TEAM_LINEUP_OTHER_CONTEXT"

    if workstream == "MANAGERS":
        if any(token in text for token in ("managerid", ".id", "name")):
            return "MANAGER_IDENTITY"
        return "MANAGER_CONTEXT"

    if workstream in {"MATCH_CONTEXT", "TEAM_MATCH_CONTEXT"}:
        if any(token in text for token in ("goal", "score", "result", "winner")):
            return "MATCH_RESULT_STATE"
        if any(token in text for token in ("kickoff", "date", "time", "minute")):
            return "MATCH_TIMING"
        if any(token in text for token in ("venue", "stadium", "ground", "attendance")):
            return "MATCH_VENUE_ATTENDANCE"
        if any(token in text for token in ("competition", "season", "gameweek", "round")):
            return "MATCH_COMPETITION_CONTEXT"
        if any(token in text for token in ("teamid", "home", "away", "team")):
            return "MATCH_TEAM_RELATIONSHIPS"
        return "MATCH_OTHER_CONTEXT"

    return "FOOTBALL_CONTEXT_REVIEW"


def _analytical_role(row: Mapping[str, object], subworkstream: str) -> str:
    if subworkstream in {
        "EVENT_GOALS_AND_ASSISTS",
        "EVENT_DISCIPLINE",
        "EVENT_SUBSTITUTIONS",
        "EVENT_TIMING",
    }:
        return "ANALYTICAL_EVENT_EVIDENCE"
    if subworkstream in {
        "PLAYER_LINEUP_ROLE_POSITION",
        "PLAYER_LINEUP_SELECTION_STATUS",
        "TEAM_FORMATION",
    }:
        return "SCOUTING_AND_TACTICAL_CONTEXT"
    if "IDENTITY" in subworkstream or "RELATIONSHIPS" in subworkstream:
        return "IDENTITY_RELATIONSHIP_SUPPORT"
    if subworkstream in {
        "MATCH_RESULT_STATE",
        "MATCH_TIMING",
        "MATCH_COMPETITION_CONTEXT",
        "MATCH_VENUE_ATTENDANCE",
    }:
        return "FIXTURE_CONTEXT_SUPPORT"
    if subworkstream.startswith("MANAGER"):
        return "MANAGER_CONTEXT_SUPPORT"
    return "SEMANTIC_REVIEW_REQUIRED"


def _priority(role: str, subworkstream: str) -> str:
    if role in {"ANALYTICAL_EVENT_EVIDENCE", "SCOUTING_AND_TACTICAL_CONTEXT"}:
        return "P0"
    if role in {"FIXTURE_CONTEXT_SUPPORT", "IDENTITY_RELATIONSHIP_SUPPORT"}:
        return "P1"
    if subworkstream.startswith("MANAGER"):
        return "P1"
    return "P2"


def triage_rows(raw_rows: Iterable[Mapping[str, object]]) -> tuple[dict[str, object], ...]:
    ledger = build_ledger(raw_rows)
    rows: list[dict[str, object]] = []

    for source in ledger["rows"]:
        if str(source.get("workstream") or "") == "TEAM_MATCH_STATISTICS":
            continue
        subworkstream = _subworkstream(source)
        role = _analytical_role(source, subworkstream)
        rows.append({
            **source,
            "subworkstream": subworkstream,
            "analytical_role": role,
            "product_priority": _priority(role, subworkstream),
            "governance_status": "SOURCE_EVIDENCE_NOT_YET_PROMOTED",
            "next_action": (
                "DEFINE_EVENT_SEMANTICS_AND_DERIVATION_RULES"
                if role == "ANALYTICAL_EVENT_EVIDENCE"
                else "DEFINE_TACTICAL_CONTEXT_SEMANTICS"
                if role == "SCOUTING_AND_TACTICAL_CONTEXT"
                else "VERIFY_IDENTITY_RELATIONSHIP_ROUTE"
                if role == "IDENTITY_RELATIONSHIP_SUPPORT"
                else "VERIFY_CONTEXT_SEMANTICS"
            ),
        })

    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    rows.sort(key=lambda row: (
        priority_order.get(str(row["product_priority"]), 9),
        str(row["subworkstream"]),
        str(row["path"]),
    ))
    return tuple(rows)


OUTPUT_FIELDS = (
    "resource",
    "path",
    "leaf_name",
    "entity_level",
    "logical_family",
    "workstream",
    "subworkstream",
    "capability_role",
    "analytical_role",
    "product_priority",
    "governance_status",
    "next_action",
    "snapshot_count",
    "snapshot_coverage_pct",
    "value_types",
    "sample_values",
    "example_match_ids",
)


def build_triage(raw_rows: Iterable[Mapping[str, object]]) -> dict[str, object]:
    rows = triage_rows(raw_rows)
    return {
        "schema_version": "1.0.0",
        "remaining_football_match_paths": len(rows),
        "workstream_counts": dict(sorted(Counter(str(row["workstream"]) for row in rows).items())),
        "subworkstream_counts": dict(sorted(Counter(str(row["subworkstream"]) for row in rows).items())),
        "analytical_role_counts": dict(sorted(Counter(str(row["analytical_role"]) for row in rows).items())),
        "priority_counts": dict(sorted(Counter(str(row["product_priority"]) for row in rows).items())),
        "rows": list(rows),
        "interpretation": (
            "This triage covers the 123 football/match raw paths outside the 249 team-match "
            "statistical paths. It is a workstream/navigation aid only: event, lineup, identity, "
            "manager and fixture-context evidence remains at its source-native grain until explicit "
            "semantic, identity and derivation governance is approved."
        ),
    }


def write_triage(result: Mapping[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "remaining_football_capability_triage.csv"
    json_path = output_dir / "remaining_football_capability_triage.json"
    rows = list(result.get("rows") or [])

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in OUTPUT_FIELDS})

    json_path.write_text(json.dumps(dict(result), indent=2, ensure_ascii=False), encoding="utf-8")
    return csv_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Triage the 123 non-team-statistical football/match PulseLive paths."
    )
    parser.add_argument("--raw-catalogue", type=Path, default=DEFAULT_RAW_CATALOGUE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    raw_catalogue = args.raw_catalogue.expanduser().resolve()
    if not raw_catalogue.is_file():
        raise SystemExit(
            f"Raw catalogue not found: {raw_catalogue}. Run the raw PulseLive catalogue first."
        )

    result = build_triage(_read_csv(raw_catalogue))
    csv_path, json_path = write_triage(result, args.output_dir.expanduser().resolve())
    preview = [
        {
            "path": row["path"],
            "subworkstream": row["subworkstream"],
            "role": row["analytical_role"],
            "priority": row["product_priority"],
        }
        for row in list(result["rows"])[:20]
    ]
    print(json.dumps({
        "remaining_football_match_paths": result["remaining_football_match_paths"],
        "workstream_counts": result["workstream_counts"],
        "subworkstream_counts": result["subworkstream_counts"],
        "analytical_role_counts": result["analytical_role_counts"],
        "priority_counts": result["priority_counts"],
        "first_20": preview,
        "csv_output": str(csv_path),
        "json_output": str(json_path),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
