"""Audit exact source-side relationships in the Team Leaderboard universe.

Evidence-first only. Reads the local team_leaderboard_candidate_values.csv when run
from frl-source-audit. No canonical promotion.

The audit verifies arithmetic identities only where all component values are present
in the same observed Team Leaderboard payload. It reports whether the identity is
EXACT, VIOLATED, or UNTESTABLE from the available evidence.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "team_leaderboard_candidate_values.csv"
OUT = ROOT / "data" / "team_leaderboard_source_relationship_audit.csv"

RELATIONSHIPS = [
    ("duels", ("duelsWon", "duelsLost"), "duelsWon + duelsLost"),
    ("goalsConceded", ("goalsConcededInsideBox", "goalsConcededOutsideBox"), "goalsConcededInsideBox + goalsConcededOutsideBox"),
    ("aerialDuels", ("aerialDuelsWon", "aerialDuelsLost"), "aerialDuelsWon + aerialDuelsLost"),
    ("crossesAndCorners_attempts", ("successfulCrossesAndCorners", "unsuccessfulCrossesAndCorners"), "successfulCrossesAndCorners + unsuccessfulCrossesAndCorners"),
    ("crossesOpenPlay_attempts", ("successfulCrossesOpenPlay", "unsuccessfulCrossesOpenPlay"), "successfulCrossesOpenPlay + unsuccessfulCrossesOpenPlay"),
    ("dribbles_attempts", ("successfulDribbles", "unsuccessfulDribbles"), "successfulDribbles + unsuccessfulDribbles"),
    ("launches_attempts", ("successfulLaunches", "unsuccessfulLaunches"), "successfulLaunches + unsuccessfulLaunches"),
    ("layoffs_attempts", ("successfulLayoffs", "unsuccessfulLayoffs"), "successfulLayoffs + unsuccessfulLayoffs"),
    ("longPasses_attempts", ("successfulLongPasses", "unsuccessfulLongPasses"), "successfulLongPasses + unsuccessfulLongPasses"),
    ("shortPasses_attempts", ("successfulShortPasses", "unsuccessfulShortPasses"), "successfulShortPasses + unsuccessfulShortPasses"),
    ("passesOwnHalf_attempts", ("successfulPassesOwnHalf", "unsuccessfulPassesOwnHalf"), "successfulPassesOwnHalf + unsuccessfulPassesOwnHalf"),
]


def read_values() -> dict[str, float]:
    if not INPUT.exists():
        return {}
    with INPUT.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    values: dict[str, float] = {}
    for row in rows:
        field = row.get("field_name", "").strip()
        raw = row.get("sample_values", "").strip()
        if not field or not raw:
            continue
        try:
            values[field] = float(raw)
        except ValueError:
            continue
    return values


def main() -> list[dict[str, str]]:
    values = read_values()
    out: list[dict[str, str]] = []
    for target, components, formula in RELATIONSHIPS:
        fields = (target, *components)
        if not all(f in values for f in fields):
            status = "UNTESTABLE"
            difference = ""
            reason = "Not all source values are present in the candidate-values artefact."
        else:
            observed = values[target]
            derived = sum(values[f] for f in components)
            difference = f"{observed - derived:g}"
            if abs(observed - derived) < 1e-9:
                status = "EXACT"
                reason = "Observed source value equals the stated arithmetic relationship."
            else:
                status = "VIOLATED"
                reason = "Observed source value does not equal the stated arithmetic relationship."
        out.append({
            "target": target,
            "components": " + ".join(components),
            "formula": formula,
            "target_value": f"{values[target]:g}" if target in values else "",
            "derived_value": f"{sum(values[f] for f in components):g}" if all(f in values for f in components) else "",
            "difference": difference,
            "status": status,
            "reason": reason,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    cols = ["target", "components", "formula", "target_value", "derived_value", "difference", "status", "reason"]
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        writer.writerows(out)
    return out


if __name__ == "__main__":
    rows = main()
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    print("FRL TEAM LEADERBOARD SOURCE RELATIONSHIP AUDIT")
    print("=" * 90)
    for key, value in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {value:3d}  {key}")
    print("\nRELATIONSHIPS")
    for row in rows:
        print(f"  {row['status']:10s}  {row['target']:34s}  observed={row['target_value']:>8s}  derived={row['derived_value']:>8s}  diff={row['difference']:>8s}")
    print(f"\nOutput: {OUT}")
    print("Source-side arithmetic verification only; no canonical promotion.")
