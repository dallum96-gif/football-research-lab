from pathlib import Path
import csv, json

ROOT = Path(__file__).resolve().parent
REG = ROOT / 'player_identity_registry.csv'
CACHE = ROOT / 'data' / 'live_pl_api_cache' / 'player_season_stats.json'
OUT = ROOT / 'data' / 'player_season_registry_key_diagnostics.csv'

def norm(v):
    return str(v).strip().lower().replace('.0','') if v is not None else ''

def main():
    print('FRL PLAYER-SEASON REGISTRY KEY DIAGNOSTICS')
    print('=' * 96)
    with REG.open(encoding='utf-8-sig', newline='') as f:
        rows=list(csv.DictReader(f))
    print(f'Registry rows: {len(rows)}')
    print('REGISTRY COLUMNS:', ' | '.join(rows[0].keys()) if rows else 'NONE')
    key_candidates=['source_player_id','player_id','playerName','player_name','full_name','name','team_code','season']
    print('\nREGISTRY KEY CANDIDATES')
    for c in key_candidates:
        vals={norm(r.get(c)) for r in rows if norm(r.get(c))}
        if vals: print(f'  {c:24} unique={len(vals):5} sample={next(iter(vals))}')
    with CACHE.open(encoding='utf-8') as f:
        doc=json.load(f)
    p=doc.get('payload',{}).get('player',{})
    pid=norm(p.get('id')); name=norm(p.get('name')); team=norm((p.get('currentTeam') or {}).get('id'))
    print('\nLIVE SAMPLE')
    print(f'  player.id={pid} name={p.get("name")} team={team}')
    print('\nCROSSWALK DIAGNOSTICS')
    for c in ['source_player_id','player_id','playerName','player_name','full_name','name']:
        vals={norm(r.get(c)) for r in rows if norm(r.get(c))}
        print(f'  live_id -> {c:20} {"MATCH" if pid in vals else "NONE"}')
        if c in ['playerName','player_name','full_name','name']:
            print(f'  live_name -> {c:18} {"MATCH" if name in vals else "NONE"}')
    out=[{'live_player_id':pid,'live_player_name':p.get('name'),'registry_rows':len(rows),'id_match':pid in {norm(r.get('source_player_id')) for r in rows},'name_match':name in {norm(r.get('name')) for r in rows}}]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=out[0].keys()); w.writeheader(); w.writerows(out)
    print(f'\nOutput: {OUT}')
    print('Evidence-only diagnostics; no identity inference and no contract promotion.')

if __name__=='__main__': main()
