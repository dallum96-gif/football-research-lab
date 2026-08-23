from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path.cwd()
CACHE = ROOT / "data" / "live_pl_api_cache"
TARGETS = {"player_season_stats.json", "player_leaderboard.json"}
TERMS = ("player_season_stats", "player_leaderboard", "player.id", "season", "comp", "competition", "playerId", "element")


def scan_text(path: Path):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        if any(term.lower() in line.lower() for term in TERMS):
            hits.append((i, line.strip()[:300]))
    return hits


def walk_json(obj, prefix=""):
    out=[]
    if isinstance(obj, dict):
        for k,v in obj.items():
            p=f"{prefix}.{k}" if prefix else k
            if any(t.lower() in k.lower() for t in ("url","uri","endpoint","path","season","comp","competition","player","id")):
                if not isinstance(v,(dict,list)):
                    out.append((p, repr(v)[:300]))
            out.extend(walk_json(v,p))
    elif isinstance(obj, list):
        for i,v in enumerate(obj[:20]):
            out.extend(walk_json(v,f"{prefix}[{i}]"))
    return out


def main():
    print("="*96)
    print("FRL PLAYER-SEASON ENDPOINT CONTEXT AUDIT")
    print("="*96)
    print(f"Workspace: {ROOT}")
    print()

    print("CACHE CONTEXT")
    for name in sorted(TARGETS):
        p=CACHE/name
        print(f"  {name}: exists={p.exists()}")
        if p.exists():
            try:
                obj=json.loads(p.read_text(encoding="utf-8-sig"))
                print(f"    top_keys={list(obj) if isinstance(obj,dict) else type(obj).__name__}")
                for key,val in walk_json(obj):
                    print(f"    {key} = {val}")
            except Exception as exc:
                print(f"    JSON_READ_ERROR={exc}")
    print()

    print("CODE / CONFIG CONTEXT")
    files=[]
    for pattern in ("*.py","*.md","*.json","*.yaml","*.yml","*.ini","*.txt"):
        files.extend(ROOT.rglob(pattern))
    seen=set()
    for p in sorted(files):
        if p in seen or "__pycache__" in p.parts or ".git" in p.parts:
            continue
        seen.add(p)
        hits=scan_text(p)
        if hits:
            print(f"  {p.relative_to(ROOT)}")
            for line_no,line in hits[:25]:
                print(f"    L{line_no}: {line}")
            if len(hits)>25:
                print(f"    ... {len(hits)-25} additional hits")
    print()
    print("INTERPRETATION")
    print("  This audit only inventories existing endpoint/request/temporal evidence.")
    print("  It does not infer Pulselive player.id -> FPL element or create identity mappings.")
    print("="*96)

if __name__ == "__main__":
    main()
