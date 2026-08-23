"""Audit independent Player / Fixture / Club attachment edges for materialised observations.

Read-only with respect to identity. This does not promote any new identity.
The three edges are evaluated independently:
  - player -> existing verified FRL player identity
  - fixture -> canonical fixture + verified source match route
  - club/team -> verified season-local team-season / persistent club identity
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ATTACHMENTS = ROOT / "data" / "entity_attachments" / "player_match_observation_attachments.csv"
FIXTURES = ROOT / "fixtures_master_corrected.csv"
TEAMS = ROOT / "identity" / "team_seasons.csv"
PLAYERS = ROOT / "player_identity_registry.csv"
OUT = ROOT / "data" / "entity_attachments" / "three_edge_player_match_attachment_audit.csv"


def n(value: object) -> str:
    return str(value or "").strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def unique_fixture_map() -> dict[tuple[str, str], dict[str, str]]:
    out: dict[tuple[str, str], dict[str, str]] = {}
    counts: Counter[tuple[str, str]] = Counter()
    rows = read_csv(FIXTURES)
    for row in rows:
        key = (n(row.get("season")), n(row.get("fixture_id")))
        if key[0] and key[1]:
            counts[key] += 1
            out[key] = row
    return {key: row for key, row in out.items() if counts[key] == 1}


def verified_team_map() -> dict[tuple[str, str], dict[str, str]]:
    out = {}
    for row in read_csv(TEAMS):
        if n(row.get("mapping_status")) != "VERIFIED":
            continue
        key = (n(row.get("season")), n(row.get("local_team_id")))
        if key[0] and key[1]:
            if key in out:
                raise ValueError(f"Duplicate verified team-season key: {key}")
            out[key] = row
    return out


def verified_player_map() -> set[tuple[str, str]]:
    return {
        (n(row.get("season")), n(row.get("source_player_id")))
        for row in read_csv(PLAYERS)
        if n(row.get("identity_status")) == "VERIFIED"
        and n(row.get("season"))
        and n(row.get("source_player_id"))
    }


def main() -> None:
    rows = read_csv(ATTACHMENTS)
    fixture_map = unique_fixture_map()
    team_map = verified_team_map()
    player_map = verified_player_map()

    output = []
    for row in rows:
        season = n(row.get("season"))
        fixture_id = n(row.get("fixture_id"))
        fixture = fixture_map.get((season, fixture_id))

        fixture_status = (
            "VERIFIED" if fixture is not None and n(row.get("fixture_attachment_status")) == "VERIFIED_SOURCE_MATCH_ROUTE"
            else "UNRESOLVED"
        )

        home_id = n(fixture.get("home_team_id")) if fixture else ""
        away_id = n(fixture.get("away_team_id")) if fixture else ""
        home_team = team_map.get((season, home_id))
        away_team = team_map.get((season, away_id))
        home_status = "VERIFIED" if home_team else "UNRESOLVED"
        away_status = "VERIFIED" if away_team else "UNRESOLVED"

        source_player_id = n(row.get("source_player_id"))
        player_status = "VERIFIED" if (season, source_player_id) in player_map else n(row.get("player_attachment_status")) or "UNRESOLVED"

        output.append({
            "season": season,
            "fixture_id": fixture_id,
            "source_match_id": n(row.get("source_match_id")),
            "source_player_id": source_player_id,
            "player_attachment_status": player_status,
            "fixture_attachment_status": fixture_status,
            "home_team_attachment_status": home_status,
            "home_team_season_id": n(home_team.get("team_season_id")) if home_team else "",
            "home_persistent_team_code": n(home_team.get("persistent_team_code")) if home_team else "",
            "away_team_attachment_status": away_status,
            "away_team_season_id": n(away_team.get("team_season_id")) if away_team else "",
            "away_persistent_team_code": n(away_team.get("persistent_team_code")) if away_team else "",
            "attachment_graph_status": (
                "ALL_THREE_VERIFIED"
                if player_status == "VERIFIED" and fixture_status == "VERIFIED" and home_status == "VERIFIED" and away_status == "VERIFIED"
                else "PLAYER_ONLY_UNRESOLVED"
                if fixture_status == "VERIFIED" and home_status == "VERIFIED" and away_status == "VERIFIED" and player_status in {"UNRESOLVED", "AMBIGUOUS"}
                else "PARTIAL_OR_UNRESOLVED"
            ),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(output[0].keys()) if output else [
        "season", "fixture_id", "source_match_id", "source_player_id",
        "player_attachment_status", "fixture_attachment_status",
        "home_team_attachment_status", "home_team_season_id", "home_persistent_team_code",
        "away_team_attachment_status", "away_team_season_id", "away_persistent_team_code",
        "attachment_graph_status",
    ]
    with OUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output)

    def count(field: str) -> Counter:
        return Counter(n(r.get(field)) for r in output)

    graphs = count("attachment_graph_status")
    print("FRL THREE-EDGE OBSERVATION ATTACHMENT AUDIT")
    print("=" * 88)
    print(f"Player-match observations reviewed: {len(output):,}")
    print("PLAYER")
    for k, v in count("player_attachment_status").most_common():
        print(f"  {v:8d} {k}")
    print("FIXTURE")
    for k, v in count("fixture_attachment_status").most_common():
        print(f"  {v:8d} {k}")
    print("HOME CLUB / TEAM")
    for k, v in count("home_team_attachment_status").most_common():
        print(f"  {v:8d} {k}")
    print("AWAY CLUB / TEAM")
    for k, v in count("away_team_attachment_status").most_common():
        print(f"  {v:8d} {k}")
    print("GRAPH")
    for k, v in graphs.most_common():
        print(f"  {v:8d} {k}")
    print(f"Output: {OUT}")
    print("Evidence-only independent edge evaluation; no identity promotion.")


if __name__ == "__main__":
    main()
