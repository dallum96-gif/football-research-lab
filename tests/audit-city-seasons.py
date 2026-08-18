import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import query_lab

rows = query_lab.load_fixtures()
registry = query_lab.load_identity_registry()

names = {
    (
        r["season"],
        r["local_team_id"],
    ): r["canonical_name"].replace("_", " ")
    for r in registry
}

print()
print("=" * 100)
print("MAN CITY 2020-21 / 2021-22 FIXTURE AUDIT")
print("=" * 100)

for season in ("2020-21", "2021-22"):

    print()
    print(f"=== {season} ===")
    print()

    for row in rows:

        if row["season"] != season:
            continue

        if "12" not in {
            str(row["home_team_id"]),
            str(row["away_team_id"]),
        }:
            continue

        home = names.get(
            (
                season,
                str(row["home_team_id"]),
            ),
            f"ID {row['home_team_id']}",
        )

        away = names.get(
            (
                season,
                str(row["away_team_id"]),
            ),
            f"ID {row['away_team_id']}",
        )

        print(
            f"fixture={row['fixture_id']:>4} | "
            f"GW={row['gameweek']:>2} | "
            f"{row['kickoff_time']} | "
            f"{home:<24} "
            f"{row['home_score']}-{row['away_score']} "
            f"{away:<24}"
        )
