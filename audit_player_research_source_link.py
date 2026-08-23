"""Read-only audit of the working Player Research -> source-player link.

Uses existing identity machinery only:
- Player Research season rows and their existing player names;
- verified season-local team identity registry;
- source playerId + source team_id from player-match files.

The source team_id is first translated through the verified season-local team
registry to the persistent club key used by Player Research. A deterministic
match requires exactly one FPL/player-research seasonal player record and one
source playerId for (season, persistent club, normalized name).
No canonical identity is promoted or mutated.
"""
from __future__ import annotations

from collections import defaultdict
import csv
from pathlib import Path
import re
import unicodedata

import player_identity_audit
import player_research
import query_lab
from relationship_enforcement import evaluate_identity

SEASONS = tuple(player_identity_audit.SEASONS)
PL_ROOT = Path(player_identity_audit.PL_ROOT)


def norm(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.casefold().replace("'", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def open_csv(path: Path):
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return path.open("r", encoding=encoding, newline="")
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode {path}")


def source_files(season: str) -> tuple[Path, ...]:
    return tuple(sorted(PL_ROOT.rglob(f"{season}_players_match_stats.csv")))


def verified_team_maps(season: str):
    rows = query_lab.load_identity_registry()
    local_to_persistent = {}
    persistent_to_names = defaultdict(set)
    for row in rows:
        if row.get("season") != season or row.get("mapping_status") != "VERIFIED":
            continue
        local = str(row.get("local_team_id", "")).strip()
        persistent = str(row.get("persistent_team_code", "")).strip()
        name = str(row.get("canonical_name", "")).replace("_", " ").strip()
        if local and persistent:
            local_to_persistent[local] = persistent
            if name:
                persistent_to_names[persistent].add(norm(name))
    return local_to_persistent, persistent_to_names


def research_index(season: str):
    out = defaultdict(set)
    for row in player_research._load_season_rows(season):
        name = norm(player_research.display_player_name(row))
        element = str(player_research.seasonal_player_id(row)).strip()
        club = norm(player_research._row_club(row))
        team_code = str(row.get("team_code", "")).strip()
        if not team_code:
            local_to_persistent, _ = verified_team_maps(season)
            team_code = local_to_persistent.get(team_code, "") if team_code else ""
        if name and element:
            # Player Research's club may already be canonical name text; resolve
            # it against the verified season registry when possible.
            _, persistent_to_names = verified_team_maps(season)
            persistent_candidates = {pid for pid, names in persistent_to_names.items() if club in names}
            for persistent in persistent_candidates:
                out[(name, persistent)].add(element)
    return out


def source_index(season: str):
    local_to_persistent, _ = verified_team_maps(season)
    out = defaultdict(set)
    for path in source_files(season):
        with open_csv(path) as handle:
            for row in csv.DictReader(handle):
                pid = str(row.get("playerId") or row.get("player_id") or "").strip()
                name = norm(row.get("playerName") or row.get("player_name") or row.get("name"))
                local = str(row.get("team_id") or "").strip()
                persistent = local_to_persistent.get(local, "")
                if pid and name and persistent:
                    out[(name, persistent)].add(pid)
    return out


def audit_season(season: str):
    research = research_index(season)
    source = source_index(season)
    keys = sorted(set(research) | set(source))

    exact = 0
    missing_source = 0
    missing_research = 0
    ambiguous = 0
    rows = []

    for name, persistent in keys:
        research_ids = sorted(research.get((name, persistent), set()))
        source_ids = sorted(source.get((name, persistent), set()))
        candidates = [
            {"source_player_id": sid}
            for sid in source_ids
        ]
        decision = evaluate_identity(
            "fpl_player_to_frl_player_identity",
            source_context_available=True,
            candidates=candidates,
        ) if research_ids and source_ids else None

        status = ""
        if not research_ids:
            status = "MISSING_RESEARCH_RECORD"
            missing_research += 1
        elif not source_ids:
            status = "MISSING_SOURCE_PLAYER"
            missing_source += 1
        elif len(research_ids) != 1 or len(source_ids) != 1:
            status = "AMBIGUOUS"
            ambiguous += 1
        else:
            status = "EXACT_NAME_TEAM"
            exact += 1

        rows.append({
            "season": season,
            "name": name,
            "persistent_team_code": persistent,
            "research_player_ids": ";".join(research_ids),
            "source_player_ids": ";".join(source_ids),
            "status": status,
        })

    return {
        "research_keys": len(research),
        "source_keys": len(source),
        "exact": exact,
        "missing_source": missing_source,
        "missing_research": missing_research,
        "ambiguous": ambiguous,
        "rows": rows,
    }


def main():
    print("=" * 104)
    print("FRL PLAYER RESEARCH -> SOURCE PLAYER LINK AUDIT")
    print("=" * 104)
    print("Existing Player Research + verified team hierarchy; no identity promotion.")
    totals = {"exact": 0, "missing_source": 0, "missing_research": 0, "ambiguous": 0}
    all_rows = []
    for i, season in enumerate(SEASONS, 1):
        print(f"  [{i:02d}/{len(SEASONS)}] {season}")
        result = audit_season(season)
        for key in totals:
            totals[key] += result[key]
        all_rows.extend(result["rows"])
        print(
            f"    exact={result['exact']:,} "
            f"missing_source={result['missing_source']:,} "
            f"missing_research={result['missing_research']:,} "
            f"ambiguous={result['ambiguous']:,}"
        )

    out = Path("data/player_research_source_link_audit.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as handle:
        fields = [
            "season", "name", "persistent_team_code",
            "research_player_ids", "source_player_ids", "status"
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_rows)

    print("\nTOTAL")
    print(f"  Exact seasonal research->source links: {totals['exact']:,}")
    print(f"  Missing source player:                 {totals['missing_source']:,}")
    print(f"  Missing Player Research record:        {totals['missing_research']:,}")
    print(f"  Ambiguous:                              {totals['ambiguous']:,}")
    print(f"Output: {out}")
    print("Evidence-only audit; no canonical identity mutation.")


if __name__ == "__main__":
    main()
