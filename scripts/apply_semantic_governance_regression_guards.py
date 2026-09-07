from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST = ROOT / "tests" / "test_variable_capability_inventory.py"


def _replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def _update_test() -> bool:
    text = TEST.read_text(encoding="utf-8-sig")
    original = text

    old = '''    review = rows["catalogue:fpl:bootstrap-static.json:sample_payload:chips"]\n    assert review["football_meaning"]["status"] == "REVIEW_REQUIRED"\n    assert "review" in inventory_unknown_policy().casefold()\n'''
    new = '''    config = rows["catalogue:fpl:bootstrap-static.json:sample_payload:chips"]\n    assert config["football_meaning"]["status"] == "ESTABLISHED"\n    assert config["capability_family"] == "context"\n    assert "rules/configuration/context" in config["football_meaning"]["text"]\n    assert "review" in inventory_unknown_policy().casefold()\n'''
    if old in text:
        text = _replace_once(text, old, new, "FPL configuration regression")

    test_name = "test_semantic_governance_reconciliation_preserves_intentional_fail_closed_residue"
    if test_name not in text:
        block = '''\n\ndef test_semantic_governance_reconciliation_preserves_intentional_fail_closed_residue():\n    inventory = build_inventory()\n    variables = inventory["variables"]\n\n    def catalogue_row(surface: str, resource: str, field: str) -> dict:\n        return next(\n            row\n            for row in variables\n            if row["record_id"].startswith("catalogue:")\n            and row["source"]["surface"] == surface\n            and row["source"]["resource"] == resource\n            and row["canonical_name"] == field\n        )\n\n    exposed = catalogue_row("FRL_LOCAL_CSV", "player_season", "leftsidePasses")\n    assert exposed["governance"]["semantic_status"] == "exposed"\n    assert exposed["football_meaning"]["status"] == "ESTABLISHED"\n\n    retained = catalogue_row("FRL_LOCAL_CSV", "player_season", "blocks")\n    assert retained["governance"]["semantic_status"] == "retained"\n    assert retained["football_meaning"]["status"] == "REVIEW_REQUIRED"\n\n    restricted = catalogue_row("FRL_LOCAL_CSV", "player_season", "unsuccessfulDribbles")\n    assert restricted["governance"]["semantic_status"] == "restricted"\n    assert restricted["football_meaning"]["status"] == "REVIEW_REQUIRED"\n\n    pulselive_exception = catalogue_row(\n        "pulselive", "match", "resources.stats.payload[].stats.freekickTotal"\n    )\n    assert pulselive_exception["football_meaning"]["status"] == "REVIEW_REQUIRED"\n'''
        text = text.rstrip() + block + "\n"

    if text != original:
        compile(text, str(TEST), "exec")
        TEST.write_text(text, encoding="utf-8", newline="")
        return True
    return False


def main() -> int:
    changed = _update_test()
    print(f"tests/test_variable_capability_inventory.py changed: {changed}")
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        r"tests\test_variable_capability_inventory.py",
        "--disable-warnings",
    ]
    result = subprocess.run(command, cwd=ROOT)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
