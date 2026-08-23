from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
FRONTIER = DATA / "local_csv_relationship_contract_audit.csv"
REG = ROOT / "player_identity_registry.csv"
OUT = DATA / "player_season_source_identity_inventory.csv"

TARGET_FIELDS = {"goals", "playerName", "season", "totalShots"}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def candidate_paths():
    paths = []
    direct = DATA / "upstream_pl_stats_schema_by_season.csv"
    if direct.exists():
        for row in read_csv(direct):
            if row.get("grain") == "player_season" and row.get("field_name") in TARGET_FIELDS:
                raw = str(row.get("representative_path", "")).strip()
                if raw:
                    p = ROOT / raw.replace("/", "\\")
                    if p.exists():
                        paths.append(p)
    for base in (ROOT / "pl_stats", ROOT / "data", ROOT / "raw_upstream"):
        if base.exists():
            for p in base.rglob("*.csv"):
                try:
                    with p.open(encoding="utf-8-sig", newline="") as f:
                        header = next(csv.reader(f), [])
                except Exception:
                    continue
                h = {x.strip() for x in header}
                if TARGET_FIELDS.intersection(h) and ("playerName" in h or "season" in h):
                    paths.append(p)
    out = []
    seen = set()
    for p in paths:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            out.append(rp)
    return sorted(out)


def norm(v):
    return str(v).strip()


def main():
    reg = read_csv(REG) if REG.exists() else []
    reg_ids = {norm(r.get("source_player_id")) for r in reg if norm(r.get("source_player_id"))}
    reg_names = Counter(norm(r.get("fpl_name_normalized")) for r in reg if norm(r.get("fpl_name_normalized")))
    reg_teams = {norm(r.get("team_code")) for r in reg if norm(r.get("team_code"))}

    paths = candidate_paths()
    print("FRL PLAYER-SEASON SOURCE IDENTITY INVENTORY")
    print("=" * 100)
    print(f"Candidate player-season evidence files: {len(paths)}")
    print(f"Player registry rows: {len(reg)}")
    print(f"Registry source_player_id values: {len(reg_ids)}")
    print(f"Registry name values: {len(reg_names)}")
    print(f"Registry team_code values: {len(reg_teams)}")

    rows_out = []
    aggregate = Counter()
    for path in paths:
        try:
            rows = read_csv(path)
        except Exception:
            continue
        if not rows:
            continue
        cols = set(rows[0].keys())
        key_cols = [c for c in rows[0].keys() if any(k in c.lower() for k in ("player", "name", "team", "season", "id"))]
        id_like = [c for c in key_cols if "id" in c.lower()]
        name_like = [c for c in key_cols if "name" in c.lower()]
        team_like = [c for c in key_cols if "team" in c.lower()]
        season_like = [c for c in key_cols if c.lower() == "season" or "season" in c.lower()]
        nonblank_counts = {c: sum(1 for r in rows if norm(r.get(c))) for c in key_cols}
        reg_overlap = {}
        for c in id_like:
            vals = {norm(r.get(c)) for r in rows if norm(r.get(c))}
            reg_overlap[c] = len(vals & reg_ids)
        for c in team_like:
            vals = {norm(r.get(c)) for r in rows if norm(r.get(c))}
            if vals and vals <= reg_teams:
                reg_overlap[c] = len(vals)
        aggregate["files"] += 1
        if name_like:
            aggregate["name_columns"] += 1
        if id_like:
            aggregate["id_columns"] += 1
        if team_like:
            aggregate["team_columns"] += 1
        if reg_overlap:
            aggregate["registry_key_overlap_files"] += 1
        rows_out.append({
            "source_file": str(path.relative_to(ROOT)),
            "row_count": len(rows),
            "target_fields_present": ",".join(sorted(TARGET_FIELDS & cols)),
            "identity_like_columns": ",".join(key_cols),
            "id_like_columns": ",".join(id_like),
            "name_like_columns": ",".join(name_like),
            "team_like_columns": ",".join(team_like),
            "season_like_columns": ",".join(season_like),
            "nonblank_identity_like_counts": ";".join(f"{k}={nonblank_counts[k]}" for k in key_cols),
            "registry_key_overlap": ";".join(f"{k}={v}" for k, v in reg_overlap.items()),
        })

    print("\nSOURCE INVENTORY SUMMARY")
    print(f"  files_scanned={aggregate['files']}")
    print(f"  files_with_name_columns={aggregate['name_columns']}")
    print(f"  files_with_id_columns={aggregate['id_columns']}")
    print(f"  files_with_team_columns={aggregate['team_columns']}")
    print(f"  files_with_registry_key_overlap={aggregate['registry_key_overlap_files']}")

    print("\nFILES")
    for r in rows_out[:20]:
        print(f"  {r['source_file']} :: rows={r['row_count']} :: target={r['target_fields_present']} :: ids={r['id_like_columns'] or '-'} :: names={r['name_like_columns'] or '-'} :: teams={r['team_like_columns'] or '-'} :: overlap={r['registry_key_overlap'] or '-'}")
    if len(rows_out) > 20:
        print(f"  ... {len(rows_out)-20} additional files written to output")

    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        fields = list(rows_out[0].keys()) if rows_out else [
            "source_file", "row_count", "target_fields_present", "identity_like_columns",
            "id_like_columns", "name_like_columns", "team_like_columns", "season_like_columns",
            "nonblank_identity_like_counts", "registry_key_overlap"
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows_out)
    print("\nOutput:", OUT)
    print("Evidence-only source-key inventory; no identity inference and no contract promotion.")


if __name__ == "__main__":
    main()
