"""Rebuild the governed packaged Team-Match projection from preserved source data.

This is a projection step, not a new evidence source. It resolves every selected
canonical fixture through FRL's verified team/fixture relationship, extracts the
approved Team-Match vocabulary declared in ``match_stats``, and writes the
runtime package consumed by ``team_research_stats``.

Rows for seasons outside the requested materialisation window are preserved.
Source blanks stay blank and are interpreted later by the governed missingness
layer; this script never coerces a missing statistic to zero.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import match_stats  # noqa: E402
import query_lab  # noqa: E402


CORE_SEASONS = (
    "2016-17",
    "2017-18",
    "2018-19",
    "2019-20",
    "2020-21",
    "2021-22",
    "2022-23",
    "2023-24",
    "2024-25",
    "2025-26",
)
FIXTURES = ROOT / "fixtures_master_corrected.csv"
DEFAULT_OUTPUT = ROOT / "data" / "fixture_match_stats.csv"


def _slug(label: str) -> str:
    return label.lower().replace(" ", "_")


def _fieldnames() -> list[str]:
    columns = ["season", "fixture_id", "source_match_id"]
    for side in ("home", "away"):
        columns.extend(f"{side}_core_{_slug(label)}" for label in match_stats.CORE_FIELDS)
        columns.extend(f"{side}_optional_{_slug(label)}" for label in match_stats.OPTIONAL_FIELDS)
    return columns


def _read_existing(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    return [dict(row) for row in match_stats.load_csv(str(path))]


def _selected_fixtures(seasons: tuple[str, ...]) -> list[dict]:
    requested = set(seasons)
    fixtures = [
        row
        for row in match_stats.load_csv(str(FIXTURES))
        if str(row.get("season") or "").strip() in requested
    ]
    for season in seasons:
        count = sum(str(row.get("season") or "").strip() == season for row in fixtures)
        if count != 380:
            raise RuntimeError(f"Expected 380 canonical fixtures for {season}, found {count}")
    return fixtures


def _materialize_fixture(fixture: dict, identity_rows: tuple[dict, ...]) -> dict[str, object]:
    resolved = match_stats.fixture_source_match(fixture, identity_rows)
    season = str(fixture.get("season") or "").strip()
    fixture_id = str(fixture.get("fixture_id") or "").strip()
    if resolved is None:
        raise RuntimeError(f"No verified direct Team-Match source for {season}/{fixture_id}")

    source_match_id, home_row, away_row = resolved
    record: dict[str, object] = {
        "season": season,
        "fixture_id": fixture_id,
        "source_match_id": str(source_match_id),
    }

    for side, source_row in (("home", home_row), ("away", away_row)):
        for label, source_field in match_stats.CORE_FIELDS.items():
            record[f"{side}_core_{_slug(label)}"] = match_stats.number(source_row.get(source_field))
        for label, source_field in match_stats.OPTIONAL_FIELDS.items():
            record[f"{side}_optional_{_slug(label)}"] = match_stats.number(source_row.get(source_field))

    return record


def materialize(pl_root: Path, seasons: tuple[str, ...], output: Path) -> dict[str, int]:
    if not pl_root.is_dir():
        raise RuntimeError(f"Preserved Premier-League-Stats root not found: {pl_root}")

    # match_stats resolves source files through this root. Clear its cache after
    # replacing the default so a caller can explicitly select the preserved copy.
    match_stats.PL_ROOT = str(pl_root)
    match_stats.season_matches.cache_clear()

    identity_rows = tuple(query_lab.load_identity_registry())
    selected = _selected_fixtures(seasons)
    generated = [
        _materialize_fixture(fixture, identity_rows)
        for fixture in selected
    ]

    selected_keys = {
        (str(row["season"]), str(row["fixture_id"]))
        for row in generated
    }
    preserved = [
        row
        for row in _read_existing(output)
        if (str(row.get("season") or ""), str(row.get("fixture_id") or "")) not in selected_keys
    ]

    rows = preserved + generated
    season_order = {season: index for index, season in enumerate((*CORE_SEASONS, "2026-27"))}
    rows.sort(
        key=lambda row: (
            season_order.get(str(row.get("season") or ""), 999),
            int(str(row.get("fixture_id") or "0") or 0),
        )
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=_fieldnames(), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    return {
        season: sum(str(row.get("season") or "") == season for row in generated)
        for season in seasons
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pl-root", type=Path, required=True)
    parser.add_argument(
        "--season",
        action="append",
        dest="seasons",
        choices=CORE_SEASONS,
        help="Historical season to rebuild; repeat as needed. Defaults to the full core decade.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    seasons = tuple(args.seasons or CORE_SEASONS)
    counts = materialize(args.pl_root, seasons, args.output)
    print("FRL RICH TEAM-MATCH MATERIALIZATION")
    for season in seasons:
        print(f"{season}: {counts[season]} fixtures")
    print(f"output={args.output}")
    print(f"core_fields={len(match_stats.CORE_FIELDS)} optional_fields={len(match_stats.OPTIONAL_FIELDS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
