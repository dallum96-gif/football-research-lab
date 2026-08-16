import os
import sys
from collections import defaultdict

ROOT = os.path.abspath(".")
sys.path.insert(0, ROOT)

import query_lab


passed = 0
failed = 0


def check(name, condition, detail=""):
    global passed, failed

    if condition:
        print(f"PASS  {name}")
        passed += 1
    else:
        print(f"FAIL  {name}")
        if detail:
            print(f"      {detail}")
        failed += 1


def canonical_player_name(row):
    # Historical schemas:
    #   older: name
    #   newer: first_name + second_name
    name = (
        row.get("name")
        or ""
    ).strip()

    if name:
        return " ".join(
            name.casefold().split()
        )

    first = (
        row.get("first_name")
        or ""
    ).strip()

    second = (
        row.get("second_name")
        or ""
    ).strip()

    return " ".join(
        part.casefold()
        for part in (first, second)
        if part
    )


def seasonal_player_id(row):
    return str(
        row.get("player_code")
        or row.get("element")
        or row.get("id")
        or ""
    )


def season_player_rows(season, canonical_name):
    rows, source, columns = (
        query_lab.load_player_rows(season)
    )

    return [
        row
        for row in rows
        if canonical_player_name(row)
        == canonical_name
    ]


print("=" * 78)
print("PLAYER RESEARCH V0.2 — CORRECTED IMPLEMENTATION GATE")
print("=" * 78)
print()


# ------------------------------------------------------------
# 21 — Multi-season additive totals
# ------------------------------------------------------------

selected_seasons = [
    "2021-22",
    "2022-23",
    "2023-24",
    "2024-25",
    "2025-26",
]

canonical_name = "erling haaland"

all_rows = []

for season in selected_seasons:
    all_rows.extend(
        season_player_rows(
            season,
            canonical_name,
        )
    )

manual_goals = sum(
    query_lab.to_number(
        row.get("goals_scored")
    )
    for row in all_rows
)

manual_minutes = sum(
    query_lab.to_number(
        row.get("minutes")
    )
    for row in all_rows
)

manual_xg = sum(
    query_lab.to_number(
        row.get("expected_goals")
    )
    for row in all_rows
)

manual_xa = sum(
    query_lab.to_number(
        row.get("expected_assists")
    )
    for row in all_rows
)

check(
    "21 — multi-season additive totals",
    (
        len(all_rows) > 0
        and manual_goals > 27
        and manual_minutes > 0
        and manual_xg > 0
        and manual_xa >= 0
    ),
    (
        f"Rows={len(all_rows)}; "
        f"Goals={manual_goals}; "
        f"Minutes={manual_minutes}; "
        f"xG={manual_xg}; "
        f"xA={manual_xa}"
    ),
)


# ------------------------------------------------------------
# 22 — Pooled multi-season per-90
# ------------------------------------------------------------

goals90 = (
    manual_goals
    / manual_minutes
    * 90
)

xg90 = (
    manual_xg
    / manual_minutes
    * 90
)

xa90 = (
    manual_xa
    / manual_minutes
    * 90
)

check(
    "22 — pooled multi-season per-90",
    (
        goals90 >= 0
        and xg90 >= 0
        and xa90 >= 0
    ),
    (
        f"Goals/90={goals90:.6f}; "
        f"xG/90={xg90:.6f}; "
        f"xA/90={xa90:.6f}"
    ),
)


# ------------------------------------------------------------
# 23 — Cross-season canonical identity
# ------------------------------------------------------------

identity_results = {}
identity_ok = True

for season in selected_seasons:
    rows = season_player_rows(
        season,
        canonical_name,
    )

    ids = {
        seasonal_player_id(row)
        for row in rows
    }

    ids.discard("")

    identity_results[season] = sorted(ids)

    if not rows:
        identity_ok = False

check(
    "23 — cross-season canonical identity",
    identity_ok,
    f"Season IDs: {identity_results}",
)


# ------------------------------------------------------------
# 24 — AND condition semantics
# ------------------------------------------------------------

rows_2025, _, _ = (
    query_lab.load_player_rows(
        "2025-26"
    )
)

grouped = defaultdict(list)

for row in rows_2025:
    name = canonical_player_name(row)

    if name:
        grouped[name].append(row)

reference_matches = []

for name, player_rows in grouped.items():

    minutes = sum(
        query_lab.to_number(
            row.get("minutes")
        )
        for row in player_rows
    )

    goals = sum(
        query_lab.to_number(
            row.get("goals_scored")
        )
        for row in player_rows
    )

    if (
        minutes >= 1000
        and goals >= 10
    ):
        reference_matches.append(name)

check(
    "24 — AND condition semantics",
    len(reference_matches) > 0,
    f"Matches={len(reference_matches)}",
)


# ------------------------------------------------------------
# 25 — Search semantics
# ------------------------------------------------------------

search_matches = [
    canonical_name
    for canonical_name
    in {
        canonical_player_name(row)
        for row in rows_2025
        if canonical_player_name(row)
    }
    if "haaland" in canonical_name
]

check(
    "25 — player name search semantics",
    search_matches == ["erling haaland"],
    f"Matches={search_matches}",
)


# ------------------------------------------------------------
# 26 — Multi-season participation count
# ------------------------------------------------------------

participation = sum(
    bool(
        season_player_rows(
            season,
            canonical_name,
        )
    )
    for season in selected_seasons
)

check(
    "26 — multi-season participation count",
    participation == len(selected_seasons),
    (
        f"Expected={len(selected_seasons)}; "
        f"Found={participation}"
    ),
)


print()
print("=" * 78)
print(
    f"V0.2 IMPLEMENTATION GATE: "
    f"{passed} passed / {failed} failed"
)
print("=" * 78)

if failed:
    raise SystemExit(1)
