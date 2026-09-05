from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import adaptive_dixon_coles as adc
import query_lab
from scripts import evaluate_adaptive_dixon_coles_v1 as study


OUTPUT = ROOT / "data" / "adaptive_dixon_coles_v1_backtest_summary.json"
TEST_MODULES = (
    "tests/test_adaptive_dixon_coles.py",
    "tests/test_poisson_model.py",
    "tests/test_poisson_evaluation.py",
    "tests/test_team_state.py",
)


def _completed(row: dict) -> bool:
    return row.get("home_score") not in (None, "") and row.get("away_score") not in (None, "")


def _raw_holdout_completed_count() -> int:
    seasons = set(adc.HOLDOUT_SCORE_SEASONS)
    return sum(
        1
        for row in query_lab.load_fixtures()
        if str(row.get("season") or "") in seasons and _completed(row)
    )


def _run_pytest() -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", *TEST_MODULES, "-q"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode == 0, output.strip()


def main() -> None:
    failures: list[str] = []
    pytest_ok, pytest_output = _run_pytest()
    if not pytest_ok:
        failures.append("Adaptive DC / Poisson / Team State regression suite failed.")

    report = None
    try:
        report = study.evaluate()
        OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except Exception as exc:  # validator must report fail closed rather than hide the study error
        failures.append(f"Controlled holdout study failed to execute: {type(exc).__name__}: {exc}")

    if report is not None:
        raw_holdout = _raw_holdout_completed_count()
        resolved_holdout = len(adc.canonical_completed_fixtures(adc.HOLDOUT_SCORE_SEASONS))
        dc = report["holdout"]["adaptive_dixon_coles"]
        poisson = report["holdout"]["poisson_v1"]
        common = report["holdout"]["common_population"]

        if raw_holdout != resolved_holdout:
            failures.append(
                f"Holdout source coverage is not fully identity/kickoff resolved: {resolved_holdout}/{raw_holdout}."
            )
        if int(dc["evaluated_fixtures"]) != raw_holdout:
            failures.append(
                f"Adaptive DC did not score the full resolved holdout slate: {dc['evaluated_fixtures']}/{raw_holdout}."
            )
        if int(common["fixtures"]) != int(poisson["evaluated_fixtures"]):
            failures.append(
                "Common-population comparison does not exactly match frozen Poisson V1's eligible holdout population."
            )
        if report["claims"]["market_edge"] != "NONE":
            failures.append("Study improperly claims a betting-market edge.")
        if report["claims"]["team_state_incremental_value"] != "NOT_TESTED_YET":
            failures.append("Team State incremental value was claimed before its registered challenger was fitted.")
        if not report["temporal_contract"]["development_and_holdout_disjoint"]:
            failures.append("Development and holdout periods overlap.")

    status = "PASSED" if not failures else "FAILED"
    print(f"FRL ADAPTIVE DIXON-COLES CHALLENGER - {status}")
    print(f"Pytest: {'PASS' if pytest_ok else 'FAIL'} ({len(TEST_MODULES)} modules)")

    if report is not None:
        raw_holdout = _raw_holdout_completed_count()
        resolved_holdout = len(adc.canonical_completed_fixtures(adc.HOLDOUT_SCORE_SEASONS))
        development = report["development"]
        holdout = report["holdout"]
        dc = holdout["adaptive_dixon_coles"]
        poisson = holdout["poisson_v1"]
        common = holdout["common_population"]
        paired = common["paired_improvement"]

        print(f"Development configs tried: {development['candidate_count']}")
        print(f"Selected config: {development['selected_config']['key']}")
        print(f"Development seasons: {' / '.join(development['score_seasons'])}")
        print(f"Untouched holdout seasons: {' / '.join(holdout['score_seasons'])}")
        print(f"Raw completed holdout fixtures: {raw_holdout}")
        print(f"Identity/kickoff-resolved holdout fixtures: {resolved_holdout}/{raw_holdout}")
        print(f"Adaptive DC full-slate coverage: {dc['evaluated_fixtures']}/{raw_holdout}")
        print(f"Poisson V1 coverage: {poisson['evaluated_fixtures']}/{raw_holdout} (excluded {poisson['excluded_fixtures']})")
        print(f"Common population: {common['fixtures']}")
        print(
            "Common log loss: "
            f"Poisson {common['poisson']['mean_log_loss']:.6f} / "
            f"Adaptive DC {common['adaptive_dixon_coles']['mean_log_loss']:.6f}"
        )
        print(
            "Common Brier: "
            f"Poisson {common['poisson']['mean_brier_1x2']:.6f} / "
            f"Adaptive DC {common['adaptive_dixon_coles']['mean_brier_1x2']:.6f}"
        )
        print(
            "Common accuracy: "
            f"Poisson {common['poisson']['top_outcome_accuracy']:.2%} / "
            f"Adaptive DC {common['adaptive_dixon_coles']['top_outcome_accuracy']:.2%}"
        )
        print(f"Paired log-loss improvement: {paired['log_loss']:+.6f} (positive favours Adaptive DC)")
        print(f"Paired Brier improvement: {paired['brier_1x2']:+.6f} (positive favours Adaptive DC)")
        print(f"New-team-prior holdout predictions: {dc['new_team_prior_predictions']}")
        print(f"Verdict: {holdout['verdict']}")
        print("Team State feature block: NOT YET FIT")
        print("Market edge claim: NONE")
        print(f"Study artifact: {OUTPUT.relative_to(ROOT)}")

    if failures:
        print("\nFailures:")
        for failure in failures:
            print(f"- {failure}")
        if not pytest_ok and pytest_output:
            print("\nPytest output:")
            print(pytest_output)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
