from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import adaptive_dixon_coles as adc
import poisson_model


OUTCOMES = ("home_win", "draw", "away_win")
OUTPUT_DEFAULT = ROOT / "data" / "adaptive_dixon_coles_v1_backtest_summary.json"


def _previous_season(season: str) -> str:
    start = int(str(season).split("-", 1)[0])
    return f"{start - 1}-{str(start)[-2:]}"


def calibration(rows: list[dict], outcome: str, bins: int = 10) -> list[dict]:
    if outcome not in OUTCOMES:
        raise ValueError(f"Unsupported outcome: {outcome}")
    buckets = [
        {"count": 0, "prediction_sum": 0.0, "actual_sum": 0}
        for _ in range(bins)
    ]
    for row in rows:
        probability = float(row[outcome])
        index = min(bins - 1, int(probability * bins))
        bucket = buckets[index]
        bucket["count"] += 1
        bucket["prediction_sum"] += probability
        bucket["actual_sum"] += int(row["actual"] == outcome)
    return [
        {
            "lower": index / bins,
            "upper": (index + 1) / bins,
            "count": bucket["count"],
            "mean_prediction": bucket["prediction_sum"] / bucket["count"],
            "observed_rate": bucket["actual_sum"] / bucket["count"],
        }
        for index, bucket in enumerate(buckets)
        if bucket["count"]
    ]


def _score_probabilities(probabilities: dict[str, float], actual: str) -> dict:
    import math

    brier = sum(
        (float(probabilities[outcome]) - (1.0 if outcome == actual else 0.0)) ** 2
        for outcome in OUTCOMES
    )
    predicted = max(OUTCOMES, key=lambda outcome: probabilities[outcome])
    return {
        "brier_1x2": brier,
        "log_loss": -math.log(max(float(probabilities[actual]), 1e-15)),
        "correct": predicted == actual,
    }


def _actual(home_score: object, away_score: object) -> str:
    home = float(home_score)
    away = float(away_score)
    if home > away:
        return "home_win"
    if home < away:
        return "away_win"
    return "draw"


def _source_rate_probabilities(source_season: str) -> dict[str, float]:
    fixtures = poisson_model.load_source_fixtures(source_season)
    counts = {outcome: 0 for outcome in OUTCOMES}
    for fixture in fixtures:
        counts[_actual(fixture["home_score"], fixture["away_score"])] += 1
    if not fixtures:
        raise ValueError(f"No completed source fixtures for {source_season}.")
    return {outcome: counts[outcome] / len(fixtures) for outcome in OUTCOMES}


def frozen_poisson_holdout() -> dict:
    rows: list[dict] = []
    exclusions: dict[str, int] = {}
    season_reports: list[dict] = []

    for target_season in adc.HOLDOUT_SCORE_SEASONS:
        source_season = _previous_season(target_season)
        report = poisson_model.backtest_previous_season(
            target_season=target_season,
            source_season=source_season,
        )
        source_rates = _source_rate_probabilities(source_season)
        season_rows = []
        for raw in report["rows"]:
            row = dict(raw)
            row["season"] = target_season
            row["source_season"] = source_season
            row["source_rate_baseline"] = _score_probabilities(source_rates, row["actual"])
            rows.append(row)
            season_rows.append(row)
        for key, value in report["exclusions"].items():
            exclusions[key] = exclusions.get(key, 0) + int(value)
        season_reports.append({
            "source_season": source_season,
            "target_season": target_season,
            "evaluated_fixtures": report["evaluated_fixtures"],
            "excluded_fixtures": report["excluded_fixtures"],
            "metrics": adc.aggregate_rows(season_rows),
            "source_rate_probabilities": source_rates,
        })

    return {
        "model": poisson_model.MODEL_VERSION,
        "rows": rows,
        "metrics": adc.aggregate_rows(rows),
        "evaluated_fixtures": len(rows),
        "excluded_fixtures": sum(exclusions.values()),
        "exclusions": exclusions,
        "season_reports": season_reports,
    }


def _source_rate_metrics(poisson_rows: list[dict]) -> dict | None:
    scored = [
        {
            **row["source_rate_baseline"],
        }
        for row in poisson_rows
        if row.get("source_rate_baseline")
    ]
    if not scored:
        return None
    count = len(scored)
    return {
        "fixtures": count,
        "mean_brier_1x2": sum(float(row["brier_1x2"]) for row in scored) / count,
        "mean_log_loss": sum(float(row["log_loss"]) for row in scored) / count,
        "top_outcome_accuracy": sum(1 for row in scored if row["correct"]) / count,
    }


def _index(rows: list[dict]) -> dict[tuple[str, str], dict]:
    return {
        (str(row["season"]), str(row["fixture_id"])): row
        for row in rows
    }


def paired_common_population(poisson_rows: list[dict], challenger_rows: list[dict]) -> dict:
    poisson_index = _index(poisson_rows)
    challenger_index = _index(challenger_rows)
    common_keys = sorted(set(poisson_index) & set(challenger_index))
    poisson_common = [poisson_index[key] for key in common_keys]
    challenger_common = [challenger_index[key] for key in common_keys]
    poisson_metrics = adc.aggregate_rows(poisson_common)
    challenger_metrics = adc.aggregate_rows(challenger_common)
    if poisson_metrics is None or challenger_metrics is None:
        raise ValueError("No common fixture population between Poisson V1 and Adaptive Dixon-Coles.")

    return {
        "fixtures": len(common_keys),
        "poisson": poisson_metrics,
        "adaptive_dixon_coles": challenger_metrics,
        "paired_improvement": {
            "log_loss": poisson_metrics["mean_log_loss"] - challenger_metrics["mean_log_loss"],
            "brier_1x2": poisson_metrics["mean_brier_1x2"] - challenger_metrics["mean_brier_1x2"],
            "top_outcome_accuracy": challenger_metrics["top_outcome_accuracy"] - poisson_metrics["top_outcome_accuracy"],
            "positive_log_loss_favors_challenger": True,
            "positive_brier_favors_challenger": True,
            "positive_accuracy_favors_challenger": True,
        },
        "calibration": {
            "poisson": {outcome: calibration(poisson_common, outcome) for outcome in OUTCOMES},
            "adaptive_dixon_coles": {outcome: calibration(challenger_common, outcome) for outcome in OUTCOMES},
        },
    }


def evaluate() -> dict:
    selection = adc.select_development_config()
    selected = selection["selected"]
    challenger = adc.run_online_backtest(
        config=selected,
        all_seasons=adc.DEFAULT_SEASONS,
        score_seasons=adc.HOLDOUT_SCORE_SEASONS,
    )
    frozen_poisson = frozen_poisson_holdout()
    common = paired_common_population(frozen_poisson["rows"], challenger["rows"])

    holdout_fixture_rows = adc.canonical_completed_fixtures(adc.HOLDOUT_SCORE_SEASONS)
    total_holdout_fixtures = len(holdout_fixture_rows)
    log_gain = float(common["paired_improvement"]["log_loss"])
    verdict = "HOLDOUT_IMPROVEMENT" if log_gain > 0 else "NO_HOLDOUT_IMPROVEMENT"

    return {
        "study_id": "ADAPTIVE_DIXON_COLES_V1_CONTROLLED_HOLDOUT",
        "status": "COMPLETED_EXPERIMENTAL",
        "baseline": poisson_model.MODEL_VERSION,
        "challenger": adc.MODEL_VERSION,
        "fitting_method": (
            "chronological online stochastic-gradient Dixon-Coles-style likelihood updates "
            "with exponential team-parameter shrinkage, L2 regularisation, home advantage, "
            "league-average new-team priors and low-score dependence correction"
        ),
        "development": {
            "score_seasons": list(adc.DEVELOPMENT_SCORE_SEASONS),
            "candidate_count": len(adc.CANDIDATE_CONFIGS),
            "selection_rule": selection["selection_rule"],
            "trials": selection["trials"],
            "selected_config": {
                "key": selected.key,
                "learning_rate": selected.learning_rate,
                "half_life_days": selected.half_life_days,
                "l2": selected.l2,
                "rho_learning_rate": selected.rho_learning_rate,
                "global_learning_rate": selected.global_learning_rate,
            },
        },
        "holdout": {
            "score_seasons": list(adc.HOLDOUT_SCORE_SEASONS),
            "total_completed_fixtures": total_holdout_fixtures,
            "adaptive_dixon_coles": {
                "evaluated_fixtures": challenger["evaluated_fixtures"],
                "metrics": challenger["metrics"],
                "new_team_prior_predictions": challenger["new_team_prior_predictions"],
                "final_state": challenger["final_state"],
                "calibration": {
                    outcome: calibration(challenger["rows"], outcome)
                    for outcome in OUTCOMES
                },
            },
            "poisson_v1": {
                "evaluated_fixtures": frozen_poisson["evaluated_fixtures"],
                "excluded_fixtures": frozen_poisson["excluded_fixtures"],
                "exclusions": frozen_poisson["exclusions"],
                "metrics": frozen_poisson["metrics"],
                "source_rate_baseline_metrics_on_poisson_population": _source_rate_metrics(frozen_poisson["rows"]),
                "season_reports": frozen_poisson["season_reports"],
            },
            "coverage": {
                "adaptive_dixon_coles": challenger["evaluated_fixtures"] / total_holdout_fixtures if total_holdout_fixtures else None,
                "poisson_v1": frozen_poisson["evaluated_fixtures"] / total_holdout_fixtures if total_holdout_fixtures else None,
            },
            "common_population": common,
            "verdict": verdict,
        },
        "temporal_contract": {
            "development_holdout_split_fixed_before_holdout_results": True,
            "development_and_holdout_disjoint": set(adc.DEVELOPMENT_SCORE_SEASONS).isdisjoint(adc.HOLDOUT_SCORE_SEASONS),
            "adaptive_prediction_before_result_update": True,
            "same_kickoff_results_never_cross_contaminate_predictions": True,
            "poisson_v1_frozen_control_unchanged": True,
            "team_state_publication_time_audit_complete": False,
        },
        "claims": {
            "market_edge": "NONE",
            "trusted_model_promotion": "NONE",
            "team_state_incremental_value": "NOT_TESTED_YET",
        },
        "limitations": [
            "This challenger uses chronological online stochastic-gradient updates; it is not a claim of exact replication of the original batch maximum-likelihood Dixon-Coles fitting procedure.",
            "A holdout win would justify deeper model research, not immediate trusted-model promotion.",
            "The Team State feature block is deliberately not fitted in this stage; it must be tested only after the adaptive-strength control is frozen.",
            "No bookmaker prices are used here, so this study cannot establish betting-market edge or profitability.",
            "Team State final-stat publication-time availability remains an explicit unresolved audit before rich historical features can be treated as deployment-equivalent pre-match information.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the controlled FRL Adaptive Dixon-Coles V1 holdout study.")
    parser.add_argument("--output", default=str(OUTPUT_DEFAULT))
    args = parser.parse_args()
    report = evaluate()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    common = report["holdout"]["common_population"]
    print("FRL ADAPTIVE DIXON-COLES V1 CONTROLLED HOLDOUT")
    print(f"selected_config={report['development']['selected_config']['key']}")
    print(f"holdout_fixtures={report['holdout']['total_completed_fixtures']}")
    print(f"dc_evaluated={report['holdout']['adaptive_dixon_coles']['evaluated_fixtures']}")
    print(f"poisson_evaluated={report['holdout']['poisson_v1']['evaluated_fixtures']}")
    print(f"common_population={common['fixtures']}")
    print(f"poisson_common_log_loss={common['poisson']['mean_log_loss']:.6f}")
    print(f"dc_common_log_loss={common['adaptive_dixon_coles']['mean_log_loss']:.6f}")
    print(f"paired_log_loss_improvement={common['paired_improvement']['log_loss']:.6f}")
    print(f"poisson_common_brier={common['poisson']['mean_brier_1x2']:.6f}")
    print(f"dc_common_brier={common['adaptive_dixon_coles']['mean_brier_1x2']:.6f}")
    print(f"verdict={report['holdout']['verdict']}")
    print(f"output={output}")


if __name__ == "__main__":
    main()
