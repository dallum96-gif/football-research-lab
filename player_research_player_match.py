"""Player Research adapter for verified player-match enrichment."""
from __future__ import annotations

from typing import Iterable

import player_match_research


def enrich_aggregate(player: dict) -> dict:
    """Add verified player-match evidence without changing existing metrics."""
    enriched = dict(player)
    evidence = player_match_research.player_match_evidence_for_records(
        player.get("_records", ())
    )
    enriched["player_match_identity_status"] = evidence["status"]
    enriched["player_match_identity_reason"] = evidence["reason"]
    enriched["player_match_source_player_id"] = evidence["source_player_id"]
    for metric, value in evidence["metrics"].items():
        enriched[f"player_match_{metric}"] = value
    return enriched


def enrich_players(players: Iterable[dict]) -> list[dict]:
    return [enrich_aggregate(player) for player in players]
