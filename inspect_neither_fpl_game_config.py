"""Inspect unresolved game_config.* FPL bootstrap fields.

Read-only audit; no grain or canonical promotion.
"""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent
TRIAGE=ROOT/"data"/"neither_fpl_bootstrap_triage.csv"
OUTPUT=ROOT/"data"/"neither_fpl_game_config_inspection.csv"
def load_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))
def subpath(field_name):
    text=field_name or ""
    return text[len("game_config."):] if text.startswith("game_config.") else text
def classify_role(field_name):
    path=subpath(field_name)
    if path.startswith("scoring."): return "SCORING_CONFIGURATION", "game_config scoring rule"
    if path.startswith("settings."): return "GAME_SETTINGS", "game_config setting"
    if path.startswith("elements.") or path.startswith("players."): return "PLAYER_CONFIGURATION", "game_config player-related configuration"
    if path.startswith("teams."): return "TEAM_CONFIGURATION", "game_config team-related configuration"
    if path.startswith("fixtures."): return "FIXTURE_CONFIGURATION", "game_config fixture-related configuration"
    if "." in path: return "NESTED_CONFIGURATION", "nested game_config property"
    return "GAME_CONFIGURATION", "top-level game_config property"
def inspect(rows):
    out=[]
    for row in rows:
        if row.get("triage_status")!="OBJECT_FAMILY_CANDIDATE" or row.get("path_root")!="game_config": continue
        role,basis=classify_role(row.get("field_name",""))
        out.append({"field_name":row.get("field_name",""),"subpath":subpath(row.get("field_name","")),"field_type":row.get("field_type",""),"object_family_candidate":row.get("object_family_candidate",""),"configuration_role":role,"classification_basis":basis,"review_status":"OPEN","resolution":""})
    return out
def run():
    rows=inspect(load_csv(TRIAGE))
    if not rows: raise ValueError("No open game_config rows found in triage input.")
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    cols=list(rows[0].keys())
    with OUTPUT.open("w",encoding="utf-8-sig",newline="") as fh:
        writer=csv.DictWriter(fh,fieldnames=cols); writer.writeheader(); writer.writerows(rows)
    roles=Counter(r["configuration_role"] for r in rows); types=Counter(r["field_type"] for r in rows)
    print("FRL NEITHER-LAYER FPL GAME_CONFIG INSPECTION")
    print("="*80); print(f"game_config fields inspected: {len(rows)}")
    print("CONFIGURATION ROLES")
    for k,v in roles.most_common(): print(f"  {k:28s} {v}")
    print("FIELD TYPES")
    for k,v in types.most_common(): print(f"  {k:28s} {v}")
    print(f"Output: {OUTPUT}")
    print("Configuration metadata only; no grain or canonical promotion.")
    return len(rows)
if __name__=="__main__": run()
