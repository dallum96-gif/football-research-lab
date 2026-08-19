from __future__ import annotations

import csv
import hashlib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT.parent / "Premier-League-Stats" / "fpl_scraper" / "fpl_stats"
RAW_ROOT = SOURCE_ROOT / "data" / "raw"
OUTPUT = ROOT / "data" / "fixture_goal_events.csv"
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
PROVENANCE_FIELDS = {"frl_source_file", "frl_source_sha256", "frl_source_row"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def candidate_files() -> list[Path]:
    """Discover every CSV in the approved raw source tree; schema decides eligibility."""
    files = list(RAW_ROOT.rglob("*.csv")) if RAW_ROOT.is_dir() else []
    canonical = SOURCE_ROOT / "data" / "fixture_goal_events.csv"
    if canonical.is_file():
        files.append(canonical)
    return sorted(set(p for p in files if p.is_file()), key=lambda p: str(p).lower())


def read_file(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        rows = list(reader)
    return fields, rows


def build():
    candidates = candidate_files()
    if not candidates:
        raise FileNotFoundError(f"No approved CSVs found under {RAW_ROOT}")

    merged: dict[str, tuple[dict[str, str], Path]] = {}
    audit = []
    candidate_count = len(candidates)
    eligible_files = []
    skipped_schema = []
    source_field_union: set[str] = set()

    for source in candidates:
        fields, rows = read_file(source)
        source_field_union.update(fields)
        missing = sorted(REQUIRED - set(fields))
        if missing:
            skipped_schema.append(source)
            audit.append({
                "status": "SKIPPED_SCHEMA",
                "source_file": str(source),
                "source_sha256": sha256(source),
                "row_count": len(rows),
                "details": ",".join(missing),
            })
            continue

        eligible_files.append(source)
        source_digest = sha256(source)

        for row_number, row in enumerate(rows, start=2):
            event_id = str(row.get("source_event_id") or "").strip()
            if not event_id:
                raise ValueError(f"Missing source_event_id in {source}:{row_number}")

            normalised = dict(row)
            normalised["frl_source_file"] = str(source)
            normalised["frl_source_sha256"] = source_digest
            normalised["frl_source_row"] = str(row_number)

            existing = merged.get(event_id)
            if existing is None:
                merged[event_id] = (normalised, source)
                continue

            old_row, old_source = existing
            comparable = {k: v for k, v in normalised.items() if k not in PROVENANCE_FIELDS}
            old_comparable = {k: v for k, v in old_row.items() if k not in PROVENANCE_FIELDS}
            if comparable != old_comparable:
                raise ValueError(f"Conflicting duplicate source_event_id {event_id}: {old_source} vs {source}")

            audit.append({
                "status": "DUPLICATE_IDENTICAL_SOURCE_ROW",
                "source_file": str(source),
                "source_sha256": source_digest,
                "row_count": 1,
                "details": event_id,
            })

    if not eligible_files:
        raise RuntimeError("No approved source CSV matched the fixture-goal evidence schema")
    if not merged:
        raise RuntimeError("Eligible fixture-goal source CSVs contained no rows")

    rows = [value[0] for value in merged.values()]
    rows.sort(key=lambda row: (
        str(row.get("season") or ""),
        int(float(row.get("fixture_id") or 0)),
        float(row.get("source_event_seconds") or 0),
        str(row.get("source_event_id") or ""),
    ))

    bad = [row for row in rows if row.get("identity_status") != "VERIFIED"]
    if bad:
        raise ValueError(f"Refusing to materialise {len(bad)} non-VERIFIED goal identities")

    fixtures_with_goals = Counter((row.get("season", ""), row.get("fixture_id", "")) for row in rows)
    reference = [
        row for row in rows
        if row.get("season") == "2016-17"
        and row.get("fixture_id") == "8"
        and row.get("source_match_id") == "855173"
    ]
    if len(reference) != 7:
        raise RuntimeError(f"Reference fixture 2016-17/8/source match 855173 must contain exactly 7 events; found {len(reference)}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({k for row in rows for k in row})
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    audit.insert(0, {
        "status": "RESOLVED",
        "source_file": ";".join(str(p) for p in eligible_files),
        "source_sha256": ";".join(sha256(p) for p in eligible_files),
        "row_count": len(rows),
        "details": (
            f"CANDIDATE_FILES={candidate_count};ELIGIBLE_FILES={len(eligible_files)};"
            f"SKIPPED_SCHEMA={len(skipped_schema)};FIXTURES_WITH_GOALS={len(fixtures_with_goals)};"
            f"SOURCE_FIELDS={len(source_field_union)}"
        ),
    })

    with AUDIT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["status", "source_file", "source_sha256", "row_count", "details"])
        writer.writeheader()
        writer.writerows(audit)

    return len(rows), len(eligible_files), len(skipped_schema), len(fixtures_with_goals), len(source_field_union), len(reference)


if __name__ == "__main__":
    rows, eligible, skipped, fixture_count, fields, reference = build()
    print(f"FIXTURE-GOAL EVIDENCE: {rows} rows written")
    print(f"ELIGIBLE SOURCE FILES: {eligible}")
    print(f"SKIPPED SCHEMA FILES: {skipped}")
    print(f"FIXTURES WITH GOALS: {fixture_count}")
    print(f"SOURCE NATIVE FIELDS: {fields}")
    print(f"REFERENCE FIXTURE EVENTS: {reference}")
    print(f"Output: {OUTPUT}")
    print(f"Audit: {AUDIT}")
