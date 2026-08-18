"""Portable FRL data-source locations.

Environment variables may override external source roots in deployed
 environments. Local development falls back to conventional project-local
 directories so the application remains usable on a developer machine.
"""
from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


def player_match_root() -> Path:
    """Return the configured player-match source root.

    FRL_PLAYER_MATCH_ROOT is the deployment override. When it is not set,
    use a project-local ``pl_stats`` directory if one exists. The function
    intentionally does not require the directory to exist; callers can
    report an unavailable optional source without crashing the application.
    """
    configured = os.getenv("FRL_PLAYER_MATCH_ROOT")
    if configured:
        return Path(configured).expanduser()

    return PROJECT_ROOT / "pl_stats"
