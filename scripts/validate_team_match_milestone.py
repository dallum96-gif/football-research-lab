from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.audit_exposed_team_match_generic_access import build_audit as build_generic_access_audit
from scripts.reconcile_pulselive_team_stat_capability import DEFAULT_RAW_CATALOGUE, build_reconciliation


CORE_TESTS = (
    ROOT / "tests" / "test_variable_resolver_governance_boundary.py",
    ROOT / "tests" / "test_exposed_team_match_generic_access_audit.py",
    ROOT / "tests" / "test_team_match_sparse_zero_candidates.py",
)


def _batch_number(path: Path) -> int:
    match = re.search(r"_v(\d+)\.json$", path.name)
    return int(match.group(1)) if match else -1


def latest_promotion_manifest() -> tuple[Path | None, dict[str, object]]:
    candidates = sorted(
        (ROOT / "data").glob("team_match_semantic_promotion_batch_v*.json"),
        key=_batch_number,
    )
    if not candidates:
        return None, {}
    path = candidates[-1]
    return path, json.loads(path.read_text(encoding="utf-8"))


def milestone_tests() -> tuple[Path, ...]:
    dynamic: set[Path] = set(CORE_TESTS)
    dynamic.update((ROOT / "tests").glob("test_team_match_semantic_promotion_batch_v*.py"))
    dynamic.update((ROOT / "tests").glob("test_team_match_v*_evidence_stack.py"))
    return tuple(sorted(path for path in dynamic if path.is_file()))


def _expected_counts(
    manifest: dict[str, object],
    *,
    expected_exposed: int | None,
    expected_uncatalogued: int | None,
    expected_raw_only: int | None,
) -> tuple[int | None, int | None, int | None]:
    expected = dict(manifest.get("expected_post_gate") or {})
    reconciliation = dict(expected.get("reconciliation") or {})
    return (
        expected_exposed if expected_exposed is not None else reconciliation.get("EXISTING_EXPOSED"),
        expected_uncatalogued if expected_uncatalogued is not None else reconciliation.get("EXISTING_SOURCE_FIELD_UNCATALOGUED"),
        expected_raw_only if expected_raw_only is not None else reconciliation.get("RAW_SNAPSHOT_ONLY"),
    )


def _run_pytest(tests: tuple[Path, ...]) -> tuple[bool, str]:
    command = [
        sys.executable,
        "-m",
        "pytest",
        *[str(path.relative_to(ROOT)) for path in tests],
        "-q",
    ]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    output = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
    return result.returncode == 0, output


def _run_docs_sync() -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_documentation_sync.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    output = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
    return result.returncode == 0, output


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run the complete local team-match milestone gate in one command: promotion/core "
            "tests, reconciliation, generic-access verification and documentation sync."
        )
    )
    parser.add_argument("--expected-exposed", type=int)
    parser.add_argument("--expected-uncatalogued", type=int)
    parser.add_argument("--expected-raw-only", type=int)
    parser.add_argument("--skip-docs-sync", action="store_true")
    args = parser.parse_args()

    manifest_path, manifest = latest_promotion_manifest()
    expected_exposed, expected_uncatalogued, expected_raw_only = _expected_counts(
        manifest,
        expected_exposed=args.expected_exposed,
        expected_uncatalogued=args.expected_uncatalogued,
        expected_raw_only=args.expected_raw_only,
    )

    tests = milestone_tests()
    pytest_ok, pytest_output = _run_pytest(tests)

    errors: list[str] = []
    if not pytest_ok:
        errors.append("Promotion/core regression suite failed.")

    raw_catalogue = DEFAULT_RAW_CATALOGUE.expanduser().resolve()
    if not raw_catalogue.is_file():
        errors.append(
            f"Raw catalogue not found: {raw_catalogue}. Run scripts/catalogue_pulselive_snapshot_variables.py first."
        )
        reconciliation = {}
        generic = {}
    else:
        reconciliation = build_reconciliation(raw_catalogue)
        generic = build_generic_access_audit(raw_catalogue)

    status_counts = dict(reconciliation.get("status_counts") or {})
    exposed = int(status_counts.get("EXISTING_EXPOSED", 0))
    uncatalogued = int(status_counts.get("EXISTING_SOURCE_FIELD_UNCATALOGUED", 0))
    raw_only = int(status_counts.get("RAW_SNAPSHOT_ONLY", 0))
    raw_paths = int(reconciliation.get("team_match_raw_paths", 0))
    remaining_packaged = sorted(
        str(row.get("source_field") or "")
        for row in reconciliation.get("rows", [])
        if str(row.get("reconciliation_status") or "")
        == "EXISTING_SOURCE_FIELD_UNCATALOGUED"
    )

    if raw_paths and raw_paths != 249:
        errors.append(f"Expected 249 team-match raw paths, found {raw_paths}.")
    if expected_exposed is not None and exposed != int(expected_exposed):
        errors.append(f"Expected {expected_exposed} exposed fields, found {exposed}.")
    if expected_uncatalogued is not None and uncatalogued != int(expected_uncatalogued):
        errors.append(f"Expected {expected_uncatalogued} uncatalogued fields, found {uncatalogued}.")
    if expected_raw_only is not None and raw_only != int(expected_raw_only):
        errors.append(f"Expected {expected_raw_only} raw-only fields, found {raw_only}.")

    generic_count = int(generic.get("exposed_team_match_stat_fields", 0))
    generic_pass = int((generic.get("generic_access_status_counts") or {}).get("PASS", 0))
    generic_all_pass = bool(generic.get("all_exposed_fields_pass_generic_access"))
    if exposed and generic_count != exposed:
        errors.append(
            f"Generic-access audit covered {generic_count} fields but reconciliation reports {exposed} exposed."
        )
    if generic_count and generic_pass != generic_count:
        errors.append(f"Generic-access audit passed {generic_pass}/{generic_count} fields.")
    if generic_count and not generic_all_pass:
        errors.append("Generic-access audit reports at least one failure.")

    docs_ok = True
    docs_output = "SKIPPED"
    if not args.skip_docs_sync:
        docs_ok, docs_output = _run_docs_sync()
        if not docs_ok:
            errors.append("Documentation sync failed.")

    print("TEAM-MATCH MILESTONE GATE - " + ("PASSED" if not errors else "FAILED"))
    if manifest_path is not None:
        print(f"Latest promotion manifest: {manifest_path.relative_to(ROOT)} [{manifest.get('status', 'UNKNOWN')}]")
    print(f"Pytest: {'PASS' if pytest_ok else 'FAIL'} ({len(tests)} test modules)")
    print(f"Reconciliation: {exposed} exposed / {uncatalogued} uncatalogued / {raw_only} raw-only")
    print(f"Generic access: {generic_pass}/{generic_count} PASS")
    print(f"Documentation sync: {'PASS' if docs_ok else 'FAIL'}")
    print(f"Remaining packaged fields: {len(remaining_packaged)}")
    print(json.dumps(remaining_packaged, indent=2))

    if errors:
        print("\nFailures:")
        for error in errors:
            print(f"- {error}")
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
