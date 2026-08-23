from __future__ import annotations
import csv, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "player_identity_namespace_bridge.csv"


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def norm(v: str | None) -> str:
    return re.sub(r"\s+", " ", (v or "").strip()).casefold()


def main():
    registry_path = ROOT / "player_identity_registry.csv"
    rows = read_csv(registry_path)
    target_ids = {"223094"}
    names = {norm(r.get("fpl_name_normalized")) for r in rows if r.get("fpl_name_normalized")}
    id_cols = [c for c in (rows[0].keys() if rows else []) if any(x in c.lower() for x in ("id", "player", "element"))]
    live_path = ROOT / "data" / "live_pl_api_cache" / "player_season_stats.json"
    payload = json.loads(live_path.read_text(encoding="utf-8"))
    p = payload.get("payload", {}).get("player", {})
    live_id = str(p.get("id", ""))
    live_name = norm(p.get("name"))
    live_team = str((p.get("currentTeam") or {}).get("id", ""))
    matches = []
    for r in rows:
        vals = {c: str(r.get(c) or "").strip() for c in id_cols}
        if live_id in vals.values() or live_name in {norm(r.get("fpl_name_normalized")), norm(r.get("playerName")), norm(r.get("name"))}:
            matches.append(r)
    out = [{
        "live_player_id": live_id,
        "live_player_name": p.get("name", ""),
        "live_team_id": live_team,
        "registry_id_columns": " | ".join(id_cols),
        "name_matches": len(matches),
        "sample_registry_rows": json.dumps(matches[:5], ensure_ascii=False),
        "status": "NAMESPACE_BRIDGE_REVIEW" if matches else "NO_DIRECT_NAMESPACE_BRIDGE"
    }]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=out[0].keys()); w.writeheader(); w.writerows(out)
    print("FRL PLAYER IDENTITY NAMESPACE BRIDGE AUDIT")
    print("=" * 96)
    print(f"Registry rows: {len(rows)}")
    print(f"Registry identity-like columns: {' | '.join(id_cols)}")
    print(f"Live player.id={live_id} name={p.get('name','')} team={live_team}")
    print(f"Registry rows matching live namespace/id or normalized name: {len(matches)}")
    print(f"STATUS: {out[0]['status']}")
    print(f"Output: {OUT}")
    print("Evidence-only namespace diagnosis; no identity inference and no contract promotion.")

if __name__ == "__main__":
    main()
