from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path

from expected_metric_routing import (
    EXPECTED_ASSISTS,
    EXPECTED_GOALS,
    EXPECTED_GOALS_ON_TARGET,
    PLAYER_MATCH_DERIVED_TEAM_MATCH,
)


ROOT = Path(__file__).resolve().parent
ARTIFACT_DIR = ROOT / "data" / "player_derived_expected_goals_v1"
METADATA = ARTIFACT_DIR / "metadata.json"
SIDES = {"home", "away"}
NON_PACKAGED_EXPECTED_METRICS = {EXPECTED_ASSISTS, EXPECTED_GOALS_ON_TARGET}


class ExpectedMetricArtifactError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def artifact_metadata() -> dict:
    if not METADATA.is_file():
        raise FileNotFoundError(f"Expected-goals metadata not found: {METADATA}")

    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    if metadata.get("representation") != PLAYER_MATCH_DERIVED_TEAM_MATCH:
        raise ExpectedMetricArtifactError(
            "Unexpected expected-goals representation in metadata"
        )
    if metadata.get("metric") != EXPECTED_GOALS:
        raise ExpectedMetricArtifactError("Unexpected metric in expected-goals metadata")

    for season in metadata.get("seasons", []):
        path = ARTIFACT_DIR / f"{season}.json"
        if not path.is_file():
            raise FileNotFoundError(f"Expected-goals season artifact not found: {path}")
        actual = hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
        expected = metadata.get("season_file_sha256", {}).get(season)
        if actual != expected:
            raise ExpectedMetricArtifactError(
                f"Expected-goals artifact hash mismatch for {season}"
            )
    return metadata


@lru_cache(maxsize=8)
def _season_rows(season: str) -> tuple[tuple[float | None, float | None], ...] | None:
    metadata = artifact_metadata()
    if season not in metadata.get("seasons", []):
        return None

    path = ARTIFACT_DIR / f"{season}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or len(payload) != 380:
        raise ExpectedMetricArtifactError(
            f"Expected-goals artifact must contain 380 fixtures for {season}"
        )

    rows: list[tuple[float | None, float | None]] = []
    for fixture_id, pair in enumerate(payload, start=1):
        if not isinstance(pair, list) or len(pair) != 2:
            raise ExpectedMetricArtifactError(
                f"Malformed expected-goals pair for {season}/{fixture_id}"
            )
        home, away = pair
        rows.append(
            (
                None if home is None else float(home),
                None if away is None else float(away),
            )
        )
    return tuple(rows)


def fixture_expected_metric_row(season: str, fixture_id: str | int) -> dict | None:
    rows = _season_rows(str(season))
    if rows is None:
        return None
    try:
        numeric_id = int(fixture_id)
    except (TypeError, ValueError):
        return None
    if numeric_id < 1 or numeric_id > len(rows):
        return None

    home, away = rows[numeric_id - 1]
    return {
        "season": str(season),
        "fixture_id": str(numeric_id),
        "representation": PLAYER_MATCH_DERIVED_TEAM_MATCH,
        "home_expected_goals": home,
        "away_expected_goals": away,
    }


def team_expected_metric_observation(
    season: str,
    fixture_id: str | int,
    side: str,
    metric: str,
) -> dict:
    if side not in SIDES:
        raise ValueError(f"Unsupported fixture side: {side}")

    metadata = artifact_metadata()
    base = {
        "metric": metric,
        "season": str(season),
        "fixture_id": str(fixture_id),
        "side": side,
        "representation": PLAYER_MATCH_DERIVED_TEAM_MATCH,
        "construction_version": metadata.get("construction_version"),
        "source_commit": metadata.get("source_commit"),
    }

    if metric in NON_PACKAGED_EXPECTED_METRICS:
        return {
            **base,
            "status": "UNAVAILABLE",
            "value": None,
            "reason": "GOVERNED_BUT_NOT_PRODUCT_PACKAGED",
        }
    if metric != EXPECTED_GOALS:
        raise ValueError(f"Unsupported expected metric: {metric}")

    row = fixture_expected_metric_row(season, fixture_id)
    if row is None:
        return {
            **base,
            "status": "UNAVAILABLE",
            "value": None,
            "reason": "FIXTURE_OUTSIDE_MATERIALIZED_ARTIFACT",
        }

    value = row[f"{side}_expected_goals"]
    if value is None:
        return {
            **base,
            "status": "MISSING_POSITIVE_TRIGGER_INPUT",
            "value": None,
            "reason": "PLAYER_XG_MISSING_WITH_POSITIVE_SHOT_TRIGGER",
        }

    return {
        **base,
        "status": "AVAILABLE",
        "value": float(value),
    }


__all__ = [
    "ARTIFACT_DIR",
    "METADATA",
    "ExpectedMetricArtifactError",
    "artifact_metadata",
    "fixture_expected_metric_row",
    "team_expected_metric_observation",
]
