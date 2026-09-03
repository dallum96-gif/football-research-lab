from __future__ import annotations

from fastapi import APIRouter, HTTPException

import matchday_pack


router = APIRouter(prefix="/api/v1/matchday", tags=["matchday"])


@router.get("/fixtures/{season}")
def get_matchday_fixtures(season: str) -> dict:
    try:
        fixtures = matchday_pack.fixture_options(season)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Matchday fixture discovery failed safely.",
        ) from exc

    return {
        "season": season,
        "pack_version": matchday_pack.MODEL_VERSION,
        "fixtures": fixtures,
    }


@router.get("/{season}/{fixture_id}")
def get_matchday_pack(season: str, fixture_id: str) -> dict:
    try:
        return matchday_pack.build_matchday_pack(season, fixture_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Matchday Stat Pack failed safely.",
        ) from exc
