from __future__ import annotations
import csv
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'
FRONTIER=DATA/'local_csv_relationship_contract_audit.csv'
REG=DATA/'player_identity_registry.csv'
OUT=DATA/'player_season_identity_key_audit.csv'

def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def main():
    rows=read(FRONTIER); targets=[r for r in rows if r.get('resource')=='player_season']
    registry=read(REG) if REG.exists() else []
    reg_ids=Counter(str(r.get('source_player_id','')).strip() for r in registry if str(r.get('source_player_id','')).strip())
    reg_teams=Counter(str(r.get('team_code','')).strip() for r in registry if str(r.get('team_code','')).strip())
    print('FRL PLAYER-SEASON IDENTITY KEY AUDIT');print('='*100)
    print(f'Player-season frontier variables: {len(targets)}')
    print(f'Player registry rows: {len(registry)}')
    print(f'Unique source_player_id values in registry: {len(reg_ids)}')
    print(f'Unique team_code values in registry: {len(reg_teams)}')
    print('\nPLAYER-SEASON VARIABLE / KEY STATUS')
    for r in targets:
        field=r.get('field_name','')
        # inventory based on known audit metadata only; no guessing
        key_status = 'SOURCE_KEY_UNSPECIFIED'
        if 'source_player_id' in field.lower(): key_status='FIELD_NAME_NOT_IDENTITY_EVIDENCE'
        print(f'  {field:45} {key_status}')
    print('\nRegistry contract evidence')
    print('  source_player_id -> player_identity_registry:', 'AVAILABLE' if reg_ids else 'NONE')
    print('  team_code -> player_identity_registry:', 'AVAILABLE' if reg_teams else 'NONE')
    print('\nOutput:', OUT)
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['field_name','source_player_registry_status','team_code_registry_status','decision'])
        w.writeheader()
        for r in targets:w.writerow({'field_name':r.get('field_name',''),'source_player_registry_status':'AVAILABLE' if reg_ids else 'NONE','team_code_registry_status':'AVAILABLE' if reg_teams else 'NONE','decision':'REVIEW_REQUIRED'})
    print('Evidence-only player-season identity audit; no identity inference and no contract promotion.')
if __name__=='__main__':main()
