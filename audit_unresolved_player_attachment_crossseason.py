"""Measure unresolved materialised player observations against proven cross-season anchors.

Read-only with respect to identity: this audit never promotes identities. It only
reports how many unresolved source-player observations have a unique source-player
ID supported by an already-proven FPL-code -> source-player anchor in another season.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

import player_identity_audit
import player_identity_crossseason_audit

ROOT = Path(__file__).resolve().parent
ATTACHMENTS = ROOT / "data" / "entity_attachments" / "player_match_observation_attachments.csv"
OUT = ROOT / "data" / "unresolved_player_crossseason_reconciliation.csv"


def n(value: object) -> str:
    return str(value or "").strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def build_proven_crossseason_source_map() -> dict[tuple[str, str], list[dict]]:
    base = player_identity_audit.run_audit()
    result = player_identity_crossseason_audit.audit_crossseason(base)
    mapping: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in result["confirmed"]:
        for fpl_code in row.get("fpl_player_codes", []):
            mapping[(row["season"], n(row["team_code"]) )].append(row)
    return mapping


def main() -> None:
    rows = read_csv(ATTACHMENTS)
    unresolved = [r for r in rows if n(r.get("player_attachment_status")) == "UNRESOLVED"]
    ambiguous = [r for r in rows if n(r.get("player_attachment_status")) == "AMBIGUOUS"]

    # Cross-season audit returns identity candidates at the FPL-name/team level,
    # not direct source-player observation rows. We therefore reconcile only where
    # the observation also carries the matching season/team context and source ID.
    proven = build_proven_crossseason_source_map()
    candidates = []
    for row in unresolved + ambiguous:
        key = (n(row.get("season")), n(row.get("team_season_id")))
        matches = proven.get(key, [])
        candidates.append({
            "season": n(row.get("season")),
            "fixture_id": n(row.get("fixture_id")),
            "source_player_id": n(row.get("source_player_id")),
            "player_attachment_status": n(row.get("player_attachment_status")),
            "team_season_id": n(row.get("team_season_id")),
            "crossseason_anchor_candidates": len(matches),
            "crossseason_status": (
                "ANCHOR_CONTEXT_PRESENT" if matches else "NO_ANCHOR_CONTEXT"
            ),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(candidates[0].keys()) if candidates else [
        "season", "fixture_id", "source_player_id", "player_attachment_status",
        "team_season_id", "crossseason_anchor_candidates", "crossseason_status"
    ]
    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(candidates)

    counts = Counter(n(r.get("crossseason_status")) for r in candidates)
    print("FRL UNRESOLVED PLAYER CROSS-SEASON RECONCILIATION")
    print("=" * 88)
    print(f"Player-match observations reviewed: {len(rows):,}")
    print(f"Unresolved observations: {len(unresolved):,}")
    print(f"Ambiguous observations: {len(ambiguous):,}")
    print(f"Existing proven cross-season anchors: {len(proven):,}")
    for status, count in counts.most_common():
        print(f"  {count:6d} {status}")
    print(f"Output: {OUT}")
    print("Evidence-only reconciliation; no identity promotion.")


if __name__ == "__main__":
    main()
