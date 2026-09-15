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


def _validate_product_contract() -> None:
    page = (ROOT / "web" / "src" / "app" / "players" / "[season]" / "[playerCode]" / "page.tsx").read_text(
        encoding="utf-8-sig"
    )
    api = (ROOT / "api" / "player_stats.py").read_text(encoding="utf-8-sig")

    if "/api/v1/player-profile-foundation/" in page:
        raise RuntimeError(
            "Player Profile presentation regressed to the feature-only foundation endpoint."
        )
    for route_fragment in (
        "/api/v1/players/",
        "/api/v1/player-seasons/",
        "/api/v1/player-profile-radar/",
    ):
        if route_fragment not in page:
            raise RuntimeError(
                f"Player Profile no longer uses established route contract: {route_fragment}"
            )
    if "?season=${encodeURIComponent(season)}" not in page:
        raise RuntimeError(
            "Player Profile season-history request does not seed longitudinal identity with the selected season."
        )
    if "import player_profile_foundation" not in api:
        raise RuntimeError(
            "Established Player API is not consuming the governed Profile foundation."
        )
    if (ROOT / "api" / "player_profile.py").exists():
        raise RuntimeError(
            "Feature-only Player Profile API router still exists; preserve the established product route contract instead."
        )


def main() -> int:
    _validate_product_contract()

    matrix = []
    for label, season, code in CASES:
        result = player_profile_foundation.build_player_profile(season, code)
        if result is None:
            raise RuntimeError(f"Acceptance case unavailable: {label} {season}/{code}")
        profile = result["profile"]
        comparison = result["comparison"]
        if profile["identity_status"] not in {"VERIFIED", "SOURCE_NATIVE_VERIFIED"}:
            raise RuntimeError(f"Acceptance case identity unresolved: {label}")
        if profile["biography"].get("available") is not True:
            raise RuntimeError(f"Acceptance case packaged biography unavailable: {label}")
        matrix.append({
            "case": label,
            "season": season,
            "route_code": code,
            "player": profile["player_name"],
            "identity_status": profile["identity_status"],
            "identity_key": profile["player_identity_key"],
            "portrait_player_code": profile["portrait_player_code"],
            "primary_club": profile["primary_club"],
            "participation_representation": profile["participation_representation"],
            "appearances": profile["appearances"],
            "starts": profile["starts"],
            "minutes": profile["minutes"],
            "biography_available": profile["biography"]["available"],
            "comparison_available": comparison["available"],
            "comparison_complete": comparison.get("complete", False),
        })

    current = player_profile_identity.resolve_route_identity("2026-27", "184029")
    historical = player_profile_identity.resolve_route_identity("2024-25", "13")
    if current.get("player_identity_key") != historical.get("player_identity_key"):
        raise RuntimeError("Ødegaard cross-season identity continuity failed.")

    seasons = player_profile_identity.profile_seasons("2026-27", "184029")
    historical_option = next(
        (row for row in seasons if row.get("season") == "2024-25"),
        None,
    )
    if historical_option is None or historical_option.get("player_code") != "13":
        raise RuntimeError(
            "Ødegaard season navigation did not retain the historical route code 13."
        )

    current_profile = player_profile_foundation.build_player_profile("2026-27", "184029")
    assert current_profile is not None
    profile = current_profile["profile"]
    if (
        profile.get("appearances") != 3
        or profile.get("starts") != 3
        or profile.get("minutes") != 224
        or profile.get("participation_representation") != "PLAYER_PROFILE_SOURCE_STATS_V1"
    ):
        raise RuntimeError(
            "Current Ødegaard descriptive participation is not using the pinned Player-Season representation."
        )
    comparison = current_profile["comparison"]
    if comparison.get("available") is not True or len(comparison.get("axes") or []) != 6:
        raise RuntimeError("Current Ødegaard six-axis Profile comparison is unavailable.")
    if any(axis.get("denominator") != "timePlayed" for axis in comparison["axes"]):
        raise RuntimeError("Player Profile contains a non-native per-90 denominator.")

    print(json.dumps({
        "milestone": "PLAYER_PROFILE_UNIVERSAL_FOUNDATION_V1",
        "status": "PASS",
        "product_route_contract": "ESTABLISHED_PLAYER_PROFILE_ENDPOINTS_PRESERVED",
        "cases": matrix,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
