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
FIXTURE_CORRECTIONS_FILE = (
    Path(__file__).resolve().parent
    / "identity"
    / "data_quality"
    / "fixture_corrections.csv"
)

# Direct team-match fields with governed decade-long source coverage.  Keep
# provider-native names at this boundary; Team Stats uses the human-readable
# labels below and preserves source blanks as missing unless separately audited.
CORE_FIELDS = {
    "Possession": "possessionPercentage",
    "Shots": "totalScoringAtt",
    "Shots on target": "ontargetScoringAtt",
    "Shots off target": "shotOffTarget",
    "Blocked shots": "blockedScoringAtt",
    "Shots inside box": "attemptsIbox",
    "Shots outside box": "attemptsObox",
    "Shots conceded inside box": "attemptsConcededIbox",
    "Shots conceded outside box": "attemptsConcededObox",
    "Hit woodwork": "hitWoodwork",
    "Corners": "cornerTaken",
    "Passes": "totalPass",
    "Accurate passes": "accuratePass",
    "Forward passes": "fwdPass",
    "Long balls": "totalLongBalls",
    "Accurate long balls": "accurateLongBalls",
    "Final third passes": "totalFinalThirdPasses",
    "Successful final third passes": "successfulFinalThirdPasses",
    "Through balls": "totalThroughBall",
    "Accurate through balls": "accurateThroughBall",
    "Crosses": "totalCross",
    "Final third entries": "finalThirdEntries",
    "Penalty area entries": "penAreaEntries",
    "Touches": "touches",
    "Touches in opposition box": "touchesInOppBox",
    "Possession lost": "possLostAll",
    "Possession won attacking third": "possWonAtt3rd",
    "Possession won middle third": "possWonMid3rd",
    "Possession won defensive third": "possWonDef3rd",
    "Ball recoveries": "ballRecovery",
    "Tackles": "totalTackle",
    "Tackles won": "wonTackle",
    "Interceptions": "interception",
    "Interceptions won": "interceptionWon",
    "Interceptions in box": "interceptionsInBox",
    "Clearances": "totalClearance",
    "Effective clearances": "effectiveClearance",
    "Blocks": "outfielderBlock",
    "Duels won": "duelWon",
    "Duels lost": "duelLost",
    "Aerial duels won": "aerialWon",
    "Aerial duels lost": "aerialLost",
    "Contests won": "wonContest",
    "Big chances scored": "bigChanceScored",
    "Open-play assists": "attAssistOpenplay",
    "Set-piece assists": "attAssistSetplay",
    "Errors leading to shot": "errorLeadToShot",
    "Errors leading to goal": "errorLeadToGoal",
    "Saves inside box": "savedIbox",
    "Saves outside box": "savedObox",
    "High claims": "totalHighClaim",
    "Keeper sweeper actions": "totalKeeperSweeper",
    "Accurate keeper sweeper actions": "accurateKeeperSweeper",
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
    "Expected goals on target conceded": "expectedGoalsOnTargetConceded",
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


@lru_cache(maxsize=1)
def fixture_corrections():
    if not FIXTURE_CORRECTIONS_FILE.is_file():
        return {}
    return {
        (row["season"], row["fixture_id"]): row
        for row in load_csv(str(FIXTURE_CORRECTIONS_FILE))
    }


def verified_fixture_correction(fixture):
    """Return a correction only when it agrees with the canonical fixture.

    Corrections are additive relationship evidence.  They may supply an actual
    kickoff for source resolution, but never replace the canonical fixture key
    or silently override contradictory fixture/team context.
    """
    correction = fixture_corrections().get(
        (str(fixture.get("season", "")).strip(), str(fixture.get("fixture_id", "")).strip())
    )
    if correction is None or correction.get("status") != "VERIFIED_CORRECTION":
        return None

    checks = (
        ("home_team_id", "home_team_id"),
        ("away_team_id", "away_team_id"),
        ("scheduled_kickoff", "kickoff_time"),
    )
    for correction_field, fixture_field in checks:
        expected = str(correction.get(correction_field, "")).strip()
        observed = str(fixture.get(fixture_field, "")).strip()
        if expected and observed and expected != observed:
            raise ValueError(
                "Verified fixture correction contradicts canonical fixture "
                f"{fixture.get('season')}/{fixture.get('fixture_id')}: "
                f"{correction_field}={expected!r}, {fixture_field}={observed!r}"
            )
    if not str(correction.get("actual_kickoff", "")).strip():
        raise ValueError(
            "Verified fixture correction has no actual kickoff: "
            f"{fixture.get('season')}/{fixture.get('fixture_id')}"
        )
    return correction

def fixture_source_match(fixture, identity_rows):
    season = fixture["season"]

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

    def candidates_for(kickoff):
        target_time = canonical_to_utc(kickoff)
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
        return candidates

    candidates = candidates_for(fixture["kickoff_time"])
    if not candidates:
        correction = verified_fixture_correction(fixture)
        if correction is not None:
            candidates = candidates_for(correction["actual_kickoff"])

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
