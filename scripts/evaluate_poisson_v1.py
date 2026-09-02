from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import poisson_model


DEFAULT_SEASONS = tuple(
    f"{year}-{str(year + 1)[-2:]}"
    for year in range(2016, 2026)
)
OUTCOMES = ("home_win", "draw", "away_win")
UNIFORM_BASELINE = {outcome: 1.0 / 3.0 for outcome in OUTCOMES}


def consecutive_pairs(seasons: tuple[str, ...]) -> tuple[tuple[str, str], ...]:
    return tuple(zip(seasons[:-1], seasons[1:]))


def calibration(rows: list[dict], outcome: str, bins: int = 10) -> list[dict]:
    if outcome not in OUTCOMES:
        raise ValueError(f"Unsupported outcome: {outcome}")
    if bins < 2:
        raise ValueError("Calibration needs at least two bins.")

    buckets = [
        {
            "count": 0,
            "prediction_sum": 0.0,
            "actual_sum": 0,
        }
        for _ in range(bins)
    ]

    for row in rows:
        probability = float(row[outcome])
        index = min(bins - 1, int(probability * bins))
        bucket = buckets[index]
        bucket["count"] += 1
        bucket["prediction_sum"] += probability
        bucket["actual_sum"] += int(row["actual"] == outcome)

    output = []
    for index, bucket in enumerate(buckets):
        count = bucket["count"]
        if not count:
            continue
        output.append(
            {
                "lower": index / bins,
                "upper": (index + 1) / bins,
                "count": count,
                "mean_prediction": bucket["prediction_sum"] / count,
                "observed_rate": bucket["actual_sum"] / count,
            }
        )
    return output


def _actual_outcome(home_score: object, away_score: object) -> str:
    home = int(float(home_score))
    away = int(float(away_score))
    if home > away:
        return "home_win"
    if home < away:
        return "away_win"
    return "draw"


def outcome_base_rates(source_season: str) -> dict[str, float]:
    """Return a leakage-safe 1X2 frequency baseline from the source season."""
    fixtures = poisson_model.load_source_fixtures(source_season)
    if not fixtures:
        raise ValueError(f"No completed source fixtures for {source_season}.")

    counts = {outcome: 0 for outcome in OUTCOMES}
    for fixture in fixtures:
        outcome = _actual_outcome(fixture["home_score"], fixture["away_score"])
        counts[outcome] += 1

    total = len(fixtures)
    return {outcome: counts[outcome] / total for outcome in OUTCOMES}


def _forecast_scores(probabilities: dict[str, float], actual: str) -> dict:
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


def add_naive_benchmarks(report: dict) -> dict:
    """Score each target fixture against uniform and source-season base rates."""
    source_baseline = outcome_base_rates(report["source_season"])
    enriched_rows = []

    for row in report["rows"]:
        copy = dict(row)
        copy["uniform_baseline"] = _forecast_scores(UNIFORM_BASELINE, row["actual"])
        copy["source_rate_baseline"] = _forecast_scores(source_baseline, row["actual"])
        enriched_rows.append(copy)

    enriched = dict(report)
    enriched["rows"] = enriched_rows
    enriched["baselines"] = {
        "uniform": dict(UNIFORM_BASELINE),
        "source_season_outcome_rates": source_baseline,
    }
    return enriched


def _aggregate_forecast(rows: list[dict], key: str) -> dict | None:
    scored = [row[key] for row in rows if key in row]
    if not scored:
        return None
    count = len(scored)
    return {
        "mean_brier_1x2": sum(item["brier_1x2"] for item in scored) / count,
        "mean_log_loss": sum(item["log_loss"] for item in scored) / count,
        "top_outcome_accuracy": sum(1 for item in scored if item["correct"]) / count,
    }


def aggregate_reports(reports: list[dict]) -> dict:
    evaluated = sum(report["evaluated_fixtures"] for report in reports)
    excluded = sum(report["excluded_fixtures"] for report in reports)
    rows = [row for report in reports for row in report["rows"]]

    if not evaluated:
        metrics = None
    else:
        metrics = {
            "mean_brier_1x2": (
                sum(row["brier_1x2"] for row in rows) / evaluated
            ),
            "mean_log_loss": (
                sum(row["log_loss"] for row in rows) / evaluated
            ),
            "top_outcome_accuracy": (
                sum(1 for row in rows if row["correct"]) / evaluated
            ),
        }

    uniform = _aggregate_forecast(rows, "uniform_baseline")
    source_rate = _aggregate_forecast(rows, "source_rate_baseline")
    benchmarks = None
    if metrics is not None and uniform is not None and source_rate is not None:
        benchmarks = {
            "uniform_1x2": uniform,
            "source_season_outcome_rates": source_rate,
            "poisson_skill": {
                "brier_improvement_vs_uniform": uniform["mean_brier_1x2"] - metrics["mean_brier_1x2"],
                "brier_improvement_vs_source_rates": source_rate["mean_brier_1x2"] - metrics["mean_brier_1x2"],
                "log_loss_improvement_vs_uniform": uniform["mean_log_loss"] - metrics["mean_log_loss"],
                "log_loss_improvement_vs_source_rates": source_rate["mean_log_loss"] - metrics["mean_log_loss"],
                "accuracy_gain_vs_source_rates": metrics["top_outcome_accuracy"] - source_rate["top_outcome_accuracy"],
            },
        }

    exclusions: dict[str, int] = {}
    for report in reports:
        for key, value in report["exclusions"].items():
            exclusions[key] = exclusions.get(key, 0) + int(value)

    return {
        "model": poisson_model.MODEL_VERSION,
        "evaluation_method": (
            "Each target Premier League season is predicted from the immediately "
            "preceding completed Premier League season. Target-season results are "
            "never used to fit that target season. Teams without a complete source-"
            "season PL representation are excluded from the generic evaluation."
        ),
        "season_pairs": [
            {
                "source_season": report["source_season"],
                "target_season": report["target_season"],
                "evaluated_fixtures": report["evaluated_fixtures"],
                "excluded_fixtures": report["excluded_fixtures"],
                "metrics": report["metrics"],
                "exclusions": report["exclusions"],
                "baselines": report.get("baselines"),
            }
            for report in reports
        ],
        "evaluated_fixtures": evaluated,
        "excluded_fixtures": excluded,
        "exclusions": exclusions,
        "metrics": metrics,
        "benchmarks": benchmarks,
        "calibration": {
            outcome: calibration(rows, outcome)
            for outcome in OUTCOMES
        },
        "limitations": [
            "This is a previous-season baseline evaluation, not a season-to-date updating model.",
            "Promoted or otherwise unseen teams are excluded instead of receiving the current 2026/27 compatibility prior.",
            "Calibration tables are descriptive reliability bins and are not themselves a recalibration transform.",
            "The source-season outcome-rate benchmark is deliberately naive and uses no team-specific information.",
        ],
    }


def evaluate(seasons: tuple[str, ...] = DEFAULT_SEASONS) -> dict:
    reports = [
        add_naive_benchmarks(
            poisson_model.backtest_previous_season(
                target_season=target,
                source_season=source,
            )
        )
        for source, target in consecutive_pairs(seasons)
    ]
    return aggregate_reports(reports)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate FRL Poisson V1 out of sample across consecutive PL seasons."
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "data" / "poisson_v1_backtest_summary.json"),
        help="JSON summary path.",
    )
    args = parser.parse_args()

    summary = evaluate()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("FRL POISSON V1 BACKTEST")
    print(f"model={summary['model']}")
    print(f"evaluated_fixtures={summary['evaluated_fixtures']}")
    print(f"excluded_fixtures={summary['excluded_fixtures']}")
    if summary["metrics"] is not None:
        print(f"mean_brier_1x2={summary['metrics']['mean_brier_1x2']:.6f}")
        print(f"mean_log_loss={summary['metrics']['mean_log_loss']:.6f}")
        print(f"top_outcome_accuracy={summary['metrics']['top_outcome_accuracy']:.4%}")
    if summary["benchmarks"] is not None:
        source = summary["benchmarks"]["source_season_outcome_rates"]
        skill = summary["benchmarks"]["poisson_skill"]
        print(f"source_rate_brier={source['mean_brier_1x2']:.6f}")
        print(f"source_rate_log_loss={source['mean_log_loss']:.6f}")
        print(f"source_rate_accuracy={source['top_outcome_accuracy']:.4%}")
        print(f"brier_gain_vs_source_rates={skill['brier_improvement_vs_source_rates']:.6f}")
        print(f"log_loss_gain_vs_source_rates={skill['log_loss_improvement_vs_source_rates']:.6f}")
        print(f"accuracy_gain_vs_source_rates={skill['accuracy_gain_vs_source_rates']:.4%}")
    print(f"output={output}")


if __name__ == "__main__":
    main()
