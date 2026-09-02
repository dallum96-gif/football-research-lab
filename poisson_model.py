from __future__ import annotations

import math
from collections import Counter
from typing import Iterable

import query_lab


MODEL_VERSION = "Poisson V1.0"
TARGET_SEASON = "2026-27"
SOURCE_SEASON = "2025-26"

# Compatibility adapter for the current 2026/27 Prediction Lab universe.
PREMIER_LEAGUE_2026_27 = [
    "Arsenal",
    "Aston Villa",
    "Bournemouth",
    "Brentford",
    "Brighton",
    "Chelsea",
    "Coventry City",
    "Crystal Palace",
    "Everton",
    "Fulham",
    "Hull City",
    "Ipswich Town",
    "Leeds United",
    "Liverpool",
    "Manchester City",
    "Manchester United",
    "Newcastle United",
    "Nottingham Forest",
    "Sunderland",
    "Tottenham Hotspur",
]

PROMOTED_TEAMS = {
    "Coventry City": {
        "home_goals_for": 51,
        "home_goals_against": 19,
        "away_goals_for": 46,
        "away_goals_against": 26,
    },
    "Ipswich Town": {
        "home_goals_for": 43,
        "home_goals_against": 17,
        "away_goals_for": 37,
        "away_goals_against": 30,
    },
    "Hull City": {
        "home_goals_for": 35,
        "home_goals_against": 34,
        "away_goals_for": 35,
        "away_goals_against": 32,
    },
}

# 2025/26 Championship scoring environment.
EFL_HOME_GOALS = 1.40
EFL_AWAY_GOALS = 1.20

PROMOTED_PRIOR_WEIGHT = 2.0 / 3.0
PROMOTED_EFL_WEIGHT = 1.0 / 3.0

# Score probabilities are expanded until each marginal Poisson distribution
# leaves at most this much probability in the omitted tail.
SCORE_TAIL_EPSILON = 1e-10
MAX_SCORE_CAP = 30


def poisson_probability(goals: int, expected_goals: float) -> float:
    if goals < 0:
        return 0.0
    if expected_goals < 0:
        raise ValueError("Expected goals must be non-negative.")
    return (
        math.exp(-expected_goals)
        * expected_goals ** goals
        / math.factorial(goals)
    )


def fair_odds(probability: float) -> float | None:
    if probability <= 0:
        return None
    return 1.0 / probability


def _completed_score(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def load_source_fixtures(source_season: str = SOURCE_SEASON) -> list[dict]:
    """Load completed canonical fixtures for one modelling source season."""
    return [
        row
        for row in query_lab.load_fixtures()
        if row["season"] == source_season
        and _completed_score(row.get("home_score"))
        and _completed_score(row.get("away_score"))
    ]


def _verified_identity_rows(season: str) -> list[dict]:
    return [
        row
        for row in query_lab.load_identity_registry()
        if row.get("season") == season
        and row.get("mapping_status") == "VERIFIED"
    ]


def _team_id_for_name(season: str, team_name: str) -> str:
    candidates = [
        row
        for row in _verified_identity_rows(season)
        if str(row.get("canonical_name") or "").replace("_", " ") == team_name
    ]
    if len(candidates) != 1:
        raise ValueError(
            f"Could not uniquely resolve {team_name} in {season}."
        )
    return str(candidates[0]["local_team_id"])


def _team_name_for_id(season: str, local_team_id: object) -> str:
    target = str(local_team_id)
    candidates = [
        row
        for row in _verified_identity_rows(season)
        if str(row.get("local_team_id")) == target
    ]
    if len(candidates) != 1:
        raise ValueError(
            f"Could not uniquely resolve local team {target} in {season}."
        )
    return str(candidates[0]["canonical_name"]).replace("_", " ")


def team_strength_from_pl(
    fixtures: Iterable[dict],
    team_name: str,
    source_season: str = SOURCE_SEASON,
) -> dict:
    """Return raw home/away scoring rates for one source-season team."""
    fixture_rows = list(fixtures)
    team_id = _team_id_for_name(source_season, team_name)

    home_matches = [
        row
        for row in fixture_rows
        if str(row["home_team_id"]) == team_id
    ]
    away_matches = [
        row
        for row in fixture_rows
        if str(row["away_team_id"]) == team_id
    ]

    if not home_matches or not away_matches:
        raise ValueError(
            f"Incomplete {source_season} data for {team_name}."
        )

    return {
        "home_attack_goals": (
            sum(float(row["home_score"]) for row in home_matches)
            / len(home_matches)
        ),
        "home_defence_goals": (
            sum(float(row["away_score"]) for row in home_matches)
            / len(home_matches)
        ),
        "away_attack_goals": (
            sum(float(row["away_score"]) for row in away_matches)
            / len(away_matches)
        ),
        "away_defence_goals": (
            sum(float(row["home_score"]) for row in away_matches)
            / len(away_matches)
        ),
        "home_matches": len(home_matches),
        "away_matches": len(away_matches),
    }


def league_environment(fixtures: Iterable[dict]) -> dict:
    fixture_rows = list(fixtures)
    if not fixture_rows:
        raise ValueError("A Poisson source season must contain completed fixtures.")

    home_goals = sum(float(row["home_score"]) for row in fixture_rows)
    away_goals = sum(float(row["away_score"]) for row in fixture_rows)
    matches = len(fixture_rows)
    home_rate = home_goals / matches
    away_rate = away_goals / matches

    if home_rate <= 0 or away_rate <= 0:
        raise ValueError("League scoring rates must be positive.")

    return {
        "home_goals": home_rate,
        "away_goals": away_rate,
        "total_goals": (home_goals + away_goals) / matches,
        "home_advantage_ratio": home_rate / away_rate,
        "matches": matches,
    }


def normalized_strength(raw: dict, league: dict) -> dict:
    return {
        "home_attack": raw["home_attack_goals"] / league["home_goals"],
        "home_defence": raw["home_defence_goals"] / league["away_goals"],
        "away_attack": raw["away_attack_goals"] / league["away_goals"],
        "away_defence": raw["away_defence_goals"] / league["home_goals"],
        "home_matches": raw["home_matches"],
        "away_matches": raw["away_matches"],
    }


def fit_source_season(source_season: str = SOURCE_SEASON) -> dict:
    """Fit the transparent four-strength Poisson model for one completed season."""
    fixtures = load_source_fixtures(source_season)
    league = league_environment(fixtures)
    strengths: dict[str, dict] = {}

    for row in _verified_identity_rows(source_season):
        team_name = str(row["canonical_name"]).replace("_", " ")
        if team_name in strengths:
            continue
        try:
            raw = team_strength_from_pl(fixtures, team_name, source_season)
        except ValueError:
            continue
        strengths[team_name] = normalized_strength(raw, league)

    if not strengths:
        raise ValueError(
            f"No complete team strengths could be fitted for {source_season}."
        )

    return {
        "model": MODEL_VERSION,
        "source_season": source_season,
        "league_environment": league,
        "team_strengths": strengths,
        "fixture_count": len(fixtures),
        "strength_method": (
            "home/away goals-for and goals-against rates divided by "
            "the corresponding league home/away scoring rate"
        ),
    }


def promoted_pl_prior(
    fixtures: Iterable[dict],
    league: dict,
    source_season: str = SOURCE_SEASON,
) -> dict:
    # Compatibility prior for the 2026/27 adapter. These are the previous
    # season's promoted cohort used by the existing V0.1 implementation.
    if source_season != "2025-26":
        raise ValueError(
            "The current promoted-team prior is governed only for 2025-26."
        )

    previous_promoted = [
        "Leeds United",
        "Burnley",
        "Sunderland",
    ]

    strengths = [
        normalized_strength(
            team_strength_from_pl(fixtures, team, source_season),
            league,
        )
        for team in previous_promoted
    ]

    return {
        key: sum(item[key] for item in strengths) / len(strengths)
        for key in (
            "home_attack",
            "home_defence",
            "away_attack",
            "away_defence",
        )
    }


def promoted_efl_strength(team: str) -> dict:
    if team not in PROMOTED_TEAMS:
        raise ValueError(f"{team} is not a promoted team.")

    values = PROMOTED_TEAMS[team]
    return {
        "home_attack": (
            (values["home_goals_for"] / 23) / EFL_HOME_GOALS
        ),
        "home_defence": (
            (values["home_goals_against"] / 23) / EFL_AWAY_GOALS
        ),
        "away_attack": (
            (values["away_goals_for"] / 23) / EFL_AWAY_GOALS
        ),
        "away_defence": (
            (values["away_goals_against"] / 23) / EFL_HOME_GOALS
        ),
    }


def current_target_strength(
    team: str,
    fitted: dict,
    fixtures: Iterable[dict],
) -> tuple[dict, str]:
    """Resolve a 2026/27 team to a source-season strength representation."""
    source_strengths = fitted["team_strengths"]

    if team in source_strengths:
        strength = dict(source_strengths[team])
        strength["representation"] = "PRIOR_SEASON_PL"
        return strength, "PRIOR_SEASON_PL"

    if team not in PROMOTED_TEAMS:
        raise ValueError(
            f"{team} has no governed {SOURCE_SEASON} strength representation."
        )

    prior = promoted_pl_prior(
        fixtures,
        fitted["league_environment"],
        fitted["source_season"],
    )
    efl = promoted_efl_strength(team)
    blended = {
        key: (
            PROMOTED_PRIOR_WEIGHT * prior[key]
            + PROMOTED_EFL_WEIGHT * efl[key]
        )
        for key in (
            "home_attack",
            "home_defence",
            "away_attack",
            "away_defence",
        )
    }
    blended.update(
        {
            "home_matches": None,
            "away_matches": None,
            "representation": "PROMOTED_BLEND",
        }
    )
    return blended, "PROMOTED_BLEND"


def expected_goal_rates(
    league: dict,
    home_strength: dict,
    away_strength: dict,
) -> tuple[float, float]:
    """Convert league baseline + attack/defence strengths into match lambdas."""
    expected_home = (
        league["home_goals"]
        * home_strength["home_attack"]
        * away_strength["away_defence"]
    )
    expected_away = (
        league["away_goals"]
        * away_strength["away_attack"]
        * home_strength["home_defence"]
    )
    return expected_home, expected_away


def _poisson_distribution(
    expected_goals: float,
    *,
    tail_epsilon: float = SCORE_TAIL_EPSILON,
) -> list[float]:
    if expected_goals < 0:
        raise ValueError("Expected goals must be non-negative.")
    if not 0 < tail_epsilon < 1:
        raise ValueError("tail_epsilon must be between zero and one.")

    probabilities = [math.exp(-expected_goals)]
    cumulative = probabilities[0]

    goals = 0
    while cumulative < 1.0 - tail_epsilon:
        goals += 1
        if goals > MAX_SCORE_CAP:
            raise ValueError(
                "Poisson score tail exceeded the configured safety cap."
            )
        previous = probabilities[-1]
        probability = (
            previous * expected_goals / goals
            if expected_goals > 0
            else 0.0
        )
        probabilities.append(probability)
        cumulative += probability

    return probabilities


def score_matrix(
    expected_home: float,
    expected_away: float,
    *,
    tail_epsilon: float = SCORE_TAIL_EPSILON,
) -> dict[tuple[int, int], float]:
    """Return a tail-safe, normalized independent Poisson score matrix."""
    home_distribution = _poisson_distribution(
        expected_home,
        tail_epsilon=tail_epsilon,
    )
    away_distribution = _poisson_distribution(
        expected_away,
        tail_epsilon=tail_epsilon,
    )

    raw = {
        (home_goals, away_goals): home_probability * away_probability
        for home_goals, home_probability in enumerate(home_distribution)
        for away_goals, away_probability in enumerate(away_distribution)
    }
    mass = sum(raw.values())
    if mass <= 0:
        raise ValueError("Poisson score matrix has no probability mass.")

    return {
        score: probability / mass
        for score, probability in raw.items()
    }


def market_probabilities(scores: dict[tuple[int, int], float]) -> dict:
    home_win = sum(
        value for (home, away), value in scores.items() if home > away
    )
    draw = sum(
        value for (home, away), value in scores.items() if home == away
    )
    away_win = sum(
        value for (home, away), value in scores.items() if home < away
    )

    over_25 = sum(
        value for (home, away), value in scores.items()
        if home + away >= 3
    )
    under_25 = 1.0 - over_25

    btts_yes = sum(
        value for (home, away), value in scores.items()
        if home > 0 and away > 0
    )
    btts_no = 1.0 - btts_yes

    return {
        "home_win": home_win,
        "draw": draw,
        "away_win": away_win,
        "over_2_5": over_25,
        "under_2_5": under_25,
        "btts": btts_yes,
        "btts_no": btts_no,
    }


def fair_odds_for_markets(probabilities: dict) -> dict:
    return {
        key: fair_odds(float(value))
        for key, value in probabilities.items()
    }


def top_correct_scores(
    scores: dict[tuple[int, int], float],
    limit: int = 10,
) -> list[dict]:
    if limit < 1:
        raise ValueError("Correct-score limit must be positive.")
    ordered = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:limit]
    return [
        {
            "home": score[0],
            "away": score[1],
            "probability": probability,
            "fair_odds": fair_odds(probability),
        }
        for score, probability in ordered
    ]


def prediction_from_strengths(
    home_team: str,
    away_team: str,
    fitted: dict,
    home_strength: dict,
    away_strength: dict,
    *,
    target_season: str | None = None,
    home_representation: str = "PRIOR_SEASON_PL",
    away_representation: str = "PRIOR_SEASON_PL",
) -> dict:
    if home_team == away_team:
        raise ValueError("Home and away teams must be different.")

    league = fitted["league_environment"]
    expected_home, expected_away = expected_goal_rates(
        league,
        home_strength,
        away_strength,
    )
    scores = score_matrix(expected_home, expected_away)
    probabilities = market_probabilities(scores)
    correct_scores = top_correct_scores(scores)
    most_likely = correct_scores[0]

    return {
        "model": MODEL_VERSION,
        "target_season": target_season,
        "source_season": fitted["source_season"],
        "home_team": home_team,
        "away_team": away_team,
        "league_environment": league,
        "inputs": {
            "home_strength": home_strength,
            "away_strength": away_strength,
            "home_representation": home_representation,
            "away_representation": away_representation,
            "strength_method": fitted["strength_method"],
            "source_matches": fitted["fixture_count"],
        },
        # Compatibility aliases retained for the existing Prediction Lab.
        "home_strength": home_strength,
        "away_strength": away_strength,
        "expected_goals": {
            "home": expected_home,
            "away": expected_away,
        },
        "probabilities": probabilities,
        "fair_odds": fair_odds_for_markets(probabilities),
        "most_likely_score": {
            "home": most_likely["home"],
            "away": most_likely["away"],
            "probability": most_likely["probability"],
        },
        "correct_scores": correct_scores,
        "methodology": {
            "goal_model": "independent Poisson",
            "home_lambda": (
                "league home goals/match × home attack strength "
                "× away defence weakness"
            ),
            "away_lambda": (
                "league away goals/match × away attack strength "
                "× home defence weakness"
            ),
            "score_tail_epsilon": SCORE_TAIL_EPSILON,
            "matrix_normalized": True,
        },
        "limitations": [
            "V1 uses goals only; it does not yet include recency, xG, lineups, injuries or opponent-strength adjustment.",
            "Home and away goal counts are modelled as independent conditional Poisson processes.",
            "Current promoted-team handling remains a separate compatibility prior and is not used for generic historical evaluation.",
        ],
    }


def prediction_for_source_season(
    home_team: str,
    away_team: str,
    source_season: str,
    *,
    target_season: str | None = None,
) -> dict:
    """Predict a matchup when both teams have a complete fitted source season."""
    fitted = fit_source_season(source_season)
    strengths = fitted["team_strengths"]
    missing = [
        team for team in (home_team, away_team)
        if team not in strengths
    ]
    if missing:
        raise ValueError(
            "No complete source-season strength for: "
            + ", ".join(missing)
        )

    return prediction_from_strengths(
        home_team,
        away_team,
        fitted,
        strengths[home_team],
        strengths[away_team],
        target_season=target_season,
    )


def poisson_prediction(home_team: str, away_team: str) -> dict:
    """Compatibility entry point for the current 2026/27 Prediction Lab."""
    if home_team not in PREMIER_LEAGUE_2026_27:
        raise ValueError(
            f"{home_team} is not in the {TARGET_SEASON} Premier League universe."
        )
    if away_team not in PREMIER_LEAGUE_2026_27:
        raise ValueError(
            f"{away_team} is not in the {TARGET_SEASON} Premier League universe."
        )
    if home_team == away_team:
        raise ValueError("Home and away teams must be different.")

    fixtures = load_source_fixtures(SOURCE_SEASON)
    fitted = fit_source_season(SOURCE_SEASON)
    home_strength, home_representation = current_target_strength(
        home_team,
        fitted,
        fixtures,
    )
    away_strength, away_representation = current_target_strength(
        away_team,
        fitted,
        fixtures,
    )
    prediction = prediction_from_strengths(
        home_team,
        away_team,
        fitted,
        home_strength,
        away_strength,
        target_season=TARGET_SEASON,
        home_representation=home_representation,
        away_representation=away_representation,
    )
    prediction["promotion_method"] = (
        "66.7% previous promoted-team Premier League prior + "
        "33.3% current Championship signal"
        if (
            home_representation == "PROMOTED_BLEND"
            or away_representation == "PROMOTED_BLEND"
        )
        else None
    )
    return prediction


def _actual_outcome(home_score: object, away_score: object) -> str:
    home = int(float(home_score))
    away = int(float(away_score))
    if home > away:
        return "home_win"
    if home < away:
        return "away_win"
    return "draw"


def _brier_1x2(probabilities: dict, actual: str) -> float:
    keys = ("home_win", "draw", "away_win")
    return sum(
        (float(probabilities[key]) - (1.0 if key == actual else 0.0)) ** 2
        for key in keys
    )


def _log_loss(probabilities: dict, actual: str) -> float:
    probability = max(float(probabilities[actual]), 1e-15)
    return -math.log(probability)


def backtest_previous_season(
    target_season: str,
    source_season: str,
) -> dict:
    """Out-of-sample 1X2 evaluation using only the previous completed season.

    Fixtures involving a team without a complete source-season PL strength are
    excluded rather than filled with the 2026/27 promoted-team compatibility
    prior. This keeps the generic evaluation representation clean.
    """
    fitted = fit_source_season(source_season)
    strengths = fitted["team_strengths"]
    target_fixtures = load_source_fixtures(target_season)

    rows = []
    exclusions = Counter()

    for fixture in target_fixtures:
        home_team = _team_name_for_id(
            target_season,
            fixture["home_team_id"],
        )
        away_team = _team_name_for_id(
            target_season,
            fixture["away_team_id"],
        )

        if home_team not in strengths or away_team not in strengths:
            exclusions["TEAM_NOT_IN_SOURCE_SEASON"] += 1
            continue

        prediction = prediction_from_strengths(
            home_team,
            away_team,
            fitted,
            strengths[home_team],
            strengths[away_team],
            target_season=target_season,
        )
        actual = _actual_outcome(
            fixture["home_score"],
            fixture["away_score"],
        )
        probabilities = prediction["probabilities"]
        predicted = max(
            ("home_win", "draw", "away_win"),
            key=lambda key: probabilities[key],
        )

        rows.append(
            {
                "fixture_id": str(fixture.get("fixture_id") or ""),
                "home_team": home_team,
                "away_team": away_team,
                "actual": actual,
                "predicted": predicted,
                "home_win": probabilities["home_win"],
                "draw": probabilities["draw"],
                "away_win": probabilities["away_win"],
                "brier_1x2": _brier_1x2(probabilities, actual),
                "log_loss": _log_loss(probabilities, actual),
                "correct": predicted == actual,
            }
        )

    if not rows:
        return {
            "model": MODEL_VERSION,
            "source_season": source_season,
            "target_season": target_season,
            "evaluated_fixtures": 0,
            "excluded_fixtures": sum(exclusions.values()),
            "exclusions": dict(exclusions),
            "metrics": None,
            "rows": [],
        }

    return {
        "model": MODEL_VERSION,
        "source_season": source_season,
        "target_season": target_season,
        "evaluated_fixtures": len(rows),
        "excluded_fixtures": sum(exclusions.values()),
        "exclusions": dict(exclusions),
        "metrics": {
            "mean_brier_1x2": (
                sum(row["brier_1x2"] for row in rows) / len(rows)
            ),
            "mean_log_loss": (
                sum(row["log_loss"] for row in rows) / len(rows)
            ),
            "top_outcome_accuracy": (
                sum(1 for row in rows if row["correct"]) / len(rows)
            ),
        },
        "rows": rows,
    }


def compare_bookmaker_odds(
    prediction: dict,
    home_odds: float,
    draw_odds: float,
    away_odds: float,
) -> dict:
    odds = {
        "home_win": float(home_odds),
        "draw": float(draw_odds),
        "away_win": float(away_odds),
    }
    if any(value <= 1.0 for value in odds.values()):
        raise ValueError("Decimal bookmaker odds must be greater than 1.0.")

    raw_market = {
        key: 1.0 / value
        for key, value in odds.items()
    }
    overround = sum(raw_market.values())
    market_probability = {
        key: value / overround
        for key, value in raw_market.items()
    }

    model_probability = prediction["probabilities"]
    probability_edge = {
        key: model_probability[key] - market_probability[key]
        for key in odds
    }
    expected_value = {
        key: model_probability[key] * odds[key] - 1.0
        for key in odds
    }

    return {
        "bookmaker_odds": odds,
        "raw_implied_probability": raw_market,
        "overround": overround,
        "market_probability": market_probability,
        "probability_edge": probability_edge,
        "expected_value": expected_value,
    }


__all__ = [
    "MODEL_VERSION",
    "SOURCE_SEASON",
    "TARGET_SEASON",
    "backtest_previous_season",
    "compare_bookmaker_odds",
    "expected_goal_rates",
    "fair_odds",
    "fair_odds_for_markets",
    "fit_source_season",
    "league_environment",
    "load_source_fixtures",
    "market_probabilities",
    "normalized_strength",
    "poisson_prediction",
    "poisson_probability",
    "prediction_for_source_season",
    "prediction_from_strengths",
    "score_matrix",
    "team_strength_from_pl",
    "top_correct_scores",
]
