"""Build the FRL variable dictionary from the observed master universe.

Navigation classification is intentionally broader than semantic approval:
- category/subcategory make the large universe navigable;
- semantic_status remains source/registry evidence;
- no field is promoted merely by heuristic classification.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "master_variable_universe.csv"
OUTPUT = ROOT / "data" / "frl_variable_dictionary.csv"

CATEGORY_RULES: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("Identity & Context", ("id", "_id", "slug", "season", "competition", "club", "country", "nationality", "code", "name", "position", "foot", "birth_date", "birthdate", "height_cm", "weight_kg", "join_date", "joindate", "onloan"), "Identity / context"),
    ("Playing Time", ("minutes", "appear", "starts", "substitute", "sub", "bench", "played", "games", "matches"), "Participation / availability"),
    ("Shooting & Finishing", ("shot", "goal", "scoring", "woodwork", "xg", "xgot", "penalty_goal", "penaltygoals", "att_", "attempt"), "Shooting / finishing"),
    ("Chance Creation", ("assist", "keypass", "chance", "big_chance", "bigchance", "creative", "finalthird", "throughball"), "Creation / chance generation"),
    ("Passing & Distribution", ("pass", "distribution", "launch", "layoff", "flickon", "throw", "keeper_throw", "goal_kick"), "Passing / distribution"),
    ("Crossing & Set Pieces", ("cross", "corner", "freekick", "free_kick", "setpiece", "set_piece", "delivery"), "Crossing / set pieces"),
    ("Dribbling & Carrying", ("dribble", "carry", "ballcarry", "ball_carry", "takeon", "take_on"), "Dribbling / carrying"),
    ("Possession & Ball Security", ("possession", "touch", "recover", "recovery", "dispossess", "lostpossession", "loss_of_possession", "ballrecovery", "ball_recovery"), "Possession / security"),
    ("Duels & Aerials", ("duel", "aerial", "contest", "fiftyfifty", "50_50", "challenge"), "Duels / aerial play"),
    ("Defending", ("tackle", "interception", "clearance", "block", "defend", "defender", "errorleadto", "lastman", "offside"), "Defensive actions"),
    ("Goalkeeping", ("save", "smother", "claim", "keeper", "goalkeeper", "punch", "catch", "parry", "sweep", "sweeper", "gk_", "goals_prevented", "goalsprevented"), "Goalkeeping"),
    ("Discipline", ("yellow", "redcard", "red_card", "secondyellow", "second_yellow", "card", "discipline", "fouls", "wasfouled", "foul"), "Cards / fouls"),
    ("Team Attack", ("team_attack", "teamattack", "forwardgoals", "midfieldergoals", "goalsopenplay", "fastbreak", "entries", "penarea", "touchesinoppbox", "woncorners", "lostcorners"), "Team attacking context"),
    ("Team Defence", ("team_defence", "teamdefence", "goalsconceded", "redcardsagainst", "clearances", "defensive"), "Team defensive context"),
    ("Tactical & Match Context", ("formation", "lineup", "substitution", "commentary", "event", "official", "referee", "attendance", "venue", "ground", "kickoff", "timestamp", "minute", "period", "home_", "away_", "result", "score", "matchweek", "gameweek", "phase", "broadcast", "manager", "staff"), "Match / tactical context"),
    ("Physical & Tracking", ("distance", "meters", "metres", "speed", "sprint", "running", "jogging", "walking", "physical", "tracking"), "Physical / tracking"),
)


def _normalise(value: str) -> str:
    return value.lower().replace("-", "_").replace(" ", "_")


def classify(field_name: str, resource: str, grain: str) -> tuple[str, str]:
    field = _normalise(field_name)
    resource_text = _normalise(resource)
    grain_text = _normalise(grain)

    # Metadata fields are recognised from the field itself. Generic resource
    # labels such as "team" must never make every team-level metric identity.
    metadata_tokens = ("id", "_id", "slug", "season", "competition", "club", "country", "nationality", "code", "name", "position", "foot", "birth_date", "birthdate", "height_cm", "weight_kg", "join_date", "joindate", "onloan")
    if any(field == token or field.startswith(f"{token}_") or field.endswith(f"_{token}") for token in metadata_tokens):
        return "Identity & Context", "Identity / context"

    if any(token in field for token in ("penaltysave", "penalty_save", "savedshots", "goodhighclaim", "saves", "save_", "smother", "punch", "catch", "parry", "keeper", "goalkeeper", "sweeper")):
        return "Goalkeeping", "Goalkeeping"
    if any(token in field for token in ("yellowcard", "yellow_cards", "redcard", "red_cards", "secondyellow", "second_yellow", "fouls", "wasfouled", "foul")):
        return "Discipline", "Cards / fouls"
    if any(token in field for token in ("formation", "lineup", "commentary", "official", "attendance", "venue", "ground", "broadcast", "kickoff", "timestamp", "minute", "period", "gameweek", "matchweek", "home_", "away_")):
        return "Tactical & Match Context", "Match / tactical context"

    # Metric classification is driven primarily from the native field name.
    for category, tokens, subcategory in CATEGORY_RULES:
        if category == "Identity & Context":
            continue
        if any(token in field for token in tokens):
            return category, subcategory

    # Pure resource-level records are context only when their field name has no
    # stronger metric signal.
    if resource_text in {"match", "fixture", "standings", "competition", "broadcast"} or grain_text in {"match", "fixture", "standings"}:
        return "Tactical & Match Context", "Match / tactical context"

    return "Unclassified Review", "Needs manual navigation review"


def run(input_path: Path = INPUT, output_path: Path = OUTPUT) -> int:
    if not input_path.exists():
        raise FileNotFoundError(
            f"Master variable universe not found: {input_path}. "
            "Run enumerate_master_variable_universe.py first."
        )

    with input_path.open("r", encoding="utf-8-sig", newline="") as fh:
        source_rows = list(csv.DictReader(fh))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "source_surface", "resource", "grain", "field_name", "field_type",
        "semantic_status", "navigation_category", "navigation_subcategory",
        "navigation_basis", "source_statuses", "source_types", "notes",
    ]

    with output_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        for row in source_rows:
            category, subcategory = classify(row.get("field_name", ""), row.get("resource", ""), row.get("grain", ""))
            writer.writerow({
                "source_surface": row.get("source_surface", ""),
                "resource": row.get("resource", ""),
                "grain": row.get("grain", ""),
                "field_name": row.get("field_name", ""),
                "field_type": row.get("field_type", ""),
                "semantic_status": row.get("status", ""),
                "navigation_category": category,
                "navigation_subcategory": subcategory,
                "navigation_basis": "heuristic navigation only; semantic approval unchanged",
                "source_statuses": row.get("statuses_seen", ""),
                "source_types": row.get("types_seen", ""),
                "notes": row.get("notes", ""),
            })
    return len(source_rows)


def main() -> None:
    count = run()
    print("FRL VARIABLE DICTIONARY")
    print("=" * 80)
    print(f"Variables classified: {count}")
    print(f"Output: {OUTPUT}")
    print("Navigation classification does not promote semantic/canonical status.")


if __name__ == "__main__":
    main()
