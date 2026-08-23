"""Inspect cached live team stats vs team leaderboard aggregation context.

Evidence-only. Reads the existing local cache when run locally; no network and no semantic promotion.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "data" / "live_pl_api_cache"
TARGETS = [
    "goalConversion","ownGoalsAccrued","pointsDroppedFromWinningPositions",
    "pointsGainedFromLosingPositions","shotsOnConcededInsideBox",
    "shotsOnConcededOutsideBox","successfulOpenPlayPasses","totalShotsConceded",
    "unsuccessfulPassesOppositionHalf"
]
ENDPOINTS=["team_leaderboard","team_stats"]

def walk(v,p=""):
    if isinstance(v,dict):
        for k,c in v.items():
            q=f"{p}.{k}" if p else k
            yield q,c
            yield from walk(c,q)
    elif isinstance(v,list) and v and isinstance(v[0],dict):
        yield from walk(v[0],p+"[]")

def main():
    print("FRL TEAM STATS AGGREGATION SCOPE EVIDENCE")
    print("="*90)
    for ep in ENDPOINTS:
        path=CACHE/f"{ep}.json"
        if not path.exists():
            print(f"{ep}: CACHE_MISSING")
            continue
        payload=json.loads(path.read_text(encoding="utf-8"))["payload"]
        print(f"\n[{ep}]")
        if ep=="team_leaderboard":
            root=payload.get("data") if isinstance(payload,dict) else None
            if isinstance(root,list):
                for i,row in enumerate(root[:3]):
                    keys=sorted(row.keys()) if isinstance(row,dict) else []
                    print(f"row[{i}] keys={keys}")
                    if isinstance(row,dict):
                        for k in ("team","id","name","season","stats"):
                            if k in row:
                                print(f"  {k}: {repr(row[k])[:300]}")
        else:
            if isinstance(payload,dict):
                print(f"root keys={sorted(payload.keys())}")
                for k in ("team","id","season","stats","competitions","data"):
                    if k in payload:
                        print(f"  {k}: {repr(payload[k])[:500]}")
        hits=[]
        for q,c in walk(payload):
            term=q.replace('[]','').split('.')[-1]
            if term in TARGETS:
                hits.append((q,c))
        for q,c in hits:
            print(f"  FIELD {q} => {type(c).__name__}: {repr(c)[:180]}")

if __name__=="__main__":
    main()
