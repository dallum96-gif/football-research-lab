from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from canonical_variable_catalogue import canonical_variables

REGISTRY = ROOT / "source_field_registry.py"
INVENTORY_JSON = ROOT / "data" / "frl_variable_capability_inventory_v1.json"

# Deliberately parked for later semantic review.
PARKED_PLAYER_SEASON = {
    "leftsidePasses", "rightsidePasses", "savesMadeFromInsideBox",
    "shotsOnTargetInBox", "straightRedCards", "successfulLongPasses",
    "blocks", "drops", "iboxTarget", "keyPassesAttemptAssists", "oboxTarget",
    "otherGoals", "putthroughBlockedDistribution", "putthroughBlockedDistributionWon",
    "secondGoalAssists", "tacklesLost", "timesTackled", "totalRedCards",
}

# These inherit an existing conservative governance decision rather than exposure.
PLAYER_SEASON_RETAINED = {
    "fiftyFifty", "freekickTotal", "successfulFiftyFifty", "winningGoal",
}
PLAYER_SEASON_RESTRICTED = {"unsuccessfulDribbles"}
TEAM_MATCH_EXPOSED = {"redCardsAgainst", "redCardsFor"}


def _replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def _current_uncatalogued_player_season() -> list[str]:
    return sorted({
        str(row.get("field_name") or "")
        for row in canonical_variables()
        if row.get("source_surface") == "FRL_LOCAL_CSV"
        and row.get("resource") == "player_season"
        and str(row.get("semantic_status") or "").upper() == "UNCATALOGUED"
    })


def _update_registry() -> tuple[bool, int, int, int]:
    uncatalogued = _current_uncatalogued_player_season()
    promotion = [field for field in uncatalogued if field not in PARKED_PLAYER_SEASON]
    statuses = {
        field: (
            "restricted" if field in PLAYER_SEASON_RESTRICTED
            else "retained" if field in PLAYER_SEASON_RETAINED
            else "exposed"
        )
        for field in promotion
    }

    text = REGISTRY.read_text(encoding="utf-8-sig")
    original = text

    if "PLAYER_SEASON_PROMOTION_BATCH_V1_FIELDS" not in text:
        lines = ["PLAYER_SEASON_PROMOTION_BATCH_V1_FIELDS = {"]
        for field in sorted(statuses):
            lines.append(f'    "{field}": "{statuses[field]}",')
        lines.extend(["}", "", ""])
        marker = "SQUAD_FIELDS = {"
        if marker not in text:
            raise RuntimeError("player-season batch insertion marker not found")
        text = text.replace(marker, "\n".join(lines) + marker, 1)

    old_player = '    + _build_family("player_season", PLAYER_SEASON_FIELDS)\n'
    new_player = '    + _build_family("player_season", PLAYER_SEASON_FIELDS | PLAYER_SEASON_PROMOTION_BATCH_V1_FIELDS)\n'
    if "PLAYER_SEASON_FIELDS | PLAYER_SEASON_PROMOTION_BATCH_V1_FIELDS" not in text:
        text = _replace_once(text, old_player, new_player, "player-season registry union")

    if "TEAM_PROMOTION_BATCH_V9_FIELDS" not in text:
        block = (
            'TEAM_PROMOTION_BATCH_V9_FIELDS = {\n'
            '    "redCardsAgainst": "exposed",\n'
            '    "redCardsFor": "exposed",\n'
            '}\n\n\n'
        )
        marker = "# The final packaged residue is governed explicitly rather than left uncatalogued."
        if marker not in text:
            raise RuntimeError("team V9 insertion marker not found")
        text = text.replace(marker, block + marker, 1)

    if "| TEAM_PROMOTION_BATCH_V9_FIELDS" not in text:
        if "| TEAM_PROMOTION_BATCH_V8_FIELDS" in text:
            old_team = "        | TEAM_PROMOTION_BATCH_V8_FIELDS\n        | TEAM_EXCEPTION_FIELDS,"
            new_team = "        | TEAM_PROMOTION_BATCH_V8_FIELDS\n        | TEAM_PROMOTION_BATCH_V9_FIELDS\n        | TEAM_EXCEPTION_FIELDS,"
        else:
            old_team = "        | TEAM_PROMOTION_BATCH_V7_FIELDS\n        | TEAM_EXCEPTION_FIELDS,"
            new_team = "        | TEAM_PROMOTION_BATCH_V7_FIELDS\n        | TEAM_PROMOTION_BATCH_V9_FIELDS\n        | TEAM_EXCEPTION_FIELDS,"
        text = _replace_once(text, old_team, new_team, "team registry V9 union")

    if text != original:
        compile(text, str(REGISTRY), "exec")
        REGISTRY.write_text(text, encoding="utf-8", newline="")

    exposed = sum(status == "exposed" for status in statuses.values())
    retained = sum(status == "retained" for status in statuses.values())
    restricted = sum(status == "restricted" for status in statuses.values())
    return text != original, exposed, retained, restricted


def main() -> int:
    changed, exposed, retained, restricted = _update_registry()

    subprocess.run(
        [sys.executable, "-c", "from variable_capability_inventory import write_inventory; write_inventory()"],
        cwd=ROOT,
        check=True,
    )

    inventory = json.loads(INVENTORY_JSON.read_text(encoding="utf-8"))
    review = [
        row for row in inventory["variables"]
        if row["football_meaning"]["status"] == "REVIEW_REQUIRED"
    ]
    by_surface: dict[str, int] = {}
    for row in review:
        surface = row["source"]["surface"]
        by_surface[surface] = by_surface.get(surface, 0) + 1

    print(f"source_field_registry.py changed: {changed}")
    print(f"Player-Season exposed in batch: {exposed}")
    print(f"Player-Season retained in batch: {retained}")
    print(f"Player-Season restricted in batch: {restricted}")
    print("Team-Match exposed in batch: 2")
    print(f"Current REVIEW_REQUIRED meanings: {len(review)}")
    print("Remaining REVIEW_REQUIRED by source surface:")
    for surface, count in sorted(by_surface.items(), key=lambda item: (-item[1], item[0])):
        print(f"  {surface}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
