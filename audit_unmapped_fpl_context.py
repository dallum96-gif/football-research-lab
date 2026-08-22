"""Read-only audit of the 285 currently unmapped variables by FPL structural context.

Evidence-first only. Consumes the local unmapped-variable profile and the source
universe/dictionary. It distinguishes structural context classes from canonical
entity attachment and never infers identity joins.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
PROFILE = DATA / "unmapped_variable_grain_profile.csv"
UNIVERSE = DATA / "master_variable_universe_decomposed.csv"
OUT = DATA / "unmapped_fpl_context_audit.csv"


def load(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def structural_class(row: dict[str, str]) -> str:
    surface = (row.get("source_surface") or "").lower()
    resource = (row.get("resource") or "").lower()
    field = (row.get("field_name") or "").lower()
    samples = (row.get("sample_values") or "").lower()

    if surface != "fpl":
        return "LOCAL_SOURCE_METADATA_REVIEW"

    if "bootstrap-static.json" in resource:
        if "chips" in field or "chip_type" in field or "overrides" in field:
            return "FPL_GAME_CONFIG_METADATA"
        if "events" in field or field.startswith("events"):
            return "FPL_GAMEWEEK_METADATA"
        return "FPL_BOOTSTRAP_STRUCTURAL_METADATA"

    if "element" in resource:
        if "fixtures" in field or "history" in field:
            return "FPL_ELEMENT_PLAYER_CONTEXT"
        return "FPL_ELEMENT_STRUCTURAL_METADATA"

    return "FPL_STRUCTURAL_REVIEW"


def main() -> list[dict[str, str]]:
    profile = load(PROFILE)
    universe = {r.get("field_name", ""): r for r in load(UNIVERSE)}

    rows = []
    for p in profile:
        field = p.get("field_name", "")
        u = universe.get(field, {})
        merged = dict(p)
        merged.update({
            "universe_resource": u.get("resource", ""),
            "universe_source_surface": u.get("source_surface", ""),
            "universe_grain": u.get("grain", ""),
        })
        merged["structural_class"] = structural_class({
            **p,
            "field_name": field,
            "resource": u.get("resource", p.get("resource", "")),
            "source_surface": u.get("source_surface", p.get("source_surface", "")),
        })
        merged["canonical_entity_status"] = "REVIEW_REQUIRED"
        merged["reason"] = (
            "Structural FPL context may explain the variable's parent object, but no canonical "
            "player/fixture/club identity route is inferred by this audit."
        )
        rows.append(merged)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    cols = [
        "field_name", "source_surface", "resource", "decomposition_basis",
        "universe_resource", "universe_source_surface", "universe_grain",
        "structural_class", "canonical_entity_status", "reason",
    ]
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        for row in rows:
            writer.writerow({c: row.get(c, "") for c in cols})
    return rows


if __name__ == "__main__":
    rows = main()
    counts = Counter(r["structural_class"] for r in rows)
    print("FRL UNMAPPED FPL STRUCTURAL CONTEXT AUDIT")
    print("=" * 100)
    print(f"Variables audited: {len(rows)}")
    for k, v in counts.most_common():
        print(f"  {v:5d}  {k}")
    print(f"Output: {OUT}")
    print("Evidence-only structural classification; canonical identity attachment remains review-only.")
