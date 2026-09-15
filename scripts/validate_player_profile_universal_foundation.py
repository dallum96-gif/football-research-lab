"""Acceptance matrix for PLAYER_PROFILE_UNIVERSAL_ROLLOUT_V1."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import player_profile_foundation
import player_profile_identity
import player_research


CASES = (
    ("current_odegaard", "2026-27", "184029", "MID", "QUALIFIED"),
    ("historical_odegaard_route", "2024-25", "13", "MID", "QUALIFIED"),
    ("current_defender", "2026-27", "226597", "DEF", "QUALIFIED"),
    ("provisional_kovacic", "2026-27", "91651", "MID", "PROVISIONAL"),
    ("provisional_eze", "2026-27", "232413", "MID", "PROVISIONAL"),
    ("goalkeeper", "2026-27", "154561", "GKP", "QUALIFIED"),
    ("forward", "2026-27", "219847", "FWD", "QUALIFIED"),
)

SUPPORTED_POSITIONS = {"GKP", "DEF", "MID", "FWD"}
SUPPORTED_SAMPLE_STATES = {
    "QUALIFIED",
    "PROVISIONAL",
    "INSUFFICIENT_SAMPLE",
}


def _validate_product_contract() -> None:
    page_path = ROOT / "web" / "src" / "app" / "players" / "[season]" / "[playerCode]"
    page = (page_path / "page.tsx").read_text(encoding="utf-8-sig")
    radar = (page_path / "MidfielderRadar.tsx").read_text(encoding="utf-8-sig")
    season_control = (page_path / "PlayerSeasonSelect.tsx").read_text(encoding="utf-8-sig")
    api = (ROOT / "api" / "player_stats.py").read_text(encoding="utf-8-sig")

    if "/api/v1/player-profile-foundation/" in page:
        raise RuntimeError("Player Profile presentation regressed to the feature-only foundation endpoint.")
    for route_fragment in (
        "/api/v1/players/",
        "/api/v1/player-seasons/",
        "/api/v1/player-profile-radar/",
    ):
        if route_fragment not in page:
            raise RuntimeError(f"Player Profile no longer uses established route contract: {route_fragment}")
    if "?season=${encodeURIComponent(season)}" not in page:
        raise RuntimeError("Player Profile history request does not seed longitudinal identity with the selected route season.")
    if "PlayerSeasonSelect" in page:
        raise RuntimeError("Player Profile hero imports or renders a season selector; current Profile must represent now while History owns prior-season navigation.")
    if "<select" in season_control or "useRouter" in season_control:
        raise RuntimeError("Player Profile season-control seam still exposes a selectable season control.")
    if "return null" not in season_control:
        raise RuntimeError("Player Profile season-control seam is not explicitly disabled for the current-state Profile.")
    if "import player_profile_foundation" not in api:
        raise RuntimeError("Established Player API is not consuming the governed Profile foundation.")
    if (ROOT / "api" / "player_profile.py").exists():
        raise RuntimeError("Feature-only Player Profile API router still exists; preserve the established product route contract instead.")

    for position_marker in ("GKP:", "DEF:", "MID:", "FWD:"):
        if position_marker not in radar:
            raise RuntimeError(f"Player Profile radar is not position-aware for {position_marker[:-1]}.")
    for required_copy in (
        "Goalkeeper profile",
        "Defender profile",
        "Midfielder profile",
        "Forward profile",
        "Statistical profile pending",
        "Provisional",
        "formal ranks withheld",
    ):
        if required_copy not in radar:
            raise RuntimeError(f"Player Profile radar copy is missing universal rollout contract: {required_copy}.")
    if "radarData ?" not in page:
        raise RuntimeError("Player Profile discards unavailable/insufficient analytical states instead of rendering them.")


def _validate_case(
    label: str,
    season: str,
    code: str,
    expected_position: str,
    expected_sample_status: str,
) -> dict:
    result = player_profile_foundation.build_player_profile(season, code)
    if result is None:
        raise RuntimeError(f"Acceptance case unavailable: {label} {season}/{code}")
    profile = result["profile"]
    comparison = result["comparison"]
    if profile["identity_status"] not in {"VERIFIED", "SOURCE_NATIVE_VERIFIED"}:
        raise RuntimeError(f"Acceptance case identity unresolved: {label}")
    if profile["biography"].get("available") is not True:
        raise RuntimeError(f"Acceptance case packaged biography unavailable: {label}")
    if profile.get("position") != expected_position:
        raise RuntimeError(
            f"Acceptance case position mismatch: {label} expected {expected_position}, got {profile.get('position')}"
        )
    if comparison.get("sample_status") != expected_sample_status:
        raise RuntimeError(
            f"Acceptance case sample-state mismatch: {label} expected {expected_sample_status}, got {comparison.get('sample_status')}"
        )

    if expected_sample_status == "QUALIFIED":
        if comparison.get("available") is not True:
            raise RuntimeError(f"Qualified acceptance comparison unavailable: {label}")
        if len(comparison.get("axes") or []) != 6:
            raise RuntimeError(f"Qualified acceptance case is not six-axis: {label}")
        if comparison.get("template_key") != f"{expected_position}_PROFILE_V1":
            raise RuntimeError(f"Acceptance case template mismatch: {label}")
        if comparison.get("complete") is not True or comparison.get("observed_axis_count") != 6:
            raise RuntimeError(f"Qualified acceptance case does not have six observed dimensions: {label}")
        if comparison.get("formal_rank_available") is not True:
            raise RuntimeError(f"Qualified acceptance case lost formal rank status: {label}")
    elif expected_sample_status == "PROVISIONAL":
        if comparison.get("available") is not True:
            raise RuntimeError(f"Provisional acceptance comparison unavailable: {label}")
        if comparison.get("comparison_mode") != "INDICATIVE":
            raise RuntimeError(f"Provisional acceptance case is not indicative-only: {label}")
        if comparison.get("formal_rank_available") is not False:
            raise RuntimeError(f"Provisional acceptance case exposes formal rank status: {label}")
        if not (0 < int(comparison.get("sample_minutes") or 0) < int(comparison.get("qualification_minutes") or 0)):
            raise RuntimeError(f"Provisional acceptance sample does not sit below qualification threshold: {label}")
        if any(axis.get("rank") is not None for axis in comparison.get("axes") or []):
            raise RuntimeError(f"Provisional acceptance case exposes formal axis ranks: {label}")
    else:
        if comparison.get("available") is not False:
            raise RuntimeError(f"Insufficient-sample acceptance case exposes a comparison: {label}")
        if comparison.get("comparison_mode") != "NONE":
            raise RuntimeError(f"Insufficient-sample acceptance case has a comparison mode: {label}")
        if comparison.get("formal_rank_available") is not False:
            raise RuntimeError(f"Insufficient-sample acceptance case exposes formal rank status: {label}")

    return {
        "case": label,
        "season": season,
        "route_code": code,
        "player": profile["player_name"],
        "position": profile["position"],
        "identity_status": profile["identity_status"],
        "identity_key": profile["player_identity_key"],
        "portrait_player_code": profile["portrait_player_code"],
        "primary_club": profile["primary_club"],
        "participation_representation": profile["participation_representation"],
        "appearances": profile["appearances"],
        "starts": profile["starts"],
        "minutes": profile["minutes"],
        "biography_available": profile["biography"]["available"],
        "sample_status": comparison.get("sample_status"),
        "sample_minutes": comparison.get("sample_minutes"),
        "qualification_minutes": comparison.get("qualification_minutes"),
        "comparison_available": comparison["available"],
        "comparison_complete": comparison.get("complete", False),
        "comparison_template": comparison.get("template_key"),
        "comparison_mode": comparison.get("comparison_mode"),
        "formal_rank_available": comparison.get("formal_rank_available"),
        "observed_axis_count": comparison.get("observed_axis_count", 0),
    }


def _validate_current_universe() -> dict:
    season = "2026-27"
    players = list(player_research.season_players(season))
    if not players:
        raise RuntimeError("Current Player directory is empty; universal rollout cannot be validated.")

    sample_states: Counter[str] = Counter()
    positions: Counter[str] = Counter()
    comparison_available = 0
    biography_available = 0
    failures: list[str] = []

    for player in players:
        code = str(player.get("player_code") or "")
        name = str(player.get("player_name") or code)
        position = str(player.get("position") or "").upper()
        positions[position] += 1
        if position not in SUPPORTED_POSITIONS:
            failures.append(f"{code} {name}: unsupported current position {position!r}")
            continue

        result = player_profile_foundation.build_player_profile(season, code)
        if result is None:
            failures.append(f"{code} {name}: profile did not build")
            continue
        if result.get("milestone") != "PLAYER_PROFILE_UNIVERSAL_ROLLOUT_V1":
            failures.append(f"{code} {name}: wrong milestone {result.get('milestone')!r}")
            continue

        profile = result["profile"]
        comparison = result["comparison"]
        status = str(comparison.get("sample_status") or "")
        sample_states[status] += 1
        if status not in SUPPORTED_SAMPLE_STATES:
            failures.append(f"{code} {name}: unsupported sample state {status!r}")
            continue

        if profile.get("biography", {}).get("available") is True:
            biography_available += 1
        if comparison.get("available") is True:
            comparison_available += 1

        sample_minutes = int(comparison.get("sample_minutes") or 0)
        qualification_minutes = int(comparison.get("qualification_minutes") or 0)
        axes = list(comparison.get("axes") or ())

        if status == "QUALIFIED":
            if sample_minutes < qualification_minutes:
                failures.append(
                    f"{code} {name}: QUALIFIED with {sample_minutes}/{qualification_minutes} minutes"
                )
            if comparison.get("comparison_mode") != "RANKED" or comparison.get("formal_rank_available") is not True:
                failures.append(f"{code} {name}: QUALIFIED without ranked comparison contract")
        elif status == "PROVISIONAL":
            if not (0 < sample_minutes < qualification_minutes):
                failures.append(
                    f"{code} {name}: PROVISIONAL with invalid {sample_minutes}/{qualification_minutes} minutes"
                )
            if comparison.get("comparison_mode") != "INDICATIVE" or comparison.get("formal_rank_available") is not False:
                failures.append(f"{code} {name}: PROVISIONAL lost indicative-only contract")
            if any(axis.get("rank") is not None for axis in axes):
                failures.append(f"{code} {name}: PROVISIONAL axis exposes formal rank")
        else:
            if comparison.get("comparison_mode") != "NONE" or comparison.get("formal_rank_available") is not False:
                failures.append(f"{code} {name}: INSUFFICIENT_SAMPLE exposes comparison/rank contract")
            if comparison.get("available") is not False:
                failures.append(f"{code} {name}: INSUFFICIENT_SAMPLE marked comparison available")

    if failures:
        preview = "\n".join(failures[:25])
        suffix = f"\n... and {len(failures) - 25} more" if len(failures) > 25 else ""
        raise RuntimeError(
            f"Universal Player Profile rollout failed for {len(failures)} current players:\n{preview}{suffix}"
        )

    for required_state in SUPPORTED_SAMPLE_STATES:
        if sample_states[required_state] == 0:
            raise RuntimeError(
                f"Current-universe validation did not exercise required sample state: {required_state}"
            )

    return {
        "season": season,
        "directory_players": len(players),
        "profile_players": len(players),
        "positions": dict(sorted(positions.items())),
        "sample_states": dict(sorted(sample_states.items())),
        "comparison_available_players": comparison_available,
        "biography_available_players": biography_available,
    }


def main() -> int:
    _validate_product_contract()

    matrix = [
        _validate_case(label, season, code, position, sample_status)
        for label, season, code, position, sample_status in CASES
    ]

    current = player_profile_identity.resolve_route_identity("2026-27", "184029")
    historical = player_profile_identity.resolve_route_identity("2024-25", "13")
    if current.get("player_identity_key") != historical.get("player_identity_key"):
        raise RuntimeError("Ødegaard cross-season identity continuity failed.")

    seasons = player_profile_identity.profile_seasons("2026-27", "184029")
    historical_option = next((row for row in seasons if row.get("season") == "2024-25"), None)
    if historical_option is None or historical_option.get("player_code") != "13":
        raise RuntimeError("Ødegaard History navigation did not retain the historical route code 13.")

    current_profile = player_profile_foundation.build_player_profile("2026-27", "184029")
    assert current_profile is not None
    profile = current_profile["profile"]
    if (
        profile.get("appearances") != 3
        or profile.get("starts") != 3
        or profile.get("minutes") != 224
        or profile.get("participation_representation") != "PLAYER_PROFILE_SOURCE_STATS_V1"
    ):
        raise RuntimeError("Current Ødegaard descriptive participation is not using the pinned Player-Season representation.")
    comparison = current_profile["comparison"]
    if comparison.get("available") is not True or len(comparison.get("axes") or []) != 6:
        raise RuntimeError("Current Ødegaard six-axis Profile comparison is unavailable.")
    if comparison.get("sample_status") != "QUALIFIED":
        raise RuntimeError("Current Ødegaard is not classified as QUALIFIED.")
    if any(axis.get("denominator") != "timePlayed" for axis in comparison["axes"]):
        raise RuntimeError("Ødegaard MID Profile contains a non-native per-90 denominator.")

    universe = _validate_current_universe()

    print(
        json.dumps(
            {
                "milestone": "PLAYER_PROFILE_UNIVERSAL_ROLLOUT_V1",
                "status": "PASS",
                "product_route_contract": "ESTABLISHED_PLAYER_PROFILE_ENDPOINTS_PRESERVED",
                "profile_time_scope": "CURRENT_STATE_WITH_HISTORY_SEPARATE",
                "position_templates": ["GKP", "DEF", "MID", "FWD"],
                "sample_states": [
                    "QUALIFIED",
                    "PROVISIONAL",
                    "INSUFFICIENT_SAMPLE",
                ],
                "cases": matrix,
                "current_universe": universe,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())