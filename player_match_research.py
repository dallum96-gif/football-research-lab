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


def player_match_evidence_for_records(rows) -> dict[str, object]:
    records = tuple(rows)
    source_ids = source_ids_for_records(records)
    if len(source_ids) != 1:
        return {
            "status": "UNAVAILABLE",
            "source_player_id": None,
            "metrics": {},
            "reason": (
                "NO_VERIFIED_SOURCE_ID" if not source_ids
                else "MULTIPLE_VERIFIED_SOURCE_IDS"
            ),
        }

    source_player_id = source_ids[0]
    seasons = sorted({str(r.get("_season") or r.get("season") or "").strip() for r in records if r.get("_season") or r.get("season")})
    source_rows = []
    for season in seasons:
        source_rows.extend(
            player_match_stats.player_match_records_for_player(
                source_player_id,
                season,
            )
        )

    metrics = player_match_stats.aggregate_rows(source_rows)
    return {
        "status": "VERIFIED",
        "source_player_id": source_player_id,
        "metrics": metrics,
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
