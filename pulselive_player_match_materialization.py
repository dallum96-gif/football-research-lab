"""Conservative materialisation of fixture-native PulseLive player stats.

This is deliberately a companion to the established five-resource fixture
snapshot. It does not modify snapshot.json or RESOURCE_NAMES.

Raw source truth is preserved first. Normalisation/governance occurs later.
"""
from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path

from pulselive_fixture_evidence import (
    archive_root as configured_archive_root,
    load_snapshot,
    resource_payload,
)
from pulselive_live import PulseLiveRequestError, player_stats
from source_family_adapters import canonical_fixture


class PlayerStatsValidationError(ValueError):
    """A fixture-player package is not safe to accept as preserved evidence."""


def player_stats_target(
    root: Path,
    source_match_id: str,
    source_player_id: str,
) -> Path:
    return (
        root
        / f"match-{source_match_id}"
        / "player-stats"
        / f"{source_player_id}.json"
    )


def validate_player_stats_package(
    package: object,
    expected_source_match_id: str,
    expected_source_player_id: str,
) -> dict:
    if not isinstance(package, dict):
        raise PlayerStatsValidationError(
            "PulseLive player-stat package must be a JSON object."
        )

    match_id = str(package.get("source_match_id") or "")
    player_id = str(package.get("source_player_id") or "")

    if match_id != str(expected_source_match_id):
        raise PlayerStatsValidationError(
            "PulseLive player-stat package belongs to another match."
        )

    if player_id != str(expected_source_player_id):
        raise PlayerStatsValidationError(
            "PulseLive player-stat package belongs to another player."
        )

    resource = package.get("resource")
    if not isinstance(resource, dict):
        raise PlayerStatsValidationError(
            "PulseLive player-stat package has no resource object."
        )

    if not resource.get("endpoint") or not resource.get("retrieved_at"):
        raise PlayerStatsValidationError(
            "PulseLive player-stat retrieval provenance is incomplete."
        )

    if int(resource.get("status_code") or 0) != 200:
        raise PlayerStatsValidationError(
            "PulseLive player-stat resource was not retrieved successfully."
        )

    payload = resource.get("payload")
    if not isinstance(payload, dict):
        raise PlayerStatsValidationError(
            "PulseLive player-stat payload must be a JSON object."
        )

    stats = payload.get("stats")
    if not isinstance(stats, dict):
        raise PlayerStatsValidationError(
            "PulseLive player-stat payload has no stats object."
        )

    metadata = payload.get("playerMetadata") or payload.get("player") or {}
    if isinstance(metadata, dict):
        metadata_id = str(
            metadata.get("id")
            or metadata.get("playerId")
            or ""
        )
        if metadata_id and metadata_id != player_id:
            raise PlayerStatsValidationError(
                "PulseLive player metadata belongs to another player."
            )

    return {
        "source_match_id": match_id,
        "source_player_id": player_id,
        "stat_fields": len(stats),
    }


def _atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary = path.with_name(
        f".{path.name}.{uuid.uuid4().hex}.tmp"
    )

    try:
        with temporary.open("w", encoding="utf-8") as handle:
            json.dump(
                payload,
                handle,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temporary, path)

    finally:
        if temporary.exists():
            temporary.unlink()


def _lineup_player_ids(lineups: object) -> tuple[str, ...]:
    if not isinstance(lineups, dict):
        raise PlayerStatsValidationError(
            "PulseLive lineup payload is not a recognised object."
        )

    player_ids: list[str] = []

    for side in ("home_team", "away_team"):
        block = lineups.get(side)
        if not isinstance(block, dict):
            continue

        players = block.get("players")
        if not isinstance(players, list):
            continue

        for player in players:
            if not isinstance(player, dict):
                continue

            player_id = str(player.get("id") or "").strip()
            if player_id:
                player_ids.append(player_id)

    unique = tuple(dict.fromkeys(player_ids))

    if not unique:
        raise PlayerStatsValidationError(
            "No PulseLive player IDs were found in the preserved lineup."
        )

    return unique


def materialize_fixture_player_stats(
    season: str,
    fixture_id: str,
    *,
    root: Path | None = None,
    force: bool = False,
    timeout: int = 15,
    max_attempts: int = 3,
    backoff_seconds: float = 2.0,
    request_interval_seconds: float = 1.0,
) -> dict:
    """Materialise every listed player's fixture-native stat payload."""

    archive = (
        root.resolve()
        if root is not None
        else configured_archive_root()
    )

    if archive is None or not archive.is_dir():
        raise RuntimeError(
            "No approved PulseLive archive root is available."
        )

    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise ValueError(
            f"Canonical fixture not found: {season}/{fixture_id}"
        )

    source_match_id = str(fixture.get("fixture_code") or "").strip()
    if not source_match_id:
        raise ValueError(
            f"Canonical fixture has no PulseLive fixture code: "
            f"{season}/{fixture_id}"
        )

    snapshot, snapshot_path = load_snapshot(source_match_id)
    if snapshot is None:
        raise PlayerStatsValidationError(
            f"No preserved fixture snapshot exists for {source_match_id}."
        )

    lineups = resource_payload(snapshot, "lineups")
    player_ids = _lineup_player_ids(lineups)

    results = []
    counts = {
        "MATERIALIZED": 0,
        "SKIPPED": 0,
        "FAILED": 0,
    }

    for index, player_id in enumerate(player_ids):
        target = player_stats_target(
            archive,
            source_match_id,
            player_id,
        )

        if target.exists() and not force:
            try:
                with target.open("r", encoding="utf-8") as handle:
                    existing = json.load(handle)

                validation = validate_player_stats_package(
                    existing,
                    source_match_id,
                    player_id,
                )

            except Exception as exc:
                raise PlayerStatsValidationError(
                    "Existing player-stat package is invalid and will not "
                    f"be overwritten automatically: {target}: {exc}"
                ) from exc

            result = {
                "status": "SKIPPED",
                "source_match_id": source_match_id,
                "source_player_id": player_id,
                "path": str(target),
                "validation": validation,
            }

        else:
            try:
                response = player_stats(
                    source_match_id,
                    player_id,
                    timeout=timeout,
                    max_attempts=max_attempts,
                    backoff_seconds=backoff_seconds,
                )

                package = {
                    "source": "Premier League / PulseLive SDP",
                    "source_match_id": source_match_id,
                    "source_player_id": player_id,
                    "retrieved_at": response.retrieved_at,
                    "resource": {
                        "endpoint": response.endpoint,
                        "retrieved_at": response.retrieved_at,
                        "status_code": response.status_code,
                        "payload": response.payload,
                        "headers": response.headers,
                    },
                }

                validation = validate_player_stats_package(
                    package,
                    source_match_id,
                    player_id,
                )

                _atomic_write_json(target, package)

                result = {
                    "status": "MATERIALIZED",
                    "source_match_id": source_match_id,
                    "source_player_id": player_id,
                    "path": str(target),
                    "validation": validation,
                }

            except PulseLiveRequestError as exc:
                counts["FAILED"] += 1
                results.append({
                    "status": "FAILED",
                    "source_match_id": source_match_id,
                    "source_player_id": player_id,
                    "endpoint": exc.endpoint,
                    "status_code": exc.status_code,
                    "transient": exc.transient,
                    "error": str(exc),
                })

                # Refusal / rate limiting is a hard stop for the batch.
                if exc.status_code == 429:
                    raise

                raise

        counts[result["status"]] += 1
        results.append(result)

        if (
            index < len(player_ids) - 1
            and request_interval_seconds > 0
            and result["status"] == "MATERIALIZED"
        ):
            time.sleep(float(request_interval_seconds))

    return {
        "season": season,
        "fixture_id": str(fixture_id),
        "source_match_id": source_match_id,
        "snapshot_path": str(snapshot_path),
        "players": len(player_ids),
        "counts": counts,
        "results": results,
    }


__all__ = [
    "PlayerStatsValidationError",
    "materialize_fixture_player_stats",
    "player_stats_target",
    "validate_player_stats_package",
]
