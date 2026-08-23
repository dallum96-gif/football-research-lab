from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

from player_identity_registry import build_registry
from source_family_adapters import player_match_source_rows, player_season_source_rows, season_fixtures

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "player_identity_layer_audit.csv"


def n(v: object) -> str:
    return str(v or "").strip()


def registry_index() -> dict[tuple[str, str], list[dict[str, str]]]:
    out: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in build_registry():
        season, sid = n(row.get("season")), n(row.get("source_player_id"))
        if season and sid and n(row.get("identity_status")) == "VERIFIED":
            out[(season, sid)].append(row)
    return out


def player_match_audit() -> tuple[list[dict[str, str]], Counter]:
    reg = registry_index()
    rows: list[dict[str, str]] = []
    counts = Counter()
    for season in sorted({n(r.get("season")) for r in _fixture_rows() if n(r.get("season"))}):
        for fixture in season_fixtures(season):
            fixture_id = n(fixture.get("fixture_id"))
            try:
                source_rows = player_match_source_rows(season, fixture_id)
            except ValueError:
                continue
            seen: dict[str, int] = Counter()
            for src in source_rows:
                sid = n(src.get("playerId") or src.get("player_id") or src.get("pl_code"))
                if sid:
                    seen[sid] += 1
            for src in source_rows:
                sid = n(src.get("playerId") or src.get("player_id") or src.get("pl_code"))
                if not sid:
                    source_status = "UNAVAILABLE"
                elif seen[sid] == 1:
                    source_status = "VERIFIED"
                else:
                    source_status = "AMBIGUOUS"
                frl = reg.get((season, sid), []) if sid else []
                frl_status = "VERIFIED" if len(frl) == 1 else ("AMBIGUOUS" if len(frl) > 1 else "UNRESOLVED")
                counts[("source", source_status)] += 1
                counts[("frl", frl_status)] += 1
                rows.append({
                    "grain": "player_match",
                    "season": season,
                    "fixture_id": fixture_id,
                    "source_player_id": sid,
                    "source_player_identity_status": source_status,
                    "frl_player_identity_status": frl_status,
                    "player_observation_status": "VERIFIED" if source_status == "VERIFIED" else "UNAVAILABLE",
                })
    return rows, counts


def player_season_audit() -> tuple[list[dict[str, str]], Counter]:
    reg = registry_index()
    rows: list[dict[str, str]] = []
    counts = Counter()
    seasons = sorted({n(r.get("season")) for r in reg})
    for season in seasons:
        source_rows = player_season_source_rows(season)
        seen: dict[str, int] = Counter(n(r.get("playerId")) for r in source_rows if n(r.get("playerId")))
        for src in source_rows:
            sid = n(src.get("playerId"))
            if not sid:
                source_status = "UNAVAILABLE"
            elif seen[sid] == 1:
                source_status = "VERIFIED"
            else:
                source_status = "AMBIGUOUS"
            frl = reg.get((season, sid), []) if sid else []
            frl_status = "VERIFIED" if len(frl) == 1 else ("AMBIGUOUS" if len(frl) > 1 else "UNRESOLVED")
            counts[("source_season", source_status)] += 1
            counts[("frl_season", frl_status)] += 1
            rows.append({
                "grain": "player_season",
                "season": season,
                "fixture_id": "",
                "source_player_id": sid,
                "source_player_identity_status": source_status,
                "frl_player_identity_status": frl_status,
                "player_observation_status": "VERIFIED" if source_status == "VERIFIED" else "UNAVAILABLE",
            })
    return rows, counts


def _fixture_rows():
    path = ROOT / "fixtures_master_corrected.csv"
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    print("FRL PLAYER IDENTITY LAYER AUDIT")
    print("=" * 88)
    print("Source Player Identity and FRL Player Identity are evaluated separately.")
    pm, pcm = player_match_audit()
    ps, pcs = player_season_audit()
    all_rows = pm + ps
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as handle:
        fields = list(all_rows[0].keys()) if all_rows else []
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"PLAYER-MATCH observations: {len(pm):,}")
    print(f"  SOURCE PLAYER IDENTITY")
    for k in ("VERIFIED", "AMBIGUOUS", "UNAVAILABLE"):
        print(f"    {pcm.get(('source', k), 0):6d} {k}")
    print(f"  FRL PLAYER IDENTITY")
    for k in ("VERIFIED", "AMBIGUOUS", "UNRESOLVED"):
        print(f"    {pcm.get(('frl', k), 0):6d} {k}")

    print(f"PLAYER-SEASON rows: {len(ps):,}")
    print(f"  SOURCE PLAYER IDENTITY")
    for k in ("VERIFIED", "AMBIGUOUS", "UNAVAILABLE"):
        print(f"    {pcs.get(('source_season', k), 0):6d} {k}")
    print(f"  FRL PLAYER IDENTITY")
    for k in ("VERIFIED", "AMBIGUOUS", "UNRESOLVED"):
        print(f"    {pcs.get(('frl_season', k), 0):6d} {k}")

    print(f"Output: {OUT}")
    print("Evidence-only audit; no identity promotion or canonical mutation.")


if __name__ == "__main__":
    main()
