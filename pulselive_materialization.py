"""Safe materialisation of governed PulseLive fixture snapshots.

This module operates only at the source-evidence boundary. Canonical fixture
identity is read from the fixture master, resolved through the established
relationship adapter, and retained as context rather than rewritten.
"""
from __future__ import annotations

import csv
import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

from pulselive_fixture_evidence import archive_root as configured_archive_root
from pulselive_fixture_evidence import normalise_events, normalise_lineups
from pulselive_live import PulseLiveRequestError, snapshot
from source_family_adapters import resolve_source_match

ROOT = Path(__file__).resolve().parent
CANONICAL_FIXTURES_PATH = ROOT / "fixtures_master_corrected.csv"
STATE_FILENAME = "materialization-state.json"
RESOURCE_NAMES = ("match", "events", "lineups", "stats", "commentary")


class SnapshotValidationError(ValueError):
    """A captured or existing snapshot is not safe to accept as complete."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _resource_payload(package: dict[str, Any], resource: str) -> Any:
    item = package.get("resources", {}).get(resource)
    return item.get("payload") if isinstance(item, dict) else None


def snapshot_target(root: Path, source_match_id: str) -> Path:
    return root / f"match-{source_match_id}" / "snapshot.json"


def validate_snapshot_package(package: Any, expected_source_match_id: str) -> dict[str, Any]:
    """Validate capture completeness without changing the preserved payload."""
    if not isinstance(package, dict):
        raise SnapshotValidationError("PulseLive snapshot must be a JSON object.")
    source_match_id = str(package.get("source_match_id") or "")
    if source_match_id != str(expected_source_match_id):
        raise SnapshotValidationError(
            f"PulseLive source match mismatch: expected {expected_source_match_id}, found {source_match_id or 'missing'}."
        )

    resources = package.get("resources")
    if not isinstance(resources, dict):
        raise SnapshotValidationError("PulseLive snapshot has no resources object.")
    for name in RESOURCE_NAMES:
        resource = resources.get(name)
        if not isinstance(resource, dict):
            raise SnapshotValidationError(f"PulseLive snapshot has no {name} resource object.")
        if "payload" not in resource:
            raise SnapshotValidationError(f"PulseLive {name} resource has no payload field.")
        if not resource.get("endpoint") or not resource.get("retrieved_at"):
            raise SnapshotValidationError(f"PulseLive {name} resource has incomplete retrieval provenance.")

    match_payload = _resource_payload(package, "match")
    if not isinstance(match_payload, dict) or str(match_payload.get("matchId") or "") != source_match_id:
        raise SnapshotValidationError("PulseLive match payload is missing or belongs to another source match.")

    events_payload = _resource_payload(package, "events")
    if not isinstance(events_payload, dict) or not any(
        key in events_payload for key in ("homeTeam", "home_team")
    ):
        raise SnapshotValidationError("PulseLive events payload is not a recognised fixture object.")
    normalised_events = normalise_events(events_payload)

    lineups_payload = _resource_payload(package, "lineups")
    try:
        normalised_lineups = normalise_lineups(lineups_payload)
    except Exception as exc:
        raise SnapshotValidationError(f"PulseLive lineup payload could not be normalised: {exc}") from exc
    players = normalised_lineups.get("players", [])
    if not players:
        raise SnapshotValidationError("PulseLive lineup payload normalised to zero players.")
    if not all(normalised_lineups.get("raw_team_payload_present", {}).get(side) for side in ("home", "away")):
        raise SnapshotValidationError("PulseLive lineup payload does not contain both fixture teams.")

    stats_payload = _resource_payload(package, "stats")
    if not isinstance(stats_payload, list) or not stats_payload:
        raise SnapshotValidationError("PulseLive stats payload is not a non-empty team-stat list.")

    commentary_payload = _resource_payload(package, "commentary")
    if not isinstance(commentary_payload, dict) or not isinstance(commentary_payload.get("data"), list):
        raise SnapshotValidationError("PulseLive commentary payload is not a recognised commentary object.")

    return {
        "event_count": len(normalised_events),
        "lineup_player_count": len(players),
        "formation": normalised_lineups.get("formations"),
        "placement_count": {
            side: len(normalised_lineups.get("placements", {}).get(side, []))
            for side in ("home", "away")
        },
        "manager_count": len(normalised_lineups.get("managers", {}).get("items", [])),
        "stats_team_count": len(stats_payload),
        "commentary_count": len(commentary_payload["data"]),
    }


def _atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def materialize_fixture(
    season: str,
    fixture_id: str,
    *,
    root: Path | None = None,
    force: bool = False,
    fetcher: Callable[..., dict[str, Any]] | None = None,
    resolved: dict[str, Any] | None = None,
    timeout: int = 15,
    max_attempts: int = 3,
    backoff_seconds: float = 2.0,
    request_interval_seconds: float = 1.0,
) -> dict[str, Any]:
    """Materialise one fixture atomically, skipping an existing valid capture."""
    archive = root.resolve() if root is not None else configured_archive_root()
    if archive is None or not archive.is_dir():
        raise RuntimeError(
            "No approved PulseLive archive root is available. Set FRL_PULSELIVE_ARCHIVE_ROOT "
            "or pass an existing approved archive directory."
        )

    relationship = resolved or resolve_source_match(season, fixture_id)
    source_match_id = str(relationship["source_match_id"])
    target = snapshot_target(archive, source_match_id)
    if target.exists() and not force:
        try:
            existing = _load_json(target)
            validation = validate_snapshot_package(existing, source_match_id)
        except Exception as exc:
            raise SnapshotValidationError(
                f"Existing snapshot is invalid and will not be overwritten automatically: {target}: {exc}"
            ) from exc
        return {
            "status": "SKIPPED",
            "season": season,
            "fixture_id": str(fixture_id),
            "source_match_id": source_match_id,
            "snapshot_path": str(target),
            "validation": validation,
        }

    capture = (fetcher or snapshot)(
        source_match_id,
        timeout=timeout,
        max_attempts=max_attempts,
        backoff_seconds=backoff_seconds,
        request_interval_seconds=request_interval_seconds,
    )
    if not isinstance(capture, dict):
        raise SnapshotValidationError("PulseLive capture did not return a snapshot object.")
    capture["frl_context"] = {
        "season": season,
        "fixture_id": str(fixture_id),
        "source_match_id": source_match_id,
        "relationship_contract": relationship.get("relationship_contract"),
        "relationship_status": relationship.get("relationship_status"),
        "resolution_basis": relationship.get("resolution_basis"),
        "fixture_correction": relationship.get("fixture_correction"),
    }
    validation = validate_snapshot_package(capture, source_match_id)
    capture["materialization"] = {
        "schema_version": 1,
        "status": "COMPLETE",
        "completed_at": _utc_now(),
        "validation": validation,
    }
    _atomic_write_json(target, capture)
    return {
        "status": "MATERIALIZED",
        "season": season,
        "fixture_id": str(fixture_id),
        "source_match_id": source_match_id,
        "snapshot_path": str(target),
        "validation": validation,
    }


def load_canonical_fixtures(path: Path = CANONICAL_FIXTURES_PATH) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    fixtures: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for row in rows:
        key = (str(row.get("season") or "").strip(), str(row.get("fixture_id") or "").strip())
        if not all(key) or key in seen:
            raise ValueError(f"Invalid or duplicate canonical fixture key: {key}")
        seen.add(key)
        fixtures.append({"season": key[0], "fixture_id": key[1]})
    return fixtures


def load_materialization_state(root: Path) -> dict[str, Any]:
    path = root / STATE_FILENAME
    if not path.is_file():
        return {"schema_version": 1, "updated_at": None, "fixtures": {}}
    state = _load_json(path)
    if not isinstance(state, dict) or not isinstance(state.get("fixtures"), dict):
        raise ValueError(f"Invalid PulseLive materialization state: {path}")
    return state


def failed_fixture_keys(state: dict[str, Any]) -> set[str]:
    return {
        key
        for key, value in state.get("fixtures", {}).items()
        if isinstance(value, dict) and value.get("status") == "FAILED"
    }


def _state_key(season: str, fixture_id: str) -> str:
    return f"{season}/{fixture_id}"


def _failure_record(season: str, fixture_id: str, exc: Exception) -> dict[str, Any]:
    record: dict[str, Any] = {
        "status": "FAILED",
        "season": season,
        "fixture_id": str(fixture_id),
        "recorded_at": _utc_now(),
        "error_type": type(exc).__name__,
        "message": str(exc),
    }
    if isinstance(exc, PulseLiveRequestError):
        record.update({
            "endpoint": exc.endpoint,
            "status_code": exc.status_code,
            "transient": exc.transient,
        })
    return record


def materialize_many(
    fixtures: Iterable[dict[str, str]],
    *,
    root: Path,
    fetcher: Callable[..., dict[str, Any]] | None = None,
    fixture_interval_seconds: float = 2.0,
    **materialize_options: Any,
) -> dict[str, Any]:
    """Materialise a bounded iterable and atomically record every outcome."""
    archive = root.resolve()
    if not archive.is_dir():
        raise RuntimeError(f"PulseLive archive root does not exist: {archive}")
    selected = list(fixtures)
    state = load_materialization_state(archive)
    counts = {"MATERIALIZED": 0, "SKIPPED": 0, "FAILED": 0}
    results: list[dict[str, Any]] = []

    for index, fixture in enumerate(selected):
        season = str(fixture["season"])
        fixture_id = str(fixture["fixture_id"])
        key = _state_key(season, fixture_id)
        try:
            relationship = resolve_source_match(season, fixture_id)
            result = materialize_fixture(
                season,
                fixture_id,
                root=archive,
                fetcher=fetcher,
                resolved=relationship,
                **materialize_options,
            )
            record = dict(result)
            record["recorded_at"] = _utc_now()
        except Exception as exc:
            record = _failure_record(season, fixture_id, exc)
        counts[record["status"]] += 1
        state["fixtures"][key] = record
        state["updated_at"] = _utc_now()
        _atomic_write_json(archive / STATE_FILENAME, state)
        results.append(record)
        if index < len(selected) - 1 and fixture_interval_seconds > 0:
            time.sleep(float(fixture_interval_seconds))

    return {"counts": counts, "results": results, "state_path": str(archive / STATE_FILENAME)}


__all__ = [
    "CANONICAL_FIXTURES_PATH",
    "RESOURCE_NAMES",
    "STATE_FILENAME",
    "SnapshotValidationError",
    "failed_fixture_keys",
    "load_canonical_fixtures",
    "load_materialization_state",
    "materialize_fixture",
    "materialize_many",
    "snapshot_target",
    "validate_snapshot_package",
]
