from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import groupby
from typing import Iterable

import poisson_model
import query_lab


MODEL_VERSION = "Adaptive Dixon-Coles V1.0"
OUTCOMES = ("home_win", "draw", "away_win")
DEFAULT_SEASONS = tuple(f"{year}-{str(year + 1)[-2:]}" for year in range(2016, 2026))
DEVELOPMENT_SCORE_SEASONS = ("2017-18", "2018-19", "2019-20", "2020-21")
HOLDOUT_SCORE_SEASONS = ("2021-22", "2022-23", "2023-24", "2024-25", "2025-26")


@dataclass(frozen=True)
class AdaptiveDCConfig:
    learning_rate: float
    half_life_days: float
    l2: float = 0.001
    rho_learning_rate: float = 0.0005
    global_learning_rate: float = 0.002

    @property
    def key(self) -> str:
        return (
            f"lr={self.learning_rate:g}|half_life={self.half_life_days:g}"
            f"|l2={self.l2:g}|rho_lr={self.rho_learning_rate:g}"
            f"|global_lr={self.global_learning_rate:g}"
        )


# Fixed before holdout evaluation. Every tried configuration is returned by the
# evaluator so model selection cannot quietly disappear from the research record.
CANDIDATE_CONFIGS = tuple(
    AdaptiveDCConfig(learning_rate=learning_rate, half_life_days=half_life)
    for learning_rate in (0.01, 0.02, 0.04)
    for half_life in (180.0, 365.0)
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


def _actual(home_goals: float, away_goals: float) -> str:
    if home_goals > away_goals:
        return "home_win"
    if home_goals < away_goals:
        return "away_win"
    return "draw"


def _scores(probabilities: dict[str, float], actual: str) -> dict[str, float | bool]:
    brier = sum(
        (float(probabilities[outcome]) - (1.0 if outcome == actual else 0.0)) ** 2
        for outcome in OUTCOMES
    )
    probability = max(float(probabilities[actual]), 1e-15)
    predicted = max(OUTCOMES, key=lambda outcome: probabilities[outcome])
    return {
        "brier_1x2": brier,
        "log_loss": -math.log(probability),
        "correct": predicted == actual,
    }


def _tau(home_goals: int, away_goals: int, home_lambda: float, away_lambda: float, rho: float) -> float:
    if home_goals == 0 and away_goals == 0:
        return 1.0 - home_lambda * away_lambda * rho
    if home_goals == 0 and away_goals == 1:
        return 1.0 + home_lambda * rho
    if home_goals == 1 and away_goals == 0:
        return 1.0 + away_lambda * rho
    if home_goals == 1 and away_goals == 1:
        return 1.0 - rho
    return 1.0


def dixon_coles_score_matrix(home_lambda: float, away_lambda: float, rho: float) -> dict[tuple[int, int], float]:
    """Return a normalized Dixon-Coles score matrix over FRL's tail-safe Poisson grid."""
    independent = poisson_model.score_matrix(home_lambda, away_lambda)
    adjusted: dict[tuple[int, int], float] = {}
    for score, probability in independent.items():
        factor = _tau(score[0], score[1], home_lambda, away_lambda, rho)
        if factor <= 0:
            raise ValueError("Dixon-Coles low-score correction became non-positive.")
        adjusted[score] = probability * factor
    mass = sum(adjusted.values())
    if mass <= 0:
        raise ValueError("Dixon-Coles score matrix has no probability mass.")
    return {score: probability / mass for score, probability in adjusted.items()}


def _tau_gradients(
    home_goals: int,
    away_goals: int,
    home_lambda: float,
    away_lambda: float,
    rho: float,
) -> tuple[float, float, float]:
    """Gradients of log(tau) w.r.t. log-lambdas and rho."""
    tau = _tau(home_goals, away_goals, home_lambda, away_lambda, rho)
    if tau <= 0:
        return 0.0, 0.0, 0.0
    if home_goals == 0 and away_goals == 0:
        common = -(home_lambda * away_lambda * rho) / tau
        return common, common, -(home_lambda * away_lambda) / tau
    if home_goals == 0 and away_goals == 1:
        return (home_lambda * rho) / tau, 0.0, home_lambda / tau
    if home_goals == 1 and away_goals == 0:
        return 0.0, (away_lambda * rho) / tau, away_lambda / tau
    if home_goals == 1 and away_goals == 1:
        return 0.0, 0.0, -1.0 / tau
    return 0.0, 0.0, 0.0


class OnlineDixonColes:
    """Chronological, regularised Dixon-Coles challenger.

    Team parameters are log attack and log defensive weakness. New teams begin at
    the league-average prior (zero/zero), avoiding the frozen Poisson control's
    promoted-team exclusion. Parameters shrink exponentially toward the league
    average as calendar time passes. Predictions never update model state.
    """

    def __init__(self, config: AdaptiveDCConfig):
        self.config = config
        self.attack: dict[str, float] = {}
        self.defence: dict[str, float] = {}
        self.matches_seen: dict[str, int] = {}
        self.intercept = math.log(1.25)
        self.home_advantage = math.log(1.15)
        self.rho = -0.05
        self.last_timestamp: datetime | None = None
        self.updates = 0

    def _ensure(self, team: str) -> None:
        self.attack.setdefault(team, 0.0)
        self.defence.setdefault(team, 0.0)
        self.matches_seen.setdefault(team, 0)

    @staticmethod
    def _clamp(value: float, lower: float, upper: float) -> float:
        return min(upper, max(lower, value))

    def advance_time(self, timestamp: datetime) -> None:
        if self.last_timestamp is None:
            self.last_timestamp = timestamp
            return
        elapsed_days = max(0.0, (timestamp - self.last_timestamp).total_seconds() / 86400.0)
        if elapsed_days > 0 and self.config.half_life_days > 0:
            factor = 0.5 ** (elapsed_days / self.config.half_life_days)
            for team in self.attack:
                self.attack[team] *= factor
                self.defence[team] *= factor
        self.last_timestamp = timestamp

    def expected_goals(self, home_team: str, away_team: str) -> tuple[float, float]:
        self._ensure(home_team)
        self._ensure(away_team)
        home_log = self.intercept + self.home_advantage + self.attack[home_team] + self.defence[away_team]
        away_log = self.intercept + self.attack[away_team] + self.defence[home_team]
        home_lambda = math.exp(self._clamp(home_log, math.log(0.15), math.log(5.0)))
        away_lambda = math.exp(self._clamp(away_log, math.log(0.15), math.log(5.0)))
        return home_lambda, away_lambda

    def predict(self, home_team: str, away_team: str) -> dict:
        home_lambda, away_lambda = self.expected_goals(home_team, away_team)
        matrix = dixon_coles_score_matrix(home_lambda, away_lambda, self.rho)
        probabilities = poisson_model.market_probabilities(matrix)
        return {
            "model": MODEL_VERSION,
            "expected_goals": {"home": home_lambda, "away": away_lambda},
            "probabilities": {outcome: float(probabilities[outcome]) for outcome in OUTCOMES},
            "rho": self.rho,
            "home_prior_matches": self.matches_seen.get(home_team, 0),
            "away_prior_matches": self.matches_seen.get(away_team, 0),
            "home_representation": (
                "ADAPTIVE_LEARNED_STRENGTH" if self.matches_seen.get(home_team, 0) else "LEAGUE_AVERAGE_NEW_TEAM_PRIOR"
            ),
            "away_representation": (
                "ADAPTIVE_LEARNED_STRENGTH" if self.matches_seen.get(away_team, 0) else "LEAGUE_AVERAGE_NEW_TEAM_PRIOR"
            ),
        }

    def _recenter(self) -> None:
        if not self.attack:
            return
        attack_mean = sum(self.attack.values()) / len(self.attack)
        defence_mean = sum(self.defence.values()) / len(self.defence)
        for team in self.attack:
            self.attack[team] -= attack_mean
            self.defence[team] -= defence_mean
        self.intercept += attack_mean + defence_mean
        self.intercept = self._clamp(self.intercept, math.log(0.65), math.log(2.25))

    def update(self, home_team: str, away_team: str, home_goals: int, away_goals: int) -> None:
        self._ensure(home_team)
        self._ensure(away_team)
        home_lambda, away_lambda = self.expected_goals(home_team, away_team)
        tau_home, tau_away, tau_rho = _tau_gradients(
            home_goals, away_goals, home_lambda, away_lambda, self.rho
        )
        grad_home = float(home_goals) - home_lambda + tau_home
        grad_away = float(away_goals) - away_lambda + tau_away

        lr = self.config.learning_rate
        shrink = max(0.0, 1.0 - lr * self.config.l2)
        for team in (home_team, away_team):
            self.attack[team] *= shrink
            self.defence[team] *= shrink

        self.attack[home_team] += lr * grad_home
        self.defence[away_team] += lr * grad_home
        self.attack[away_team] += lr * grad_away
        self.defence[home_team] += lr * grad_away

        self.intercept += self.config.global_learning_rate * (grad_home + grad_away)
        self.home_advantage += self.config.global_learning_rate * grad_home
        self.rho += self.config.rho_learning_rate * tau_rho

        for team in (home_team, away_team):
            self.attack[team] = self._clamp(self.attack[team], -1.5, 1.5)
            self.defence[team] = self._clamp(self.defence[team], -1.5, 1.5)
        self.home_advantage = self._clamp(self.home_advantage, -0.35, 0.65)
        # Negative rho raises 0-0/1-1 mass and lowers adjacent one-goal cells;
        # this bound guarantees positive tau over the model's lambda safety range.
        self.rho = self._clamp(self.rho, -0.15, 0.0)
        self._recenter()

        self.matches_seen[home_team] += 1
        self.matches_seen[away_team] += 1
        self.updates += 1



def _identity_index() -> dict[tuple[str, str], dict]:
    index: dict[tuple[str, str], dict] = {}
    for row in query_lab.load_identity_registry():
        if str(row.get("mapping_status") or "") != "VERIFIED":
            continue
        season = str(row.get("season") or "").strip()
        local_id = str(row.get("local_team_id") or "").strip()
        code = str(row.get("persistent_team_code") or "").strip()
        if season and local_id and code:
            index[(season, local_id)] = {
                "team_code": code,
                "name": str(row.get("canonical_name") or "").replace("_", " ").strip(),
            }
    return index


def canonical_completed_fixtures(seasons: Iterable[str] = DEFAULT_SEASONS) -> list[dict]:
    selected = set(str(season) for season in seasons)
    identities = _identity_index()
    rows: list[dict] = []
    for fixture in query_lab.load_fixtures():
        season = str(fixture.get("season") or "")
        if season not in selected:
            continue
        home_goals = _number(fixture.get("home_score"))
        away_goals = _number(fixture.get("away_score"))
        kickoff = _dt(fixture.get("kickoff_time"))
        home = identities.get((season, str(fixture.get("home_team_id") or "")))
        away = identities.get((season, str(fixture.get("away_team_id") or "")))
        if home_goals is None or away_goals is None or kickoff is None or home is None or away is None:
            continue
        rows.append({
            "season": season,
            "fixture_id": str(fixture.get("fixture_id") or ""),
            "kickoff": kickoff,
            "kickoff_time": fixture.get("kickoff_time"),
            "home_team_code": home["team_code"],
            "away_team_code": away["team_code"],
            "home_team": home["name"],
            "away_team": away["name"],
            "home_goals": int(home_goals),
            "away_goals": int(away_goals),
        })
    rows.sort(key=lambda row: (row["kickoff"], row["season"], row["fixture_id"]))
    return rows


def aggregate_rows(rows: list[dict]) -> dict | None:
    if not rows:
        return None
    count = len(rows)
    return {
        "fixtures": count,
        "mean_brier_1x2": sum(float(row["brier_1x2"]) for row in rows) / count,
        "mean_log_loss": sum(float(row["log_loss"]) for row in rows) / count,
        "top_outcome_accuracy": sum(1 for row in rows if row["correct"]) / count,
    }


def run_online_backtest(
    *,
    config: AdaptiveDCConfig,
    all_seasons: Iterable[str] = DEFAULT_SEASONS,
    score_seasons: Iterable[str],
) -> dict:
    score_set = set(score_seasons)
    fixtures = canonical_completed_fixtures(all_seasons)
    model = OnlineDixonColes(config)
    rows: list[dict] = []
    new_team_prior_predictions = 0

    # Crucial temporal guard: simultaneous fixtures are all predicted before any
    # result from that kickoff timestamp is allowed to update model state.
    for kickoff, grouped in groupby(fixtures, key=lambda row: row["kickoff"]):
        batch = list(grouped)
        model.advance_time(kickoff)
        pending: list[tuple[dict, dict]] = []
        for fixture in batch:
            prediction = model.predict(fixture["home_team_code"], fixture["away_team_code"])
            pending.append((fixture, prediction))
            if fixture["season"] in score_set:
                if prediction["home_prior_matches"] == 0 or prediction["away_prior_matches"] == 0:
                    new_team_prior_predictions += 1
                actual = _actual(fixture["home_goals"], fixture["away_goals"])
                scored = _scores(prediction["probabilities"], actual)
                probabilities = prediction["probabilities"]
                rows.append({
                    "season": fixture["season"],
                    "fixture_id": fixture["fixture_id"],
                    "kickoff_time": fixture["kickoff_time"],
                    "home_team": fixture["home_team"],
                    "away_team": fixture["away_team"],
                    "actual": actual,
                    "home_win": probabilities["home_win"],
                    "draw": probabilities["draw"],
                    "away_win": probabilities["away_win"],
                    "brier_1x2": scored["brier_1x2"],
                    "log_loss": scored["log_loss"],
                    "correct": scored["correct"],
                    "home_prior_matches": prediction["home_prior_matches"],
                    "away_prior_matches": prediction["away_prior_matches"],
                    "home_representation": prediction["home_representation"],
                    "away_representation": prediction["away_representation"],
                    "expected_home_goals": prediction["expected_goals"]["home"],
                    "expected_away_goals": prediction["expected_goals"]["away"],
                    "rho": prediction["rho"],
                })
        for fixture, _prediction in pending:
            model.update(
                fixture["home_team_code"],
                fixture["away_team_code"],
                fixture["home_goals"],
                fixture["away_goals"],
            )

    return {
        "model": MODEL_VERSION,
        "config": {
            "key": config.key,
            "learning_rate": config.learning_rate,
            "half_life_days": config.half_life_days,
            "l2": config.l2,
            "rho_learning_rate": config.rho_learning_rate,
            "global_learning_rate": config.global_learning_rate,
        },
        "score_seasons": list(score_seasons),
        "evaluated_fixtures": len(rows),
        "new_team_prior_predictions": new_team_prior_predictions,
        "metrics": aggregate_rows(rows),
        "rows": rows,
        "final_state": {
            "updates": model.updates,
            "rho": model.rho,
            "home_advantage": model.home_advantage,
            "intercept": model.intercept,
            "teams_seen": len(model.matches_seen),
        },
        "temporal_contract": {
            "prediction_before_result_update": True,
            "same_kickoff_batching": True,
            "future_results_used": False,
        },
    }


def select_development_config() -> dict:
    trials = []
    for config in CANDIDATE_CONFIGS:
        report = run_online_backtest(
            config=config,
            all_seasons=DEFAULT_SEASONS[:5],
            score_seasons=DEVELOPMENT_SCORE_SEASONS,
        )
        metrics = report["metrics"]
        if metrics is None:
            continue
        trials.append({
            "config": report["config"],
            "mean_log_loss": metrics["mean_log_loss"],
            "mean_brier_1x2": metrics["mean_brier_1x2"],
            "fixtures": metrics["fixtures"],
        })
    if not trials:
        raise ValueError("No Adaptive Dixon-Coles development configurations could be scored.")
    ordered = sorted(trials, key=lambda row: (row["mean_log_loss"], row["mean_brier_1x2"], row["config"]["key"]))
    winner_key = ordered[0]["config"]["key"]
    selected = next(config for config in CANDIDATE_CONFIGS if config.key == winner_key)
    return {
        "selection_rule": "lowest development multiclass log loss; Brier then config key break ties",
        "development_score_seasons": list(DEVELOPMENT_SCORE_SEASONS),
        "trials": ordered,
        "selected": selected,
    }


__all__ = [
    "AdaptiveDCConfig",
    "CANDIDATE_CONFIGS",
    "DEFAULT_SEASONS",
    "DEVELOPMENT_SCORE_SEASONS",
    "HOLDOUT_SCORE_SEASONS",
    "MODEL_VERSION",
    "OnlineDixonColes",
    "aggregate_rows",
    "canonical_completed_fixtures",
    "dixon_coles_score_matrix",
    "run_online_backtest",
    "select_development_config",
]
