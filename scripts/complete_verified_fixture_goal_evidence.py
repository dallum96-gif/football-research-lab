from __future__ import annotations

import csv
import os
import shutil
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOALS = ROOT / "data" / "fixture_goal_events.csv"
RECOVERY = ROOT / "data" / "raw" / "fixture_goal_events_secondary_recovery_2016_17.csv"

# The staged PulseLive source and its stage report are source-layer evidence,
# not canonical FRL data. Prefer the known local upstream source workspace,
# with an environment-variable override for portability.
def discover_source_root() -> Path:
    configured = os.environ.get("FRL_SOURCE_ROOT", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()

    candidates = [
        ROOT.parent / "Premier-League-Stats" / "fpl_scraper" / "fpl_stats",
        ROOT.parent / "Premier-League-Stats" / "fpl_scraper" / "fpl_stats".replace("/", os.sep),
    ]
    for candidate in candidates:
        if (candidate / "data" / "raw" / "fixture_goal_events_stage_report.csv").is_file():
            return candidate

    return candidates[0]


SOURCE_ROOT = discover_source_root()
STAGE = SOURCE_ROOT / "data" / "raw" / "fixture_goal_events_stage_report.csv"
AUDIT = ROOT / "data" / "fixture_goal_events_build_audit.csv"

REQUIRED_RECOVERY = {
    "season", "canonical_fixture_id", "source_match_id", "source_event_id",
    "source_event_type", "source_event_time_label", "source_scorer_name",
    "source_scorer_team", "source_scorer_player_team", "source_fixture_home",
    "source_fixture_away", "source_fixture_home_score", "source_fixture_away_score",
    "scoring_side", "own_goal", "evidence_source_url",
}


def load(path: Path) -> list[dict[str, str]]:
    """Load CSV rows and repair the known one-column shape defect in recovery rows."""
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            return []

        rows: list[dict[str, str]] = []
        expected = len(header)
        normalized_count = 0

        for line_no, values in enumerate(reader, start=2):
            if len(values) == expected:
                row_values = values
            elif path == RECOVERY and len(values) == expected + 1:
                scorer_id_index = header.index("source_scorer_id")
                home_index = header.index("source_fixture_home")
                if (
                    scorer_id_index + 1 < len(values)
                    and home_index == scorer_id_index + 1
                    and values[scorer_id_index] == ""
                    and values[home_index] == ""
                ):
                    row_values = values[:home_index] + values[home_index + 1:]
                    normalized_count += 1
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

    if normalized_count:
        print(f"RECOVERY ROW SHAPE NORMALIZED: {normalized_count}")
    return rows


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(path)


def as_int(value: str | None) -> int:
    return int(float(str(value or "0").strip()))


def fixture_key(row: dict[str, str]) -> tuple[str, str]:
    return (
        str(row.get("season") or "").strip(),
        str(row.get("fixture_id") or row.get("canonical_fixture_id") or "").strip(),
    )


def main() -> None:
    if not GOALS.is_file():
        raise FileNotFoundError(GOALS)
    if not RECOVERY.is_file():
        raise FileNotFoundError(RECOVERY)
    if not STAGE.is_file():
        raise FileNotFoundError(
            f"Missing stage report: {STAGE}\n"
            f"Resolved source root: {SOURCE_ROOT}\n"
            "Set FRL_SOURCE_ROOT if your upstream source tree is elsewhere."
        )

    current = load(GOALS)
    recovery = load(RECOVERY)
    stage = load(STAGE)

    if not current:
        raise RuntimeError("Canonical goal evidence is empty")
    if not recovery:
        raise RuntimeError("Verified recovery file is empty")

    missing = sorted(REQUIRED_RECOVERY - set(recovery[0].keys()))
    if missing:
        raise RuntimeError(f"Recovery schema missing fields: {missing}")

    recovery_ids = [str(row.get("source_event_id") or "").strip() for row in recovery]
    if any(not event_id for event_id in recovery_ids):
        raise RuntimeError("Recovery rows contain blank source_event_id")
    duplicate_recovery = [k for k, v in Counter(recovery_ids).items() if v > 1]
    if duplicate_recovery:
        raise RuntimeError(f"Duplicate recovery event IDs: {duplicate_recovery}")

    current_ids = {str(row.get("source_event_id") or "").strip() for row in current}
    overlap = current_ids.intersection(recovery_ids)
    if overlap:
        raise RuntimeError(f"Recovery overlaps existing canonical event IDs: {sorted(overlap)[:10]}")

    for row in recovery:
        if str(row.get("source_event_type") or "").strip().casefold() != "goal":
            raise RuntimeError(f"Recovery contains non-goal event: {row.get('source_event_id')}")

        event_id = str(row.get("source_event_id") or "").strip()
        season = str(row.get("season") or "").strip()
        canonical_fixture_id = str(row.get("canonical_fixture_id") or "").strip()
        home = str(row.get("source_fixture_home") or "").strip()
        away = str(row.get("source_fixture_away") or "").strip()
        player_team = str(
            row.get("source_scorer_player_team")
            or row.get("source_scorer_team")
            or ""
        ).strip()
        declared_side = str(row.get("scoring_side") or "").strip().lower()

        if not season or not canonical_fixture_id:
            raise RuntimeError(f"Recovery missing canonical fixture identity: {event_id}")
        if not home or not away:
            raise RuntimeError(f"Recovery missing fixture sides: {event_id}")
        if not player_team:
            raise RuntimeError(f"Recovery missing scorer/player team: {event_id}")
        if str(row.get("evidence_source_url") or "").strip() == "":
            raise RuntimeError(f"Recovery missing evidence URL: {event_id}")

        own_goal = str(row.get("own_goal") or "false").strip().casefold() == "true"

        scorer_side = "home" if player_team == home else "away" if player_team == away else ""
        if not scorer_side:
            raise RuntimeError(
                f"Recovery scorer team cannot be reconciled to fixture sides: "
                f"{event_id} player_team={player_team!r} home={home!r} away={away!r}"
            )

        derived_side = ("away" if scorer_side == "home" else "home") if own_goal else scorer_side
        if declared_side and declared_side != derived_side:
            raise RuntimeError(
                f"Recovery scoring-side mismatch: {event_id} "
                f"declared={declared_side!r} derived={derived_side!r}"
            )
        row["scoring_side"] = derived_side
        # Promote canonical fixture identity into the canonical output schema.
        row["fixture_id"] = canonical_fixture_id

    merged = list(current) + recovery
    fields = list(current[0].keys())
    for row in recovery:
        for key in row.keys():
            if key not in fields:
                fields.append(key)

    if len({str(row.get("source_event_id") or "") for row in merged}) != len(merged):
        raise RuntimeError("Merged canonical evidence contains duplicate source_event_id values")

    # The stage report remains provenance evidence, but its expected_goal_count is
    # not the completeness oracle for failed requests: several failed fixtures have
    # known final scores that disagree with that field. Build the authoritative
    # fixture score from the event rows themselves, using the highest observed
    # final-score pair for each fixture.
    fixture_scores: dict[tuple[str, str], tuple[int, int]] = {}
    for row in merged:
        key = fixture_key(row)
        home_score = row.get("source_fixture_home_score")
        away_score = row.get("source_fixture_away_score")
        if home_score is None or away_score is None or home_score == "" or away_score == "":
            continue
        pair = (as_int(home_score), as_int(away_score))
        previous = fixture_scores.get(key)
        if previous is None or sum(pair) >= sum(previous):
            fixture_scores[key] = pair

    stage_by_fixture = {
        (
            str(row.get("season") or "").strip(),
            str(row.get("canonical_fixture_id") or "").strip(),
        ): row
        for row in stage
    }
    counts = Counter(fixture_key(row) for row in merged)

    incomplete = []
    for key, report in stage_by_fixture.items():
        score = fixture_scores.get(key)
        if score is not None:
            expected = sum(score)
            oracle = "FINAL_SCORE"
        else:
            expected = as_int(report.get("expected_goal_count"))
            oracle = "STAGE_REPORT_FALLBACK"

        actual = counts.get(key, 0)
        if actual != expected:
            incomplete.append((key, expected, actual, report.get("status"), oracle, score))

    reference = [
        row for row in merged
        if row.get("season") == "2016-17"
        and str(row.get("fixture_id")) == "8"
        and str(row.get("source_match_id")) == "855173"
    ]
    if len(reference) != 7:
        raise RuntimeError(f"Reference fixture 2016-17/8 expected 7 events, found {len(reference)}")

    backup = GOALS.with_suffix(GOALS.suffix + ".pre_verified_recovery.bak")
    if not backup.exists():
        shutil.copy2(GOALS, backup)

    write(GOALS, merged, fields)

    audit_fields = [
        "status", "source_file", "row_count", "recovery_rows_added",
        "fixtures_expected", "fixtures_goal_complete", "unresolved_fixtures",
        "reference_fixture_rows", "notes",
    ]
    audit_row = {
        "status": "PASSED" if not incomplete else "BLOCKED",
        "source_file": str(RECOVERY),
        "row_count": len(merged),
        "recovery_rows_added": len(recovery),
        "fixtures_expected": len(stage_by_fixture),
        "fixtures_goal_complete": sum(1 for key in stage_by_fixture if key not in {item[0] for item in incomplete}),
        "unresolved_fixtures": len(incomplete),
        "reference_fixture_rows": len(reference),
        "notes": "Verified secondary recovery merged; final-score oracle used where stage request failed or disagreed.",
    }
    write(AUDIT, [audit_row], audit_fields)

    print("============================================================")
    print("VERIFIED FIXTURE GOAL EVIDENCE COMPLETION")
    print("============================================================")
    print(f"Source root:             {SOURCE_ROOT}")
    print(f"Stage report:            {STAGE}")
    print(f"Existing canonical rows: {len(current)}")
    print(f"Verified recovery rows:  {len(recovery)}")
    print(f"Merged canonical rows:   {len(merged)}")
    print(f"Fixtures expected:       {len(stage_by_fixture)}")
    print(f"Fixtures goal-complete:  {audit_row['fixtures_goal_complete']}/{len(stage_by_fixture)}")
    print(f"Unresolved fixtures:     {len(incomplete)}")
    print(f"Reference fixture rows:  {len(reference)}")
    print(f"Output:                  {GOALS}")
    print(f"Audit:                   {AUDIT}")

    if incomplete:
        for row in incomplete[:25]:
            print(
                f"INCOMPLETE {row[0]} expected={row[1]} actual={row[2]} "
                f"status={row[3]} oracle={row[4]} score={row[5]}"
            )
        raise SystemExit(1)

    print("AUDIT PASSED: all fixtures have complete verified goal evidence.")


if __name__ == "__main__":
    main()
