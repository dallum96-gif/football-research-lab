"""Audit the actual squad-resource evidence and team-season relationship keys.

Evidence-only. Searches local files by content/schema rather than guessed filenames,
then compares observed squad-like team keys to identity/team-season registries.
No canonical identity assignment or relationship promotion.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = DATA / "local_squad_identity_relationship_audit.csv"

KEYS = ("team_id", "team", "club", "team_code", "code", "id", "season", "team_season_id")


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        r = csv.DictReader(fh)
        return (r.fieldnames or [], list(r))


def inspect_json(path: Path):
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return [], []
    rows = []
    if isinstance(obj, list) and obj and isinstance(obj[0], dict):
        rows = obj
    elif isinstance(obj, dict):
        for v in obj.values():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                rows = v
                break
    cols = sorted({k for r in rows[:20] for k in r})
    return cols, rows[:500]


def likely_squad(path: Path, cols: list[str], rows: list[dict[str, str]]) -> bool:
    text = (str(path) + " " + " ".join(cols)).lower()
    if "squad" in text:
        return True
    keyhits = {c for c in cols if c.lower() in KEYS or any(t in c.lower() for t in ("team_id", "team_code", "club_id"))}
    return len(keyhits) >= 2 and any("season" in c.lower() for c in cols)


def load_team_registry():
    path = ROOT / "identity" / "team_seasons.csv"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main():
    registry = load_team_registry()
    registry_local = Counter(str(r.get("local_team_id", "")).strip() for r in registry if r.get("local_team_id", "").strip())
    registry_persistent = Counter(str(r.get("persistent_team_code", "")).strip() for r in registry if r.get("persistent_team_code", "").strip())
    registry_season_team = Counter((str(r.get("season", "")).strip(), str(r.get("local_team_id", "")).strip()) for r in registry if r.get("season", "").strip() and r.get("local_team_id", "").strip())

    candidates = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.name.startswith("."):
            continue
        suffix = path.suffix.lower()
        if suffix == ".csv":
            try:
                cols, rows = read_csv(path)
            except Exception:
                continue
        elif suffix == ".json":
            cols, rows = inspect_json(path)
        else:
            continue
        if likely_squad(path, cols, rows):
            candidates.append((path, cols, rows))

    out = []
    for path, cols, rows in candidates:
        idcols = [c for c in cols if c.lower() in KEYS or any(t in c.lower() for t in ("team_id", "team_code", "club_id"))]
        seasoncols = [c for c in cols if "season" in c.lower()]
        for c in idcols:
            vals = [str(r.get(c, "")).strip() for r in rows if str(r.get(c, "")).strip()]
            if not vals:
                continue
            matched_local = sum(1 for v in vals if v in registry_local)
            matched_persistent = sum(1 for v in vals if v in registry_persistent)
            out.append({
                "file": str(path.relative_to(ROOT)),
                "row_sample_count": len(rows),
                "key_column": c,
                "season_columns": " | ".join(seasoncols),
                "distinct_values_sample": len(set(vals)),
                "registry_local_team_id_matches": matched_local,
                "registry_persistent_team_code_matches": matched_persistent,
                "registry_season_local_team_pairs": len({(str(r.get(seasoncols[0], "")).strip() if seasoncols else "", str(r.get(c, "")).strip()) for r in rows if str(r.get(c, "")).strip() and seasoncols}),
            })

    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        cols = ["file","row_sample_count","key_column","season_columns","distinct_values_sample","registry_local_team_id_matches","registry_persistent_team_code_matches","registry_season_local_team_pairs"]
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(out)

    print("FRL LOCAL SQUAD IDENTITY RELATIONSHIP AUDIT")
    print("=" * 100)
    print(f"Team-season registry rows: {len(registry)}")
    print(f"Squad-like evidence files discovered: {len(candidates)}")
    print(f"Identity-key observations reviewed: {len(out)}")
    for r in out[:25]:
        print(f"  {r['file']} :: {r['key_column']} :: local_matches={r['registry_local_team_id_matches']} persistent_matches={r['registry_persistent_team_code_matches']}")
    print(f"Output: {OUT}")
    print("Evidence-only squad crosswalk; no inferred identity and no contract promotion.")


if __name__ == "__main__":
    main()
