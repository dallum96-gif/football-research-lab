from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from canonical_variable_catalogue import canonical_variables
from fpl_variable_access import fpl_catalogue
from source_field_registry import fields_for_family


def _leaf(field: str) -> str:
    text = str(field or "").replace("[]", "")
    return text.split(".")[-1]


def _segments(field: str) -> tuple[str, ...]:
    text = str(field or "").replace("[]", "")
    return tuple(part for part in text.split(".") if part)


def _normalise(name: str) -> str:
    text = re.sub(r"[^a-z0-9]", "", str(name or "").casefold())
    replacements = (
        ("passes", "pass"),
        ("tackles", "tackle"),
        ("clearances", "clearance"),
        ("crosses", "cross"),
        ("corners", "corner"),
        ("duels", "duel"),
        ("fouls", "foul"),
        ("offsides", "offside"),
        ("savesmade", "saves"),
        ("saves", "save"),
        ("recoveries", "recovery"),
    )
    for source, target in replacements:
        text = text.replace(source, target)
    return text


def _is_observed_raw(row: dict[str, str]) -> bool:
    return str(row.get("semantic_status") or "").upper() == "OBSERVED_IN_RAW_PAYLOAD"


def _governed_team_fields() -> dict[str, str]:
    return {
        spec.source_field: spec.semantic_status
        for spec in fields_for_family("team_match")
        if spec.semantic_status in {"exposed", "derived", "retained", "restricted"}
    }


def _fpl_exposed_fields() -> set[str]:
    return {str(row.get("field_name") or "") for row in fpl_catalogue()}


def _pulse_match_candidate(field: str, governed: dict[str, str]) -> tuple[str, str | None]:
    segments = _segments(field)
    for segment in reversed(segments):
        if segment in governed:
            return "EXACT_GOVERNED_SEGMENT", segment

    by_norm: dict[str, list[str]] = defaultdict(list)
    for candidate in governed:
        by_norm[_normalise(candidate)].append(candidate)
    for segment in reversed(segments):
        matches = by_norm.get(_normalise(segment), [])
        if len(matches) == 1 and matches[0] != segment:
            return "UNIQUE_NORMALISED_GOVERNED_SEGMENT", matches[0]
    return "NO_GOVERNED_STAT_MATCH", None


def _fpl_bucket(row: dict[str, str], exposed: set[str]) -> str:
    field = str(row.get("field_name") or "")
    resource = str(row.get("resource") or "")
    if field in exposed:
        return "ALREADY_RESEARCH_EXPOSED"
    if resource == "bootstrap-static.json":
        if field.startswith("elements[]"):
            return "PLAYER_SNAPSHOT_REVIEW"
        if field.startswith("teams[]"):
            return "TEAM_SNAPSHOT_REVIEW"
        return "CONFIGURATION_CONTEXT_CANDIDATE"
    if field.startswith("history[]") or field.startswith("history_past[]"):
        return "PLAYER_PERFORMANCE_REVIEW"
    if field.startswith("fixtures[]"):
        return "FIXTURE_FORECAST_REVIEW"
    return "OTHER_FPL_REVIEW"


def main() -> int:
    rows = [row for row in canonical_variables() if _is_observed_raw(row)]
    fpl_rows = [row for row in rows if row.get("source_surface") == "fpl"]
    pulse_rows = [row for row in rows if row.get("source_surface") == "pulselive"]

    exposed_fpl = _fpl_exposed_fields()
    governed_team = _governed_team_fields()

    print(f"Observed raw-payload backlog: {len(rows)}")
    print(f"  FPL: {len(fpl_rows)}")
    print(f"  PulseLive: {len(pulse_rows)}")

    fpl_counts = Counter(_fpl_bucket(row, exposed_fpl) for row in fpl_rows)
    print("\nFPL action buckets:")
    for key, value in fpl_counts.most_common():
        print(f"  {key}: {value}")

    fpl_context = [
        str(row.get("field_name") or "")
        for row in fpl_rows
        if _fpl_bucket(row, exposed_fpl) == "CONFIGURATION_CONTEXT_CANDIDATE"
    ]
    if fpl_context:
        print("\nFPL configuration/context examples:")
        for field in fpl_context[:30]:
            print(f"  {field}")

    pulse_team_rows = [
        row for row in pulse_rows
        if str(row.get("field_name") or "").startswith("resources.stats")
    ]
    pulse_other_rows = [row for row in pulse_rows if row not in pulse_team_rows]

    candidate_rows: list[tuple[str, str, str | None]] = []
    pulse_counts = Counter()
    for row in pulse_team_rows:
        field = str(row.get("field_name") or "")
        bucket, candidate = _pulse_match_candidate(field, governed_team)
        pulse_counts[bucket] += 1
        candidate_rows.append((field, bucket, candidate))

    print("\nPulseLive Team-Match action buckets:")
    print(f"  TOTAL_STATS_PATHS: {len(pulse_team_rows)}")
    for key, value in pulse_counts.most_common():
        print(f"  {key}: {value}")

    matched = [item for item in candidate_rows if item[2]]
    if matched:
        print("\nPulseLive governed Team-Match candidates:")
        for field, bucket, candidate in matched[:100]:
            print(f"  {field} -> {candidate} :: {bucket} [{governed_team[candidate]}]")

    unmatched = [item for item in candidate_rows if not item[2]]
    if unmatched:
        print("\nPulseLive Team-Match paths still unmatched:")
        for field, bucket, _ in unmatched[:100]:
            print(f"  {field} :: {bucket}")

    other_by_prefix = Counter()
    for row in pulse_other_rows:
        field = str(row.get("field_name") or "")
        if field.startswith("resources.events"):
            key = "EVENTS"
        elif field.startswith("resources.lineups"):
            key = "LINEUPS"
        elif field.startswith("resources.commentary"):
            key = "COMMENTARY"
        else:
            key = "FIXTURE_OR_OTHER_CONTEXT"
        other_by_prefix[key] += 1

    print("\nOther PulseLive structural groups:")
    for key, value in other_by_prefix.most_common():
        print(f"  {key}: {value}")

    print("\nInterpretation:")
    print("  ALREADY_RESEARCH_EXPOSED is bookkeeping, not new FPL semantic work.")
    print("  CONFIGURATION_CONTEXT_CANDIDATE should be classified as context/infrastructure before any football-metric promotion.")
    print("  PulseLive EXACT/UNIQUE_NORMALISED candidates reuse an already governed Team-Match source-native concept only as review candidates; this audit does not promote them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
