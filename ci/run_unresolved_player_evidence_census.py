"""CI runner for the unresolved Player-Match evidence census.

This wrapper redirects the existing read-only audit machinery to a checked-out
copy of the preserved upstream Premier-League-Stats source archive. It does
not modify FRL identity logic, registries, or canonical data.
"""
from __future__ import annotations

import os
from pathlib import Path

source_root = Path(os.environ["FRL_PL_ROOT"]).resolve()
if not source_root.is_dir():
    raise FileNotFoundError(f"Source archive not found: {source_root}")

# Patch the existing hard-coded local source root before modules that import
# the value are loaded. No application source code is modified.
import match_stats  # noqa: E402

match_stats.PL_ROOT = str(source_root)

import player_identity_audit  # noqa: E402

player_identity_audit.PL_ROOT = source_root

import source_family_adapters  # noqa: E402

source_family_adapters.PL_ROOT = str(source_root)

from audit_unresolved_player_match_evidence import classify, print_report  # noqa: E402


if __name__ == "__main__":
    print_report(classify())
