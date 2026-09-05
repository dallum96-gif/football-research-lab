from __future__ import annotations

from fastapi import APIRouter, HTTPException

import head_to_head


router = APIRouter(prefix="/api/v1/head-to-head", tags=["head-to-head"])


@router.get("/{season}/{fixture_id}")
def get_head_to_head_pack(season: str, fixture_id: str) -> dict:
    try:
        return head_to_head.build_head_to_head_pack(season, fixture_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Head-to-Head research pack failed safely.",
        ) from exc
