from __future__ import annotations

from api.frl_runtime import app


def test_active_runtime_registers_fixture_evidence_route() -> None:
    paths = {route.path for route in app.routes}
    assert "/api/v1/fixtures/{season}/{fixture_id}/evidence" in paths
