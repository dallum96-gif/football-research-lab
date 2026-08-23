from __future__ import annotations
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
OUT = DATA / 'player_season_live_identity_shape.csv'
CANDIDATES = [
    DATA / 'live_pl_api_cache' / 'player_season_stats.json',
    DATA / 'live_pl_api_cache' / 'player_leaderboard.json',
]

def walk(obj, path=''):
    rows=[]
    if isinstance(obj, dict):
        for k,v in obj.items():
            p=f'{path}.{k}' if path else k
            rows.append((p,type(v).__name__,v if not isinstance(v,(dict,list)) else None))
            rows.extend(walk(v,p))
    elif isinstance(obj,list):
        for i,v in enumerate(obj[:5]):
            rows.extend(walk(v,f'{path}[{i}]'))
    return rows

def main():
    print('FRL PLAYER-SEASON LIVE IDENTITY SHAPE AUDIT')
    print('='*100)
    found=False
    for path in CANDIDATES:
        print(f'FILE: {path}')
        if not path.exists():
            print('  EXISTS=False')
            continue
        found=True
        data=json.loads(path.read_text(encoding='utf-8'))
        print(f'  EXISTS=True type={type(data).__name__}')
        if isinstance(data,dict): print(f'  TOP_KEYS={list(data.keys())[:50]}')
        elif isinstance(data,list): print(f'  LIST_LENGTH={len(data)}')
        rows=walk(data)
        interesting=[]
        for p,t,v in rows:
            low=p.lower()
            if any(x in low for x in ('player','element','team','season','name','id','stats')):
                interesting.append((p,t,'' if v is None else str(v)))
        for p,t,v in interesting[:120]:
            print(f'  {p} :: {t} :: {v}')
    if not found:
        print('NO_LOCAL_PLAYER_SEASON_CACHE_FOUND')
    print('Output:', OUT)
    OUT.write_text('field_path,observed_type,sample_value\n', encoding='utf-8-sig')
    print('Evidence-only live-shape inspection; no identity inference and no contract promotion.')

if __name__=='__main__':
    main()
