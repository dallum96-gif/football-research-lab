from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT.parent / "Premier-League-Stats" / "fpl_scraper" / "fpl_stats"
BUILDER = ROOT / "build_fixture_goal_evidence_complete.py"


def main() -> None:
    if not SOURCE_ROOT.is_dir():
        raise FileNotFoundError(f"Missing canonical source repository: {SOURCE_ROOT}")
    if not BUILDER.is_file():
        raise FileNotFoundError(f"Missing complete goal builder: {BUILDER}")

    spec = importlib.util.spec_from_file_location("fixture_goal_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load builder module: {BUILDER}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    source_raw = SOURCE_ROOT / "data" / "raw"
    frl_raw = ROOT / "data" / "raw"

    module.PULSELIVE = source_raw / "fixture_goal_events_pulselive.staged.csv"
    module.STAGE_REPORT = source_raw / "fixture_goal_events_stage_report.csv"
    module.MANUAL_RECOVERY = frl_raw / "fixture_goal_events_secondary_recovery_2016_17.csv"
    module.SECONDARY_CACHE = frl_raw / "_secondary_goal_dataset_cache.csv"

    print("FIXTURE-GOAL COMPLETE BUILDER: canonical source paths injected")
    print(f"SOURCE ROOT: {SOURCE_ROOT}")
    print(f"PULSELIVE: {module.PULSELIVE}")
    print(f"STAGE REPORT: {module.STAGE_REPORT}")
    print(f"MANUAL RECOVERY: {module.MANUAL_RECOVERY}")
    print("GUI: untouched")
    print("")

    module.main()


if __name__ == "__main__":
    main()
