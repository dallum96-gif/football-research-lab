import csv
import os
from pathlib import Path
from datetime import datetime
from functools import lru_cache
from zoneinfo import ZoneInfo

PL_ROOT = r"C:\Users\dlall\football_database\Premier-League-Stats\pl_stats"
PACKAGED_STATS_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "fixture_match_stats.csv"
)

CORE_FIELDS = {
    "Possession": "possessionPercentage",
    "Shots": "totalScoringAtt",
    "Shots on target": "ontargetScoringAtt",
    "Shots off target": "shotOffTarget",
    "Blocked shots": "blockedScoringAtt",
    "Corners": "cornerTaken",
    "Passes": "totalPass",
    "Accurate passes": "accuratePass",
    "Crosses": "totalCross",
    "Tackles": "totalTackle",
    "Tackles won": "wonTackle",
    "Interceptions": "interception",
    "Interceptions won": "interceptionWon",
    "Clearances": "totalClearance",
    "Effective clearances": "effectiveClearance",
    "Fouls won": "fkFoulWon",
    "Fouls conceded": "fkFoulLost",
    "Offsides": "totalOffside",
    "Yellow cards": "totalYelCard",
    "Red cards": "totalRedCard",
}

OPTIONAL_FIELDS = {
    "Saves": "saves",
    "Big chances created": "bigChanceCreated",
    "Big chances missed": "bigChanceMissed",
    "Expected goals": "expectedGoals",
    "Expected assists": "expectedAssists",
    "Expected goals on target": "expectedGoalsOnTarget",
    "Attendance": "attendance",
}

def load_csv(path):
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(path, "r", encoding=encoding, newline="") as f:
                return list(csv.DictReader(f))
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode CSV: {path}")

def source_to_utc(value):
    return datetime.strptime(
        value,
        "%Y-%m-%d %H:%M:%S",
    ).replace(
        tzinfo=ZoneInfo("Europe/London")
    ).astimezone(ZoneInfo("UTC"))

def canonical_to_utc(value):
    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    ).astimezone(ZoneInfo("UTC"))

def number(value):
    if value in (None, ""):
        return None
    try:
        n = float(value)
        return int(n) if n.is_integer() else n
    except (TypeError, ValueError):
        return None

@lru_cache(maxsize=32)
def season_matches(season):
    matches = {}

    for folder in os.listdir(PL_ROOT):
        path = os.path.join(
            PL_ROOT,
            folder,
            "events_stats",
            f"{season}_events_stats.csv",
        )

        if not os.path.isfile(path):
            continue

        for row in load_csv(path):
            match_id = str(row.get("matchId", "")).strip()
            if match_id:
                matches.setdefault(match_id, []).append(row)

    return matches

def fixture_source_match(fixture, identity_rows):
    season = fixture["season"]

    # Canonical local team ID -> persistent PL team identity.
    identity = {
        (
            row["season"],
            str(row["local_team_id"]).strip(),
        ): str(row["persistent_team_code"]).strip()
        for row in identity_rows
        if row["season"] == season
        and row["mapping_status"] == "VERIFIED"
    }

    home_persistent = identity.get(
        (
            season,
            str(fixture["home_team_id"]).strip(),
        )
    )

    away_persistent = identity.get(
        (
            season,
            str(fixture["away_team_id"]).strip(),
        )
    )

    if not home_persistent or not away_persistent:
        raise ValueError(
            f"Missing verified identity for "
            f"{season}/{fixture['fixture_id']}"
        )

    target_time = canonical_to_utc(
        fixture["kickoff_time"]
    )

    candidates = []

    for match_id, rows in season_matches(season).items():

        home = next(
            (
                row for row in rows
                if row.get("venue", "").strip().lower() == "home"
            ),
            None,
        )

        away = next(
            (
                row for row in rows
                if row.get("venue", "").strip().lower() == "away"
            ),
            None,
        )

        if home is None or away is None:
            continue

        try:
            source_time = source_to_utc(
                home["kickoff"]
            )
        except (KeyError, TypeError, ValueError):
            continue

        if source_time != target_time:
            continue

        if str(home.get("team_id", "")).strip() != home_persistent:
            continue

        if str(away.get("team_id", "")).strip() != away_persistent:
            continue

        candidates.append(
            (match_id, home, away)
        )

    if len(candidates) > 1:
        raise ValueError(
            f"Ambiguous PL source match for "
            f"{season}/{fixture['fixture_id']}"
        )

    return candidates[0] if candidates else None

def extract(row, fields):
    return {
        label: number(row.get(source_field))
        for label, source_field in fields.items()
    }

@lru_cache(maxsize=1)
def packaged_stats():
    if not PACKAGED_STATS_FILE.is_file():
        return {}

    rows = load_csv(
        str(PACKAGED_STATS_FILE)
    )

    return {
        (
            row["season"],
            row["fixture_id"],
        ): row
        for row in rows
    }


def packaged_fixture_stats(fixture):
    rows = packaged_stats()

    row = rows.get(
        (
            fixture["season"],
            str(fixture["fixture_id"]),
        )
    )

    if row is None:
        return None

    def packaged_value(
        prefix,
        label,
    ):
        key = (
            f"{prefix}_"
            f"{label}"
            .lower()
            .replace(" ", "_")
        )

        value = row.get(key, "")

        return number(value)

    home_core = {
        label: packaged_value(
            "home_core",
            label,
        )
        for label in CORE_FIELDS
    }

    away_core = {
        label: packaged_value(
            "away_core",
            label,
        )
        for label in CORE_FIELDS
    }

    home_optional = {
        label: packaged_value(
            "home_optional",
            label,
        )
        for label in OPTIONAL_FIELDS
    }

    away_optional = {
        label: packaged_value(
            "away_optional",
            label,
        )
        for label in OPTIONAL_FIELDS
    }

    return {
        "status": "AVAILABLE",
        "source_match_id": row[
            "source_match_id"
        ],
        "home": {
            "core": home_core,
            "optional": home_optional,
        },
        "away": {
            "core": away_core,
            "optional": away_optional,
        },
    }


def fixture_stats(fixture, identity_rows):
    packaged = packaged_fixture_stats(
        fixture
    )

    if packaged is not None:
        return packaged

    source_match = fixture_source_match(
        fixture,
        identity_rows,
    )

    if source_match is None:
        return {
            "status": "UNAVAILABLE",
            "source_match_id": None,
            "home": {},
            "away": {},
        }

    match_id, home_row, away_row = source_match

    return {
        "status": "AVAILABLE",
        "source_match_id": match_id,
        "home": {
            "core": extract(
                home_row,
                CORE_FIELDS,
            ),
            "optional": extract(
                home_row,
                OPTIONAL_FIELDS,
            ),
        },
        "away": {
            "core": extract(
                away_row,
                CORE_FIELDS,
            ),
            "optional": extract(
                away_row,
                OPTIONAL_FIELDS,
            ),
        },
    }
