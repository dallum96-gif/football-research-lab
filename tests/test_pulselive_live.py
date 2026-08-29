from __future__ import annotations

import io
import json
from email.message import Message
from urllib.error import HTTPError

import pytest

import pulselive_live


class _Response(io.BytesIO):
    def __init__(self, payload: object, status: int = 200) -> None:
        super().__init__(json.dumps(payload).encode("utf-8"))
        self.status = status
        self.headers = Message()

    def getcode(self) -> int:
        return self.status

    def __enter__(self):
        return self

    def __exit__(self, *args) -> None:
        self.close()


def test_transient_server_failure_is_retried_with_bounded_backoff(monkeypatch) -> None:
    calls = []
    outcomes = [
        HTTPError("https://example", 503, "unavailable", Message(), None),
        _Response({"matchId": "855173"}),
    ]

    def fake_urlopen(request, timeout):
        calls.append((request.full_url, timeout))
        outcome = outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    sleeps = []
    monkeypatch.setattr(pulselive_live, "urlopen", fake_urlopen)
    monkeypatch.setattr(pulselive_live.time, "sleep", sleeps.append)

    response = pulselive_live.match("855173", max_attempts=2, backoff_seconds=0.25)

    assert response.status_code == 200
    assert response.payload == {"matchId": "855173"}
    assert len(calls) == 2
    assert sleeps == [0.25]


def test_non_transient_not_found_is_not_retried(monkeypatch) -> None:
    calls = []

    def fake_urlopen(request, timeout):
        calls.append(request.full_url)
        raise HTTPError(request.full_url, 404, "not found", Message(), None)

    monkeypatch.setattr(pulselive_live, "urlopen", fake_urlopen)

    with pytest.raises(pulselive_live.PulseLiveRequestError) as error:
        pulselive_live.events("missing", max_attempts=5)

    assert error.value.status_code == 404
    assert error.value.transient is False
    assert len(calls) == 1
