"""Read-only audit of the PL playerId -> current FPL -> Player Research chain.

Evidence chain:
  historical/source-family playerId + same-season squad name/team
      -> current FPL player directory player_code/element/name/team
      -> existing Player Research seasonal identity semantics

No identity promotion or canonical mutation is performed.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from collections import defaultdict
from pathlib import Path


SEASON = "2025-26"


def normalize_name(value: object) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.casefold().replace("'", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def read_csv(path: Path) -> list[dict[str, str]]:
    last = None
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as fh:
                return list(csv.DictReader(fh))
        except UnicodeDecodeError as exc:
            last = exc
    raise ValueError(f"Could not decode CSV: {path}") from last


def source_squad(root: Path) -> dict[str, set[tuple[str, str]]]:
    """source_player_id -> {(normalized_name, team_code)} from current squads."""
    out: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for path in sorted(root.glob(f"pl_stats/*/squad/{SEASON}_squad.csv")):
        club = path.parent.parent.name
        team_code = club.rsplit("_", 1)[-1]
        for row in read_csv(path):
            pid = str(row.get("playerId") or "").strip()
            name = normalize_name(row.get("displayName") or "")
            if pid and name:
                out[pid].add((name, team_code))
    return out


def fpl_current(root: Path) -> dict[str, set[tuple[str, str, str]]]:
    """FPL player_code -> {(element, normalized_name, team_code)}."""
    out: dict[str, set[tuple[str, str, str]]] = defaultdict(set)
    for path in sorted(root.glob("fpl_scraper/fpl_stats/players/*/2025-26_gw_stats.csv")):
        code = path.parent.name.rsplit("_", 1)[-1]
        if not code.isdigit():
            continue
        for row in read_csv(path):
            element = str(row.get("element") or "").strip()
            name = normalize_name(
                f"{row.get('first_name') or ''} {row.get('second_name') or ''}"
            )
            team = str(row.get("team_code") or "").strip()
            if element and name and team:
                out[code].add((element, name, team))
    return out


def research_names(root: Path) -> dict[str, dict[str, set[str]]]:
    """normalized research name -> season -> seasonal ids."""
    out: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for path in sorted(root.glob("fpl_scraper/fpl_stats/_merged/players/*_all_players_gw.csv")):
        season = path.name.split("_", 1)[0]
        for row in read_csv(path):
            name = normalize_name(row.get("name"))
            if not name:
                name = normalize_name(
                    f"{row.get('first_name') or ''} {row.get('second_name') or ''}"
                )
            sid = str(
                row.get("player_code")
                or row.get("element")
                or row.get("id")
                or ""
            ).strip()
            if name and sid:
                out[name][season].add(sid)
    return out


def registry_unique_ids(audit_root: Path) -> set[str]:
    path = audit_root / "player_identity_registry.csv"
    if not path.is_file():
        return set()
    unique: dict[str, set[str]] = defaultdict(set)
    for row in read_csv(path):
        if str(row.get("identity_status") or "").strip() != "VERIFIED":
            continue
        sid = str(row.get("source_player_id") or "").strip()
        name = normalize_name(row.get("fpl_name_normalized") or "")
        if sid and name:
            unique[sid].add(name)
    return {sid for sid, names in unique.items() if len(names) == 1}


def match_source_to_fpl(
    squad: dict[str, set[tuple[str, str]]],
    fpl: dict[str, set[tuple[str, str, str]]],
) -> dict[str, set[str]]:
    by_name_team: dict[tuple[str, str], set[str]] = defaultdict(set)
    by_name: dict[str, set[str]] = defaultdict(set)
    for code, records in fpl.items():
        for _element, name, team in records:
            by_name_team[(name, team)].add(code)
            by_name[name].add(code)

    out: dict[str, set[str]] = defaultdict(set)
    for sid, records in squad.items():
        for name, team in records:
            exact = by_name_team.get((name, team), set())
            if len(exact) == 1:
                out[sid].update(exact)
                continue
            name_only = by_name.get(name, set())
            if len(name_only) == 1:
                out[sid].update(name_only)
    return out


def research_unique_for_name(name: str, research: dict[str, dict[str, set[str]]]) -> bool:
    seasons = research.get(name, {})
    if not seasons:
        return False
    return all(len(ids) <= 1 for ids in seasons.values())


def main() -> None:
    root = Path(__file__).resolve().parent / "source"
    squad = source_squad(root)
    fpl = fpl_current(root)
    research = research_names(root)
    existing_registry_ids = registry_unique_ids(Path(__file__).resolve().parent)

    source_to_codes = match_source_to_fpl(squad, fpl)
    code_to_names: dict[str, set[str]] = defaultdict(set)
    for code, records in fpl.items():
        for _element, name, _team in records:
            code_to_names[code].add(name)

    unique_bridge_ids: set[str] = set()
    review_bridge_ids: set[str] = set()
    source_to_research: dict[str, set[str]] = defaultdict(set)

    for sid, codes in source_to_codes.items():
        for code in codes:
            for name in code_to_names.get(code, set()):
                if research_unique_for_name(name, research):
                    source_to_research[sid].add(name)
                else:
                    review_bridge_ids.add(sid)
        if len(source_to_research.get(sid, set())) == 1:
            unique_bridge_ids.add(sid)
        elif len(source_to_research.get(sid, set())) > 1:
            review_bridge_ids.add(sid)

    # Historical Player-Match observation counts from the same source family.
    obs_by_sid: Counter = Counter()
    total_obs = 0
    for path in sorted(root.glob("pl_stats/*/players_match_stats/*_players_match_stats.csv")):
        season = path.name.split("_", 1)[0]
        if not (season[:4].isdigit() and "-" in season):
            continue
        for row in read_csv(path):
            sid = str(
                row.get("playerId")
                or row.get("pl_code")
                or row.get("player_id")
                or ""
            ).strip()
            if sid:
                obs_by_sid[sid] += 1
                total_obs += 1

    new_ids = unique_bridge_ids - existing_registry_ids
    new_obs = sum(obs_by_sid[sid] for sid in new_ids)
    all_unique_obs = sum(obs_by_sid[sid] for sid in unique_bridge_ids)

    print("=" * 104)
    print("FRL PL PLAYERID -> CURRENT FPL -> PLAYER RESEARCH CLOSURE AUDIT")
    print("=" * 104)
    print("Existing source-family evidence only; no identity promotion.")
    print(f"Current-season source squad player IDs: {len(squad):,}")
    print(f"Current FPL player codes observed:      {len(fpl):,}")
    print(f"Source IDs bridged to unique research:  {len(unique_bridge_ids):,}")
    print(f"Source IDs requiring review:            {len(review_bridge_ids):,}")
    print(f"Already covered by verified registry:   {len(existing_registry_ids):,}")
    print()
    print(f"Player-match observations:              {total_obs:,}")
    print(f"Unique bridged observations:            {all_unique_obs:,}")
    print(f"New observations beyond registry:       {new_obs:,}")
    print()
    examples = 0
    for sid in sorted(new_ids, key=int):
        print(f"  source={sid} research={sorted(source_to_research[sid])}")
        examples += 1
        if examples >= 20:
            break
    print()
    print("No files were written or modified.")
    print("=" * 104)


if __name__ == "__main__":
    from collections import Counter
    main()
