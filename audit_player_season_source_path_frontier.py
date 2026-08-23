from __future__ import annotations
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
TARGETS = {'goals', 'playerName', 'season', 'totalShots'}
SCHEMA = DATA / 'upstream_pl_stats_schema_by_season.csv'
LIVE = DATA / 'player_season_live_universe.csv'
OUT = DATA / 'player_season_source_path_frontier.csv'

def read(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def norm(v):
    return str(v or '').strip()

def main():
    schema = read(SCHEMA) if SCHEMA.exists() else []
    live = read(LIVE) if LIVE.exists() else []
    print('FRL PLAYER-SEASON SOURCE PATH FRONTIER')
    print('=' * 100)
    print(f'Target variables: {len(TARGETS)}')
    for field in sorted(TARGETS):
        srows = [r for r in schema if norm(r.get('field_name')) == field]
        lrows = [r for r in live if norm(r.get('field_name')) == field]
        print(f'\n{field}')
        print(f'  schema rows: {len(srows)}')
        for r in srows[:10]:
            print(f"  schema :: grain={norm(r.get('grain'))} season={norm(r.get('season'))} path={norm(r.get('representative_path'))}")
        if len(srows) > 10:
            print(f'  ... {len(srows)-10} additional schema rows')
        print(f'  live-universe rows: {len(lrows)}')
        for r in lrows[:10]:
            print(f"  live :: endpoint={norm(r.get('endpoint'))} path={norm(r.get('field_path'))} type={norm(r.get('field_type'))}")
    print('\nLOCAL MATERIALISATION CHECK')
    candidate_paths = []
    for r in schema:
        if norm(r.get('field_name')) in TARGETS and norm(r.get('representative_path')):
            p = ROOT / norm(r.get('representative_path')).replace('/', str(Path('/')))
            candidate_paths.append((norm(r.get('field_name')), norm(r.get('representative_path')), p.exists()))
    seen = set()
    for field, source_path, exists in candidate_paths:
        key=(field, source_path)
        if key in seen: continue
        seen.add(key)
        print(f'  {field} :: exists_under_audit_root={exists} :: {source_path}')
    print('\nOutput:', OUT)
    with OUT.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['field_name','schema_rows','live_universe_rows','representative_paths','local_path_exists'])
        w.writeheader()
        for field in sorted(TARGETS):
            srows=[r for r in schema if norm(r.get('field_name'))==field]
            lrows=[r for r in live if norm(r.get('field_name'))==field]
            paths=sorted({norm(r.get('representative_path')) for r in srows if norm(r.get('representative_path'))})
            exists=any((ROOT / p.replace('/', str(Path('/')))).exists() for p in paths)
            w.writerow({'field_name':field,'schema_rows':len(srows),'live_universe_rows':len(lrows),'representative_paths':' || '.join(paths),'local_path_exists':exists})
    print('Evidence-only source-path tracing; no identity inference and no contract promotion.')

if __name__ == '__main__':
    main()
