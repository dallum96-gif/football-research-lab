"""Read-only audit of historical PL squad -> historical FPL -> Player Research closure.

The PL squad surface provides source playerId + displayName + season team context.
Historical FPL merged player files provide seasonal element/name/team context.
The audit reconciles those native source-family identities conservatively and then
checks the resulting FPL identity against existing Player Research semantics.
No canonical identities are created or mutated.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

SEASONS = tuple(f"{year}-{str(year + 1)[-2:]}" for year in range(2016, 2026))


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


def load_team_map(audit_root: Path) -> dict[tuple[str, str], str]:
    path = audit_root / "identity" / "team_seasons.csv"
    out: dict[tuple[str, str], str] = {}
    for row in read_csv(path):
        season = str(row.get("season") or "").strip()
        local = str(row.get("local_team_id") or "").strip()
        persistent = str(row.get("persistent_team_code") or "").strip()
        if season and local and persistent:
            out[(season, local)] = persistent
    return out


def load_squad(root: Path) -> dict[tuple[str, str], set[tuple[str, str]]]:
    """(season, source_player_id) -> {(name, persistent_team_code)}."""
    out: dict[tuple[str, str], set[tuple[str, str]]] = defaultdict(set)
    for season in SEASONS:
        for path in sorted(root.glob(f"pl_stats/*/squad/{season}_squad.csv")):
            club = path.parent.parent.name
            team_code = club.rsplit("_", 1)[-1]
            for row in read_csv(path):
                sid = str(row.get("playerId") or "").strip()
                name = normalize_name(row.get("displayName"))
                if sid and name:
                    out[(season, sid)].add((name, team_code))
    return out


def load_fpl(audit_root: Path, source_root: Path, team_map: dict[tuple[str, str], str]):
    """Return seasonal FPL records and name->seasonal-id groups."""
    by_key: dict[tuple[str, str], set[tuple[str, str, str]]] = defaultdict(set)
    research: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))

    for season in SEASONS:
        path = source_root / "fpl_scraper" / "fpl_stats" / "_merged" / "players" / f"{season}_all_players_gw.csv"
        rows = read_csv(path)
        for row in rows:
            name = normalize_name(row.get("name"))
            if not name:
                name = normalize_name(f"{row.get('first_name') or ''} {row.get('second_name') or ''}")
            seasonal_id = str(row.get("player_code") or row.get("element") or row.get("id") or "").strip()
            if not name or not seasonal_id:
                continue

            team_raw = str(row.get("team_code") or row.get("team") or "").strip()
            persistent_team = team_map.get((season, team_raw), team_raw)
            by_key[(season, name)].add((seasonal_id, persistent_team, str(row.get("name") or "").strip()))
            research[name][season].add(seasonal_id)

    return by_key, research


def registry_unique_ids(audit_root: Path) -> set[str]:
    path = audit_root / "player_identity_registry.csv"
    unique: dict[str, set[str]] = defaultdict(set)
    for row in read_csv(path):
        if str(row.get("identity_status") or "").strip() != "VERIFIED":
            continue
        sid = str(row.get("source_player_id") or "").strip()
        name = normalize_name(row.get("fpl_name_normalized"))
        if sid and name:
            unique[sid].add(name)
    return {sid for sid, names in unique.items() if len(names) == 1}


def source_observations(source_root: Path) -> Counter:
    obs = Counter()
    for season in SEASONS:
        for path in sorted(source_root.glob(f"pl_stats/*/players_match_stats/{season}_players_match_stats.csv")):
            for row in read_csv(path):
                sid = str(row.get("playerId") or row.get("pl_code") or row.get("player_id") or "").strip()
                if sid:
                    obs[sid] += 1
    return obs


def main() -> None:
    audit_root = Path(__file__).resolve().parent
    source_root = audit_root / "source"
    team_map = load_team_map(audit_root)
    squad = load_squad(source_root)
    fpl_by_key, research = load_fpl(audit_root, source_root, team_map)
    existing_ids = registry_unique_ids(audit_root)
    observations = source_observations(source_root)

    sid_to_research: dict[str, set[str]] = defaultdict(set)
    review: set[str] = set()
    evidence_seasons: dict[str, set[str]] = defaultdict(set)

    for (season, sid), squad_records in squad.items():
        for name, team_code in squad_records:
            candidates = {
                (seasonal_id, fpl_name)
                for seasonal_id, persistent_team, fpl_name in fpl_by_key.get((season, name), set())
                if persistent_team == team_code
            }
            if len(candidates) == 1:
                _seasonal_id, fpl_display = next(iter(candidates))
                if name in research and all(len(ids) <= 1 for ids in research[name].values()):
                    sid_to_research[sid].add(name)
                    evidence_seasons[sid].add(season)
                else:
                    review.add(sid)
            elif len(candidates) > 1:
                review.add(sid)

    unique_ids = {sid for sid, names in sid_to_research.items() if len(names) == 1}
    unique_ids -= review
    new_ids = unique_ids - existing_ids

    print("=" * 104)
    print("FRL PL SQUAD -> HISTORICAL FPL -> PLAYER RESEARCH CLOSURE AUDIT")
    print("=" * 104)
    print("Existing source-family evidence + existing team hierarchy; no promotion.")
    print(f"Source Player IDs observed:                 {len(observations):,}")
    print(f"Source IDs with verified registry coverage: {len(existing_ids):,}")
    print(f"New unique research IDs from squad/FPL:     {len(new_ids):,}")
    print(f"Review IDs from ambiguity/conflict:          {len(review):,}")
    print()
    print(f"Player-match observations total:             {sum(observations.values()):,}")
    print(f"Newly coverable observations:                {sum(observations[sid] for sid in new_ids):,}")
    print()

    for sid in sorted(new_ids, key=lambda x: int(x) if x.isdigit() else x)[:30]:
        print(f"  source={sid} research={sorted(sid_to_research[sid])} seasons={sorted(evidence_seasons[sid])}")

    print()
    print("No files were written or modified.")
    print("=" * 104)


if __name__ == "__main__":
    main()
