"""Canonical context helpers for universal FRL variable access.

This module defines context objects passed to the resolver. It deliberately
contains no source-specific joins or storage assumptions.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FixtureContext:
    season: str
    fixture_id: int


@dataclass(frozen=True)
class TeamFixtureContext:
    season: str
    fixture_id: int
    persistent_team_code: str


@dataclass(frozen=True)
class PlayerFixtureContext:
    season: str
    fixture_id: int
    canonical_player_id: str


@dataclass(frozen=True)
class PlayerSeasonContext:
    season: str
    canonical_player_id: str


@dataclass(frozen=True)
class TeamSeasonContext:
    season: str
    persistent_team_code: str


@dataclass(frozen=True)
class EventContext:
    season: str
    fixture_id: int
    source_event_identity: str


__all__ = [
    "FixtureContext",
    "TeamFixtureContext",
    "PlayerFixtureContext",
    "PlayerSeasonContext",
    "TeamSeasonContext",
    "EventContext",
]
