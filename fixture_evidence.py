from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

TEAM_EVIDENCE = DATA / "fixture_team_evidence.csv"
PLAYER_EVIDENCE = DATA / "player_match_evidence.csv"


def _read(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _season_fixture(rows: list[dict[str, str]], season: str, fixture_id: str) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row.get("frl_season") == season
        and str(row.get("frl_fixture_id", "")).strip() == str(fixture_id).strip()
    ]


def _display(value: str | None) -> str:
    if value in (None, ""):
        return "—"
    try:
        number = float(value)
        return str(int(number)) if number.is_integer() else f"{number:.1f}"
    except (TypeError, ValueError):
        return value


def fixture_evidence(season: str, fixture_id: str) -> dict:
    team_rows = _season_fixture(_read(TEAM_EVIDENCE), season, fixture_id)
    player_rows = _season_fixture(_read(PLAYER_EVIDENCE), season, fixture_id)

    return {
        "season": season,
        "fixture_id": str(fixture_id),
        "team": {
            "status": "AVAILABLE" if len(team_rows) == 2 else "UNAVAILABLE",
            "rows": team_rows,
            "source_fields": sorted(
                field.removeprefix("source_")
                for field in (team_rows[0].keys() if team_rows else [])
                if field.startswith("source_")
            ),
        },
        "players": {
            "status": "AVAILABLE" if player_rows else "UNAVAILABLE",
            "rows": player_rows,
            "source_fields": sorted(
                field.removeprefix("source_")
                for field in (player_rows[0].keys() if player_rows else [])
                if field.startswith("source_")
            ),
        },
        "availability": {
            "team_evidence_file": str(TEAM_EVIDENCE),
            "player_evidence_file": str(PLAYER_EVIDENCE),
            "team_rows": len(team_rows),
            "player_rows": len(player_rows),
        },
    }


def team_evidence_table(rows: list[dict[str, str]], fields: list[str]) -> list[dict[str, str]]:
    output = []
    for row in rows:
        item = {"Statistic": field for field in fields}
        item["Team"] = row.get("source_team", "")
        for field in fields:
            item[field] = _display(row.get(f"source_{field}"))
        output.append(item)
    return output


def player_display_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    output = []
    for row in rows:
        output.append(
            {
                "Player": row.get("source_playerName", "Unknown player"),
                "Team": row.get("source_team", ""),
                "Role": row.get("frl_participation_status", "unknown"),
                "Minutes": _display(row.get("source_minutesPlayed")),
                "Goals": _display(row.get("source_goals")),
                "Assists": _display(row.get("source_goalAssist")),
                "Rating": _display(row.get("source_rating")),
                "Source player ID": row.get("frl_source_player_id", ""),
            }
        )
    return output
