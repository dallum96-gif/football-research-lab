from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import team_state  # noqa: E402


TESTS = (
    ROOT / "tests" / "test_team_state.py",
    ROOT / "tests" / "test_matchday_pack.py",
    ROOT / "tests" / "test_team_analysis_kernel.py",
)
EXPERIMENT = ROOT / "data" / "experiments" / "team_state_underlying_performance_v1.json"
COMPETITIVE_STANDARD = ROOT / "FRL_COMPETITIVE_INTELLIGENCE_STANDARD.md"


def _run_pytest() -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", *[str(path.relative_to(ROOT)) for path in TESTS], "-q"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    output = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
    return result.returncode == 0, output


def main() -> int:
    errors: list[str] = []
    pytest_ok, pytest_output = _run_pytest()
    if not pytest_ok:
        errors.append("Team State / Matchday / team-kernel regression suite failed.")

    try:
        states = team_state.fixture_team_states("2025-26", "200")
    except Exception as exc:
        states = {}
        errors.append(f"Live Team State reconstruction failed: {exc}")

    for side in ("home", "away"):
        state = states.get(side) or {}
        recent = (state.get("windows") or {}).get("recent_5") or {}
        if recent.get("sample_size") != 5:
            errors.append(f"{side}: expected five-match recent state window.")
        if recent.get("representation_mixing_detected"):
            errors.append(f"{side}: expected-goals representation mixing detected.")
        temporal = state.get("temporal_contract") or {}
        if temporal.get("target_kickoff_enforced") is not True:
            errors.append(f"{side}: target kickoff is not enforced.")
        if temporal.get("predictive_research_status") != "EXPERIMENTAL_UNTIL_INFORMATION_AVAILABILITY_AUDIT":
            errors.append(f"{side}: temporal limitation is not explicit.")

    metric_count = len(team_state.STATE_METRICS)
    if metric_count != 16:
        errors.append(f"Expected 16 deliberately selected V1 state metrics, found {metric_count}.")

    if not EXPERIMENT.is_file():
        errors.append("Registered forecasting experiment manifest is missing.")
        experiment_status = "MISSING"
    else:
        experiment = json.loads(EXPERIMENT.read_text(encoding="utf-8"))
        experiment_status = str(experiment.get("status") or "UNKNOWN")
        if experiment_status != "DESIGN_REGISTERED_NOT_RUN":
            errors.append(f"Unexpected experiment status: {experiment_status}")
        if not experiment.get("primary_feature_block"):
            errors.append("Experiment primary feature block is empty.")

    if not COMPETITIVE_STANDARD.is_file():
        errors.append("Competitive-intelligence standing standard is missing.")

    print("FRL TEAM STATE & FIXTURE INTELLIGENCE V1 - " + ("PASSED" if not errors else "FAILED"))
    print(f"Pytest: {'PASS' if pytest_ok else 'FAIL'} ({len(TESTS)} modules)")
    print(f"Team State metrics: {metric_count}")
    print("Pre-fixture windows: recent_5 / recent_10 / season_to_date / prior_season")
    print("Temporal cutoff: target kickoff ENFORCED")
    print("Historical publication-time proof: EXPLICITLY NOT YET PROVEN")
    print("Expected-goals representation: PLAYER_MATCH_DERIVED_TEAM_MATCH only")
    print("Matchday API: /api/v1/matchday/state/{season}/{fixture_id}")
    print(f"Forecasting experiment: {experiment_status}")
    print(f"Competitive intelligence standard: {'PRESENT' if COMPETITIVE_STANDARD.is_file() else 'MISSING'}")

    if errors:
        print("\nFailures:")
        for error in errors:
            print(f"- {error}")
        if pytest_output:
            print("\nPytest output:")
            print(pytest_output)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
