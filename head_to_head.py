from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache

import adaptive_dixon_coles as adc
import matchday_pack
import poisson_model
import query_api
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
    {"key": "goal_1_plus", "label": "1+ goal", "source_key": "goals_for", "threshold": 1.0, "unit": "goals"},
    {"key": "shots_10_plus", "label": "10+ shots", "source_key": "Shots", "threshold": 10.0, "unit": "shots"},
    {"key": "sot_4_plus", "label": "4+ shots on target", "source_key": "Shots on target", "threshold": 4.0, "unit": "shots"},
    {"key": "corners_4_plus", "label": "4+ corners", "source_key": "Corners", "threshold": 4.0, "unit": "corners"},
    {"key": "cards_2_plus", "label": "2+ yellow cards", "source_key": "Yellow cards", "threshold": 2.0, "unit": "cards"},
)


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
    values: list[float] = []
    extractor = _opponent_metric if opponent else _own_metric
    for match in matches:
        value = extractor(match, source_key)
        if value is not None:
            values.append(value)
    hits = sum(1 for value in values if value >= threshold)
    return {
        "hits": hits,
        "observed_matches": len(values),
        "eligible_matches": len(matches),
        "hit_rate": (hits / len(values)) if values else None,
        "coverage_status": (
            "COMPLETE" if values and len(values) == len(matches)
            else "PARTIAL" if values
            else "UNAVAILABLE"
        ),
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
    return {
        "pack_version": MODEL_VERSION,
        "fixture": fixture,
        "as_of": fixture.get("kickoff_time"),
        "forecast": forecast,
        "profiles": base["teams"],
        "players": base["players"],
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
            "The evidence index is descriptive and must not be presented as an estimated betting probability.",
            "Player watchlists remain current-season FPL evidence and can be thin early in the season.",
            "Foul-drawn/foul-committed and referee-adjusted card matchup modelling remains withheld until its semantics and coverage are governed.",
            "The Head-to-Head route deliberately avoids the legacy external Player-Match filesystem dependency used by full fixture-detail enrichment.",
        ],
    }


__all__ = ["MODEL_VERSION", "BETBUILDER_THRESHOLDS", "build_head_to_head_pack"]
