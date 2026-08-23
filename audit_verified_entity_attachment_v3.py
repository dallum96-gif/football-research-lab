"""Audit structurally eligible variable/entity attachment using current or legacy eligibility shapes."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent; DATA=ROOT/'data'; ELIG=DATA/'variable_attachment_eligibility.csv'; OUT=DATA/'verified_entity_attachment_v3.csv'

def read(p):
    with p.open('r',encoding='utf-8-sig',newline='') as f:
        r=csv.DictReader(f); return list(r), r.fieldnames or []
def n(v): return str(v or '').strip()

def status_for(r,e):
    x=n(r.get(f'eligibility_{e.lower()}'))
    if x: return x
    x=n(r.get(f'{e.lower()}_eligibility'))
    if x: return x
    # Legacy 3-row shape
    entity=n(r.get('entity') or r.get('target_entity')).upper()
    if entity==e:
        return n(r.get('eligibility_status'))
    return ''

def structural(status,e):
    if status in {'GRAIN_COMPATIBLE','GRAIN_OR_CONTRACT_COMPATIBLE'}: return True
    if status: return False
    grain=n(r.get('grain')).lower()
    if e=='PLAYER': return grain in {'player','player_season','player_match'}
    if e=='FIXTURE': return grain in {'fixture','player_match','team_match','event'} or n(r.get('identity_contract')).lower()=='canonical_fixture_to_source_match'
    return grain in {'team','team_match','squad'} or n(r.get('identity_contract')).lower()=='canonical_team_season_to_source_team'

def contract_for(r,e):
    g=n(r.get('grain')).lower(); c=n(r.get('identity_contract')).lower(); rel=n(r.get('relationship_kind')).upper()
    if e=='PLAYER': return g in {'player','player_season','player_match'} or c in {'fpl_player_to_frl_player_identity','source_player_identity_to_player_season','player_identity_to_player_match_observations'}
    if e=='FIXTURE': return g in {'fixture','player_match','team_match','event'} or c=='canonical_fixture_to_source_match'
    return g in {'team','team_match','squad'} or c=='canonical_team_season_to_source_team'

def main():
    rows,cols=read(ELIG); print('FRL VERIFIED ENTITY ATTACHMENT AUDIT V3'); print('='*100); print(f'Eligibility rows: {len(rows)}')
    out=[]; counters={e:Counter() for e in ('PLAYER','FIXTURE','TEAM')}
    for r in rows:
        # Current shape: one row per variable. Legacy shape: entity-specific rows.
        for e in ('PLAYER','FIXTURE','TEAM'):
            if n(r.get('entity') or r.get('target_entity')) and n(r.get('entity') or r.get('target_entity')).upper()!=e:
                continue
            status=status_for(r,e)
            ok=structural(status,e)
            contract=contract_for(r,e)
            if not ok: result='NOT_STRUCTURALLY_ELIGIBLE'
            elif contract: result='EXPLICIT_CONTRACT_ROUTE_PRESENT_REQUIRES_EVIDENCE_CHECK'
            else: result='STRUCTURALLY_ELIGIBLE_NO_EXPLICIT_CONTRACT'
            counters[e][result]+=1
            item=dict(r); item['target_entity']=e; item['eligibility_status_normalized']=status; item['verification_result']=result; item['explicit_contract_detected']='TRUE' if contract else 'FALSE'; out.append(item)
    for e in ('PLAYER','FIXTURE','TEAM'):
        print('\n'+e)
        for k,v in counters[e].most_common(): print(f'{v:6}  {k}')
    fields=list(dict.fromkeys(cols+['target_entity','eligibility_status_normalized','verification_result','explicit_contract_detected']))
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(out)
    print(f'\nOutput: {OUT}')
    print('Evidence-only verification; no inferred joins and no canonical promotion.')
if __name__=='__main__': main()
