"""Read-only audit of the Pulselive -> FPL element -> verified source-player bridge.

This audit is deliberately evidence-only. It does not create or promote an
identity relationship. It tests whether the live Pulselive player.id can be
connected to the existing FRL player identity chain through independent
namespace evidence.

Expected chain:

    Pulselive player.id
        -> FPL element
        -> player_identity_registry.source_player_id

The existing FRL contracts remain authoritative:
- provider IDs are source-local until verified;
- player identity is season-aware;
- unknown/ambiguous identity fails closed;
- player/team/season evidence is reported separately.
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
REGISTRY = ROOT / "player_identity_registry.csv"
LIVE_STATS = ROOT / "data" / "live_pl_api_cache" / "player_season_stats.json"
LIVE_LEADERBOARD = ROOT / "data" / "live_pl_api_cache" / "player_leaderboard.json"


def norm(value: Any) -> str:
    if value is None:
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.casefold()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def load_registry() -> list[dict[str, str]]:
    with REGISTRY.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def player_identity_from_stats(payload: dict[str, Any]) -> dict[str, str]:
    player = payload.get("payload", {}).get("player", {})
    team = player.get("currentTeam", {}) or {}
    return {
        "pulselive_id": str(player.get("id") or "").strip(),
        "name": str(player.get("name") or "").strip(),
        "team_code": str(team.get("id") or "").strip(),
        "team_name": str(team.get("name") or "").strip(),
    }


def player_identity_from_leaderboard(payload: dict[str, Any]) -> dict[str, str]:
    data = payload.get("payload", {}).get("data", [])
    if not data:
        return {"pulselive_id": "", "name": "", "team_code": "", "team_name": ""}
    metadata = data[0].get("playerMetadata", {}) or {}
    team = metadata.get("currentTeam", {}) or {}
    return {
        "pulselive_id": str(metadata.get("id") or "").strip(),
        "name": str(metadata.get("name") or "").strip(),
        "team_code": str(team.get("id") or "").strip(),
        "team_name": str(team.get("name") or "").strip(),
    }


def candidate_registry_rows(registry: list[dict[str, str]], live: dict[str, str]) -> list[dict[str, str]]:
    name = norm(live["name"])
    team = str(live["team_code"])
    rows = [r for r in registry if norm(r.get("fpl_name_normalized")) == name]
    if team:
        team_rows = [r for r in rows if str(r.get("team_code") or "") == team]
        if team_rows:
            rows = team_rows
    return rows


def main() -> None:
    print("FRL PLAYER NAMESPACE THREE-WAY BRIDGE AUDIT")
    print("=" * 96)

    registry = load_registry()
    stats = load_json(LIVE_STATS)
    leaderboard = load_json(LIVE_LEADERBOARD)

    observations = []
    if stats:
        observations.append(("player_season_stats", player_identity_from_stats(stats)))
    if leaderboard:
        observations.append(("player_leaderboard", player_identity_from_leaderboard(leaderboard)))

    print(f"Registry rows: {len(registry):,}")
    print(f"Live identity observations: {len(observations):,}")

    all_candidate_sets: list[set[tuple[str, str, str, str]]] = []

    for source_name, live in observations:
        candidates = candidate_registry_rows(registry, live)
        candidate_keys = {
            (
                str(r.get("season") or ""),
                str(r.get("fpl_element") or ""),
                str(r.get("source_player_id") or ""),
                str(r.get("team_code") or ""),
            )
            for r in candidates
        }
        all_candidate_sets.append(candidate_keys)

        print()
        print(f"{source_name}")
        print(f"  Pulselive id={live['pulselive_id'] or 'MISSING'}")
        print(f"  name={live['name'] or 'MISSING'}")
        print(f"  team={live['team_code'] or 'MISSING'} ({live['team_name'] or 'MISSING'})")
        print(f"  registry candidates={len(candidates):,}")
        for row in candidates[:10]:
            print(
                "  candidate :: "
                f"season={row.get('season')} "
                f"fpl_element={row.get('fpl_element')} "
                f"source_player_id={row.get('source_player_id')} "
                f"team_code={row.get('team_code')} "
                f"confidence={row.get('confidence')} "
                f"status={row.get('identity_status')} "
                f"method={row.get('match_method')}"
            )

    shared = set.intersection(*all_candidate_sets) if all_candidate_sets else set()

    # A true three-way bridge still requires explicit evidence that the live
    # namespace itself maps to the FPL element. The present live payload gives
    # only Pulselive id + name + current team; it does not expose fpl_element.
    live_has_fpl_element = False

    print()
    print("THREE-WAY BRIDGE STATUS")
    print(f"  shared registry identity rows across live observations: {len(shared):,}")
    print(f"  live payload explicitly exposes FPL element: {live_has_fpl_element}")

    if len(shared) == 1 and live_has_fpl_element:
        status = "THREE_WAY_BRIDGE_VERIFIED"
    elif len(shared) == 1:
        status = "TWO_EDGE_CANDIDATE_ONLY"
    elif len(shared) > 1:
        status = "AMBIGUOUS_REGISTRY_CANDIDATE"
    elif len(shared) == 0 and observations:
        status = "NO_SHARED_REGISTRY_CANDIDATE"
    else:
        status = "NO_LIVE_IDENTITY_EVIDENCE"

    print(f"  STATUS: {status}")
    print()
    print("INTERPRETATION")
    if status == "TWO_EDGE_CANDIDATE_ONLY":
        print("  The live Pulselive identity and registry identity agree on name/team,")
        print("  but no live or stored evidence in this audit proves Pulselive player.id -> FPL element.")
        print("  Therefore the registry row remains a candidate, not a promoted three-way bridge.")
    elif status == "THREE_WAY_BRIDGE_VERIFIED":
        print("  Pulselive player.id -> FPL element -> verified source_player_id is explicitly evidenced.")
    else:
        print("  The existing evidence is insufficient to establish a unique three-way identity bridge.")

    print()
    print("No canonical identity or relationship was created or modified.")
    print("=" * 96)


if __name__ == "__main__":
    main()
