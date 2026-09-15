from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

import player_profile_foundation


router = APIRouter()


@router.get(
    "/api/v1/player-profile-foundation/{season}/{player_code}",
    response_model=dict[str, Any],
)
def get_player_profile_foundation(season: str, player_code: str) -> dict[str, Any]:
    try:
        result = player_profile_foundation.build_player_profile(season, player_code)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Player Profile foundation failed safely.",
        ) from exc

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Player Profile is unavailable for this player and season.",
        )
    return result
