from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent; DATA=ROOT/'data'
MATRIX=DATA/'variable_entity_route_verification.csv'
OUT=DATA/'team_fixture_route_frontiers.csv'

def read(p):
    with p.open('r',encoding='utf-8-sig',newline='') as f:
        r=csv.DictReader(f); return list(r), r.fieldnames or []
def n(v): return str(v or '').strip()

def main():
    rows,cols=read(MATRIX)
    targets=[r for r in rows if n(r.get('target_entity')).upper() in {'TEAM','FIXTURE'} and n(r.get('verification_status'))=='GRAIN_ROUTE_EVIDENCE_REQUIRED']
    # tolerate alternate result field names used by prior audits
    if not targets:
        targets=[r for r in rows if n(r.get('target_entity')).upper() in {'TEAM','FIXTURE'} and n(r.get('verification_result'))=='GRAIN_ROUTE_EVIDENCE_REQUIRED']
    print('FRL TEAM / FIXTURE ROUTE EVIDENCE FRONTIER')
    print('='*100)
    print(f'Frontier rows: {len(targets)}')
    by=Counter((n(r.get('target_entity')).upper(), n(r.get('grain'))) for r in targets)
    for (e,g),c in sorted(by.items(), key=lambda x:(x[0][0],-x[1],x[0][1])):
        print(f'{e:8} {c:5} grain={g or "<blank>"}')
    fam=Counter(n(r.get('resource')) for r in targets)
    print('\nRESOURCE')
    for k,v in fam.most_common(): print(f'{v:5} {k or "<blank>"}')
    fields=list(dict.fromkeys(cols+['frontier_reason']))
    out=[]
    for r in targets:
        e=n(r.get('target_entity')).upper(); g=n(r.get('grain')); c=n(r.get('identity_contract')); basis=[]
        if e=='TEAM':
            if g in {'team_match','team','squad'}: basis.append('team-grain-source-evidence')
            elif c=='canonical_team_season_to_source_team': basis.append('team-season-contract')
        elif e=='FIXTURE':
            if g in {'fixture','team_match','player_match','event'}: basis.append('fixture-grain-source-evidence')
            elif c=='canonical_fixture_to_source_match': basis.append('fixture-source-contract')
        if not basis: basis.append('grain-specific-route-not-yet-established')
        x=dict(r); x['frontier_reason']=';'.join(basis); out.append(x)
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(out)
    print(f'\nOutput: {OUT}')
    print('Evidence-only frontier profiling; no inferred joins and no canonical promotion.')
if __name__=='__main__': main()
