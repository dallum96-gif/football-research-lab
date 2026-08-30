from collections import defaultdict
import math

import query_lab


TARGET_SEASON = "2026-27"
SOURCE_SEASON = "2025-26"

# The only teams exposed by the V0.1 Prediction Lab.
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

MAX_GOALS = 8


def poisson_probability(
    goals,
    expected_goals,
):
    return (
        math.exp(-expected_goals)
        * expected_goals ** goals
        / math.factorial(goals)
    )


def fair_odds(
    probability,
):
    if probability <= 0:
        return None

    return 1.0 / probability


def _completed_score(value):
    if value is None:
        return False

    if isinstance(value, str):
        return bool(value.strip())

    return True


def load_source_fixtures():
    return [
        row
        for row in query_lab.load_fixtures()
        if row["season"] == SOURCE_SEASON
        and _completed_score(row.get("home_score"))
        and _completed_score(row.get("away_score"))
    ]


def team_strength_from_pl(
    fixtures,
    team_name,
):
    # Resolve the canonical local team ID from the existing
    # verified identity registry.
    identity_rows = (
        query_lab.load_identity_registry()
    )

    candidates = [
        row
        for row in identity_rows
        if row["season"] == SOURCE_SEASON
        and row["canonical_name"].replace(
            "_",
            " ",
        ) == team_name
    ]

    if len(candidates) != 1:
        raise ValueError(
            f"Could not uniquely resolve "
            f"{team_name} in {SOURCE_SEASON}."
        )

    team_id = str(
        candidates[0]["local_team_id"]
    )

    home_matches = [
        row
        for row in fixtures
        if str(row["home_team_id"]) == team_id
    ]

    away_matches = [
        row
        for row in fixtures
        if str(row["away_team_id"]) == team_id
    ]

    if not home_matches or not away_matches:
        raise ValueError(
            f"Incomplete 2025/26 data for {team_name}."
        )

    return {
        "home_attack_goals": (
            sum(
                int(row["home_score"])
                for row in home_matches
            )
            / len(home_matches)
        ),
        "home_defence_goals": (
            sum(
                int(row["away_score"])
                for row in home_matches
            )
            / len(home_matches)
        ),
        "away_attack_goals": (
            sum(
                int(row["away_score"])
                for row in away_matches
            )
            / len(away_matches)
        ),
        "away_defence_goals": (
            sum(
                int(row["home_score"])
                for row in away_matches
            )
            / len(away_matches)
        ),
        "home_matches": len(home_matches),
        "away_matches": len(away_matches),
    }


def league_environment(
    fixtures,
):
    return {
        "home_goals": (
            sum(
                int(row["home_score"])
                for row in fixtures
            )
            / len(fixtures)
        ),
        "away_goals": (
            sum(
                int(row["away_score"])
                for row in fixtures
            )
            / len(fixtures)
        ),
        "matches": len(fixtures),
    }


def normalized_strength(
    raw,
    league,
):
    return {
        "home_attack": (
            raw["home_attack_goals"]
            / league["home_goals"]
        ),
        "home_defence": (
            raw["home_defence_goals"]
            / league["away_goals"]
        ),
        "away_attack": (
            raw["away_attack_goals"]
            / league["away_goals"]
        ),
        "away_defence": (
            raw["away_defence_goals"]
            / league["home_goals"]
        ),
        "home_matches": raw["home_matches"],
        "away_matches": raw["away_matches"],
    }


def promoted_pl_prior(
    fixtures,
    league,
):
    # Previous season's promoted cohort:
    # Leeds, Burnley and Sunderland.
    previous_promoted = [
        "Leeds United",
        "Burnley",
        "Sunderland",
    ]

    strengths = [
        normalized_strength(
            team_strength_from_pl(
                fixtures,
                team,
            ),
            league,
        )
        for team in previous_promoted
    ]

    return {
        key: (
            sum(
                item[key]
                for item in strengths
            )
            / len(strengths)
        )
        for key in (
            "home_attack",
            "home_defence",
            "away_attack",
            "away_defence",
        )
    }


def promoted_efl_strength(
    team,
    league,
):
    if team not in PROMOTED_TEAMS:
        raise ValueError(
            f"{team} is not a promoted team."
        )

    values = PROMOTED_TEAMS[team]

    raw = {
        "home_attack": (
            (
                values["home_goals_for"]
                / 23
            )
            / EFL_HOME_GOALS
        ),
        "home_defence": (
            (
                values["home_goals_against"]
                / 23
            )
            / EFL_AWAY_GOALS
        ),
        "away_attack": (
            (
                values["away_goals_for"]
                / 23
            )
            / EFL_AWAY_GOALS
        ),
        "away_defence": (
            (
                values["away_goals_against"]
                / 23
            )
            / EFL_HOME_GOALS
        ),
    }

    return raw


def team_strength(
    team,
    fixtures,
    league,
):
    if team in PROMOTED_TEAMS:
        prior = promoted_pl_prior(
            fixtures,
            league,
        )

        efl = promoted_efl_strength(
            team,
            league,
        )

        return {
            key: (
                PROMOTED_PRIOR_WEIGHT
                * prior[key]
                + PROMOTED_EFL_WEIGHT
                * efl[key]
            )
            for key in (
                "home_attack",
                "home_defence",
                "away_attack",
                "away_defence",
            )
        }

    raw = team_strength_from_pl(
        fixtures,
        team,
    )

    return normalized_strength(
        raw,
        league,
    )


def poisson_prediction(
    home_team,
    away_team,
):
    if home_team not in PREMIER_LEAGUE_2026_27:
        raise ValueError(
            f"{home_team} is not in the 2026/27 "
            "Premier League universe."
        )

    if away_team not in PREMIER_LEAGUE_2026_27:
        raise ValueError(
            f"{away_team} is not in the 2026/27 "
            "Premier League universe."
        )

    if home_team == away_team:
        raise ValueError(
            "Home and away teams must be different."
        )

    fixtures = load_source_fixtures()
    league = league_environment(
        fixtures
    )

    home_strength = team_strength(
        home_team,
        fixtures,
        league,
    )

    away_strength = team_strength(
        away_team,
        fixtures,
        league,
    )

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

    scores = {}

    for home_goals in range(
        MAX_GOALS + 1
    ):
        home_probability = poisson_probability(
            home_goals,
            expected_home,
        )

        for away_goals in range(
            MAX_GOALS + 1
        ):
            away_probability = poisson_probability(
                away_goals,
                expected_away,
            )

            scores[
                (home_goals, away_goals)
            ] = (
                home_probability
                * away_probability
            )

    home_win = sum(
        value
        for (home, away), value in scores.items()
        if home > away
    )

    draw = sum(
        value
        for (home, away), value in scores.items()
        if home == away
    )

    away_win = sum(
        value
        for (home, away), value in scores.items()
        if home < away
    )

    over_25 = sum(
        value
        for (home, away), value in scores.items()
        if home + away >= 3
    )

    btts = sum(
        value
        for (home, away), value in scores.items()
        if home > 0 and away > 0
    )

    most_likely = max(
        scores.items(),
        key=lambda item: item[1],
    )

    return {
        "model": "Poisson V0.1",
        "target_season": TARGET_SEASON,
        "source_season": SOURCE_SEASON,
        "home_team": home_team,
        "away_team": away_team,
        "league_environment": league,
        "home_strength": home_strength,
        "away_strength": away_strength,
        "promotion_method": (
            "66.7% previous promoted-team "
            "Premier League prior + "
            "33.3% current Championship signal"
        ),
        "expected_goals": {
            "home": expected_home,
            "away": expected_away,
        },
        "probabilities": {
            "home_win": home_win,
            "draw": draw,
            "away_win": away_win,
            "over_2_5": over_25,
            "btts": btts,
        },
        "fair_odds": {
            "home_win": fair_odds(home_win),
            "draw": fair_odds(draw),
            "away_win": fair_odds(away_win),
        },
        "most_likely_score": {
            "home": most_likely[0][0],
            "away": most_likely[0][1],
            "probability": most_likely[1],
        },
    }


def compare_bookmaker_odds(
    prediction,
    home_odds,
    draw_odds,
    away_odds,
):
    odds = {
        "home_win": float(home_odds),
        "draw": float(draw_odds),
        "away_win": float(away_odds),
    }

    raw_market = {
        key: 1.0 / value
        for key, value in odds.items()
    }

    overround = sum(
        raw_market.values()
    )

    market_probability = {
        key: value / overround
        for key, value in raw_market.items()
    }

    model_probability = prediction[
        "probabilities"
    ]

    probability_edge = {
        key: (
            model_probability[key]
            - market_probability[key]
        )
        for key in odds
    }

    expected_value = {
        key: (
            model_probability[key]
            * odds[key]
            - 1.0
        )
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
