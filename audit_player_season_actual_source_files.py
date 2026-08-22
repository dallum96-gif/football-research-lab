from __future__ import annotations
import csv
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'data'/'player_season_actual_source_identity_inventory.csv'

def read_header(path: Path):
    try:
        with path.open(encoding='utf-8-sig', newline='') as f:
            r=csv.reader(f)
            return next(r, [])
    except Exception:
        return []

def is_candidate(path: Path, header: list[str]) -> bool:
    if path.name.startswith('.'):
        return False
    low={h.strip().lower() for h in header}
    # Require actual player-season/stat content signals; explicitly exclude known schema/audit/catalog outputs.
    if 'playername' not in low and 'player_name' not in low and 'name' not in low:
        return False
    stat_signals={'goals','totalshots','gamesplayed','minutes','assists','team_code','source_player_id','fpl_element'}
    if not (low & stat_signals):
        return False
    bad_tokens=('schema','universe','classification','audit','coverage','catalog','dictionary','capability')
    return not any(t in str(path).lower() for t in bad_tokens)

def main():
    rows=[]
    for p in ROOT.rglob('*.csv'):
        if 'data' + str(p).split('data',1)[-1] and any(x in p.parts for x in ('.git','node_modules')):
            continue
        header=read_header(p)
        if not header or not is_candidate(p, header):
            continue
        low={h.strip().lower():h.strip() for h in header}
        identity=[low[k] for k in ('source_player_id','player_id','playerid','fpl_element') if k in low]
        names=[low[k] for k in ('playername','player_name','name') if k in low]
        teams=[low[k] for k in ('team_code','team_id','team') if k in low]
        seasons=[low[k] for k in ('season','season_name') if k in low]
        rows.append({'path':str(p.relative_to(ROOT)),'columns':len(header),'identity_columns':'|'.join(identity),'name_columns':'|'.join(names),'team_columns':'|'.join(teams),'season_columns':'|'.join(seasons)})
    rows.sort(key=lambda x:x['path'])
    print('FRL PLAYER-SEASON ACTUAL SOURCE FILE AUDIT')
    print('='*100)
    print(f'Candidate actual source files: {len(rows)}')
    for r in rows[:100]:
        print(f"  {r['path']} :: identity={r['identity_columns'] or '-'} :: names={r['name_columns'] or '-'} :: teams={r['team_columns'] or '-'} :: season={r['season_columns'] or '-'}")
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['path','columns','identity_columns','name_columns','team_columns','season_columns'])
        w.writeheader(); w.writerows(rows)
    print('Output:',OUT)
    print('Evidence-only source-file discovery; no identity inference and no contract promotion.')

if __name__=='__main__': main()
