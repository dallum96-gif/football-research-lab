from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from functools import lru_cache

import adaptive_dixon_coles as adc
import matchday_pack
import poisson_model
import query_api
import source_family_adapters
import team_research_stats


MODEL_VERSION = "head-to-head-v1"
FROZEN_ADAPTIVE_DC_CONFIG = adc.AdaptiveDCConfig(
    learning_rate=0.04,
    half_life_days=365.0,
    l2=0.001,
    rho_learning_rate=0.0005,
    global_learning_rate=0.002,
)

# Fixed before this V1 is evaluated in product. These are familiar market-like
# thresholds for evidence summarisation, not optimised cut-points and not model
# probabilities.
BETBUILDER_THRESHOLDS = (
    {
        "key": "goal_1_plus",
        "family": "Goals",
        "label": "1+ goal",
        "source_key": "goals_for",
        "threshold": 1.0,
        "unit": "goals",
    },
    {
        "key": "shots_10_plus",
        "family": "Shots",
        "label": "10+ shots",
        "source_key": "Shots",
        "threshold": 10.0,
        "unit": "shots",
    },
    {
        "key": "sot_4_plus",
        "family": "SOT",
        "label": "4+ shots on target",
        "source_key": "Shots on target",
        "threshold": 4.0,
        "unit": "shots",
    },
    {
        "key": "corners_4_plus",
        "family": "Corners",
        "label": "4+ corners",
        "source_key": "Corners",
        "threshold": 4.0,
        "unit": "corners",
    },
    {
        "key": "cards_2_plus",
        "family": "Cards",
        "label": "2+ yellow cards",
        "source_key": "Yellow cards",
        "threshold": 2.0,
        "unit": "cards",
    },
)

# Matchday player questions are deliberately limited to betting-relevant event
# counts. Recoveries and defensive contribution remain valid research metrics,
# but they are not promoted into this consumer-facing fixture cheat sheet.
PLAYER_MARKET_SPECS = (
    {
        "key": "player_shots_2_plus",
        "family": "Shots",
        "label": "2+ shots",
        "source": "player_match",
        "source_key": "totalShots",
        "threshold": 2.0,
        "unit": "shots",
    },
    {
        "key": "player_sot_1_plus",
        "family": "SOT",
        "label": "1+ shot on target",
        "source": "player_match",
        "source_key": "onTargetScoringAttempt",
        "threshold": 1.0,
        "unit": "shots",
    },
    {
        "key": "player_fouls_won_1_plus",
        "family": "Fouls won",
        "label": "1+ foul won",
        "source": "player_match",
        "source_key": "wasFouled",
        "threshold": 1.0,
        "unit": "fouls",
    },
    {
        "key": "player_fouls_committed_1_plus",
        "family": "Fouls committed",
        "label": "1+ foul committed",
        "source": "player_match",
        "source_key": "fouls",
        "threshold": 1.0,
        "unit": "fouls",
    },
    {
        "key": "player_goal_1_plus",
        "family": "Goals",
        "label": "1+ goal",
        "source": "fpl",
        "source_key": "source_goals_scored",
        "threshold": 1.0,
        "unit": "goals",
    },
    {
        "key": "player_card_1_plus",
        "family": "Cards",
        "label": "1+ card",
        "source": "fpl",
        "source_key": "__cards__",
        "threshold": 1.0,
        "unit": "cards",
    },
)

# These four current PulseLive fields have already passed FRL's sparse-zero
# audit in rich_player_projection.py. Applying zero here is limited to a player
# who actually participated in the fixture and only to these audited additive
# event counts. Historical source blanks remain unavailable.
_CURRENT_SAFE_PLAYER_ZERO_FIELDS = frozenset({
    "totalShots",
    "onTargetScoringAttempt",
    "wasFouled",
    "fouls",
})


def _dt(value: object) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _number(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _canonical_fixture(season: str, fixture_id: str) -> dict:
    rows = query_api.fixtures(season=season, team=None, limit=500)["results"]
    fixture = next(
        (dict(row) for row in rows if str(row.get("fixture_id") or "") == str(fixture_id)),
        None,
    )
    if fixture is None:
        raise ValueError(f"Fixture not found: {season}/{fixture_id}")
    return fixture


@lru_cache(maxsize=2048)
def _team_fixture_metric(season: str, team_name: str, fixture_id: str, source_key: str) -> float | None:
    team_code = team_research_stats.team_code_for_name(season, team_name)
    if not team_code:
        return None
    row = next(
        (
            item
            for item in team_research_stats.team_match_stats(season, team_code)
            if str(item.get("fixture_id")) == str(fixture_id)
        ),
        None,
    )
    if row is None:
        return None
    return _number(row.get(source_key))


def _own_metric(match: dict, source_key: str) -> float | None:
    if source_key == "goals_for":
        return _number(match.get("goals_for"))
    return _number((match.get("metrics") or {}).get(source_key))


def _opponent_metric(match: dict, source_key: str) -> float | None:
    if source_key == "goals_for":
        return _number(match.get("goals_against"))
    return _team_fixture_metric(
        str(match.get("season") or ""),
        str(match.get("opponent") or ""),
        str(match.get("fixture_id") or ""),
        source_key,
    )


def _threshold_summary(matches: list[dict], source_key: str, threshold: float, *, opponent: bool) -> dict:
    observations: list[dict] = []
    extractor = _opponent_metric if opponent else _own_metric
    for match in matches:
        value = extractor(match, source_key)
        if value is None:
            continue
        observations.append(
            {
                "season": str(match.get("season") or ""),
                "fixture_id": str(match.get("fixture_id") or ""),
                "kickoff_time": match.get("kickoff_time"),
                "opponent": str(match.get("opponent") or ""),
                "venue": match.get("venue"),
                "value": value,
                "hit": value >= threshold,
            }
        )

    hits = sum(1 for observation in observations if observation["hit"])
    values = [float(observation["value"]) for observation in observations]
    return {
        "hits": hits,
        "observed_matches": len(observations),
        "eligible_matches": len(matches),
        "hit_rate": (hits / len(observations)) if observations else None,
        "average": (sum(values) / len(values)) if values else None,
        "coverage_status": (
            "COMPLETE" if observations and len(observations) == len(matches)
            else "PARTIAL" if observations
            else "UNAVAILABLE"
        ),
        "sequence_order": "MOST_RECENT_FIRST",
        "observations": observations,
    }


def _btts_summary(matches: list[dict]) -> dict:
    observations: list[dict] = []
    for match in matches:
        goals_for = _number(match.get("goals_for"))
        goals_against = _number(match.get("goals_against"))
        if goals_for is None or goals_against is None:
            continue
        observations.append(
            {
                "season": str(match.get("season") or ""),
                "fixture_id": str(match.get("fixture_id") or ""),
                "kickoff_time": match.get("kickoff_time"),
                "opponent": str(match.get("opponent") or ""),
                "venue": match.get("venue"),
                "goals_for": goals_for,
                "goals_against": goals_against,
                "hit": goals_for >= 1.0 and goals_against >= 1.0,
            }
        )

    hits = sum(1 for observation in observations if observation["hit"])
    return {
        "hits": hits,
        "observed_matches": len(observations),
        "eligible_matches": len(matches),
        "hit_rate": (hits / len(observations)) if observations else None,
        "coverage_status": (
            "COMPLETE" if observations and len(observations) == len(matches)
            else "PARTIAL" if observations
            else "UNAVAILABLE"
        ),
        "sequence_order": "MOST_RECENT_FIRST",
        "observations": observations,
    }


def _evidence_label(team_rate: float | None, allowance_rate: float | None) -> tuple[str, float | None]:
    available = [value for value in (team_rate, allowance_rate) if value is not None]
    if not available:
        return "UNAVAILABLE", None
    index = sum(available) / len(available)
    if len(available) == 2 and min(available) >= 0.60 and index >= 0.70:
        return "STRONG", index
    if index >= 0.60:
        return "FAVOURABLE", index
    if index >= 0.45:
        return "MIXED", index
    return "WEAK", index


def _betbuilder_entries(pack: dict) -> list[dict]:
    entries: list[dict] = []
    for side, opponent_side in (("home", "away"), ("away", "home")):
        team = pack["teams"][side]
        opponent = pack["teams"][opponent_side]
        team_matches = list(team.get("matches") or [])
        opponent_matches = list(opponent.get("matches") or [])
        for spec in BETBUILDER_THRESHOLDS:
            own = _threshold_summary(
                team_matches,
                str(spec["source_key"]),
                float(spec["threshold"]),
                opponent=False,
            )
            allowed = _threshold_summary(
                opponent_matches,
                str(spec["source_key"]),
                float(spec["threshold"]),
                opponent=True,
            )
            label, index = _evidence_label(own["hit_rate"], allowed["hit_rate"])
            entries.append(
                {
                    "id": f"{side}_{spec['key']}",
                    "side": side,
                    "family": spec["family"],
                    "team_name": team["team_name"],
                    "opponent_name": opponent["team_name"],
                    "market_label": f"{team['team_name']} {spec['label']}",
                    "metric_label": spec["label"],
                    "source_key": spec["source_key"],
                    "threshold": spec["threshold"],
                    "unit": spec["unit"],
                    "team_recent": own,
                    "opponent_allowance": allowed,
                    "evidence_label": label,
                    "evidence_index": index,
                    "interpretation": (
                        f"How often {team['team_name']} cleared the fixed threshold in its recent pre-match window, "
                        f"paired with how often opponents cleared the same threshold against {opponent['team_name']}."
                    ),
                }
            )
    return entries


def _market_lanes(entries: list[dict]) -> list[dict]:
    by_side_and_key = {
        (str(entry["side"]), str(entry["source_key"])): entry
        for entry in entries
    }
    lanes: list[dict] = []
    for spec in BETBUILDER_THRESHOLDS:
        source_key = str(spec["source_key"])
        home = by_side_and_key.get(("home", source_key))
        away = by_side_and_key.get(("away", source_key))
        if home is None or away is None:
            continue
        lanes.append(
            {
                "key": spec["key"],
                "family": spec["family"],
                "market_line": {
                    "label": spec["label"],
                    "threshold": spec["threshold"],
                    "unit": spec["unit"],
                    "source_key": spec["source_key"],
                },
                "home_lane": {
                    "team_name": home["team_name"],
                    "opponent_name": home["opponent_name"],
                    "attack": home["team_recent"],
                    "defence_allowance": home["opponent_allowance"],
                    "evidence_label": home["evidence_label"],
                    "evidence_index": home["evidence_index"],
                },
                "away_lane": {
                    "team_name": away["team_name"],
                    "opponent_name": away["opponent_name"],
                    "attack": away["team_recent"],
                    "defence_allowance": away["opponent_allowance"],
                    "evidence_label": away["evidence_label"],
                    "evidence_index": away["evidence_index"],
                },
            }
        )
    return lanes


def _player_row_name(row: dict) -> str:
    direct = str(
        row.get("playerName")
        or row.get("knownName")
        or row.get("name")
        or ""
    ).strip()
    if direct:
        return direct
    parts = [
        str(row.get("firstName") or row.get("first_name") or "").strip(),
        str(row.get("lastName") or row.get("last_name") or "").strip(),
    ]
    return " ".join(part for part in parts if part) or str(row.get("pl_code") or row.get("playerId") or "Player")


def _participated(row: dict) -> bool:
    minutes = _number(row.get("minutesPlayed"))
    if minutes is None:
        minutes = _number(row.get("minsPlayed"))
    return minutes is not None and minutes > 0


def _recent_current_matches(team: dict, season: str) -> list[dict]:
    return [
        match
        for match in list(team.get("matches") or [])
        if str(match.get("season") or "") == season
    ][:matchday_pack.RECENT_MATCH_LIMIT]


def _rich_player_observations(team: dict, season: str, source_key: str, threshold: float) -> dict[str, dict]:
    matches = _recent_current_matches(team, season)
    by_player: dict[str, dict] = {}
    field_universe: set[str] = set()
    try:
        field_universe = set(source_family_adapters.player_match_source_fields(season))
    except (FileNotFoundError, ValueError):
        field_universe = set()
    field_available = source_key in field_universe

    for order, match in enumerate(matches):
        fixture_id = str(match.get("fixture_id") or "")
        try:
            rows = source_family_adapters.player_match_source_rows(season, fixture_id)
        except (FileNotFoundError, ValueError):
            continue
        expected_venue = str(match.get("venue") or "").strip().casefold()
        for row in rows:
            if str(row.get("venue") or "").strip().casefold() != expected_venue:
                continue
            if not _participated(row):
                continue
            player_code = str(row.get("pl_code") or row.get("playerId") or "").strip()
            if not player_code:
                continue
            value = _number(row.get(source_key))
            if (
                value is None
                and season == "2026-27"
                and field_available
                and source_key in _CURRENT_SAFE_PLAYER_ZERO_FIELDS
            ):
                value = 0.0
            if value is None:
                continue
            player = by_player.setdefault(
                player_code,
                {
                    "player_code": player_code,
                    "player_name": _player_row_name(row),
                    "position": str(row.get("position") or ""),
                    "observations": [],
                },
            )
            player["observations"].append(
                {
                    "season": season,
                    "fixture_id": fixture_id,
                    "kickoff_time": match.get("kickoff_time"),
                    "opponent": str(match.get("opponent") or ""),
                    "value": value,
                    "hit": value >= threshold,
                    "order": order,
                }
            )

    return by_player


def _fpl_player_observations(team: dict, season: str, source_key: str, threshold: float) -> dict[str, dict]:
    matches = _recent_current_matches(team, season)
    fixture_order = {
        str(match.get("fixture_id") or ""): (order, match)
        for order, match in enumerate(matches)
    }
    team_code = str(team.get("persistent_team_code") or "")
    by_player: dict[str, dict] = {}

    for row in matchday_pack._fpl_rows():
        if str(row.get("frl_season") or "") != season:
            continue
        if str(row.get("frl_team_id") or "") != team_code:
            continue
        if str(row.get("frl_fixture_relationship_status") or "") != "VERIFIED":
            continue
        minutes = _number(row.get("source_minutes")) or 0.0
        if minutes <= 0:
            continue
        fixture_id = str(row.get("frl_fixture_id") or "")
        context = fixture_order.get(fixture_id)
        if context is None:
            continue
        order, match = context
        if source_key == "__cards__":
            yellow = _number(row.get("source_yellow_cards"))
            red = _number(row.get("source_red_cards"))
            if yellow is None or red is None:
                continue
            value = yellow + red
        else:
            value = _number(row.get(source_key))
            if value is None:
                continue
        player_code = str(row.get("source_player_code") or row.get("frl_player_identity_key") or "").strip()
        if not player_code:
            continue
        player = by_player.setdefault(
            player_code,
            {
                "player_code": player_code,
                "player_name": matchday_pack._player_display_name(row),
                "position": str(row.get("source_position") or ""),
                "observations": [],
            },
        )
        player["observations"].append(
            {
                "season": season,
                "fixture_id": fixture_id,
                "kickoff_time": match.get("kickoff_time"),
                "opponent": str(match.get("opponent") or ""),
                "value": value,
                "hit": value >= threshold,
                "order": order,
            }
        )

    return by_player


def _rank_player_market_players(by_player: dict[str, dict], eligible_matches: int) -> list[dict]:
    players: list[dict] = []
    for player in by_player.values():
        observations = sorted(player["observations"], key=lambda observation: observation["order"])
        hits = sum(1 for observation in observations if observation["hit"])
        total = sum(float(observation["value"]) for observation in observations)
        players.append(
            {
                "player_code": player["player_code"],
                "player_name": player["player_name"],
                "position": player["position"],
                "hits": hits,
                "observed_appearances": len(observations),
                "eligible_team_matches": eligible_matches,
                "total": total,
                "observations": [
                    {key: value for key, value in observation.items() if key != "order"}
                    for observation in observations[:matchday_pack.RECENT_MATCH_LIMIT]
                ],
            }
        )
    players.sort(
        key=lambda player: (
            -int(player["hits"]),
            -float(player["total"]),
            -int(player["observed_appearances"]),
            str(player["player_name"]).casefold(),
        )
    )
    return players[:4]


def _player_markets(base: dict, fixture: dict) -> list[dict]:
    season = str(fixture.get("season") or "")
    markets: list[dict] = []
    for spec in PLAYER_MARKET_SPECS:
        side_payloads: dict[str, dict] = {}
        for side in ("home", "away"):
            team = base["teams"][side]
            matches = _recent_current_matches(team, season)
            if spec["source"] == "player_match":
                by_player = _rich_player_observations(
                    team,
                    season,
                    str(spec["source_key"]),
                    float(spec["threshold"]),
                )
            else:
                by_player = _fpl_player_observations(
                    team,
                    season,
                    str(spec["source_key"]),
                    float(spec["threshold"]),
                )
            side_payloads[side] = {
                "team_name": team["team_name"],
                "eligible_team_matches": len(matches),
                "players": _rank_player_market_players(by_player, len(matches)),
            }
        markets.append(
            {
                "key": spec["key"],
                "family": spec["family"],
                "label": spec["label"],
                "threshold": spec["threshold"],
                "unit": spec["unit"],
                "source": spec["source"],
                "home": side_payloads["home"],
                "away": side_payloads["away"],
                "sample_definition": "up to five most recent current-season team fixtures before kickoff; player denominators count only observed appearances",
            }
        )
    return markets


def _adaptive_prediction(fixture: dict) -> dict:
    target_kickoff = _dt(fixture.get("kickoff_time"))
    if target_kickoff is None:
        return {"status": "UNAVAILABLE", "reason": "Fixture kickoff is unavailable."}

    season = str(fixture.get("season") or "")
    home_name = str(fixture.get("home_team_name") or "")
    away_name = str(fixture.get("away_team_name") or "")
    home_code = team_research_stats.team_code_for_name(season, home_name)
    away_code = team_research_stats.team_code_for_name(season, away_name)
    if not home_code or not away_code:
        return {"status": "UNAVAILABLE", "reason": "Verified team identity is unavailable for the target fixture."}

    seasons = tuple(adc.DEFAULT_SEASONS) + ((season,) if season not in adc.DEFAULT_SEASONS else tuple())
    training = [row for row in adc.canonical_completed_fixtures(seasons) if row["kickoff"] < target_kickoff]
    model = adc.OnlineDixonColes(FROZEN_ADAPTIVE_DC_CONFIG)
    for row in training:
        model.advance_time(row["kickoff"])
        model.update(
            row["home_team_code"],
            row["away_team_code"],
            row["home_goals"],
            row["away_goals"],
        )
    model.advance_time(target_kickoff)
    prediction = model.predict(home_code, away_code)
    home_lambda = float(prediction["expected_goals"]["home"])
    away_lambda = float(prediction["expected_goals"]["away"])
    rho = float(prediction["rho"])
    matrix = adc.dixon_coles_score_matrix(home_lambda, away_lambda, rho)
    markets = poisson_model.market_probabilities(matrix)
    correct_scores = sorted(matrix.items(), key=lambda item: (-item[1], item[0]))[:5]
    return {
        "status": "AVAILABLE",
        "model": adc.MODEL_VERSION,
        "control_status": "FROZEN_EXPERIMENTAL_CONTROL",
        "training_fixtures": len(training),
        "expected_goals": {"home": home_lambda, "away": away_lambda},
        "probabilities": {key: float(value) for key, value in markets.items()},
        "rho": rho,
        "correct_scores": [
            {"home": score[0], "away": score[1], "probability": float(probability)}
            for score, probability in correct_scores
        ],
        "temporal_contract": {
            "target_kickoff": fixture.get("kickoff_time"),
            "training_results_strictly_before_target_kickoff": True,
            "future_results_used": False,
        },
    }


def _portable_base_pack(season: str, fixture_id: str) -> dict:
    fixture = _canonical_fixture(season, fixture_id)
    teams = {
        "home": matchday_pack._recent_team_side(fixture, "home"),
        "away": matchday_pack._recent_team_side(fixture, "away"),
    }
    players = {
        "home": matchday_pack._player_recent_side(fixture, "home"),
        "away": matchday_pack._player_recent_side(fixture, "away"),
    }
    current_team_min = min(
        int(teams["home"]["current_season_sample_size"]),
        int(teams["away"]["current_season_sample_size"]),
    )
    current_player_min = min(
        int(players["home"]["fixture_evidence_count"]),
        int(players["away"]["fixture_evidence_count"]),
    )
    early_season = current_team_min < matchday_pack.RECENT_MATCH_LIMIT or current_player_min < matchday_pack.RECENT_MATCH_LIMIT
    return {
        "fixture": fixture,
        "teams": teams,
        "players": players,
        "data_maturity": {
            "status": "EARLY_SEASON" if early_season else "RECENT_WINDOW_MATURE",
            "team_current_season_matches": {
                "home": teams["home"]["current_season_sample_size"],
                "away": teams["away"]["current_season_sample_size"],
            },
            "player_fixture_evidence_matches": {
                "home": players["home"]["fixture_evidence_count"],
                "away": players["away"]["fixture_evidence_count"],
            },
            "note": (
                "Early-season current campaign evidence is still thin. Team Last 5 can bridge the summer through governed persistent club identity; Player Last 5 remains current-season only."
                if early_season
                else "Both teams have a full five-match current-season recent window and at least five current-season player-evidence fixtures before kickoff."
            ),
        },
    }


def build_head_to_head_pack(season: str, fixture_id: str) -> dict:
    base = _portable_base_pack(season, fixture_id)
    fixture = dict(base["fixture"])
    forecast = _adaptive_prediction(fixture)
    entries = _betbuilder_entries(base)
    btts = {
        "key": "btts",
        "family": "BTTS",
        "label": "Both teams to score",
        "home_team_name": base["teams"]["home"]["team_name"],
        "away_team_name": base["teams"]["away"]["team_name"],
        "home_recent": _btts_summary(list(base["teams"]["home"].get("matches") or [])),
        "away_recent": _btts_summary(list(base["teams"]["away"].get("matches") or [])),
        "interpretation": "How often both teams scored in each club's own recent pre-match fixtures. This is descriptive recent scoreline evidence, not a calibrated BTTS probability.",
    }
    return {
        "pack_version": MODEL_VERSION,
        "fixture": fixture,
        "as_of": fixture.get("kickoff_time"),
        "forecast": forecast,
        "profiles": base["teams"],
        "players": base["players"],
        "market_lanes": _market_lanes(entries),
        "fixture_markets": {"btts": btts},
        "player_markets": _player_markets(base, fixture),
        "betbuilder": {
            "status": "EVIDENCE_PACK_NOT_BETTING_ADVICE",
            "threshold_policy": "Fixed common thresholds; no threshold was selected or tuned after seeing target-match results.",
            "index_definition": "Mean of observed recent team hit rate and opponent allowance hit rate. It is an evidence index, not a calibrated event probability.",
            "entries": entries,
        },
        "data_maturity": base.get("data_maturity"),
        "limitations": [
            "V1 uses up to five completed fixtures strictly before kickoff for team evidence.",
            "Opponent allowance is reconstructed from the same governed fixture/team representations rather than assumed from team labels.",
            "Last-five threshold sequences include only observed values; the observed/eligible denominator remains visible when coverage is partial.",
            "BTTS recent evidence is reconstructed from each team's governed pre-kickoff scorelines and is descriptive rather than a calibrated probability.",
            "Player betting-market evidence is current-season only and uses up to five recent team fixtures before kickoff; each player's denominator counts only appearances with observed evidence.",
            "Current PulseLive sparse-zero handling is restricted to previously audited additive event-count fields and only when the player participated.",
            "The evidence index is descriptive and must not be presented as an estimated betting probability.",
            "Foul-drawn/foul-committed player evidence is descriptive recent evidence; no referee adjustment or calibrated player-prop model is claimed.",
            "The Head-to-Head route deliberately avoids the legacy external Player-Match filesystem dependency used by full fixture-detail enrichment for current 2026/27 PulseLive evidence.",
        ],
    }


__all__ = [
    "MODEL_VERSION",
    "BETBUILDER_THRESHOLDS",
    "PLAYER_MARKET_SPECS",
    "build_head_to_head_pack",
]
