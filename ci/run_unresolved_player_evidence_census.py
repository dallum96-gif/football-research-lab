"""CI runner for the canonical Player evidence census.

Redirects existing source-root constants for a CI checkout. The underlying
census is read-only and does not modify identity registries or canonical data.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

source_root = Path(os.environ["FRL_PL_ROOT"]).resolve()
if not source_root.is_dir():
    raise FileNotFoundError(f"Source archive not found: {source_root}")

import match_stats  # noqa: E402
import player_match_stats  # noqa: E402

match_stats.PL_ROOT = str(source_root)
player_match_stats.PL_ROOT = source_root

import player_identity_audit  # noqa: E402

player_identity_audit.PL_ROOT = source_root

import source_family_adapters  # noqa: E402

source_family_adapters.PL_ROOT = str(source_root)

from audit_unresolved_player_match_canonical_evidence import classify, print_report  # noqa: E402


if __name__ == "__main__":
    print_report(classify())
