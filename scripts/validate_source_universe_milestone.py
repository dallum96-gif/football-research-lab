from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from raw_team_stat_research import fixture_raw_team_stat_values, raw_team_stat_fields
from scripts.audit_exposed_team_match_generic_access import build_audit as build_team_generic_audit
from scripts.audit_player_match_source_universe import build_audit as build_player_audit
from scripts.reconcile_pulselive_team_stat_capability import DEFAULT_RAW_CATALOGUE, build_reconciliation
from scripts.validate_team_match_milestone import milestone_tests
from source_family_adapters import season_fixtures
from variable_resolver import resolve_variable

PLAYER_TEST = ROOT / "tests" / "test_player_match_source_universe_bulk.py"


def _pytest() -> tuple[bool, str, int]:
    tests = tuple(sorted(set((*milestone_tests(), PLAYER_TEST))))
    result = subprocess.run(
        [sys.executable, "-m", "pytest", *[str(p.relative_to(ROOT)) for p in tests], "-q"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    output = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
    return result.returncode == 0, output, len(tests)


def _docs_sync() -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_documentation_sync.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    output = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
    return result.returncode == 0, output


def _player_generic_access(player_audit: dict[str, object]) -> tuple[int, int, list[str]]:
    rows = list(player_audit.get("rows") or [])
    failures: list[str] = []
    checked = 0
    passed = 0
    fixture_cache: dict[str, str] = {}
    for row in rows:
        if row.get("registry_status") != "exposed":
            continue
        seasons = list(row.get("seasons") or [])
        if not seasons:
            failures.append(f"{row.get('source_field')}: exposed but no observed season")
            continue
        season = str(seasons[0])
        if season not in fixture_cache:
            fixtures = season_fixtures(season)
            if not fixtures:
                failures.append(f"{season}: no canonical fixtures")
                continue
            fixture_cache[season] = str(fixtures[0]["fixture_id"])
        checked += 1
        field = str(row["source_field"])
        try:
            result = resolve_variable(
                field,
                family="player_match",
                season=season,
                fixture_id=fixture_cache[season],
            )
            if result.get("family") != "player_match":
                raise AssertionError(f"unexpected family {result.get('family')}")
            passed += 1
        except Exception as exc:  # gate reports every failure together
            failures.append(f"{field} ({season}): {type(exc).__name__}: {exc}")
    return checked, passed, failures


def main() -> int:
    errors: list[str] = []

    pytest_ok, pytest_output, test_count = _pytest()
    if not pytest_ok:
        errors.append("Regression suite failed.")

    raw_catalogue = DEFAULT_RAW_CATALOGUE.expanduser().resolve()
    if not raw_catalogue.is_file():
        errors.append(f"Raw PulseLive catalogue unavailable: {raw_catalogue}")
        team = {}
        team_generic = {}
        raw_only_fields: set[str] = set()
    else:
        team = build_reconciliation(raw_catalogue)
        team_generic = build_team_generic_audit(raw_catalogue)
        raw_only_fields = {
            str(row.get("source_field") or "")
            for row in team.get("rows", [])
            if row.get("reconciliation_status") == "RAW_SNAPSHOT_ONLY"
        }

    status = dict(team.get("status_counts") or {})
    exposed = int(status.get("EXISTING_EXPOSED", 0))
    retained = int(status.get("EXISTING_RETAINED", 0))
    restricted = int(status.get("EXISTING_RESTRICTED", 0))
    uncatalogued = int(status.get("EXISTING_SOURCE_FIELD_UNCATALOGUED", 0))
    raw_only = int(status.get("RAW_SNAPSHOT_ONLY", 0))
    if (exposed, retained, restricted, uncatalogued, raw_only) != (176, 8, 6, 0, 59):
        errors.append(
            "Unexpected team reconciliation: expected 176 exposed / 8 retained / 6 restricted / "
            f"0 uncatalogued / 59 raw-only, found {exposed}/{retained}/{restricted}/{uncatalogued}/{raw_only}."
        )

    generic_count = int(team_generic.get("exposed_team_match_stat_fields", 0))
    generic_pass = int((team_generic.get("generic_access_status_counts") or {}).get("PASS", 0))
    if generic_count != 176 or generic_pass != 176 or not team_generic.get("all_exposed_fields_pass_generic_access"):
        errors.append(f"Team generic access expected 176/176 PASS; found {generic_pass}/{generic_count}.")

    raw_index = set(raw_team_stat_fields())
    raw_route_missing = sorted(raw_only_fields - raw_index)
    raw_routed = len(raw_only_fields & raw_index)
    if len(raw_index) != 249:
        errors.append(f"Raw team route index expected 249 fields; found {len(raw_index)}.")
    if raw_route_missing or raw_routed != 59:
        errors.append(f"Raw team route expected 59/59 raw-only fields; routed {raw_routed}; missing={raw_route_missing}.")

    # Integration canary: route a real raw-only field through canonical fixture -> source snapshot.
    if raw_only_fields:
        fixtures = season_fixtures("2016-17")
        if fixtures:
            try:
                canary = fixture_raw_team_stat_values(
                    "2016-17", str(fixtures[0]["fixture_id"]), sorted(raw_only_fields)[0]
                )
                if canary.get("source_rows") != 2:
                    errors.append(
                        f"Raw-team integration canary expected two team rows; found {canary.get('source_rows')}."
                    )
            except Exception as exc:
                errors.append(f"Raw-team integration canary failed: {type(exc).__name__}: {exc}")

    try:
        player = build_player_audit()
    except Exception as exc:
        player = {}
        errors.append(f"Player source audit failed: {type(exc).__name__}: {exc}")

    player_union = int(player.get("observed_source_field_union", 0))
    player_counts = dict(player.get("registry_status_counts_for_observed_fields") or {})
    player_uncatalogued = list(player.get("uncatalogued_observed_fields") or [])
    if player_union != 86:
        errors.append(f"Player-Match decade union expected 86 source fields; found {player_union}.")
    if player_counts != {"exposed": 81, "restricted": 1, "retained": 4}:
        errors.append(f"Unexpected Player-Match registry counts: {player_counts}.")
    if player_uncatalogued:
        errors.append(f"Observed Player-Match fields remain uncatalogued: {player_uncatalogued}")

    player_checked = player_pass = 0
    player_failures: list[str] = []
    if player:
        player_checked, player_pass, player_failures = _player_generic_access(player)
        if player_checked != 81 or player_pass != 81 or player_failures:
            errors.append(
                f"Player-Match generic access expected 81/81 PASS; found {player_pass}/{player_checked}."
            )

    docs_ok, docs_output = _docs_sync()
    if not docs_ok:
        errors.append("Documentation sync failed.")

    print("FRL SOURCE-UNIVERSE MILESTONE - " + ("PASSED" if not errors else "FAILED"))
    print(f"Pytest: {'PASS' if pytest_ok else 'FAIL'} ({test_count} modules)")
    print(
        "Team packaged/governed: "
        f"{exposed} exposed / {retained} retained / {restricted} restricted / {uncatalogued} uncatalogued"
    )
    print(f"Team canonical generic access: {generic_pass}/{generic_count} PASS")
    print(f"Team raw-only pathway: {raw_routed}/59 ROUTED through preserved PulseLive stats")
    print(
        "Player-Match source universe: "
        f"{player_union} observed / {player_counts.get('exposed', 0)} exposed / "
        f"{player_counts.get('retained', 0)} retained / {player_counts.get('restricted', 0)} restricted"
    )
    print(f"Player-Match generic access: {player_pass}/{player_checked} PASS")
    print("Partial-period player fields: INCLUDED (unavailable outside observed seasons; never coerced to zero)")
    print(f"Documentation sync: {'PASS' if docs_ok else 'FAIL'}")

    if errors:
        print("\nFailures:")
        for error in errors:
            print(f"- {error}")
        if player_failures:
            print("\nPlayer generic-access failures:")
            for failure in player_failures:
                print(f"- {failure}")
        if not pytest_ok and pytest_output:
            print("\nPytest output:")
            print(pytest_output)
        if not docs_ok and docs_output:
            print("\nDocumentation-sync output:")
            print(docs_output)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
