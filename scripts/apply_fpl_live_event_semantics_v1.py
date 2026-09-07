from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

INVENTORY = ROOT / "variable_capability_inventory.py"


def _replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def _update_inventory_generator() -> bool:
    text = INVENTORY.read_text(encoding="utf-8-sig")
    original = text

    anchor = '''    if surface == "fpl" and field in _fpl_research_exposed_fields():\n        return {\n            "status": "ESTABLISHED",\n            "text": f"FPL source-native field '{field}' explicitly approved by the authoritative FPL research registry.",\n        }\n\n'''

    addition = '''    if surface == "fpl" and field in _fpl_research_exposed_fields():\n        return {\n            "status": "ESTABLISHED",\n            "text": f"FPL source-native field '{field}' explicitly approved by the authoritative FPL research registry.",\n        }\n\n    # The live gameweek endpoint is another FPL representation of many metrics\n    # already approved on bootstrap-static / element-summary surfaces. Reuse only\n    # an exact source-native metric leaf; do not assert Opta/provider equivalence.\n    if surface == "fpl" and row.get("resource") == "event":\n        if field.startswith("elements[].stats."):\n            metric = leaf\n            approved_metric = any(\n                candidate.endswith(f".{metric}")\n                for candidate in _fpl_research_exposed_fields()\n            )\n            if approved_metric:\n                return {\n                    "status": "ESTABLISHED",\n                    "text": f"FPL live-gameweek metric '{metric}' reuses the same FPL source-native metric name already approved on another FPL representation.",\n                }\n\n        if (\n            field in {\n                "elements",\n                "elements[].id",\n                "elements[].modified",\n                "elements[].stats",\n                "elements[].explain",\n            }\n            or field.startswith("elements[].explain[].")\n        ):\n            return {\n                "status": "ESTABLISHED",\n                "text": f"FPL live-gameweek scoring/context structure '{field}'; preserved as source-native gameweek context rather than a standalone football metric.",\n            }\n\n'''

    if "FPL live-gameweek metric" not in text:
        text = _replace_once(text, anchor, addition, "FPL live event semantic insertion")

    if text != original:
        compile(text, str(INVENTORY), "exec")
        INVENTORY.write_text(text, encoding="utf-8", newline="")
        return True
    return False


def _native(row: dict) -> str:
    fields = row.get("source", {}).get("native_fields", [])
    return str(fields[0]) if fields else ""


def main() -> int:
    changed = _update_inventory_generator()

    from variable_capability_inventory import write_inventory

    inventory = write_inventory(ROOT)
    review = [
        row for row in inventory["variables"]
        if row["football_meaning"]["status"] == "REVIEW_REQUIRED"
    ]
    by_surface = Counter(row["source"]["surface"] for row in review)
    fpl_event = [
        row for row in review
        if row["source"]["surface"] == "fpl"
        and row["source"]["resource"] == "event"
    ]

    print(f"variable_capability_inventory.py changed: {changed}")
    print(f"Current REVIEW_REQUIRED meanings: {len(review)}")
    print("Remaining REVIEW_REQUIRED by source surface:")
    for key, value in by_surface.most_common():
        print(f"  {key}: {value}")
    print(f"Remaining FPL live-event REVIEW_REQUIRED rows: {len(fpl_event)}")
    for row in fpl_event:
        print(f"  {_native(row)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
