from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REGISTRY_PATH = ROOT / "data" / "reference" / "club_profiles_v1.json"
VISUAL_OVERRIDES_PATH = (
    ROOT / "data" / "reference" / "club_profile_visual_overrides_v1.json"
)


def _document() -> dict:
    with REGISTRY_PATH.open("r", encoding="utf-8") as handle:
        document = json.load(handle)

    if not VISUAL_OVERRIDES_PATH.exists():
        return document

    with VISUAL_OVERRIDES_PATH.open("r", encoding="utf-8") as handle:
        overrides = json.load(handle)

    profiles_by_name = {
        str(profile.get("canonical_name") or "").strip(): profile
        for profile in document.get("profiles") or []
    }

    for override in overrides.get("profiles") or []:
        canonical_name = str(
            override.get("canonical_name") or ""
        ).strip()
        profile = profiles_by_name.get(canonical_name)
        visual_override = override.get("visual")

        if profile is None or not isinstance(visual_override, dict):
            continue

        visual = profile.get("visual")
        if not isinstance(visual, dict):
            visual = {}
            profile["visual"] = visual

        visual.update(copy.deepcopy(visual_override))

    return document


def all_profiles() -> list[dict]:
    document = _document()
    return list(document.get("profiles") or [])


def get_profile(
    persistent_team_code: str,
    season: str | None = None,
) -> dict | None:
    requested_code = str(persistent_team_code).strip()

    document = _document()

    match = next(
        (
            profile
            for profile in document.get("profiles") or []
            if str(profile.get("persistent_team_code") or "").strip()
            == requested_code
        ),
        None,
    )

    if match is None:
        return None

    result = copy.deepcopy(match)

    leadership_by_season = (
        result.pop("leadership_by_season", {}) or {}
    )

    result["season"] = season
    result["leadership"] = (
        leadership_by_season.get(season)
        if season is not None
        else None
    )

    limitations: list[str] = []

    if result.get("status") != "CURATED":
        limitations.append(
            "The persistent club identity is registered, but the "
            "biographical profile has not yet been curated."
        )

    honours = result.get("honours") or {}
    if honours.get("categories"):
        limitations.append(
            "Club honours are a current all-time profile snapshot, "
            "not an as-of reconstruction for the selected season."
        )

    result["limitations"] = limitations

    result["provenance"] = {
        "registry": "data/reference/club_profiles_v1.json",
        "identity_authority": "identity/team_seasons.csv",
        "verified_as_of": result.get("verified_as_of"),
    }

    result["schema_version"] = str(
        document.get("schema_version") or "unknown"
    )

    return result
