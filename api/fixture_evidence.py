from __future__ import annotations

from fastapi import APIRouter, HTTPException

from fixture_evidence import fixture_evidence as source_fixture_evidence
from fixture_research_access import fixture_research_result

router = APIRouter()


def _with_enrichment_fallback(base: dict, error: Exception) -> dict:
    result = dict(base)
    limitations = list(result.get("limitations") or [])
    limitations.append(
        "Player-Match participation enrichment was unavailable for this request; "
        "source-native fixture event and tactical evidence remains available."
    )
    result["limitations"] = limitations

    provenance = dict(result.get("provenance") or {})
    provenance["participation_enrichment"] = {
        "status": "UNAVAILABLE",
        "optional": True,
        "failure_type": type(error).__name__,
    }
    result["provenance"] = provenance
    return result


@router.get("/api/v1/fixtures/{season}/{fixture_id}/evidence")
def get_fixture_evidence(season: str, fixture_id: str) -> dict:
    fixture_key = str(fixture_id)

    # Retrieve governed source-native fixture evidence first. Optional
    # Player-Match participation enrichment must never suppress valid PulseLive
    # events, lineups, formations, managers or fixture metadata.
    try:
        base = source_fixture_evidence(season, fixture_key)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail="Fixture evidence source unavailable.") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Fixture evidence query failed safely.") from exc

    if base.get("status") == "UNAVAILABLE":
        return base

    try:
        return fixture_research_result(season, fixture_key)
    except Exception as exc:
        return _with_enrichment_fallback(base, exc)
