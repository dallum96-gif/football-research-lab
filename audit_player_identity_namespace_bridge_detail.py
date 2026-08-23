import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REG = ROOT / 'player_identity_registry.csv'
LIVE = ROOT / 'data' / 'live_pl_api_cache' / 'player_season_stats.json'
OUT = ROOT / 'data' / 'player_identity_namespace_bridge_detail.csv'


def norm(s):
    return ''.join(ch.lower() for ch in str(s).strip() if ch.isalnum())


def main():
    import json
    with REG.open('r', encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    payload = json.loads(LIVE.read_text(encoding='utf-8-sig'))['payload']
    p = payload['player']
    live_id = str(p.get('id',''))
    live_name = str(p.get('name',''))
    print('FRL PLAYER IDENTITY NAMESPACE BRIDGE DETAIL')
    print('=' * 96)
    print(f'Registry rows: {len(rows)}')
    print(f'Live player.id={live_id} name={live_name}')
    matches=[]
    for r in rows:
        reasons=[]
        for key in ('source_player_id','fpl_element'):
            if str(r.get(key,'')) == live_id:
                reasons.append(f'{key}=LIVE_ID')
        for key in ('fpl_name_normalized','name','player_name'):
            if norm(r.get(key,'')) == norm(live_name):
                reasons.append(f'{key}=NORMALIZED_NAME')
        if reasons:
            matches.append((r,reasons))
    print(f'Candidate registry rows: {len(matches)}')
    for i,(r,reasons) in enumerate(matches,1):
        print(f'[{i}] reasons={";".join(reasons)}')
        print('    ' + ' | '.join(f'{k}={r.get(k,"")}' for k in ('season','fpl_element','fpl_name_normalized','team_code','source_player_id','match_method','confidence','identity_status','evidence_basis')))
    print('')
    print('INTERPRETATION')
    if any(any('LIVE_ID' in x for x in reasons) for _,reasons in matches):
        print('  DIRECT_NAMESPACE_MATCH')
    elif any(any('NORMALIZED_NAME' in x for x in reasons) for _,reasons in matches):
        print('  NAME_ONLY_CANDIDATE')
    else:
        print('  NO_BRIDGE_CANDIDATE')
    print('Output:', OUT)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('w', encoding='utf-8-sig', newline='') as f:
        w=csv.writer(f)
        w.writerow(['live_id','live_name','reason','season','fpl_element','fpl_name_normalized','team_code','source_player_id','match_method','confidence','identity_status','evidence_basis'])
        for r,reasons in matches:
            for reason in reasons:
                w.writerow([live_id,live_name,reason,*[r.get(k,'') for k in ('season','fpl_element','fpl_name_normalized','team_code','source_player_id','match_method','confidence','identity_status','evidence_basis')]])
    print('Evidence-only namespace bridge detail; no identity inference and no contract promotion.')

if __name__ == '__main__':
    main()
