from __future__ import annotations

import argparse
import json
import math
import random
import sys
from dataclasses import replace
from itertools import groupby
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import adaptive_dixon_coles as adc
from scripts import evaluate_adaptive_dixon_coles_v1 as evaluation


OUTPUT_DEFAULT = ROOT / "data" / "adaptive_dixon_coles_v1_robustness.json"
BOOTSTRAP_SEED = 20260905
BOOTSTRAP_REPS = 4000
OUTCOMES = ("home_win", "draw", "away_win")


def _score(probabilities: dict[str, float], actual: str) -> dict:
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


def _run_zero_rho_backtest(config: adc.AdaptiveDCConfig) -> dict:
    """Run the selected adaptive-strength model with the DC low-score term disabled.

    Setting rho=0 and rho_learning_rate=0 makes the update likelihood independent
    Poisson while retaining the same adaptive attack/defence, decay, regularisation,
    intercept and home-advantage machinery. This isolates whether the Dixon-Coles
    correction itself adds value beyond adaptive strengths.
    """
    zero_rho_config = replace(config, rho_learning_rate=0.0)
    fixtures = adc.canonical_completed_fixtures(adc.DEFAULT_SEASONS)
    model = adc.OnlineDixonColes(zero_rho_config)
    model.rho = 0.0
    rows: list[dict] = []

    for kickoff, grouped in groupby(fixtures, key=lambda row: row["kickoff"]):
        batch = list(grouped)
        model.advance_time(kickoff)
        pending: list[tuple[dict, dict]] = []
        for fixture in batch:
            prediction = model.predict(fixture["home_team_code"], fixture["away_team_code"])
            pending.append((fixture, prediction))
            if fixture["season"] not in set(adc.HOLDOUT_SCORE_SEASONS):
                continue
            actual = adc._actual(fixture["home_goals"], fixture["away_goals"])
            scored = _score(prediction["probabilities"], actual)
            probabilities = prediction["probabilities"]
            rows.append({
                "season": fixture["season"],
                "fixture_id": fixture["fixture_id"],
                "actual": actual,
                "home_win": probabilities["home_win"],
                "draw": probabilities["draw"],
                "away_win": probabilities["away_win"],
                **scored,
            })
        for fixture, _prediction in pending:
            model.update(
                fixture["home_team_code"],
                fixture["away_team_code"],
                fixture["home_goals"],
                fixture["away_goals"],
            )

    return {
        "label": "ADAPTIVE_STRENGTH_ZERO_RHO",
        "evaluated_fixtures": len(rows),
        "metrics": adc.aggregate_rows(rows),
        "rows": rows,
        "final_rho": model.rho,
    }


def _index(rows: list[dict]) -> dict[tuple[str, str], dict]:
    return {(str(row["season"]), str(row["fixture_id"])): row for row in rows}


def _season_stability(poisson_rows: list[dict], dc_rows: list[dict]) -> list[dict]:
    p_index = _index(poisson_rows)
    d_index = _index(dc_rows)
    output = []
    for season in adc.HOLDOUT_SCORE_SEASONS:
        keys = sorted(
            key for key in (set(p_index) & set(d_index)) if key[0] == season
        )
        p = [p_index[key] for key in keys]
        d = [d_index[key] for key in keys]
        p_metrics = adc.aggregate_rows(p)
        d_metrics = adc.aggregate_rows(d)
        if p_metrics is None or d_metrics is None:
            continue
        output.append({
            "season": season,
            "fixtures": len(keys),
            "poisson_log_loss": p_metrics["mean_log_loss"],
            "adaptive_dc_log_loss": d_metrics["mean_log_loss"],
            "log_loss_improvement": p_metrics["mean_log_loss"] - d_metrics["mean_log_loss"],
            "poisson_brier": p_metrics["mean_brier_1x2"],
            "adaptive_dc_brier": d_metrics["mean_brier_1x2"],
            "brier_improvement": p_metrics["mean_brier_1x2"] - d_metrics["mean_brier_1x2"],
            "poisson_accuracy": p_metrics["top_outcome_accuracy"],
            "adaptive_dc_accuracy": d_metrics["top_outcome_accuracy"],
        })
    return output


def _bootstrap_mean_ci(values: list[float], reps: int = BOOTSTRAP_REPS) -> dict:
    if not values:
        raise ValueError("Bootstrap requires at least one paired value.")
    rng = random.Random(BOOTSTRAP_SEED)
    n = len(values)
    estimates = []
    for _ in range(reps):
        total = 0.0
        for _index_value in range(n):
            total += values[rng.randrange(n)]
        estimates.append(total / n)
    estimates.sort()

    def percentile(p: float) -> float:
        position = (len(estimates) - 1) * p
        lower = int(math.floor(position))
        upper = int(math.ceil(position))
        if lower == upper:
            return estimates[lower]
        fraction = position - lower
        return estimates[lower] * (1.0 - fraction) + estimates[upper] * fraction

    return {
        "observed_mean": sum(values) / n,
        "bootstrap_reps": reps,
        "seed": BOOTSTRAP_SEED,
        "ci_95": [percentile(0.025), percentile(0.975)],
        "share_bootstrap_means_above_zero": sum(1 for value in estimates if value > 0.0) / len(estimates),
    }


def _paired_uncertainty(poisson_rows: list[dict], dc_rows: list[dict]) -> dict:
    p_index = _index(poisson_rows)
    d_index = _index(dc_rows)
    keys = sorted(set(p_index) & set(d_index))
    log_deltas = [float(p_index[key]["log_loss"]) - float(d_index[key]["log_loss"]) for key in keys]
    brier_deltas = [float(p_index[key]["brier_1x2"]) - float(d_index[key]["brier_1x2"]) for key in keys]
    return {
        "fixtures": len(keys),
        "positive_favours_adaptive_dc": True,
        "log_loss_improvement": _bootstrap_mean_ci(log_deltas),
        "brier_improvement": _bootstrap_mean_ci(brier_deltas),
    }


def _calibration_summary(rows: list[dict]) -> dict:
    total = len(rows)
    outcome_summary = {}
    for outcome in OUTCOMES:
        bins = evaluation.calibration(rows, outcome)
        ece = sum(
            int(bucket["count"]) * abs(float(bucket["mean_prediction"]) - float(bucket["observed_rate"]))
            for bucket in bins
        ) / total if total else None
        max_gap = max(
            (abs(float(bucket["mean_prediction"]) - float(bucket["observed_rate"])) for bucket in bins),
            default=None,
        )
        outcome_summary[outcome] = {
            "ece": ece,
            "max_bin_gap": max_gap,
            "bins": bins,
        }

    confidence = {}
    for threshold in (0.50, 0.60, 0.70):
        selected = []
        for row in rows:
            predicted = max(OUTCOMES, key=lambda outcome: float(row[outcome]))
            probability = float(row[predicted])
            if probability >= threshold:
                selected.append((probability, predicted == row["actual"]))
        if selected:
            mean_confidence = sum(item[0] for item in selected) / len(selected)
            accuracy = sum(1 for _probability, correct in selected if correct) / len(selected)
            confidence[f"gte_{int(threshold * 100)}"] = {
                "fixtures": len(selected),
                "mean_confidence": mean_confidence,
                "accuracy": accuracy,
                "confidence_minus_accuracy": mean_confidence - accuracy,
            }
        else:
            confidence[f"gte_{int(threshold * 100)}"] = {"fixtures": 0}

    return {
        "fixtures": total,
        "outcomes": outcome_summary,
        "top_outcome_confidence": confidence,
    }


def audit() -> dict:
    selection = adc.select_development_config()
    selected = selection["selected"]
    full_dc = adc.run_online_backtest(
        config=selected,
        all_seasons=adc.DEFAULT_SEASONS,
        score_seasons=adc.HOLDOUT_SCORE_SEASONS,
    )
    poisson = evaluation.frozen_poisson_holdout()
    zero_rho = _run_zero_rho_backtest(selected)
    common = evaluation.paired_common_population(poisson["rows"], full_dc["rows"])
    uncertainty = _paired_uncertainty(poisson["rows"], full_dc["rows"])
    seasons = _season_stability(poisson["rows"], full_dc["rows"])
    calibration = _calibration_summary(full_dc["rows"])

    full_metrics = full_dc["metrics"]
    zero_metrics = zero_rho["metrics"]
    if full_metrics is None or zero_metrics is None:
        raise ValueError("Adaptive DC robustness audit could not score holdout fixtures.")

    rho_ablation = {
        "fixtures": full_metrics["fixtures"],
        "adaptive_strength_zero_rho": zero_metrics,
        "adaptive_dixon_coles": full_metrics,
        "dc_minus_zero_rho": {
            "log_loss_improvement": zero_metrics["mean_log_loss"] - full_metrics["mean_log_loss"],
            "brier_improvement": zero_metrics["mean_brier_1x2"] - full_metrics["mean_brier_1x2"],
            "accuracy_improvement": full_metrics["top_outcome_accuracy"] - zero_metrics["top_outcome_accuracy"],
        },
        "interpretation": "Positive log-loss/Brier values mean the learned Dixon-Coles low-score correction adds value beyond adaptive strengths.",
    }

    ci_low = uncertainty["log_loss_improvement"]["ci_95"][0]
    aggregate_gain = common["paired_improvement"]["log_loss"]
    freeze_status = (
        "CONTROL_FREEZE_SUPPORTED_FOR_NEXT_EXPERIMENT"
        if aggregate_gain > 0 and ci_low > 0
        else "ROBUSTNESS_REVIEW_REQUIRED_BEFORE_CONTROL_FREEZE"
    )

    return {
        "study_id": "ADAPTIVE_DIXON_COLES_V1_ROBUSTNESS_CLOSEOUT",
        "status": "COMPLETED_EXPERIMENTAL",
        "selected_config": selected.key,
        "holdout_seasons": list(adc.HOLDOUT_SCORE_SEASONS),
        "common_population": common,
        "season_stability": seasons,
        "paired_uncertainty": uncertainty,
        "calibration": calibration,
        "rho_ablation": rho_ablation,
        "control_freeze_status": freeze_status,
        "claims": {
            "trusted_model_promotion": "NONE",
            "market_edge": "NONE",
            "team_state_incremental_value": "NOT_TESTED_YET",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit Adaptive Dixon-Coles V1 holdout robustness.")
    parser.add_argument("--output", default=str(OUTPUT_DEFAULT))
    args = parser.parse_args()

    report = audit()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    common = report["common_population"]
    uncertainty = report["paired_uncertainty"]["log_loss_improvement"]
    ablation = report["rho_ablation"]["dc_minus_zero_rho"]
    calibration = report["calibration"]["top_outcome_confidence"]

    print("FRL ADAPTIVE DIXON-COLES V1 ROBUSTNESS CLOSEOUT")
    print(f"selected_config={report['selected_config']}")
    print(f"common_population={common['fixtures']}")
    print(f"paired_log_loss_improvement={common['paired_improvement']['log_loss']:.6f}")
    print(
        "paired_log_loss_bootstrap_95ci="
        f"[{uncertainty['ci_95'][0]:.6f}, {uncertainty['ci_95'][1]:.6f}]"
    )
    print("season_log_loss_improvement=" + ", ".join(
        f"{row['season']}:{row['log_loss_improvement']:+.4f}" for row in report["season_stability"]
    ))
    print(f"rho_log_loss_improvement={ablation['log_loss_improvement']:+.6f}")
    for key in ("gte_50", "gte_60", "gte_70"):
        row = calibration[key]
        if row.get("fixtures"):
            print(
                f"confidence_{key}=n{row['fixtures']} mean_p={row['mean_confidence']:.3f} "
                f"accuracy={row['accuracy']:.3f} gap={row['confidence_minus_accuracy']:+.3f}"
            )
        else:
            print(f"confidence_{key}=n0")
    print(f"control_freeze_status={report['control_freeze_status']}")
    print(f"output={output}")


if __name__ == "__main__":
    main()
