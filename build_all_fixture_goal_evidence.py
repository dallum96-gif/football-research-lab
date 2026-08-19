from __future__ import annotations

import csv
import hashlib
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def candidate_files() -> list[Path]:
    files = []
    if RAW_ROOT.is_dir():
        files.extend(
            p for p in RAW_ROOT.rglob("*.csv")
            if "fixture_goal" in p.name.lower()
            and "event" in p.name.lower()
        )
    canonical = SOURCE_ROOT / "data" / "fixture_goal_events.csv"
    if canonical.is_file():
        files.append(canonical)
    return sorted(set(files), key=lambda p: str(p).lower())


def read_file(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        rows = list(reader)
    return fields, rows


def build():
    sources = candidate_files()
    if not sources:
        raise FileNotFoundError(
            "No approved fixture goal-event CSVs found under the local "
            f"Premier-League-Stats source tree: {RAW_ROOT}"
        )

    merged: dict[str, tuple[dict[str, str], Path]] = {}
    audit = []
    source_field_union: set[str] = set()

    for source in sources:
        fields, rows = read_file(source)
        source_field_union.update(fields)
        missing = sorted(REQUIRED - set(fields))
        if missing:
            audit.append({
                "status": "SKIPPED_SCHEMA",
                "source_file": str(source),
                "source_sha256": sha256(source),
                "row_count": len(rows),
                "details": ",".join(missing),
            })
            continue

        for row_number, row in enumerate(rows, start=2):
            event_id = str(row.get("source_event_id") or "").strip()
            if not event_id:
                raise ValueError(f"Missing source_event_id in {source}:{row_number}")

            normalised = dict(row)
            normalised["frl_source_file"] = str(source)
            normalised["frl_source_sha256"] = sha256(source)
            normalised["frl_source_row"] = str(row_number)

            existing = merged.get(event_id)
            if existing is None:
                merged[event_id] = (normalised, source)
                continue

            old_row, old_source = existing
            comparable = {k: v for k, v in normalised.items() if k not in {"frl_source_file", "frl_source_sha256", "frl_source_row"}}
            old_comparable = {k: v for k, v in old_row.items() if k not in {"frl_source_file", "frl_source_sha256", "frl_source_row"}}

            if comparable != old_comparable:
                raise ValueError(
                    "Conflicting duplicate source_event_id "
                    f"{event_id}: {old_source} vs {source}"
                )

            audit.append({
                "status": "DUPLICATE_IDENTICAL_SOURCE_ROW",
                "source_file": str(source),
                "source_sha256": sha256(source),
                "row_count": 1,
                "details": event_id,
            })

    if not merged:
        raise RuntimeError("No valid fixture goal-event rows were found in approved source files")

    rows = [value[0] for value in merged.values()]
    rows.sort(
        key=lambda row: (
            str(row.get("season") or ""),
            int(float(row.get("fixture_id") or 0)),
            float(row.get("source_event_seconds") or 0),
            int(float(row.get("source_event_id") or 0)),
        )
    )

    if any(row.get("identity_status") != "VERIFIED" for row in rows):
        bad = sum(row.get("identity_status") != "VERIFIED" for row in rows)
        raise ValueError(f"Refusing to materialise {bad} non-VERIFIED goal identities")

    reference = [
        row for row in rows
        if row.get("season") == "2016-17"
        and row.get("fixture_id") == "8"
        and row.get("source_match_id") == "855173"
    ]
    if len(reference) != 7:
        raise RuntimeError(
            "Reference fixture 2016-17/8/source match 855173 must contain exactly "
            f"7 verified events; found {len(reference)}"
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({k for row in rows for k in row})
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    audit.insert(0, {
        "status": "RESOLVED",
        "source_file": ";".join(str(p) for p in sources),
        "source_sha256": ";".join(sha256(p) for p in sources),
        "row_count": len(rows),
        "details": f"SOURCE FILES={len(sources)};SOURCE FIELDS={len(source_field_union)}",
    })
    audit_fields = ["status", "source_file", "source_sha256", "row_count", "details"]
    with AUDIT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=audit_fields)
        writer.writeheader()
        writer.writerows(audit)

    return len(rows), len(source_field_union), len(sources), len(reference)


if __name__ == "__main__":
    row_count, field_count, source_count, reference_count = build()
    print(f"FIXTURE-GOAL EVIDENCE: {row_count} rows written")
    print(f"SOURCE FILES: {source_count}")
    print(f"SOURCE NATIVE FIELDS: {field_count}")
    print(f"REFERENCE FIXTURE EVENTS: {reference_count}")
    print(f"Output: {OUTPUT}")
    print(f"Audit: {AUDIT}")
