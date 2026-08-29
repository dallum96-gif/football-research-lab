"""Thin, fail-closed adapter for the current Premier League PulseLive SDP feed.

The live adapter is source evidence only. It never writes canonical fixture
identity or analytical data and never guesses an FRL identity from a source ID.
"""
from __future__ import annotations

import json
import time
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
    status_code: int
    payload: object
    headers: dict[str, str]


class PulseLiveRequestError(RuntimeError):
    """Structured request failure used by conservative bulk acquisition."""

    def __init__(
        self,
        message: str,
        *,
        endpoint: str,
        status_code: int | None = None,
        transient: bool = False,
    ) -> None:
        super().__init__(message)
        self.endpoint = endpoint
        self.status_code = status_code
        self.transient = transient


def _retry_after_seconds(headers: object) -> float | None:
    value = headers.get("Retry-After") if hasattr(headers, "get") else None
    if value in (None, ""):
        return None
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        return None


def _get(
    path: str,
    timeout: int = 15,
    *,
    max_attempts: int = 1,
    backoff_seconds: float = 1.0,
) -> LiveResponse:
    url = f"{BASE_URL}{path}"
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    attempts = max(1, int(max_attempts))
    for attempt in range(1, attempts + 1):
        retry_after = None
        cause: Exception
        try:
            with urlopen(request, timeout=timeout) as response:
                payload = json.load(response)
                headers = {str(k).lower(): str(v) for k, v in response.headers.items()}
                status_code = int(getattr(response, "status", response.getcode()))
            return LiveResponse(
                endpoint=url,
                retrieved_at=datetime.now(timezone.utc).isoformat(),
                status_code=status_code,
                payload=payload,
                headers=headers,
            )
        except HTTPError as exc:
            cause = exc
            status_code = int(exc.code)
            transient = status_code == 429 or 500 <= status_code <= 599
            retry_after = _retry_after_seconds(exc.headers)
            failure = PulseLiveRequestError(
                f"PulseLive request failed: {url}: HTTP {status_code}",
                endpoint=url,
                status_code=status_code,
                transient=transient,
            )
        except (URLError, TimeoutError) as exc:
            cause = exc
            failure = PulseLiveRequestError(
                f"PulseLive request failed: {url}: {exc}",
                endpoint=url,
                transient=True,
            )
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            cause = exc
            failure = PulseLiveRequestError(
                f"PulseLive response was not valid JSON: {url}: {exc}",
                endpoint=url,
                transient=False,
            )

        if not failure.transient or attempt >= attempts:
            raise failure from cause
        delay = max(float(backoff_seconds) * (2 ** (attempt - 1)), retry_after or 0.0)
        time.sleep(delay)

    raise AssertionError("unreachable")


def match(match_id: str | int, **request_options) -> LiveResponse:
    return _get(f"/api/v2/matches/{match_id}", **request_options)


def events(match_id: str | int, **request_options) -> LiveResponse:
    return _get(f"/api/v1/matches/{match_id}/events", **request_options)


def lineups(match_id: str | int, **request_options) -> LiveResponse:
    return _get(f"/api/v3/matches/{match_id}/lineups", **request_options)


def stats(match_id: str | int, **request_options) -> LiveResponse:
    return _get(f"/api/v3/matches/{match_id}/stats", **request_options)


def commentary(match_id: str | int, limit: int = 20, **request_options) -> LiveResponse:
    return _get(
        f"/api/v1/matches/{match_id}/commentary?_limit={int(limit)}&_sort=timestamp:desc",
        **request_options,
    )


def snapshot(
    match_id: str | int,
    *,
    timeout: int = 15,
    max_attempts: int = 1,
    backoff_seconds: float = 1.0,
    request_interval_seconds: float = 0.0,
) -> dict:
    """Fetch the complete current match evidence package in one call site."""
    request_options = {
        "timeout": timeout,
        "max_attempts": max_attempts,
        "backoff_seconds": backoff_seconds,
    }
    fetchers = (
        ("match", match),
        ("events", events),
        ("lineups", lineups),
        ("stats", stats),
        ("commentary", commentary),
    )
    responses: dict[str, LiveResponse] = {}
    for index, (name, fetch) in enumerate(fetchers):
        responses[name] = fetch(match_id, **request_options)
        if index < len(fetchers) - 1 and request_interval_seconds > 0:
            time.sleep(float(request_interval_seconds))
    retrieved_at = datetime.now(timezone.utc).isoformat()
    return {
        "source": "Premier League / PulseLive SDP",
        "source_match_id": str(match_id),
        "retrieved_at": retrieved_at,
        "resources": {
            key: {
                "endpoint": value.endpoint,
                "retrieved_at": value.retrieved_at,
                "status_code": value.status_code,
                "payload": value.payload,
                "headers": value.headers,
            }
            for key, value in responses.items()
        },
    }
