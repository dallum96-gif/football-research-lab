from __future__ import annotations

import csv
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT.parent / "Premier-League-Stats" / "fpl_scraper" / "fpl_stats"
BUILDER = ROOT / "build_fixture_goal_evidence_complete.py"
RECOVERY = ROOT / "data" / "raw" / "fixture_goal_events_secondary_recovery_2016_17.csv"


def norm(value: str | None) -> str:
    text = str(value or "").casefold().replace("_", " ").strip()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def load_recovery_rows() -> list[dict[str, str]]:
    with RECOVERY.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    if not SOURCE_ROOT.is_dir():
        raise FileNotFoundError(f"Missing canonical source repository: {SOURCE_ROOT}")
    if not BUILDER.is_file():
        raise FileNotFoundError(f"Missing complete goal builder: {BUILDER}")
    if not RECOVERY.is_file():
        raise FileNotFoundError(f"Missing secondary recovery source: {RECOVERY}")

    spec = importlib.util.spec_from_file_location("fixture_goal_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load builder module: {BUILDER}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    source_raw = SOURCE_ROOT / "data" / "raw"
    module.PULSELIVE = source_raw / "fixture_goal_events_pulselive.staged.csv"
    module.MANUAL_RECOVERY = RECOVERY
    module.STAGE_REPORT = source_raw / "fixture_goal_events_stage_report.csv"
    module.TEAM_EVIDENCE = ROOT / "data" / "fixture_team_evidence.csv"
    module.FIXTURES_MASTER = ROOT / "fixtures_master.csv"
    module.SECONDARY_CACHE = source_raw / "_secondary_goal_dataset_cache.csv"

    original_manual = module.manual_recovery_rows

    def resilient_manual_recovery_rows() -> list[dict[str, str]]:
        rows = original_manual()
        if rows:
            return rows

        raw_rows = load_recovery_rows()
        sides = module.fixture_sides()
        repaired: list[dict[str, str]] = []

        for row in raw_rows:
            item = dict(row)
            season = str(item.get("season") or "").strip()
            fixture_id = str(item.get("canonical_fixture_id") or "").strip()
            canonical = sides.get((season, fixture_id), {})
            home = canonical.get("home") or str(item.get("source_fixture_home") or "").replace("_", " ").strip()
            away = canonical.get("away") or str(item.get("source_fixture_away") or "").replace("_", " ").strip()
            scorer_team = str(item.get("source_scorer_team") or "").replace("_", " ").strip()
            own_goal = str(item.get("own_goal") or "").casefold() == "true"

            side = str(item.get("scoring_side") or "").strip().casefold()
            if side not in {"home", "away"}:
                scorer_norm = norm(scorer_team)
                if scorer_norm == norm(home):
                    side = "away" if own_goal else "home"
                elif scorer_norm == norm(away):
                    side = "home" if own_goal else "away"
                else:
                    raise RuntimeError(
                        f"Manual recovery scorer cannot be reconciled: {season}/{fixture_id}/"
                        f"{item.get('source_scorer_name')} = {scorer_team!r} vs {home!r}/{away!r}"
                    )

            item["scoring_side"] = side
            item["source_fixture_home"] = home
            item["source_fixture_away"] = away
            item["source_scorer_team"] = home if side == "home" else away
            repaired.append(item)

        return repaired

    module.manual_recovery_rows = resilient_manual_recovery_rows

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
