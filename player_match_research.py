"""Verified player-match enrichment for Player Research.

This adapter is intentionally fail-closed. It consumes only the locally
materialized player_identity_registry.csv produced by the audited registry
builder and only enriches an FPL record when exactly one verified external
source playerId is available.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from functools import lru_cache

import player_match_stats


REGISTRY_PATH = Path("player_identity_registry.csv")


@lru_cache(maxsize=1)
def load_registry(path: str = str(REGISTRY_PATH)) -> dict[tuple[str, str], str]:
    p = Path(path)
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = csv.DictReader(handle)
        mapping: dict[tuple[str, str], str] = {}
        for row in rows:
            if str(row.get("identity_status", "")).strip() != "VERIFIED":
                continue
            season = str(row.get("season", "")).strip()
            element = str(row.get("fpl_element", "")).strip()
            source_id = str(row.get("source_player_id", "")).strip()
            if not season or not element or not source_id:
                continue
            key = (season, element)
            if key in mapping and mapping[key] != source_id:
                raise ValueError(f"Conflicting verified registry rows for {key}")
            mapping[key] = source_id
        return mapping


def source_player_id_for_record(row: dict) -> str | None:
    season = str(row.get("_season") or row.get("season") or "").strip()
    element = str(row.get("element") or "").strip()
    if not season or not element:
        return None
    return load_registry().get((season, element))


def source_ids_for_records(rows) -> tuple[str, ...]:
    ids = {
        source_player_id_for_record(row)
        for row in rows
    }
    ids.discard(None)
    return tuple(sorted(ids))


def _season_source_player_id(records):
    """Resolve exactly one verified source player ID for each season."""
    by_season = defaultdict(list)

    for row in records:
        season = str(row.get("_season") or row.get("season") or "").strip()
        if not season:
            continue
        by_season[season].append(row)

    resolved = {}

    for season, season_records in by_season.items():
        source_ids = {
            source_player_id_for_record(row)
            for row in season_records
        }
        source_ids.discard(None)

        if len(source_ids) != 1:
            return None

        resolved[season] = next(iter(source_ids))

    return resolved


@lru_cache(maxsize=32)
def _season_totals(season):
    """Return cached player-match totals for one season."""
    return player_match_stats.player_season_totals(season)


def player_match_evidence_for_records(rows):
    records = tuple(rows)

    if not records:
        return {
            "status": "UNAVAILABLE",
            "source_player_id": None,
            "metrics": {},
            "reason": "NO_RECORDS",
        }

    season_source_ids = _season_source_player_id(records)

    if not season_source_ids:
        return {
            "status": "UNAVAILABLE",
            "source_player_id": None,
            "metrics": {},
            "reason": "NO_VERIFIED_SOURCE_ID",
        }

    metrics_by_season = []

    for season in sorted(season_source_ids):
        source_player_id = season_source_ids[season]
        totals = _season_totals(season)
        metrics = totals.get(source_player_id)

        if metrics is None:
            return {
                "status": "UNAVAILABLE",
                "source_player_id": None,
                "metrics": {},
                "reason": "SOURCE_PLAYER_DATA_UNAVAILABLE",
            }

        metrics_by_season.append(metrics)

    pooled = {}
    metric_names = set().union(
        *(metrics.keys() for metrics in metrics_by_season)
    )

    for metric in metric_names:
        values = [metrics.get(metric) for metrics in metrics_by_season]
        numeric_values = [value for value in values if value is not None]
        pooled[metric] = sum(numeric_values) if numeric_values else None

    passes = pooled.get("passes")
    accurate_passes = pooled.get("accurate_passes")
    pooled["pass_accuracy"] = (
        accurate_passes / passes * 100.0
        if passes not in (None, 0) and accurate_passes is not None
        else None
    )

    unique_source_ids = sorted(set(season_source_ids.values()))

    return {
        "status": "VERIFIED",
        "source_player_id": unique_source_ids[0] if len(unique_source_ids) == 1 else None,
        "source_player_ids": unique_source_ids,
        "season_source_player_ids": dict(season_source_ids),
        "metrics": pooled,
        "reason": "VERIFIED_FPL_ELEMENT_TO_SOURCE_PLAYER_ID",
    }


def enrich_player(player: dict) -> dict:
    enriched = dict(player)
    evidence = player_match_evidence_for_records(
        player.get("_records", ())
    )
    enriched["player_match_source_player_id"] = evidence["source_player_id"]
    enriched["player_match_identity_status"] = evidence["status"]
    enriched["player_match_identity_reason"] = evidence["reason"]
    for metric, value in evidence["metrics"].items():
        enriched[f"player_match_{metric}"] = value
    return enriched


def conflict_report() -> list[dict[str, object]]:
    """Return verified-candidate conflicts excluded from promotion."""
    import player_identity_crosswalk

    report = player_identity_crosswalk.summarize()
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in report["confirmed"]:
        grouped[(row["season"], row["element"])].append(row)

    conflicts = []
    for key, rows in grouped.items():
        source_ids = sorted({row["source_player_id"] for row in rows})
        if len(source_ids) > 1:
            conflicts.append({
                "season": key[0],
                "fpl_element": key[1],
                "source_player_ids": source_ids,
                "candidates": rows,
            })
    return conflicts
