"""Generate or verify the governed FRL Variable Capability Inventory."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from variable_capability_inventory import outputs_are_current, write_inventory


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if the tracked JSON/CSV/summary artifacts differ from a fresh deterministic generation.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Optional destination for generated artifacts (not valid with --check).",
    )
    args = parser.parse_args()

    if args.check and args.output_dir is not None:
        parser.error("--check and --output-dir cannot be used together")

    if args.check:
        if not outputs_are_current(ROOT):
            print("FRL Variable Capability Inventory artifacts are stale.", file=sys.stderr)
            return 1
        print("FRL Variable Capability Inventory artifacts are current.")
        return 0

    inventory = write_inventory(ROOT, args.output_dir)
    summary = inventory["summary"]
    print(f"Inventory version: {summary['inventory_version']}")
    print(f"Families: {summary['family_count']}")
    print(f"Variable records: {summary['variable_record_count']}")
    print(f"Canonical catalogue records: {summary['canonical_catalogue_variable_count']}")
    print(f"Supplemental existing capabilities: {summary['supplemental_existing_capability_count']}")
    print(f"UNKNOWN/REVIEW meanings: {summary['meaning_unknown_or_review_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
