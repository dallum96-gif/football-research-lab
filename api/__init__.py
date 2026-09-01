from fastapi.middleware.cors import CORSMiddleware

from . import frl_api as _frl_api
from .player_performance import router as player_performance_router
from .fixture_evidence import router as fixture_evidence_router
from .team_stats_rankings import router as team_stats_rankings_router
from .player_stats import router as player_stats_router

_frl_api.app.include_router(player_performance_router)
_frl_api.app.include_router(fixture_evidence_router)
_frl_api.app.include_router(team_stats_rankings_router)
_frl_api.app.include_router(player_stats_router)

# Isolated FRL worktrees deliberately run Next on different localhost ports.
# Keep browser-origin development requests local-only without pinning the API
# to one frontend port (the base app historically allowed only :3000).
_frl_api.app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):\d+$".replace(r"\\.", r"\.").replace(r"\\d", r"\d"),
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)
