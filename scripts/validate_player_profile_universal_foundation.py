"""Acceptance matrix for PLAYER_PROFILE_UNIVERSAL_FOUNDATION_V1."""
from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import player_profile_foundation
import player_profile_identity


CASES = (
    ("current_odegaard", "2026-27", "184029"),
    ("historical_odegaard_route", "2024-25", "13"),
    ("current_defender", "2026-27", "226597"),
    ("low_minute_mid", "2026-27", "232413"),
    ("goalkeeper", "2026-27", "154561"),
    ("forward", "2026-27", "219847"),
)


def main() -> int:
    matrix = []
    for label, season, code in CASES:
        result = player_profile_foundation.build_player_profile(season, code)
        if result is None:
            raise RuntimeError(f"Acceptance case unavailable: {label} {season}/{code}")
        profile = result["profile"]
        comparison = result["comparison"]
        matrix.append({
            "case": label,
            "season": season,
            "route_code": code,
            "player": profile["player_name"],
            "identity_status": profile["identity_status"],
            "identity_key": profile["player_identity_key"],
            "portrait_player_code": profile["portrait_player_code"],
            "primary_club": profile["primary_club"],
            "biography_available": profile["biography"]["available"],
            "comparison_available": comparison["available"],
            "comparison_complete": comparison.get("complete", False),
        })

    current = player_profile_identity.resolve_route_identity("2026-27", "184029")
    historical = player_profile_identity.resolve_route_identity("2024-25", "13")
    if current.get("player_identity_key") != historical.get("player_identity_key"):
        raise RuntimeError("Ødegaard cross-season identity continuity failed.")

    current_profile = player_profile_foundation.build_player_profile("2026-27", "184029")
    assert current_profile is not None
    if current_profile["profile"]["biography"].get("available") is not True:
        raise RuntimeError("Current Ødegaard packaged biography is unavailable.")
    comparison = current_profile["comparison"]
    if comparison.get("available") is not True or len(comparison.get("axes") or []) != 6:
        raise RuntimeError("Current Ødegaard six-axis Profile comparison is unavailable.")
    if any(axis.get("denominator") != "timePlayed" for axis in comparison["axes"]):
        raise RuntimeError("Player Profile contains a non-native per-90 denominator.")

    print(json.dumps({
        "milestone": "PLAYER_PROFILE_UNIVERSAL_FOUNDATION_V1",
        "status": "PASS",
        "cases": matrix,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
