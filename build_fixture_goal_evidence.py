from __future__ import annotations

import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE = (
    ROOT.parent
    / "Premier-League-Stats"
    / "fpl_scraper"
    / "fpl_stats"
    / "data"
    / "fixture_goal_events.csv"
)
OUT = ROOT / "data" / "fixture_goal_events.csv"
AUDIT = ROOT / "data" / "fixture_goal_events_build_audit.csv"

REQUIRED = {
    "season",
    "fixture_id",
    "source_match_id",
    "source_event_id",
    "source_event_time_label",
    "source_scorer_name",
    "source_scorer_team",
    "source_fixture_home",
    "source_fixture_away",
    "identity_status",
}


def discover_source() -> Path:
    candidates = [
        DEFAULT_SOURCE,
        ROOT.parent / "Premier-League-Stats" / "fpl_scraper" / "fpl_stats" / "data" / "raw" / "fixture_goal_events.csv",
    ]
    existing = [p for p in candidates if p.is_file()]
    if not existing:
        raise FileNotFoundError(
            "Approved local goal-event source not found. Checked:\n"
            + "\n".join(str(p) for p in candidates)
        )
    return existing[0]


def load(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = reader.fieldnames or []
    missing = sorted(REQUIRED - set(fields))
    if missing:
        raise ValueError("Goal-event source missing required fields: " + ", ".join(missing))
    return rows, fields


def build():
    source = discover_source()
    rows, fields = load(source)

    if not rows:
        raise ValueError("Goal-event source contains no rows")

    for row in rows:
        if row.get("identity_status") != "VERIFIED":
            raise ValueError(
                "Refusing to promote non-VERIFIED goal event "
                f"{row.get('season')}/{row.get('fixture_id')}/{row.get('source_event_id')}"
            )

    source_bytes = source.read_bytes()
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()

    OUT.parent.mkdir(parents=True, exist_ok=True)

    output_fields = [
        "frl_source_file",
        "frl_source_sha256",
        "frl_source_row",
    ] + fields

    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields)
        writer.writeheader()
        for index, row in enumerate(rows, start=2):
            output = {
                "frl_source_file": str(source),
                "frl_source_sha256": source_sha256,
                "frl_source_row": index,
            }
            output.update(row)
            writer.writerow(output)

    with AUDIT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["status", "source_file", "source_sha256", "rows", "fields"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "status": "RESOLVED",
                "source_file": str(source),
                "source_sha256": source_sha256,
                "rows": len(rows),
                "fields": len(fields),
            }
        )

    target = [
        r for r in rows
        if r.get("season") == "2016-17"
        and r.get("fixture_id") == "8"
        and r.get("source_match_id") == "855173"
    ]
    if len(target) != 7:
        raise ValueError(
            "Reference fixture validation failed: expected 7 verified events for "
            "2016-17 fixture 8 / source match 855173, found " + str(len(target))
        )

    return source, rows, fields


if __name__ == "__main__":
    source, rows, fields = build()
    print(f"FIXTURE-GOAL EVIDENCE: {len(rows)} rows written")
    print(f"SOURCE NATIVE FIELDS: {len(fields)}")
    print("REFERENCE FIXTURE EVENTS: 7")
    print(f"Source: {source}")
    print(f"Output: {OUT}")
    print(f"Audit: {AUDIT}")
