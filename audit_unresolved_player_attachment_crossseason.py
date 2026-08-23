"""Measure unresolved materialised player observations against proven cross-season anchors.

Evidence-only: no identity promotion and no registry mutation.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

import player_identity_audit
import player_identity_crossseason_audit

ROOT = Path(__file__).resolve().parent
PLAYER_MATCH = ROOT / "data" / "entity_attachments" / "player_match_observation_attachments.csv"
PLAYER_SEASON = ROOT / "data" / "entity_attachments" / "player_season_observation_attachments.csv"
TEAM_SEASONS = ROOT / "identity" / "team_seasons.csv"
OUT = ROOT / "data" / "unresolved_player_crossseason_reconciliation.csv"


def n(value: object) -> str:
    return str(value or "").strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def proven_anchors() -> tuple[dict[tuple[str, str, str], set[str]], dict[tuple[str, str], set[str]]]:
    report = player_identity_audit.run_audit()
    cross = player_identity_crossseason_audit.audit_crossseason(report)
    by_season_team_source: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    by_season_source: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in cross["confirmed"]:
        season = n(row.get("season"))
        team = n(row.get("team_code"))
        source = n(row.get("source_player_id"))
        for fpl_code in row.get("fpl_player_codes", []):
            if season and team and source and n(fpl_code):
                by_season_team_source[(season, team, source)].add(n(fpl_code))
                by_season_source[(season, source)].add(n(fpl_code))
    return by_season_team_source, by_season_source


def team_code_by_team_season() -> dict[str, str]:
    mapping = {}
    for row in read_csv(TEAM_SEASONS):
        key = n(row.get("team_season_id"))
        code = n(row.get("persistent_team_code"))
        if key and code:
            mapping[key] = code
    return mapping


def main() -> None:
    team_code_map = team_code_by_team_season()
    by_season_team_source, by_season_source = proven_anchors()

    pm = read_csv(PLAYER_MATCH)
    ps = read_csv(PLAYER_SEASON)
    out: list[dict[str, object]] = []

    for row in pm:
        status = n(row.get("player_attachment_status"))
        if status not in {"UNRESOLVED", "AMBIGUOUS"}:
            continue
        season = n(row.get("season"))
        source = n(row.get("source_player_id"))
        team_code = team_code_map.get(n(row.get("team_season_id")), "")
        candidates = sorted(by_season_team_source.get((season, team_code, source), set()))
        out.append({
            "grain": "player_match",
            "season": season,
            "fixture_id": n(row.get("fixture_id")),
            "source_player_id": source,
            "team_season_id": n(row.get("team_season_id")),
            "persistent_team_code": team_code,
            "original_status": status,
            "crossseason_fpl_candidates": ";".join(candidates),
            "crossseason_status": "UNIQUE_ANCHOR" if len(candidates) == 1 else ("MULTIPLE_ANCHORS" if len(candidates) > 1 else "NO_UNIQUE_ANCHOR"),
        })

    for row in ps:
        status = n(row.get("player_attachment_status"))
        if status not in {"UNRESOLVED", "AMBIGUOUS"}:
            continue
        season = n(row.get("season"))
        source = n(row.get("source_player_id"))
        candidates = sorted(by_season_source.get((season, source), set()))
        out.append({
            "grain": "player_season",
            "season": season,
            "fixture_id": "",
            "source_player_id": source,
            "team_season_id": "",
            "persistent_team_code": "",
            "original_status": status,
            "crossseason_fpl_candidates": ";".join(candidates),
            "crossseason_status": "UNIQUE_ANCHOR" if len(candidates) == 1 else ("MULTIPLE_ANCHORS" if len(candidates) > 1 else "NO_UNIQUE_ANCHOR"),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(out[0].keys()) if out else [
        "grain", "season", "fixture_id", "source_player_id", "team_season_id",
        "persistent_team_code", "original_status", "crossseason_fpl_candidates", "crossseason_status"
    ]
    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out)

    counts = Counter((n(r["grain"]), n(r["crossseason_status"])) for r in out)
    print("FRL UNRESOLVED PLAYER CROSS-SEASON RECONCILIATION")
    print("=" * 88)
    print(f"Unresolved/ambiguous observations reviewed: {len(out):,}")
    for (grain, status), count in sorted(counts.items()):
        print(f"  {grain:15s} {count:6d} {status}")
    print(f"Output: {OUT}")
    print("Evidence-only reconciliation; no identity promotion.")


if __name__ == "__main__":
    main()
