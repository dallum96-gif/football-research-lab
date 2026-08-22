"""Build a conservative Player-Season capability map from live discovery evidence.

Evidence-first only. Uses the existing live player-season semantic decision and
inspection artefacts plus the FRL variable dictionary. No canonical promotion.
"""
from __future__ import annotations
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DECISIONS = ROOT / "data" / "player_season_semantic_decisions.csv"
INSPECTION = ROOT / "data" / "player_season_candidate_inspection.csv"
DICTIONARY = ROOT / "data" / "frl_variable_dictionary.csv"
OUTPUT = ROOT / "data" / "player_season_capability_map.csv"

FAMILY_PREFIXES = {
    "Finishing & Goals": ("goal", "expected", "penalt", "shots"),
    "Passing & Territory": ("pass", "openplay", "layoff", "launch"),
    "Crossing & Set Pieces": ("cross", "corner"),
    "Defending": ("tackle", "interception", "block", "clear", "save"),
    "Duels & Aerials": ("duel", "aerial"),
    "Dribbling": ("drib",),
    "Possession & Involvement": ("touch", "appearance", "start", "games"),
    "Discipline & Offside": ("card", "foul", "offside"),
}

def family(field: str) -> str:
    low = field.lower()
    for name, prefixes in FAMILY_PREFIXES.items():
        if any(low.startswith(p) for p in prefixes):
            return name
    return "Review"

def load_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))

def run() -> list[dict[str, str]]:
    decisions = load_rows(DECISIONS)
    inspection = load_rows(INSPECTION)
    dictionary = load_rows(DICTIONARY)
    dict_fields = {r.get("field_name", r.get("field", r.get("variable", r.get("name", "")))) for r in dictionary}
    inspect_by_field: dict[str, dict[str, str]] = {}
    for r in inspection:
        field = r.get("field_name", "")
        if field and field not in inspect_by_field:
            inspect_by_field[field] = r

    out=[]
    for d in decisions:
        field=d.get("field_name", "")
        if not field:
            continue
        semantic=d.get("semantic_status", d.get("decision", ""))
        source_endpoints=d.get("endpoints", d.get("endpoint", ""))
        if semantic == "PLAYER_SEASON_EQUIVALENT_REVIEW":
            status = "FRL_PLAYER_SEASON_COVERAGE_REVIEW"
        elif semantic == "MIXED_GRAIN_REVIEW":
            status = "MIXED_GRAIN_REVIEW"
        else:
            status = semantic or "REVIEW"
        r=inspect_by_field.get(field,{})
        out.append({
            "field_name": field,
            "family": family(field),
            "field_type": r.get("field_type", ""),
            "sample_values": r.get("sample_values", r.get("sample", "")),
            "live_endpoints": source_endpoints,
            "semantic_decision": semantic,
            "frl_exact_dictionary_name_match": "TRUE" if field in dict_fields else "FALSE",
            "capability_status": status,
        })
    out.sort(key=lambda x:(x["family"], x["field_name"]))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        cols=list(out[0]) if out else ["field_name"]
        w=csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(out)
    return out

if __name__ == "__main__":
    rows=run()
    totals: dict[str,int]={}
    for r in rows:
        totals[r["capability_status"]]=totals.get(r["capability_status"],0)+1
    print("FRL PLAYER-SEASON CAPABILITY MAP")
    print("="*90)
    print(f"Analytical concepts mapped: {len(rows)}")
    for k,v in sorted(totals.items(), key=lambda x:(-x[1],x[0])):
        print(f"  {v:4d}  {k}")
    print(f"Output: {OUTPUT}")
    print("Evidence-first capability mapping only; no semantic/canonical promotion.")
