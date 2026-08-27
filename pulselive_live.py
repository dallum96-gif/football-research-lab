"""Thin, fail-closed adapter for the current Premier League PulseLive SDP feed.

The live adapter is source evidence only. It never writes canonical fixture
identity or analytical data and never guesses an FRL identity from a source ID.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = "https://sdp-prem-prod.premier-league-prod.pulselive.com"
USER_AGENT = "Mozilla/5.0"


@dataclass(frozen=True)
class LiveResponse:
    endpoint: str
    retrieved_at: str
    payload: object
    headers: dict[str, str]


def _get(path: str, timeout: int = 15) -> LiveResponse:
    url = f"{BASE_URL}{path}"
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
            headers = {str(k).lower(): str(v) for k, v in response.headers.items()}
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"PulseLive request failed: {url}: {exc}") from exc

    return LiveResponse(
        endpoint=url,
        retrieved_at=datetime.now(timezone.utc).isoformat(),
        payload=payload,
        headers=headers,
    )


def match(match_id: str | int) -> LiveResponse:
    return _get(f"/api/v2/matches/{match_id}")


def events(match_id: str | int) -> LiveResponse:
    return _get(f"/api/v1/matches/{match_id}/events")


def lineups(match_id: str | int) -> LiveResponse:
    return _get(f"/api/v3/matches/{match_id}/lineups")


def stats(match_id: str | int) -> LiveResponse:
    return _get(f"/api/v3/matches/{match_id}/stats")


def commentary(match_id: str | int, limit: int = 20) -> LiveResponse:
    return _get(f"/api/v1/matches/{match_id}/commentary?_limit={int(limit)}&_sort=timestamp:desc")


def snapshot(match_id: str | int) -> dict:
    """Fetch the complete current match evidence package in one call site."""
    responses = {
        "match": match(match_id),
        "events": events(match_id),
        "lineups": lineups(match_id),
        "stats": stats(match_id),
        "commentary": commentary(match_id),
    }
    retrieved_at = datetime.now(timezone.utc).isoformat()
    return {
        "source": "Premier League / PulseLive SDP",
        "source_match_id": str(match_id),
        "retrieved_at": retrieved_at,
        "resources": {
            key: {
                "endpoint": value.endpoint,
                "retrieved_at": value.retrieved_at,
                "payload": value.payload,
                "headers": value.headers,
            }
            for key, value in responses.items()
        },
    }
