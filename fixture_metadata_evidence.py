"""Compose source-backed fixture metadata for the fixture evidence API.

Historical FRL team-match rows remain the established metadata source where
available. Preserved PulseLive match snapshots supplement that contract for the
newer match-centre archive without creating a GUI-specific truth layer.
"""
from __future__ import annotations

from typing import Any

from pulselive_fixture_evidence import load_snapshot, resource_payload
from source_family_adapters import fixture_metadata, resolve_source_match


def _text(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value).strip() or None


def _number(value: Any) -> int | float | None:
    if value in (None, ""):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return int(number) if number.is_integer() else number


def _named_entity(value: Any) -> str | None:
    if isinstance(value, dict):
        for key in ("name", "displayName", "label", "shortName"):
            text = _text(value.get(key))
            if text:
                return text
        return None
    return _text(value)


def _official_role(item: dict[str, Any]) -> str:
    return str(item.get("role") or item.get("type") or "").strip().casefold()


def _referee_from_payload(payload: dict[str, Any]) -> str | None:
    direct = _named_entity(payload.get("referee"))
    if direct:
        return direct

    candidates: list[dict[str, Any]] = []
    for key in ("matchOfficials", "officials"):
        value = payload.get(key)
        if isinstance(value, list):
            candidates.extend(item for item in value if isinstance(item, dict))
        elif isinstance(value, dict):
            nested = value.get("matchOfficials") or value.get("items")
            if isinstance(nested, list):
                candidates.extend(item for item in nested if isinstance(item, dict))

    for item in candidates:
        if _official_role(item) in {"referee", "main", "main referee"}:
            name = _named_entity(item)
            if name:
                return name
    return None


def fixture_metadata_result(season: str, fixture_id: str) -> dict[str, Any]:
    """Return the richest preserved source-native metadata for one fixture."""
    resolved = resolve_source_match(season, fixture_id)
    metadata = dict(fixture_metadata(season, fixture_id))

    # Some historical source rows carry referee directly even though the older
    # fixture_metadata contract never exposed it.
    source_referee = _text(resolved["home"].get("referee")) or _text(
        resolved["away"].get("referee")
    )
    if source_referee:
        metadata["referee"] = source_referee

    snapshot, path = load_snapshot(str(resolved["source_match_id"]))
    if snapshot is None:
        metadata.setdefault("referee", None)
        metadata["metadata_provenance"] = {
            "historical_source": True,
            "pulselive_match_snapshot": False,
        }
        return metadata

    match_payload = resource_payload(snapshot, "match")
    if isinstance(match_payload, dict):
        ground = _named_entity(match_payload.get("ground"))
        attendance = _number(match_payload.get("attendance"))
        referee = _referee_from_payload(match_payload)

        if ground:
            metadata["ground"] = ground
        if attendance is not None:
            metadata["attendance"] = attendance
        if referee:
            metadata["referee"] = referee

    metadata.setdefault("referee", None)
    metadata["metadata_provenance"] = {
        "historical_source": True,
        "pulselive_match_snapshot": True,
        "pulselive_snapshot_path": str(path),
        "pulselive_match_fields": ["ground", "attendance", "referee/officials"],
    }
    return metadata


__all__ = ["fixture_metadata_result"]
