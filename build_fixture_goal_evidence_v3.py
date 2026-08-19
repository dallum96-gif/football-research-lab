from __future__ import annotations

import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT.parent / "Premier-League-Stats" / "fpl_scraper" / "fpl_stats"
PULSELIVE = SOURCE_ROOT / "data" / "raw" / "fixture_goal_events_pulselive.staged.csv"
STAGE_REPORT = SOURCE_ROOT / "data" / "raw" / "fixture_goal_events_stage_report.csv"
TEAM_EVIDENCE = ROOT / "data" / "fixture_team_evidence.csv"
OUTPUT = ROOT / "data" / "fixture_goal_events.csv"
AUDIT = ROOT / "data" / "fixture_goal_events_build_audit.csv"

REQUIRED_EVENT = {
    "season",
    "canonical_fixture_id",
    "source_match_id",
    "source_event_id",
    "source_event_type",
    "source_event_seconds",
    "source_event_time_label",
    "source_event_text",
    "source_scorer_name",
    "source_scorer_team",
    "source_scorer_id",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def fixture_sides() -> dict[tuple[str, str], dict[str, str]]:
    if not TEAM_EVIDENCE.is_file():
        raise FileNotFoundError(
            f"Required FRL fixture-team evidence missing: {TEAM_EVIDENCE}. "
            "Build fixture team evidence first."
        )

    fields, rows = read_csv(TEAM_EVIDENCE)
    required = {"frl_season", "frl_fixture_id", "frl_venue", "source_team", "source_matchId"}
    missing = sorted(required - set(fields))
    if missing:
        raise RuntimeError(f"Fixture-team evidence missing fields: {missing}")

    sides: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        season = str(row.get("frl_season") or "").strip()
        fixture_id = str(row.get("frl_fixture_id") or "").strip()
        venue = str(row.get("frl_venue") or "").strip().lower()
        team = str(row.get("source_team") or "").replace("_", " ").strip()
        match_id = str(row.get("source_matchId") or "").strip()
        if not season or not fixture_id or not team:
            continue
        record = sides.setdefault((season, fixture_id), {})
        if venue == "home":
            record["home"] = team
        elif venue == "away":
            record["away"] = team
        if match_id:
            record["source_match_id"] = match_id

    return sides


def count_audit() -> dict[tuple[str, str], dict[str, str]]:
    if not STAGE_REPORT.is_file():
        raise FileNotFoundError(f"Goal stage report missing: {STAGE_REPORT}")

    fields, rows = read_csv(STAGE_REPORT)
    required = {
        "season",
        "canonical_fixture_id",
        "expected_goal_count",
        "observed_goal_count",
        "status",
    }
    missing = sorted(required - set(fields))
    if missing:
        raise RuntimeError(f"Goal stage report missing fields: {missing}")

    return {
        (str(row.get("season") or "").strip(), str(row.get("canonical_fixture_id") or "").strip()): row
        for row in rows
    }


def build():
    if not PULSELIVE.is_file():
        raise FileNotFoundError(f"PulseLive staged goal source missing: {PULSELIVE}")

    event_fields, event_rows = read_csv(PULSELIVE)
    missing = sorted(REQUIRED_EVENT - set(event_fields))
    if missing:
        raise RuntimeError(f"PulseLive staged goal source missing fields: {missing}")

    sides = fixture_sides()
    audits = count_audit()
    output_rows: list[dict[str, str]] = []
    audit_rows: list[dict[str, str]] = []
    seen: set[str] = set()
    mismatch_fixtures: set[tuple[str, str]] = set()

    for key, report in audits.items():
        if str(report.get("status") or "") != "OK":
            mismatch_fixtures.add(key)

    for row_number, row in enumerate(event_rows, start=2):
        season = str(row.get("season") or "").strip()
        fixture_id = str(row.get("canonical_fixture_id") or "").strip()
        match_id = str(row.get("source_match_id") or "").strip()
        event_id = str(row.get("source_event_id") or "").strip()

        if not season or not fixture_id or not event_id:
            raise ValueError(f"Incomplete PulseLive event row: {PULSELIVE}:{row_number}")
        if str(row.get("source_event_type") or "").strip().lower() != "goal":
            raise ValueError(f"Non-goal event in goal source: {PULSELIVE}:{row_number}")
        if event_id in seen:
            raise ValueError(f"Duplicate source_event_id in goal source: {event_id}")
        seen.add(event_id)

        side = sides.get((season, fixture_id), {})
        home = side.get("home", "")
        away = side.get("away", "")
        scorer_team = str(row.get("source_scorer_team") or "").replace("_", " ").strip()

        if not home or not away:
            raise RuntimeError(
                f"Canonical fixture sides unavailable for {season}/{fixture_id}; "
                "refusing to materialise goal event."
            )

        if scorer_team not in {home, away}:
            raise RuntimeError(
                f"Goal scorer team cannot be reconciled to fixture sides for "
                f"{season}/{fixture_id}/{event_id}: {scorer_team!r} vs {home!r}/{away!r}"
            )

        report = audits.get((season, fixture_id))
        audit_status = str(report.get("status") if report else "NO_STAGE_REPORT")
        if audit_status != "OK":
            mismatch_fixtures.add((season, fixture_id))

        normalised = dict(row)
        normalised["fixture_id"] = fixture_id
        normalised["source_fixture_home"] = home
        normalised["source_fixture_away"] = away
        normalised["identity_status"] = "VERIFIED"
        normalised["goal_count_audit_status"] = audit_status
        normalised["goal_count_expected"] = str(report.get("expected_goal_count") if report else "")
        normalised["goal_count_observed"] = str(report.get("observed_goal_count") if report else "")
        normalised["frl_source_file"] = str(PULSELIVE)
        normalised["frl_source_sha256"] = sha256(PULSELIVE)
        normalised["frl_source_row"] = str(row_number)
        normalised["frl_stage_report_file"] = str(STAGE_REPORT)
        normalised["frl_stage_report_sha256"] = sha256(STAGE_REPORT)
        normalised["frl_team_evidence_file"] = str(TEAM_EVIDENCE)
        normalised["frl_team_evidence_sha256"] = sha256(TEAM_EVIDENCE)
        output_rows.append(normalised)

    output_rows.sort(
        key=lambda item: (
            item["season"],
            int(float(item["fixture_id"])),
            float(item.get("source_event_seconds") or 0),
            int(float(item.get("source_event_id") or 0)),
        )
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in output_rows for key in row})
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(output_rows)

    audit_rows.insert(0, {
        "status": "RESOLVED",
        "source_file": str(PULSELIVE),
        "source_sha256": sha256(PULSELIVE),
        "row_count": len(output_rows),
        "details": (
            f"FIXTURES_WITH_GOALS={len({(r['season'], r['fixture_id']) for r in output_rows})};"
            f"SOURCE_FIELDS={len(event_fields)};"
            f"STAGE_REPORT_FIXTURES={len(audits)};"
            f"GOAL_COUNT_MISMATCH_FIXTURES={len(mismatch_fixtures)}"
        ),
    })
    if mismatch_fixtures:
        for season, fixture_id in sorted(mismatch_fixtures):
            report = audits.get((season, fixture_id), {})
            audit_rows.append({
                "status": "GOAL_COUNT_MISMATCH",
                "source_file": str(STAGE_REPORT),
                "source_sha256": sha256(STAGE_REPORT),
                "row_count": 1,
                "details": (
                    f"{season}/{fixture_id}: expected={report.get('expected_goal_count','')} "
                    f"observed={report.get('observed_goal_count','')} "
                    f"status={report.get('status','')}"
                ),
            })

    with AUDIT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["status", "source_file", "source_sha256", "row_count", "details"],
        )
        writer.writeheader()
        writer.writerows(audit_rows)

    reference = [
        row for row in output_rows
        if row.get("season") == "2016-17"
        and row.get("fixture_id") == "8"
        and row.get("source_match_id") == "855173"
    ]
    if len(reference) != 7:
        raise RuntimeError(f"Reference fixture must contain exactly 7 events; found {len(reference)}")

    return len(output_rows), len({(r['season'], r['fixture_id']) for r in output_rows}), len(mismatch_fixtures), len(reference)


if __name__ == "__main__":
    rows, fixtures, mismatches, reference = build()
    print(f"FIXTURE-GOAL EVIDENCE V3: {rows} rows written")
    print(f"FIXTURES WITH GOALS: {fixtures}")
    print(f"GOAL COUNT MISMATCH FIXTURES: {mismatches}")
    print(f"REFERENCE FIXTURE EVENTS: {reference}")
    print(f"Output: {OUTPUT}")
    print(f"Audit: {AUDIT}")
