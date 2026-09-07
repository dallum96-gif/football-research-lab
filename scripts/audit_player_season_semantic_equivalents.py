from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from canonical_variable_catalogue import canonical_variables
from source_field_registry import fields_for_family


GOVERNED_FAMILIES = ("team_match", "player_match", "player_season", "squad")

# Conservative provider-dialect normalisation only. These replacements are used
# to generate review candidates, never to promote semantics automatically.
TOKEN_EQUIVALENTS = {
    "passes": "pass",
    "passses": "pass",
    "tackles": "tackle",
    "clearances": "clearance",
    "corners": "corner",
    "crosses": "cross",
    "duels": "duel",
    "goals": "goal",
    "savesmade": "saves",
    "saves": "save",
    "offsides": "offside",
    "fouls": "foul",
    "launches": "launch",
    "layoffs": "layoff",
    "touches": "touch",
    "recoveries": "recovery",
    "penalties": "penalty",
    "throws": "throw",
}

EXPLICIT_EQUIVALENTS = {
    "totalPasses": ("totalPass",),
    "forwardPasses": ("fwdPass",),
    "backwardPasses": ("backwardPass",),
    "openPlayPasses": ("openPlayPass",),
    "leftsidePasses": ("leftsidePass", "passesLeft"),
    "rightsidePasses": ("rightsidePass", "passesRight"),
    "totalClearances": ("totalClearance",),
    "totalTackles": ("totalTackle",),
    "duelsWon": ("duelWon",),
    "duelsLost": ("duelLost",),
    "recoveries": ("ballRecovery",),
    "offsides": ("totalOffside",),
    "yellowCards": ("totalYelCard",),
    "straightRedCards": ("totalRedCard",),
    "savesMade": ("saves",),
    "savesMadeFromInsideBox": ("savedShotsFromInsideTheBox", "savedIbox"),
    "penaltiesSaved": ("penaltySave",),
    "savesFromPenalty": ("penaltySave",),
    "penaltiesFaced": ("penaltyFaced",),
    "penaltiesConceded": ("penaltyConceded",),
    "totalFoulsWon": ("fkFoulWon",),
    "totalFoulsConceded": ("fkFoulLost",),
    "successfulLongPasses": ("accurateLongBalls", "longPassOwnToOppSuccess"),
    "successfulPassesOppositionHalf": ("accurateOppositionHalfPasses",),
    "successfulPassesOwnHalf": ("accurateOwnHalfPasses",),
    "totalTouchesInOppositionBox": ("touchesInOppBox",),
    "clearancesOffTheLine": ("clearanceOffLine",),
    "lastPlayerTackle": ("lastManTackle",),
    "iboxBlocked": ("shotsBlockedInBox",),
    "oboxBlocked": ("shotsBlockedOutsideBox",),
    "shotsOnTargetInBox": ("shotsOnTargetIncGoals",),
    "successfulCrossesOpenPlay": ("accurateCrossNocorner",),
    "successfulCornersIntoBox": ("accurateCornersIntobox",),
    "successfulLaunches": ("accurateLaunches",),
    "successfulLayoffs": ("accurateLayoffs",),
}


def _normalise(name: str) -> str:
    text = re.sub(r"[^a-z0-9]", "", name.casefold())
    for source, target in sorted(TOKEN_EQUIVALENTS.items(), key=lambda item: -len(item[0])):
        text = text.replace(source, target)
    return text


def _governed() -> dict[str, list[tuple[str, str]]]:
    result: dict[str, list[tuple[str, str]]] = {}
    for family in GOVERNED_FAMILIES:
        for spec in fields_for_family(family):
            if spec.semantic_status not in {"exposed", "derived"}:
                continue
            result.setdefault(spec.source_field, []).append((family, spec.semantic_status))
    return result


def _uncatalogued_player_season() -> list[dict[str, str]]:
    return [
        row for row in canonical_variables()
        if row.get("source_surface") == "FRL_LOCAL_CSV"
        and row.get("resource") == "player_season"
        and row.get("semantic_status") == "UNCATALOGUED"
    ]


def main() -> int:
    governed = _governed()
    normalised: dict[str, list[str]] = {}
    for name in governed:
        normalised.setdefault(_normalise(name), []).append(name)

    rows = _uncatalogued_player_season()
    output: list[tuple[str, str, tuple[str, ...]]] = []
    counts = Counter()

    for row in rows:
        field = str(row.get("field_name") or "")
        candidates: list[str] = []
        route = "NO_CONTROLLED_EQUIVALENT"

        explicit = [name for name in EXPLICIT_EQUIVALENTS.get(field, ()) if name in governed]
        if explicit:
            candidates = explicit
            route = "EXPLICIT_DIALECT_EQUIVALENT"
        else:
            candidates = [name for name in normalised.get(_normalise(field), []) if name != field]
            if candidates:
                route = "NORMALISED_NAME_EQUIVALENT"

        counts[route] += 1
        output.append((field, route, tuple(candidates)))

    print(f"Uncatalogued Player-Season fields: {len(rows)}")
    print("Candidate classes:")
    for key, value in sorted(counts.items()):
        print(f"  {key}: {value}")

    print("\nControlled semantic-equivalence candidates:")
    for field, route, candidates in output:
        if not candidates:
            continue
        descriptions = []
        for candidate in candidates:
            locations = ", ".join(f"{family}={status}" for family, status in governed[candidate])
            descriptions.append(f"{candidate} [{locations}]")
        print(f"  {field} -> {'; '.join(descriptions)} :: {route}")

    print("\nStill genuinely unmatched:")
    for field, route, candidates in output:
        if not candidates:
            print(f"  {field}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
