from __future__ import annotations

import csv
import hashlib
import importlib.util
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT.parent / "Premier-League-Stats" / "fpl_scraper" / "fpl_stats"
BUILDER = ROOT / "build_fixture_goal_evidence_complete.py"
MANUAL_RECOVERY = ROOT / "data" / "raw" / "fixture_goal_events_secondary_recovery_2016_17.csv"
RECOVERY_URL = "https://raw.githubusercontent.com/dallum96-gif/football-research-lab/feature/complete-player-match-evidence-2026-08-19/data/raw/fixture_goal_events_secondary_recovery_2016_17.csv"
EXPECTED_RECOVERY_SHA256 = "b52ce2aab0ff885a51c10020844fd90b50b3863d"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _ensure_authoritative_recovery_file() -> None:
    MANUAL_RECOVERY.parent.mkdir(parents=True, exist_ok=True)
    current_sha = _sha256(MANUAL_RECOVERY) if MANUAL_RECOVERY.is_file() else ""
    if current_sha == EXPECTED_RECOVERY_SHA256:
        return
    request = urllib.request.Request(RECOVERY_URL, headers={"User-Agent": "football-research-lab/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read()
    MANUAL_RECOVERY.write_bytes(payload)
    refreshed_sha = _sha256(MANUAL_RECOVERY)
    if refreshed_sha != EXPECTED_RECOVERY_SHA256:
        raise RuntimeError(
            "Recovery artifact SHA mismatch after refresh: "
            f"expected={EXPECTED_RECOVERY_SHA256} actual={refreshed_sha}"
        )


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
    "tottenham hotspur": "spurs", "tottenham": "spurs", "spurs": "spurs",
    "manchester city": "man city", "man city": "man city",
    "manchester united": "man utd", "man utd": "man utd",
    "middlesbrough": "boro", "boro": "boro",
    "west bromwich albion": "west brom", "west brom": "west brom",
    "west ham united": "west ham", "west ham": "west ham",
    "swansea city": "swansea", "swansea": "swansea",
    "hull city": "hull", "hull": "hull",
    "leicester city": "leicester", "leicester": "leicester",
    "stoke city": "stoke", "stoke": "stoke",
}


def _resilient_manual_recovery_rows() -> list[dict[str, str]]:
    _ensure_authoritative_recovery_file()
    rows = _load_rows(MANUAL_RECOVERY)
    output: list[dict[str, str]] = []
    for row in rows:
        item = dict(row)
        season = str(item.get("season") or "").strip()
        fixture_id = str(item.get("canonical_fixture_id") or "").strip()
        home = str(item.get("source_fixture_home") or "").replace("_", " ").strip()
        away = str(item.get("source_fixture_away") or "").replace("_", " ").strip()
        if not home or not away:
            raise RuntimeError(
                f"Recovery row missing explicit fixture sides: {season}/{fixture_id}/"
                f"{item.get('source_scorer_name','')}"
            )
        scoring_side = str(item.get("scoring_side") or "").strip().lower()
        own_goal = str(item.get("own_goal") or "false").strip().casefold() == "true"
        if scoring_side not in {"home", "away"}:
            scorer_team = str(item.get("source_scorer_team") or "").replace("_", " ").strip()
            target = ALIASES.get(scorer_team.casefold(), scorer_team.casefold())
            home_target = ALIASES.get(home.casefold(), home.casefold())
            away_target = ALIASES.get(away.casefold(), away.casefold())
            if target == home_target:
                scoring_side = "home"
            elif target == away_target:
                scoring_side = "away"
            else:
                raise RuntimeError(
                    f"Cannot derive scoring side for authoritative recovery row: "
                    f"{season}/{fixture_id}/{item.get('source_scorer_name','')} "
                    f"{scorer_team!r} vs {home!r}/{away!r}"
                )
            if own_goal:
                scoring_side = "away" if scoring_side == "home" else "home"
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
    _ensure_authoritative_recovery_file()
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
    print(f"RECOVERY SHA256: {_sha256(MANUAL_RECOVERY)}")
    print("GUI: untouched")
    print("")
    module.main()


if __name__ == "__main__":
    main()
