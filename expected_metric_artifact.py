from __future__ import annotations

import csv
import gzip
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
ARTIFACT = ROOT / "data" / "frl_player_derived_expected_metrics_v1.csv.gz"
METADATA = ROOT / "data" / "frl_player_derived_expected_metrics_v1_metadata.json"

METRIC_SLUGS = {
    EXPECTED_GOALS: "expected_goals",
    EXPECTED_ASSISTS: "expected_assists",
    EXPECTED_GOALS_ON_TARGET: "expected_goals_on_target",
}
SIDES = {"home", "away"}


class ExpectedMetricArtifactError(RuntimeError):
    pass


def _number(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


@lru_cache(maxsize=1)
def artifact_metadata() -> dict:
    if not METADATA.is_file():
        raise FileNotFoundError(f"Expected-metric metadata not found: {METADATA}")
    if not ARTIFACT.is_file():
        raise FileNotFoundError(f"Expected-metric artifact not found: {ARTIFACT}")

    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    if metadata.get("representation") != PLAYER_MATCH_DERIVED_TEAM_MATCH:
        raise ExpectedMetricArtifactError(
            "Unexpected expected-metric representation in metadata"
        )

    actual_hash = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()
    if metadata.get("artifact_sha256") != actual_hash:
        raise ExpectedMetricArtifactError(
            "Expected-metric artifact hash does not match governed metadata"
        )
    return metadata


@lru_cache(maxsize=1)
def _rows() -> dict[tuple[str, str], dict[str, str]]:
    metadata = artifact_metadata()
    with gzip.open(ARTIFACT, mode="rt", encoding="utf-8", newline="") as handle:
        rows = tuple(csv.DictReader(handle))

    if len(rows) != int(metadata.get("row_count", 0)):
        raise ExpectedMetricArtifactError(
            "Expected-metric artifact row count does not match metadata"
        )

    index: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        key = (str(row.get("season", "")), str(row.get("fixture_id", "")))
        if not all(key):
            raise ExpectedMetricArtifactError("Expected-metric artifact contains an empty key")
        if key in index:
            raise ExpectedMetricArtifactError(
                f"Duplicate expected-metric artifact key: {key}"
            )
        if row.get("representation") != PLAYER_MATCH_DERIVED_TEAM_MATCH:
            raise ExpectedMetricArtifactError(
                f"Unexpected row representation for {key}"
            )
        index[key] = row
    return index


def fixture_expected_metric_row(season: str, fixture_id: str | int) -> dict[str, str] | None:
    return _rows().get((str(season), str(fixture_id)))


def team_expected_metric_observation(
    season: str,
    fixture_id: str | int,
    side: str,
    metric: str,
) -> dict:
    if side not in SIDES:
        raise ValueError(f"Unsupported fixture side: {side}")
    try:
        slug = METRIC_SLUGS[metric]
    except KeyError as exc:
        raise ValueError(f"Unsupported expected metric: {metric}") from exc

    row = fixture_expected_metric_row(season, fixture_id)
    metadata = artifact_metadata()
    if row is None:
        return {
            "status": "UNAVAILABLE",
            "value": None,
            "metric": metric,
            "season": str(season),
            "fixture_id": str(fixture_id),
            "side": side,
            "representation": PLAYER_MATCH_DERIVED_TEAM_MATCH,
            "construction_version": metadata.get("construction_version"),
            "source_commit": metadata.get("source_commit"),
            "reason": "FIXTURE_OUTSIDE_MATERIALIZED_ARTIFACT",
        }

    status = str(row.get(f"{side}_{slug}_status") or "UNAVAILABLE")
    value = _number(row.get(f"{side}_{slug}"))
    if status != "AVAILABLE":
        value = None

    return {
        "status": status,
        "value": value,
        "metric": metric,
        "season": str(season),
        "fixture_id": str(fixture_id),
        "side": side,
        "representation": row.get("representation"),
        "construction_version": row.get("construction_version"),
        "source_commit": metadata.get("source_commit"),
        "direct_source_match_id": row.get("direct_source_match_id"),
        "player_source_match_id": row.get("player_source_match_id"),
        "source_observed_rows": int(row.get(f"{side}_{slug}_source_observed_rows") or 0),
        "structural_zero_rows": int(row.get(f"{side}_{slug}_structural_zero_rows") or 0),
        "unsafe_missing_rows": int(row.get(f"{side}_{slug}_unsafe_missing_rows") or 0),
    }


__all__ = [
    "ARTIFACT",
    "METADATA",
    "ExpectedMetricArtifactError",
    "artifact_metadata",
    "fixture_expected_metric_row",
    "team_expected_metric_observation",
]
