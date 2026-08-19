from __future__ import annotations

import csv
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures_master.csv"
AUDIT = ROOT / "data" / "fixture_master_goal_score_correction_audit.csv"
BACKUP = FIXTURES.with_suffix(FIXTURES.suffix + ".pre_goal_score_corrections.bak")

TARGETS = {
    ("2016-17", "23"): ("1", "1"),
    ("2016-17", "99"): ("1", "1"),
    ("2016-17", "308"): ("4", "2"),
}


def load_rows() -> tuple[list[str], list[dict[str, str]]]:
    with FIXTURES.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    if not fields:
        raise RuntimeError("fixtures_master.csv has no header")
    return fields, rows


def write_rows(fields: list[str], rows: list[dict[str, str]]) -> None:
    tmp = FIXTURES.with_suffix(FIXTURES.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(FIXTURES)


def main() -> None:
    if not FIXTURES.is_file():
        raise FileNotFoundError(FIXTURES)

    fields, rows = load_rows()
    required = {"season", "fixture_id", "home_score", "away_score"}
    missing = sorted(required - set(fields))
    if missing:
        raise RuntimeError(f"fixtures_master.csv missing fields: {missing}")

    found: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        key = (str(row.get("season") or "").strip(), str(row.get("fixture_id") or "").strip())
        if key in TARGETS:
            if key in found:
                raise RuntimeError(f"Duplicate target fixture identity in master: {key}")
            found[key] = row

    missing_targets = sorted(set(TARGETS) - set(found))
    if missing_targets:
        raise RuntimeError(f"Target fixtures missing from master: {missing_targets}")

    print("============================================================")
    print("FIXTURE MASTER GOAL-SCORE CORRECTION")
    print("============================================================")

    changes = []
    for key, new_score in TARGETS.items():
        row = found[key]
        old_score = (str(row.get("home_score") or ""), str(row.get("away_score") or ""))
        print(f"{key}: {old_score[0]}-{old_score[1]} -> {new_score[0]}-{new_score[1]}")
        if old_score == new_score:
            continue
        changes.append((key, old_score, new_score))
        row["home_score"], row["away_score"] = new_score

    if not changes:
        print("No changes required: fixture master already reconciled.")
        return

    if not BACKUP.exists():
        shutil.copy2(FIXTURES, BACKUP)

    write_rows(fields, rows)

    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "season", "fixture_id", "old_home_score", "old_away_score",
            "new_home_score", "new_away_score", "reason"
        ])
        for key, old_score, new_score in changes:
            writer.writerow([
                key[0], key[1], old_score[0], old_score[1],
                new_score[0], new_score[1],
                "Reconciled to verified fixture goal-event evidence"
            ])

    print(f"CORRECTED FIXTURES: {len(changes)}")
    print(f"Backup: {BACKUP}")
    print(f"Audit:  {AUDIT}")
    print("FIXTURE MASTER CORRECTION: COMPLETE")


if __name__ == "__main__":
    main()
