from . import frl_api as _frl_api
from .player_performance import router as player_performance_router

_frl_api.app.include_router(player_performance_router)
