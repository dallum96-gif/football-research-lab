"""Local-first, read-only discovery of Squad source materialisation.

Searches the audit root for candidate JSON/CSV source artefacts containing the
16 declared Squad fields or likely squad/player-profile keys. It does not infer
identity, create joins, or promote any relationship.
"""
from __future__ import annotations

import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "squad_source_materialisation_frontier.csv"
TARGETS = {
    "playerId", "displayName", "firstName", "lastName", "shirtNumber", "position",
    "preferredFoot", "nationality", "isoCode", "birthDate", "birthCountry", "age",
    "height_cm", "weight_kg", "joinDate", "onLoan",
}
LIKELY_KEYS = {"playerId", "player_id", "id", "name", "displayName", "team_id", "teamId", "season", "players", "squad", "elements"}

def json_keys(obj):
    keys = set()
    stack = [obj]
    while stack:
        x = stack.pop()
        if isinstance(x, dict):
            keys.update(map(str, x.keys()))
            stack.extend(x.values())
        elif isinstance(x, list):
            stack.extend(x[:20])
    return keys

def main():
    rows=[]
    for p in ROOT.rglob("*"):
        if not p.is_file() or p.name.startswith("."):
            continue
        rel=p.relative_to(ROOT)
        if "__pycache__" in rel.parts or "data" in rel.parts and p.suffix not in {".json", ".csv"}:
            continue
        suffix=p.suffix.lower()
        try:
            if suffix==".json":
                with p.open("r",encoding="utf-8") as f: obj=json.load(f)
                keys=json_keys(obj)
                hits=sorted(TARGETS & keys)
                likely=sorted(LIKELY_KEYS & keys)
                if hits or (len(likely)>=3 and ("playerId" in keys or "players" in keys or "squad" in keys)):
                    rows.append({"path":str(rel),"type":"json","target_field_hits":";".join(hits),"likely_key_hits":";".join(likely)})
            elif suffix==".csv":
                with p.open("r",encoding="utf-8-sig",newline="") as f:
                    r=csv.reader(f); header=next(r,[])
                hits=sorted(TARGETS & set(header)); likely=sorted(LIKELY_KEYS & set(header))
                if hits or (len(likely)>=3 and ("playerId" in likely or "players" in likely or "squad" in likely)):
                    rows.append({"path":str(rel),"type":"csv","target_field_hits":";".join(hits),"likely_key_hits":";".join(likely)})
        except Exception:
            continue
    rows.sort(key=lambda r:(-len(r["target_field_hits"].split(";") if r["target_field_hits"] else []), r["path"]))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["path","type","target_field_hits","likely_key_hits"]); w.writeheader(); w.writerows(rows)
    print("FRL SQUAD SOURCE MATERIALISATION FRONTIER")
    print("="*100)
    print(f"Candidate files: {len(rows)}")
    for r in rows[:40]:
        print(f"{r['type'].upper():4} {r['path']} :: targets={r['target_field_hits'] or '-'} :: keys={r['likely_key_hits'] or '-'}")
    print(f"Output: {OUT}")
    print("Evidence-only local source discovery; no identity inference and no contract promotion.")

if __name__ == "__main__": main()
