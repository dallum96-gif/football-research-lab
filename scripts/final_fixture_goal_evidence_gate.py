from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOALS = ROOT / "data" / "fixture_goal_events.csv"
RECOVERY = ROOT / "data" / "raw" / "fixture_goal_events_secondary_recovery_2016_17.csv"
FIXTURES = ROOT / "fixtures_master.csv"
STAGE = ROOT.parent / "Premier-League-Stats" / "fpl_scraper" / "fpl_stats" / "data" / "raw" / "fixture_goal_events_stage_report.csv"
AUDIT = ROOT / "data" / "fixture_goal_events_final_gate_audit.csv"

TARGET_SEASON = "2016-17"
REFERENCE_FIXTURE = ("2016-17", "8", "855173")


def load(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def as_int(value: str | None) -> int:
    return int(float(str(value or "0").strip()))


def key(row: dict[str, str]) -> tuple[str, str]:
    return (
        str(row.get("season") or "").strip(),
        str(row.get("fixture_id") or row.get("canonical_fixture_id") or "").strip(),
    )


def normalise_recovery_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    # The existing recovery artifact has a known one-column defect for rows with
    # blank scorer IDs. Repair only that exact shape.
    if not rows:
        return rows

    raw_header = list(rows[0].keys())
    # DictReader has already collapsed the extra column into None keys in some
    # Python versions, so also accept rows where canonical fields are missing and
    # recover from the raw CSV through a direct reader below is preferable.
    with RECOVERY.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        expected = len(header)
        out: list[dict[str, str]] = []
        normalised = 0
        scorer_idx = header.index("source_scorer_id")
        home_idx = header.index("source_fixture_home")

        for line_no, values in enumerate(reader, start=2):
            if len(values) == expected:
                fixed = values
            elif len(values) == expected + 1 and home_idx == scorer_idx + 1 and values[scorer_idx] == "" and values[home_idx] == "":
                fixed = values[:home_idx] + values[home_idx + 1:]
                normalised += 1
            else:
                raise RuntimeError(
                    f"Unexpected recovery CSV row shape at line {line_no}: {len(values)} fields; expected {expected}."
                )
            out.append(dict(zip(header, fixed)))

    print(f"Recovery rows loaded: {len(out)}")
    print(f"Recovery rows shape-normalised: {normalised}")
    return out


def main() -> None:
    for path in (GOALS, RECOVERY, FIXTURES, STAGE):
        if not path.is_file():
            raise FileNotFoundError(path)

    goals = load(GOALS)
    recovery = normalise_recovery_rows(load(RECOVERY))
    fixtures = [r for r in load(FIXTURES) if str(r.get("season") or "").strip() == TARGET_SEASON]
    stage = [r for r in load(STAGE) if str(r.get("season") or "").strip() == TARGET_SEASON]

    print("============================================================")
    print("FINAL FIXTURE GOAL EVIDENCE GATE")
    print("============================================================")
    print(f"Target season:             {TARGET_SEASON}")
    print(f"Canonical evidence rows:  {len(goals)}")
    print(f"Verified recovery rows:   {len(recovery)}")
    print(f"Fixture master rows:      {len(fixtures)}")
    print(f"Stage report rows:        {len(stage)}")
    print()

    fixture_master: dict[tuple[str, str], tuple[int, int]] = {}
    for row in fixtures:
        k = key(row)
        if k in fixture_master:
            raise RuntimeError(f"Duplicate fixture master key: {k}")
        fixture_master[k] = (as_int(row.get("home_score")), as_int(row.get("away_score")))

    if len(fixture_master) != 380:
        raise RuntimeError(f"Expected 380 fixtures for {TARGET_SEASON}, found {len(fixture_master)}")

    stage_by_fixture = {key(r): r for r in stage}
    goal_counts = Counter(key(r) for r in goals)
    recovery_ids = {str(r.get("source_event_id") or "").strip() for r in recovery}
    canonical_ids = {str(r.get("source_event_id") or "").strip() for r in goals}

    missing_recovery_ids = sorted(recovery_ids - canonical_ids)
    print(f"Recovery events already in canonical: {len(recovery_ids) - len(missing_recovery_ids)}")
    print(f"Recovery events absent from canonical: {len(missing_recovery_ids)}")

    # Build source-verified score state from goal-event rows. A fixture can have
    # multiple event rows; all populated score pairs must agree.
    score_pairs: defaultdict[tuple[str, str], set[tuple[int, int]]] = defaultdict(set)
    for row in goals:
        k = key(row)
        hs = row.get("source_fixture_home_score")
        aws = row.get("source_fixture_away_score")
        if hs not in (None, "") and aws not in (None, ""):
            score_pairs[k].add((as_int(hs), as_int(aws)))

    failures: list[str] = []
    master_conflicts: list[tuple[tuple[str, str], tuple[int, int], tuple[int, int], int]] = []

    for k, master_score in sorted(fixture_master.items()):
        actual = goal_counts.get(k, 0)
        observed_scores = score_pairs.get(k, set())

        if len(observed_scores) > 1:
            failures.append(f"{k}: conflicting source score pairs {sorted(observed_scores)}")
            continue

        verified_score = next(iter(observed_scores), None)
        expected_from_master = sum(master_score)
        if verified_score is not None:
            expected_from_verified = sum(verified_score)
            if expected_from_verified != actual:
                failures.append(
                    f"{k}: verified source score {verified_score[0]}-{verified_score[1]} "
                    f"requires {expected_from_verified} goals but canonical has {actual}"
                )
            if verified_score != master_score:
                master_conflicts.append((k, master_score, verified_score, actual))
            expected = expected_from_verified
        else:
            expected = expected_from_master

        if actual != expected:
            stage_status = stage_by_fixture.get(k, {}).get("status", "")
            failures.append(
                f"{k}: expected {expected} goals, canonical has {actual} (stage={stage_status})"
            )

    reference = [
        r for r in goals
        if str(r.get("season") or "").strip() == REFERENCE_FIXTURE[0]
        and str(r.get("fixture_id") or r.get("canonical_fixture_id") or "").strip() == REFERENCE_FIXTURE[1]
        and str(r.get("source_match_id") or "").strip() == REFERENCE_FIXTURE[2]
    ]
    if len(reference) != 7:
        failures.append(f"Reference fixture expected 7 events, found {len(reference)}")

    duplicate_ids = [k for k, v in Counter(
        str(r.get("source_event_id") or "").strip() for r in goals
    ).items() if k and v > 1]
    if duplicate_ids:
        failures.append(f"Duplicate canonical source_event_id values: {duplicate_ids[:10]}")

    print()
    print("=== MASTER SCORE CONFLICTS ===")
    print(f"Conflicts: {len(master_conflicts)}")
    for k, master, verified, actual in master_conflicts:
        print(
            f"{k}: fixture_master={master[0]}-{master[1]} | "
            f"verified_event_source={verified[0]}-{verified[1]} | events={actual}"
        )

    print()
    print("=== FINAL VERDICT ===")
    if failures:
        print("AUDIT BLOCKED")
        for failure in failures:
            print(" -", failure)
        raise SystemExit(1)

    print("AUDIT PASSED")
    print(f"Fixtures complete: 380/380")
    print(f"Canonical goal events: {len(goals)}")
    print(f"Reference fixture events: {len(reference)}")
    print(f"Fixture-master/source-score conflicts: {len(master_conflicts)}")

    rows = [{
        "status": "PASSED",
        "season": TARGET_SEASON,
        "fixtures_checked": 380,
        "fixtures_complete": 380,
        "canonical_goal_events": len(goals),
        "recovery_events": len(recovery),
        "master_score_conflicts": len(master_conflicts),
        "reference_fixture_events": len(reference),
        "notes": "Source-verified event score state takes precedence over conflicting fixture-master score; no canonical write performed by this gate.",
    }]
    fields = list(rows[0].keys())
    tmp = AUDIT.with_suffix(AUDIT.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(AUDIT)
    print(f"Audit written: {AUDIT}")


if __name__ == "__main__":
    main()
