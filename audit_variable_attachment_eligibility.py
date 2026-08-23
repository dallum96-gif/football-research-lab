"""Summarize variable attachment eligibility from established FRL metadata only."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent; DATA=ROOT/'data'; MATRIX=DATA/'variable_entity_attachment_matrix.csv'; OUT=DATA/'variable_attachment_eligibility.csv'
def read(p):
    with p.open('r',encoding='utf-8-sig',newline='') as f:
        r=csv.DictReader(f); return list(r), r.fieldnames or []
def n(v): return str(v or '').strip()
def main():
    rows, cols=read(MATRIX)
    print('FRL VARIABLE ATTACHMENT ELIGIBILITY')
    print('='*100); print(f'Variables reviewed: {len(rows)}')
    print('Eligibility is metadata-derived only; it does not prove a join.')
    entities={'PLAYER':('grain', 'relationship_kind','identity_contract','source_identity_required','provenance_requirement'),'FIXTURE':('grain','relationship_kind','identity_contract','source_identity_required','provenance_requirement'),'TEAM':('grain','relationship_kind','identity_contract','source_identity_required','provenance_requirement')}
    out=[]; counters={e:Counter() for e in entities}
    for r in rows:
        grain=n(r.get('grain')); rel=n(r.get('relationship_kind')); contract=n(r.get('identity_contract')); req=n(r.get('source_identity_required')).upper(); prov=n(r.get('provenance_requirement'))
        for e in entities:
            if e=='PLAYER':
                if grain in {'player','player_match','player_season'}: state='GRAIN_COMPATIBLE'
                elif grain in {'team_match','team','fixture','event','squad'}: state='NON_PLAYER_GRAIN'
                else: state='GRAIN_UNMAPPED'
            elif e=='FIXTURE':
                if grain in {'fixture','team_match','player_match','event'} or contract=='canonical_fixture_to_source_match': state='GRAIN_OR_CONTRACT_COMPATIBLE'
                elif grain in {'player_season','player','team','squad'}: state='NO_DIRECT_FIXTURE_GRAIN'
                else: state='GRAIN_UNMAPPED'
            else:
                if grain in {'team','team_match','squad'} or contract=='canonical_team_season_to_source_team': state='GRAIN_OR_CONTRACT_COMPATIBLE'
                elif grain in {'player','player_match','player_season','fixture','event'}: state='NO_DIRECT_TEAM_GRAIN'
                else: state='GRAIN_UNMAPPED'
            counters[e][state]+=1
            out.append({**r,'eligibility_'+e.lower():state})
    for e,c in counters.items():
        print('\n'+e+' ELIGIBILITY')
        for k,v in c.most_common(): print(f'{v:6} {k}')
    fields=cols+['eligibility_player','eligibility_fixture','eligibility_team']
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(out)
    print(f'\nOutput: {OUT}')
if __name__=='__main__': main()
