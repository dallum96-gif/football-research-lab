from __future__ import annotations

import csv
import os
import shutil
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOALS = ROOT / "data" / "fixture_goal_events.csv"
RECOVERY = ROOT / "data" / "raw" / "fixture_goal_events_secondary_recovery_2016_17.csv"
FIXTURES = ROOT / "fixtures_master.csv"
AUDIT = ROOT / "data" / "fixture_goal_events_build_audit.csv"


def discover_source_root() -> Path:
    configured = os.environ.get("FRL_SOURCE_ROOT", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return ROOT.parent / "Premier-League-Stats" / "fpl_scraper" / "fpl_stats"


SOURCE_ROOT = discover_source_root()
STAGE = SOURCE_ROOT / "data" / "raw" / "fixture_goal_events_stage_report.csv"

REQUIRED_RECOVERY = {
    "season", "canonical_fixture_id", "source_match_id", "source_event_id",
    "source_event_type", "source_event_time_label", "source_scorer_name",
    "source_scorer_team", "source_scorer_player_team", "source_fixture_home",
    "source_fixture_away", "source_fixture_home_score", "source_fixture_away_score",
    "scoring_side", "own_goal", "evidence_source_url",
}

REQUIRED_FIXTURE = {
    "season", "fixture_id", "home_score", "away_score",
}


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            return []

        rows: list[dict[str, str]] = []
        expected = len(header)
        normalized = 0

        for line_no, values in enumerate(reader, start=2):
            if len(values) == expected:
                row_values = values
            elif path == RECOVERY and len(values) == expected + 1:
                scorer_id_index = header.index("source_scorer_id")
                home_index = header.index("source_fixture_home")
                if (
                    home_index == scorer_id_index + 1
                    and values[scorer_id_index] == ""
                    and values[home_index] == ""
                ):
                    row_values = values[:home_index] + values[home_index + 1:]
                    normalized += 1
                else:
                    raise RuntimeError(
                        f"Recovery CSV unexpected row shape at line {line_no}: "
                        f"expected {expected}, found {len(values)}"
                    )
            else:
                raise RuntimeError(
                    f"CSV row shape invalid at {path}:{line_no}: "
                    f"expected {expected}, found {len(values)}"
                )

            rows.append(dict(zip(header, row_values)))

    if normalized:
        print(f"RECOVERY ROW SHAPE NORMALIZED: {normalized}")
    return rows


def as_int(value: str | None) -> int:
    return int(float(str(value or "0").strip()))


def key_of(row: dict[str, str]) -> tuple[str, str]:
    return (
        str(row.get("season") or "").strip(),
        str(row.get("fixture_id") or row.get("canonical_fixture_id") or "").strip(),
    )


def normalise_recovery_row(row: dict[str, str]) -> dict[str, str]:
    row = dict(row)
    event_id = str(row.get("source_event_id") or "").strip()
    season = str(row.get("season") or "").strip()
    fixture_id = str(row.get("canonical_fixture_id") or "").strip()
    home = str(row.get("source_fixture_home") or "").strip()
    away = str(row.get("source_fixture_away") or "").strip()
    player_team = str(
        row.get("source_scorer_player_team")
        or row.get("source_scorer_team")
        or ""
    ).strip()

    if not season or not fixture_id:
        raise RuntimeError(f"Recovery missing canonical fixture identity: {event_id}")
    if not home or not away:
        raise RuntimeError(f"Recovery missing fixture sides: {event_id}")
    if not player_team:
        raise RuntimeError(f"Recovery missing scorer/player team: {event_id}")
    if not str(row.get("evidence_source_url") or "").strip():
        raise RuntimeError(f"Recovery missing evidence URL: {event_id}")
    if str(row.get("source_event_type") or "").strip().casefold() != "goal":
        raise RuntimeError(f"Recovery contains non-goal event: {event_id}")

    own_goal = str(row.get("own_goal") or "false").strip().casefold() == "true"
    scorer_side = "home" if player_team == home else "away" if player_team == away else ""
    if not scorer_side:
        raise RuntimeError(
            f"Recovery scorer team cannot be reconciled to fixture sides: {event_id} "
            f"player_team={player_team!r} home={home!r} away={away!r}"
        )

    derived_side = ("away" if scorer_side == "home" else "home") if own_goal else scorer_side
    declared_side = str(row.get("scoring_side") or "").strip().lower()
    if declared_side and declared_side != derived_side:
        raise RuntimeError(
            f"Recovery scoring-side mismatch: {event_id} "
            f"declared={declared_side!r} derived={derived_side!r}"
        )

    row["fixture_id"] = fixture_id
    row["scoring_side"] = derived_side
    row.setdefault("evidence_origin", "MANUAL_SECONDARY_VERIFIED")
    return row


def validate_fixture_master(rows: list[dict[str, str]]) -> dict[tuple[str, str], tuple[int, int]]:
    if not rows:
        raise RuntimeError("fixtures_master.csv is empty")
    missing = sorted(REQUIRED_FIXTURE - set(rows[0]))
    if missing:
        raise RuntimeError(f"fixtures_master.csv missing required fields: {missing}")

    scores: dict[tuple[str, str], tuple[int, int]] = {}
    for row in rows:
        key = key_of(row)
        if not key[0] or not key[1]:
            raise RuntimeError("fixtures_master.csv contains blank season/fixture_id")
        score = (as_int(row.get("home_score")), as_int(row.get("away_score")))
        if key in scores and scores[key] != score:
            raise RuntimeError(f"Fixture master score conflict: {key}")
        scores[key] = score

    if len(scores) != 380:
        raise RuntimeError(f"Expected 380 canonical fixtures, found {len(scores)}")
    return scores


def validate_existing_rows(current: list[dict[str, str]]) -> list[dict[str, str]]:
    result = []
    seen: set[str] = set()
    for row in current:
        row = dict(row)
        event_id = str(row.get("source_event_id") or "").strip()
        if not event_id:
            raise RuntimeError("Canonical goal evidence contains blank source_event_id")
        if event_id in seen:
            raise RuntimeError(f"Canonical goal evidence contains duplicate source_event_id: {event_id}")
        seen.add(event_id)
        if not row.get("fixture_id") and row.get("canonical_fixture_id"):
            row["fixture_id"] = str(row["canonical_fixture_id"]).strip()
        result.append(row)
    return result


def write_atomic(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(path)


def main() -> None:
    for path in (GOALS, RECOVERY, FIXTURES):
        if not path.is_file():
            raise FileNotFoundError(path)
    if not STAGE.is_file():
        raise FileNotFoundError(
            f"Missing stage report: {STAGE}\n"
            f"Resolved source root: {SOURCE_ROOT}"
        )

    current = validate_existing_rows(load_csv(GOALS))
    recovery = [normalise_recovery_row(row) for row in load_csv(RECOVERY)]
    fixture_scores = validate_fixture_master(load_csv(FIXTURES))
    stage = load_csv(STAGE)

    missing = sorted(REQUIRED_RECOVERY - set(recovery[0])) if recovery else sorted(REQUIRED_RECOVERY)
    if missing:
        raise RuntimeError(f"Recovery schema missing fields: {missing}")

    recovery_by_id: dict[str, dict[str, str]] = {}
    for row in recovery:
        event_id = row["source_event_id"].strip()
        if event_id in recovery_by_id:
            raise RuntimeError(f"Duplicate recovery event ID: {event_id}")
        recovery_by_id[event_id] = row

    current_by_id = {row["source_event_id"].strip(): row for row in current}
    already_integrated = 0
    new_rows: list[dict[str, str]] = []

    for event_id, recovery_row in recovery_by_id.items():
        if event_id in current_by_id:
            existing = current_by_id[event_id]
            for field in ("season", "fixture_id", "source_scorer_name", "source_scorer_team", "scoring_side"):
                if str(existing.get(field) or "").strip() != str(recovery_row.get(field) or "").strip():
                    raise RuntimeError(f"Existing recovery row conflicts with recovery source: {event_id} field={field}")
            already_integrated += 1
        else:
            new_rows.append(recovery_row)

    merged = current + new_rows
    fields = list(merged[0].keys()) if merged else []
    for row in merged:
        for field in row:
            if field not in fields:
                fields.append(field)

    counts = Counter(key_of(row) for row in merged)
    incomplete = []
    for key, score in fixture_scores.items():
        expected = score[0] + score[1]
        actual = counts.get(key, 0)
        if actual != expected:
            stage_row = next(
                (row for row in stage if key_of(row) == key),
                {},
            )
            incomplete.append(
                (key, expected, actual, stage_row.get("status", ""), score)
            )

    reference = [
        row for row in merged
        if row.get("season") == "2016-17"
        and str(row.get("fixture_id")) == "8"
        and str(row.get("source_match_id")) == "855173"
    ]
    if len(reference) != 7:
        raise RuntimeError(f"Reference fixture 2016-17/8 expected 7 events, found {len(reference)}")

    print("============================================================")
    print("VERIFIED FIXTURE GOAL EVIDENCE COMPLETION")
    print("============================================================")
    print(f"Source root:             {SOURCE_ROOT}")
    print(f"Existing canonical rows: {len(current)}")
    print(f"Recovery rows:           {len(recovery)}")
    print(f"Already integrated:      {already_integrated}")
    print(f"New rows to add:         {len(new_rows)}")
    print(f"Candidate merged rows:   {len(merged)}")
    print(f"Fixtures expected:       {len(fixture_scores)}")
    print(f"Fixtures goal-complete:  {len(fixture_scores) - len(incomplete)}/{len(fixture_scores)}")
    print(f"Unresolved fixtures:     {len(incomplete)}")
    print(f"Reference fixture rows:  {len(reference)}")

    if incomplete:
        for key, expected, actual, status, score in incomplete[:25]:
            print(
                f"INCOMPLETE {key} expected={expected} actual={actual} "
                f"final_score={score[0]}-{score[1]} stage_status={status}"
            )
        print("AUDIT BLOCKED: canonical file NOT modified.")
        raise SystemExit(1)

    backup = GOALS.with_suffix(GOALS.suffix + ".pre_verified_recovery.bak")
    if not backup.exists():
        shutil.copy2(GOALS, backup)

    write_atomic(GOALS, merged, fields)

    audit_fields = [
        "status", "source_file", "row_count", "recovery_rows_total",
        "recovery_rows_already_integrated", "recovery_rows_added",
        "fixtures_expected", "fixtures_goal_complete", "unresolved_fixtures",
        "reference_fixture_rows", "notes",
    ]
    audit_row = {
        "status": "PASSED",
        "source_file": str(RECOVERY),
        "row_count": len(merged),
        "recovery_rows_total": len(recovery),
        "recovery_rows_already_integrated": already_integrated,
        "recovery_rows_added": len(new_rows),
        "fixtures_expected": len(fixture_scores),
        "fixtures_goal_complete": len(fixture_scores),
        "unresolved_fixtures": 0,
        "reference_fixture_rows": len(reference),
        "notes": "Final-score oracle from fixtures_master.csv; write occurs only after full audit passes.",
    }
    write_atomic(AUDIT, [audit_row], audit_fields)

    print(f"Output:                  {GOALS}")
    print(f"Audit:                   {AUDIT}")
    print("AUDIT PASSED: all 380 fixtures have complete verified goal evidence.")


if __name__ == "__main__":
    main()
