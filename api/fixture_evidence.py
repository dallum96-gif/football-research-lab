from __future__ import annotations

from fastapi import APIRouter, HTTPException

from fixture_research_access import fixture_research_result

router = APIRouter()


@router.get("/api/v1/fixtures/{season}/{fixture_id}/evidence")
def get_fixture_evidence(season: str, fixture_id: str) -> dict:
    try:
        return fixture_research_result(season, str(fixture_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail="Fixture evidence source unavailable.") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Fixture evidence query failed safely.") from exc
