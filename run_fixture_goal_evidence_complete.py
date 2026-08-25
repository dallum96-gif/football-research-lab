from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT.parent / "Premier-League-Stats" / "fpl_scraper" / "fpl_stats"
BUILDER = ROOT / "build_fixture_goal_evidence_complete.py"
MANUAL_RECOVERY = ROOT / "data" / "raw" / "fixture_goal_events_secondary_recovery_2016_17.csv"


def _load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _norm(value: str | None) -> str:
    import re
    import unicodedata

    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.casefold().replace("'", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


ALIASES = {
    "tottenham hotspur": "spurs",
    "tottenham": "spurs",
    "spurs": "spurs",
    "manchester city": "man city",
    "man city": "man city",
    "manchester united": "man utd",
    "man utd": "man utd",
    "middlesbrough": "boro",
    "boro": "boro",
    "west bromwich albion": "west brom",
    "west brom": "west brom",
    "west ham united": "west ham",
    "west ham": "west ham",
    "swansea city": "swansea",
    "swansea": "swansea",
    "hull city": "hull",
    "hull": "hull",
    "leicester city": "leicester",
    "leicester": "leicester",
    "stoke city": "stoke",
    "stoke": "stoke",
}


def _resilient_manual_recovery_rows() -> list[dict[str, str]]:
    """Use explicit recovery provenance first; derive missing side fields only when absent."""
    if not MANUAL_RECOVERY.is_file():
        return []

    rows = _load_rows(MANUAL_RECOVERY)
    side_map: dict[tuple[str, str], dict[str, str]] = {}
    team_evidence = ROOT / "data" / "fixture_team_evidence.csv"
    if team_evidence.is_file():
        for row in _load_rows(team_evidence):
            season = str(row.get("frl_season") or "").strip()
            fixture_id = str(row.get("frl_fixture_id") or "").strip()
            venue = str(row.get("frl_venue") or "").strip().lower()
            team = str(row.get("source_team") or "").replace("_", " ").strip()
            if season and fixture_id and team and venue in {"home", "away"}:
                side_map.setdefault((season, fixture_id), {})[venue] = team

    output: list[dict[str, str]] = []
    for row in rows:
        item = dict(row)
        season = str(item.get("season") or "").strip()
        fixture_id = str(item.get("canonical_fixture_id") or "").strip()
        side = side_map.get((season, fixture_id), {})

        home = str(item.get("source_fixture_home") or "").replace("_", " ").strip() or side.get("home", "")
        away = str(item.get("source_fixture_away") or "").replace("_", " ").strip() or side.get("away", "")
        if not home or not away:
            raise RuntimeError(
                f"Recovery row missing fixture sides: {season}/{fixture_id}/{item.get('source_scorer_name','')}"
            )

        # Prefer the recovery source's explicit final scoring side. Only derive it when absent.
        scoring_side = str(item.get("scoring_side") or "").strip().lower()
        own_goal = str(item.get("own_goal") or "false").strip().casefold() == "true"

        if scoring_side not in {"home", "away"}:
            scorer_team = str(item.get("source_scorer_team") or "").replace("_", " ").strip()
            target = ALIASES.get(scorer_team.casefold(), scorer_team.casefold())
            if target == ALIASES.get(home.casefold(), home.casefold()):
                player_side = "home"
            elif target == ALIASES.get(away.casefold(), away.casefold()):
                player_side = "away"
            else:
                raise RuntimeError(
                    f"Cannot derive scoring side for recovery row: "
                    f"{season}/{fixture_id}/{item.get('source_scorer_name','')} "
                    f"{scorer_team!r} vs {home!r}/{away!r}"
                )
            scoring_side = ("away" if player_side == "home" else "home") if own_goal else player_side

        if scoring_side not in {"home", "away"}:
            raise RuntimeError(
                f"Invalid recovery scoring side: {season}/{fixture_id}/"
                f"{item.get('source_scorer_name','')}: {scoring_side!r}"
            )

        item["source_fixture_home"] = home
        item["source_fixture_away"] = away
        item["scoring_side"] = scoring_side
        output.append(item)

    return output


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
    module.PULSELIVE = source_raw / "fixture_goal_events_pulselive.staged.csv"
    module.MANUAL_RECOVERY = MANUAL_RECOVERY
    module.STAGE_REPORT = source_raw / "fixture_goal_events_stage_report.csv"
    module.SECONDARY_CACHE = source_raw / "_secondary_goal_dataset_cache.csv"
    module.manual_recovery_rows = _resilient_manual_recovery_rows

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
