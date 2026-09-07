from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REGISTRY = ROOT / "source_field_registry.py"

EXPOSED = {
    "leftsidePasses",
    "rightsidePasses",
    "savesMadeFromInsideBox",
    "shotsOnTargetInBox",
    "straightRedCards",
    "successfulLongPasses",
    "iboxTarget",
    "oboxTarget",
    "tacklesLost",
    "timesTackled",
    "totalRedCards",
}

RETAINED = {
    "blocks",
    "drops",
    "keyPassesAttemptAssists",
    "otherGoals",
    "putthroughBlockedDistribution",
    "putthroughBlockedDistributionWon",
    "secondGoalAssists",
}


def _update_registry() -> bool:
    text = REGISTRY.read_text(encoding="utf-8-sig")
    original = text

    constant = "PLAYER_SEASON_FINAL_SEMANTIC_RESIDUE_FIELDS"
    if constant not in text:
        lines = [
            "# Final Player-Season semantic residue. Exposed fields are reusable only under",
            "# their exact provider-native names; no cross-grain/canonical alias is asserted.",
            f"{constant} = {{",
        ]
        for field in sorted(EXPOSED):
            lines.append(f'    "{field}": "exposed",')
        for field in sorted(RETAINED):
            lines.append(f'    "{field}": "retained",')
        lines.extend(["}", "", ""])
        block = "\n".join(lines)

        marker = "SQUAD_FIELDS = {"
        if marker not in text:
            raise RuntimeError("source_field_registry.py: SQUAD_FIELDS insertion marker not found")
        text = text.replace(marker, block + marker, 1)

    # Match the player_season builder structurally rather than relying on exact
    # punctuation/line wrapping. Earlier local promotion batches may already have
    # expanded the union across several lines.
    pattern = re.compile(
        r'_build_family\(\s*"player_season"\s*,\s*(?P<expr>.*?)\s*\)',
        re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        raise RuntimeError("source_field_registry.py: player_season family construction not found")

    segment = match.group(0)
    if constant not in segment:
        expr = match.group("expr").rstrip()
        replacement = f'_build_family("player_season", {expr} | {constant})'
        text = text[:match.start()] + replacement + text[match.end():]

    if text != original:
        compile(text, str(REGISTRY), "exec")
        REGISTRY.write_text(text, encoding="utf-8", newline="")
        return True
    return False


def main() -> int:
    changed = _update_registry()

    # Rebuild after registry mutation so canonical semantic overlays see the batch.
    from variable_capability_inventory import write_inventory
    inventory = write_inventory(ROOT)
    review = [row for row in inventory["variables"] if row["football_meaning"]["status"] == "REVIEW_REQUIRED"]
    by_surface = Counter(row["source"]["surface"] for row in review)

    player_season_review = [
        row for row in review
        if row["source"]["surface"] == "FRL_LOCAL_CSV"
        and row["source"]["resource"] == "player_season"
    ]

    print(f"source_field_registry.py changed: {changed}")
    print(f"Final Player-Season fields exposed: {len(EXPOSED)}")
    print(f"Final opaque Player-Season fields retained: {len(RETAINED)}")
    print(f"Current REVIEW_REQUIRED meanings: {len(review)}")
    print("Remaining REVIEW_REQUIRED by source surface:")
    for key, value in by_surface.most_common():
        print(f"  {key}: {value}")
    print(f"Remaining Player-Season REVIEW_REQUIRED rows: {len(player_season_review)}")
    for row in player_season_review:
        fields = row["source"].get("native_fields", [])
        print(f"  {fields[0] if fields else row['canonical_name']} [{row['governance'].get('semantic_status', 'UNKNOWN')}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
