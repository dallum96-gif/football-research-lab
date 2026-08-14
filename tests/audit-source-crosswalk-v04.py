import csv
import os
from collections import defaultdict

ROOT = r"C:\Users\dlall\football_database\Premier-League-Stats\fpl_scraper\fpl_stats"
PL_ROOT = r"C:\Users\dlall\football_database\Premier-League-Stats\pl_stats"
FIXTURE_FILE = os.path.join(ROOT, "fixtures_master.csv")

CLUBS = {
    "Manchester City": ("Man_City_43", "43"),
    "West Ham": ("West_Ham_21", "21"),
    "Bournemouth": ("Bournemouth_91", "91"),
}

SEASONS = [
    "2016-17",
    "2017-18",
    "2018-19",
    "2019-20",
    "2020-21",
    "2021-22",
    "2022-23",
    "2023-24",
    "2024-25",
    "2025-26",
]


def load_csv(path):
    with open(
        path,
        "r",
        encoding="latin-1",
        newline=""
    ) as handle:
        return list(csv.DictReader(handle))


fixtures = load_csv(FIXTURE_FILE)

# Exact source-documented match-level join:
# fixture_code <-> matchId
fixture_lookup = {}

for row in fixtures:

    key = (
        row["season"],
        str(row.get("fixture_code", "")).strip()
    )

    if key[1]:
        fixture_lookup[key] = row


print()
print("=" * 82)
print(" SOURCE CROSSWALK AUDIT V0.4")
print("=" * 82)
print()
print(
    "Join 1: PL matchId <-> FPL fixture_code"
)
print(
    "Join 2: PL persistent club folder <-> persistent team identity"
)
print(
    "Team-season identity is then derived from the matched fixture side."
)
print()


for club_name, (folder, persistent_id) in CLUBS.items():

    print("=" * 82)
    print(
        f"{club_name} | persistent team_id = {persistent_id}"
    )
    print("=" * 82)

    for season in SEASONS:

        event_file = os.path.join(
            PL_ROOT,
            folder,
            "events_stats",
            f"{season}_events_stats.csv"
        )

        if not os.path.isfile(event_file):

            print(
                f"{season} | NO EVENT FILE"
            )

            continue

        events = [
            row
            for row in load_csv(event_file)
            if str(row.get("team_id", "")).strip()
            == persistent_id
        ]

        matched = 0
        missing = 0
        conflicts = 0
        local_ids = set()
        unmatched_examples = []

        for event in events:

            match_id = str(
                event.get("matchId", "")
            ).strip()

            fixture = fixture_lookup.get(
                (season, match_id)
            )

            if fixture is None:

                missing += 1

                if len(unmatched_examples) < 5:
                    unmatched_examples.append(
                        match_id
                    )

                continue

            venue = str(
                event.get("venue", "")
            ).strip().lower()

            if venue == "home":

                local_id = str(
                    fixture["home_team_id"]
                )

            elif venue == "away":

                local_id = str(
                    fixture["away_team_id"]
                )

            else:

                conflicts += 1
                continue

            local_ids.add(local_id)
            matched += 1

        status = "STRONG"

        if missing > 0:
            status = "INCOMPLETE"

        if conflicts > 0:
            status = "REVIEW"

        if len(local_ids) != 1:
            status = "IDENTITY_CONFLICT"

        print(
            f"{season} | "
            f"events={len(events):>2} | "
            f"matched={matched:>2} | "
            f"missing_matchid={missing:>2} | "
            f"venue_conflicts={conflicts:>2} | "
            f"local_ids="
            f"{','.join(sorted(local_ids, key=int)) or '-'} | "
            f"status={status}"
        )

        if unmatched_examples:
            print(
                "    Missing match IDs: "
                + ", ".join(unmatched_examples)
            )

    print()


print("=" * 82)
print("AUDIT COMPLETE")
print("=" * 82)
