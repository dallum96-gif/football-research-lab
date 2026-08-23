from __future__ import annotations
import csv, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
CACHE=ROOT/'data'/'live_pl_api_cache'
REG=ROOT/'player_identity_registry.csv'
OUT=ROOT/'data'/'player_season_live_identity_crosswalk.csv'

def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def norm(v): return str(v or '').strip()

def main():
    reg=read_csv(REG)
    by_id={norm(r.get('source_player_id')):r for r in reg if norm(r.get('source_player_id'))}
    ps=json.loads((CACHE/'player_season_stats.json').read_text(encoding='utf-8'))
    pl=json.loads((CACHE/'player_leaderboard.json').read_text(encoding='utf-8'))
    samples=[]
    p=ps.get('payload',{}).get('player') or {}
    if p:samples.append(('player_season_stats',p))
    data=pl.get('payload',{}).get('data') or []
    for x in data[:25]:
        pm=x.get('playerMetadata') or {}
        if pm:samples.append(('player_leaderboard',pm))
    print('FRL PLAYER-SEASON LIVE IDENTITY CROSSWALK')
    print('='*100)
    print(f'Player registry rows: {len(reg)}')
    print(f'Live identity observations: {len(samples)}')
    matched=0; ambiguous=0; missing=0; out=[]
    for endpoint,p in samples:
        sid=norm(p.get('id')); name=norm(p.get('name')); team=p.get('currentTeam') or {}; tid=norm(team.get('id')); tname=norm(team.get('name'))
        r=by_id.get(sid)
        status='SOURCE_ID_MATCH' if r else 'SOURCE_ID_NOT_IN_REGISTRY'
        if r: matched+=1
        else: missing+=1
        out.append({'endpoint':endpoint,'source_player_id':sid,'player_name':name,'current_team_id':tid,'current_team_name':tname,'registry_status':status,'registry_season':norm(r.get('season')) if r else ''})
        print(f'  {endpoint:22} id={sid:10} name={name:25} team={tid:5} {status}')
    print('\nSUMMARY')
    print(f'  source_id matches: {matched}')
    print(f'  source_id missing: {missing}')
    print(f'  sample player identity fields present: {len(samples)}')
    print('\nTARGET FIELD LIVE ATTACHMENT')
    for f in ('goals','playerName','season','totalShots'):
        print(f'  {f:20} player identity object present in live source -> REVIEW')
    print('\nIMPORTANT: season is not assumed from payload identity; it requires request/source temporal evidence.')
    print('Output:',OUT)
    with OUT.open('w',encoding='utf-8-sig',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=out[0].keys() if out else ['endpoint'])
        w.writeheader(); w.writerows(out)
    print('Evidence-only live identity crosswalk; no canonical promotion.')
if __name__=='__main__':main()
