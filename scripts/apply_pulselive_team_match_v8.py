from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pulselive_team_stat_semantics import PULSELIVE_TEAM_STAT_FIELDS


REGISTRY = ROOT / "source_field_registry.py"
INVENTORY = ROOT / "variable_capability_inventory.py"


def _replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def _update_source_registry() -> bool:
    text = REGISTRY.read_text(encoding="utf-8-sig")
    original = text

    if "TEAM_PROMOTION_BATCH_V8_FIELDS" not in text:
        lines = ["TEAM_PROMOTION_BATCH_V8_FIELDS = {"]
        for field in sorted(PULSELIVE_TEAM_STAT_FIELDS):
            lines.append(f'    "{field}": "exposed",')
        lines.extend(["}", "", ""])
        block = "\n".join(lines)
        marker = "# The final packaged residue is governed explicitly rather than left uncatalogued."
        if marker not in text:
            raise RuntimeError("source_field_registry.py: V8 insertion marker not found")
        text = text.replace(marker, block + marker, 1)

    union_old = "        | TEAM_PROMOTION_BATCH_V7_FIELDS\n        | TEAM_EXCEPTION_FIELDS,"
    union_new = "        | TEAM_PROMOTION_BATCH_V7_FIELDS\n        | TEAM_PROMOTION_BATCH_V8_FIELDS\n        | TEAM_EXCEPTION_FIELDS,"
    if "| TEAM_PROMOTION_BATCH_V8_FIELDS" not in text:
        text = _replace_once(text, union_old, union_new, "source registry union")

    if text != original:
        compile(text, str(REGISTRY), "exec")
        REGISTRY.write_text(text, encoding="utf-8", newline="")
        return True
    return False


def _update_inventory_generator() -> bool:
    text = INVENTORY.read_text(encoding="utf-8-sig")
    original = text

    if "from functools import lru_cache" not in text:
        text = _replace_once(
            text,
            "import json\nimport re\n",
            "import json\nimport re\nfrom functools import lru_cache\n",
            "inventory lru_cache import",
        )

    import_anchor = "from variable_resolver import ALIASES\n"
    extra_imports = (
        "from pulselive_team_stat_semantics import (\n"
        "    PULSELIVE_TEAM_CONTEXT_PATH_MEANINGS,\n"
        "    PULSELIVE_TEAM_STAT_MEANINGS,\n"
        ")\n"
        "from source_field_registry import fields_for_family\n"
    )
    if "PULSELIVE_TEAM_STAT_MEANINGS" not in text.split("FIELD_MEANINGS", 1)[0]:
        text = _replace_once(text, import_anchor, import_anchor + extra_imports, "inventory semantic imports")

    old_infra = '''    return (\n        ".headers" in field\n        or field.endswith(".endpoint")\n        or ".params" in field\n        or field.endswith(".status_code")\n        or field in {"retrieved_at", "source", "source_match_id", "resources"}\n    )\n'''
    new_infra = '''    return (\n        ".headers" in field\n        or field.endswith(".endpoint")\n        or ".params" in field\n        or field.endswith(".status_code")\n        or field.endswith(".retrieved_at")\n        or field in {\n            "retrieved_at", "source", "source_match_id", "resources",\n            "resources.stats", "resources.stats.payload", "resources.stats.payload[].stats",\n        }\n    )\n'''
    if "resources.stats.payload[].stats\"" not in text.split("def _fpl_family_and_grain", 1)[0]:
        text = _replace_once(text, old_infra, new_infra, "PulseLive infrastructure classification")

    old_meaning = '''def _meaning(row: dict[str, str], family: str) -> dict[str, str]:\n    field = row.get("field_name", "")\n    leaf = re.sub(r"\\[\\]", "", field).split(".")[-1]\n    if family == "infrastructure":\n        return {"status": "ESTABLISHED", "text": "Acquisition or provenance metadata; not football performance evidence."}\n    if field in FIELD_MEANINGS:\n        return {"status": "ESTABLISHED", "text": FIELD_MEANINGS[field]}\n    if leaf in FIELD_MEANINGS:\n        return {"status": "ESTABLISHED", "text": FIELD_MEANINGS[leaf]}\n    category = row.get("navigation_subcategory") or row.get("navigation_category") or "unclassified football evidence"\n    return {\n        "status": "REVIEW_REQUIRED",\n        "text": f"Source-native field '{field}' associated with {category}; its exact provider definition has not been separately approved by FRL.",\n    }\n'''

    new_meaning = '''@lru_cache(maxsize=1)\ndef _fpl_research_exposed_fields() -> frozenset[str]:\n    return frozenset(str(item.get("field_name") or "") for item in fpl_catalogue())\n\n\n@lru_cache(maxsize=1)\ndef _governed_team_semantic_statuses() -> dict[str, str]:\n    return {spec.source_field: spec.semantic_status for spec in fields_for_family("team_match")}\n\n\ndef _meaning(row: dict[str, str], family: str) -> dict[str, str]:\n    field = row.get("field_name", "")\n    leaf = re.sub(r"\\[\\]", "", field).split(".")[-1]\n    surface = row.get("source_surface", "")\n    semantic_status = str(row.get("semantic_status") or "").strip().lower()\n\n    if family == "infrastructure":\n        return {"status": "ESTABLISHED", "text": "Acquisition or provenance metadata; not football performance evidence."}\n    if field in FIELD_MEANINGS:\n        return {"status": "ESTABLISHED", "text": FIELD_MEANINGS[field]}\n    if leaf in FIELD_MEANINGS:\n        return {"status": "ESTABLISHED", "text": FIELD_MEANINGS[leaf]}\n\n    if semantic_status in {"exposed", "derived"}:\n        return {\n            "status": "ESTABLISHED",\n            "text": f"FRL-governed source-native field '{field}'; its provider-native identity is preserved without relabelling.",\n        }\n\n    if surface == "fpl" and field in _fpl_research_exposed_fields():\n        return {\n            "status": "ESTABLISHED",\n            "text": f"FPL source-native field '{field}' explicitly approved by the authoritative FPL research registry.",\n        }\n\n    if surface == "pulselive":\n        context_meaning = PULSELIVE_TEAM_CONTEXT_PATH_MEANINGS.get(field)\n        if context_meaning:\n            return {"status": "ESTABLISHED", "text": context_meaning}\n\n        if field.startswith("resources.stats.payload[].stats."):\n            explicit_meaning = PULSELIVE_TEAM_STAT_MEANINGS.get(leaf)\n            if explicit_meaning:\n                return {"status": "ESTABLISHED", "text": explicit_meaning}\n            team_status = _governed_team_semantic_statuses().get(leaf, "")\n            if team_status in {"exposed", "derived"}:\n                return {\n                    "status": "ESTABLISHED",\n                    "text": f"PulseLive Team-Match field '{leaf}' reuses the same governed provider-native Team-Match concept already approved by FRL.",\n                }\n\n    category = row.get("navigation_subcategory") or row.get("navigation_category") or "unclassified football evidence"\n    return {\n        "status": "REVIEW_REQUIRED",\n        "text": f"Source-native field '{field}' associated with {category}; its exact provider definition has not been separately approved by FRL.",\n    }\n'''

    if "def _governed_team_semantic_statuses" not in text:
        text = _replace_once(text, old_meaning, new_meaning, "inventory meaning reconciliation")

    # V9 structural/context reconciliation. These are source-role classifications,
    # not new cross-provider football-stat equivalence claims.
    category_marker = '    category = row.get("navigation_subcategory") or row.get("navigation_category") or "unclassified football evidence"\n'
    if "FPL rules/configuration/context field" not in text:
        structural = '''    resource = row.get("resource", "")\n\n    if surface == "fpl" and resource == "bootstrap-static.json":\n        return {\n            "status": "ESTABLISHED",\n            "text": f"FPL rules/configuration/context field '{field}'; preserved as source configuration rather than a football performance metric.",\n        }\n\n    if surface == "pulselive":\n        if field == "resources.stats.payload[].teamId":\n            return {\n                "status": "ESTABLISHED",\n                "text": "PulseLive source team identifier attaching one Team-Match statistics payload to its fixture team; identity context rather than a performance measure.",\n            }\n        if field.startswith("resources.events"):\n            return {\n                "status": "ESTABLISHED",\n                "text": f"PulseLive source-native fixture-event structure field '{field}'; event identity/timing/type semantics are preserved without asserting cross-provider equivalence.",\n            }\n        if field.startswith("resources.lineups"):\n            return {\n                "status": "ESTABLISHED",\n                "text": f"PulseLive source-native lineup/formation/manager context field '{field}'; preserved as fixture context rather than a scalar performance metric.",\n            }\n        if field.startswith("resources.commentary"):\n            return {\n                "status": "ESTABLISHED",\n                "text": f"PulseLive source-native commentary structure field '{field}'; preserved as match-centre narrative/pagination context rather than a performance metric.",\n            }\n        if field.startswith("resources.match"):\n            return {\n                "status": "ESTABLISHED",\n                "text": f"PulseLive source-native fixture context field '{field}'; preserved as match identity/state/context without asserting cross-provider equivalence.",\n            }\n\n'''
        if category_marker not in text:
            raise RuntimeError("variable_capability_inventory.py: V9 structural insertion marker not found")
        text = text.replace(category_marker, structural + category_marker, 1)

    if text != original:
        compile(text, str(INVENTORY), "exec")
        INVENTORY.write_text(text, encoding="utf-8", newline="")
        return True
    return False


def main() -> int:
    registry_changed = _update_source_registry()
    inventory_changed = _update_inventory_generator()

    from variable_capability_inventory import write_inventory

    inventory = write_inventory(ROOT)
    variables = inventory["variables"]
    review = [row for row in variables if row["football_meaning"]["status"] == "REVIEW_REQUIRED"]
    by_surface = Counter(row["source"]["surface"] for row in review)
    pulse_team_review = [
        row for row in review
        if row["source"]["surface"] == "pulselive"
        and row["source"]["native_fields"]
        and str(row["source"]["native_fields"][0]).startswith("resources.stats")
    ]

    print(f"source_field_registry.py changed: {registry_changed}")
    print(f"variable_capability_inventory.py changed: {inventory_changed}")
    print(f"V8 atomic PulseLive Team-Match fields governed: {len(PULSELIVE_TEAM_STAT_FIELDS)}")
    print(f"Current REVIEW_REQUIRED meanings after regeneration: {len(review)}")
    print("Remaining REVIEW_REQUIRED by source surface:")
    for key, value in by_surface.most_common():
        print(f"  {key}: {value}")
    print(f"Remaining PulseLive resources.stats REVIEW_REQUIRED paths: {len(pulse_team_review)}")
    for row in pulse_team_review[:50]:
        print(f"  {row['source']['native_fields'][0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
