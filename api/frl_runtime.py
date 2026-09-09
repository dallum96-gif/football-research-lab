from __future__ import annotations

"""Canonical local FastAPI composition for the active FRL web application.

`api.frl_api` contains the established application and legacy inline routes.
Additional modular routers are composed here so local development runs the
same route surface the Next.js frontend expects.
"""

from api.frl_api import app
from api.fixture_evidence import router as fixture_evidence_router


_REGISTERED_PATHS = {route.path for route in app.routes}

if "/api/v1/fixtures/{season}/{fixture_id}/evidence" not in _REGISTERED_PATHS:
    app.include_router(fixture_evidence_router)
