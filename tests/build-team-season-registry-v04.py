import csv
import json
import os
import urllib.request
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = r"C:\Users\dlall\football_database\Premier-League-Stats\fpl_scraper\fpl_stats"
PL_ROOT = r"C:\Users\dlall\football_database\Premier-League-Stats\pl_stats"

FIXTURE_FILE = os.path.join(
    ROOT,
    "fixtures_master.csv"
)

TEAM_INDEX_FILE = os.path.join(
    PL_ROOT,
    "_index",
    "_teams_index.json"
)

OUTPUT_DIR = os.path.join(
    ROOT,
    "identity"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "team_seasons.csv"
)

PROVENANCE_FILE = os.path.join(
    OUTPUT_DIR,
    "team_seasons_provenance.csv"
)

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

PROBLEM_SEASONS = {
    "2020-21",
    "2021-22",
}

UK = ZoneInfo("Europe/London")
UTC = ZoneInfo("UTC")

FPL_TEAMS_URL = (
    "https://raw.githubusercontent.com/"
    "vaastav/Fantasy-Premier-League/master/data/"
    "{season}/teams.csv"
)


def load_csv(path):
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(
                path,
                "r",
                encoding=encoding,
                newline="",
            ) as handle:
                return list(csv.DictReader(handle))
        except UnicodeDecodeError:
            pass

    raise RuntimeError(f"Could not decode {path}")


def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as handle:
        return json.load(handle)


def archive_to_utc(value):
    local = datetime.strptime(
        value.strip(),
        "%Y-%m-%d %H:%M:%S",
    ).replace(tzinfo=UK)

    return local.astimezone(UTC)


def fixture_to_utc(value):
    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    ).astimezone(UTC)


def fetch_external_teams(season):

    url = FPL_TEAMS_URL.format(
        season=season
    )

    with urllib.request.urlopen(
        url,
        timeout=30,
    ) as response:

        text = response.read().decode(
            "utf-8-sig"
        )

    rows = list(
        csv.DictReader(
            text.splitlines()
        )
    )

    return rows, url


# ============================================================
# SOURCE 1 — fixture universe
# ============================================================

fixtures = load_csv(FIXTURE_FILE)

fixture_team_seasons = set()

for fixture in fixtures:

    if fixture["season"] not in SEASONS:
        continue

    for side in (
        "home_team_id",
        "away_team_id",
    ):

        local_id = str(
            fixture[side]
        ).strip()

        if local_id:
            fixture_team_seasons.add(
                (
                    fixture["season"],
                    local_id,
                )
            )


print()
print("=" * 82)
print("BUILDING TEAM-SEASON REGISTRY V0.4")
print("=" * 82)
print()

print(
    f"Fixture team-season universe: "
    f"{len(fixture_team_seasons)}"
)

if len(fixture_team_seasons) != 200:
    raise RuntimeError(
        "Expected exactly 200 Premier League "
        "team-season combinations."
    )


# ============================================================
# SOURCE 2 — persistent PL identity index
# ============================================================

team_index = load_json(
    TEAM_INDEX_FILE
)

persistent_names = {
    str(code): name
    for code, name in team_index.items()
}

print(
    f"Persistent PL team identities: "
    f"{len(persistent_names)}"
)


# ============================================================
# SOURCE 3 — fixture lookup for local seasons
# ============================================================

fixture_lookup = defaultdict(list)

for fixture in fixtures:

    try:
        key = (
            fixture["season"],
            fixture_to_utc(
                fixture["kickoff_time"]
            ),
        )

        fixture_lookup[key].append(
            fixture
        )

    except Exception:
        continue


# ============================================================
# Build registry
# ============================================================

registry = []
provenance = []


for season in SEASONS:

    print(
        f"Processing {season}..."
    )

    # --------------------------------------------------------
    # 2020-21 / 2021-22:
    # authoritative historical FPL teams.csv
    # --------------------------------------------------------

    if season in PROBLEM_SEASONS:

        rows, source_url = fetch_external_teams(
            season
        )

        if len(rows) != 20:
            raise RuntimeError(
                f"{season}: expected 20 external "
                f"team rows, got {len(rows)}"
            )

        for row in rows:

            local_id = str(
                row["id"]
            ).strip()

            team_code = str(
                row["code"]
            ).strip()

            if not local_id or not team_code:
                raise RuntimeError(
                    f"{season}: incomplete external "
                    "team mapping."
                )

            if (
                season,
                local_id,
            ) not in fixture_team_seasons:

                raise RuntimeError(
                    f"{season}: external local ID "
                    f"{local_id} not found in "
                    "fixtures_master.csv."
                )

            if team_code not in persistent_names:
                raise RuntimeError(
                    f"{season}: external team_code "
                    f"{team_code} not found in "
                    "_teams_index.json."
                )

            registry.append(
                {
                    "team_season_id":
                        f"{season}:{team_code}",
                    "season": season,
                    "club_id": team_code,
                    "canonical_name":
                        persistent_names[team_code],
                    "persistent_team_code":
                        team_code,
                    "local_team_id":
                        local_id,
                    "source_name":
                        row["name"],
                    "mapping_status":
                        "VERIFIED",
                    "mapping_source":
                        "Historical FPL teams.csv",
                }
            )

        provenance.append(
            {
                "season": season,
                "method":
                    "historical_fpl_teams_csv",
                "source":
                    source_url,
                "notes":
                    "Used because local PL event "
                    "kickoff bridge is unavailable "
                    "for this season.",
            }
        )

        continue


    # --------------------------------------------------------
    # All other seasons:
    # derive persistent club -> local team ID from the
    # complete season of PL event evidence.
    # --------------------------------------------------------

    # Get clubs actually present in this season's fixtures.
    local_ids = {
        local_id
        for (
            s,
            local_id
        ) in fixture_team_seasons
        if s == season
    }

    # Candidate observations:
    # local team ID -> persistent PL code.
    observations = defaultdict(
        list
    )

    for persistent_code, persistent_name in (
        persistent_names.items()
    ):

        folder = None

        # Find the persistent club folder.
        expected_prefixes = [
            f"{persistent_name}_",
            persistent_name.replace(
                " ",
                "_"
            ) + "_",
        ]

        for entry in os.scandir(
            PL_ROOT
        ):

            if not entry.is_dir():
                continue

            if not entry.name.endswith(
                f"_{persistent_code}"
            ):
                continue

            if entry.name in {
                "_badges",
                "_index",
                "_merged",
            }:
                continue

            folder = entry.name
            break

        if folder is None:
            continue

        event_file = os.path.join(
            PL_ROOT,
            folder,
            "events_stats",
            f"{season}_events_stats.csv",
        )

        if not os.path.isfile(event_file):
            continue

        events = [
            row
            for row in load_csv(event_file)
            if str(
                row.get("team_id", "")
            ).strip()
            == persistent_code
        ]

        for event in events:

            try:
                kickoff = archive_to_utc(
                    event["kickoff"]
                )
            except Exception:
                continue

            venue = str(
                event.get(
                    "venue",
                    ""
                )
            ).strip().lower()

            if venue not in (
                "home",
                "away",
            ):
                continue

            candidates = fixture_lookup.get(
                (
                    season,
                    kickoff,
                ),
                [],
            )

            candidate_ids = set()

            for fixture in candidates:

                if venue == "home":
                    candidate_ids.add(
                        str(
                            fixture[
                                "home_team_id"
                            ]
                        )
                    )

                elif venue == "away":
                    candidate_ids.add(
                        str(
                            fixture[
                                "away_team_id"
                            ]
                        )
                    )

            if len(candidate_ids) == 1:

                local_id = next(
                    iter(candidate_ids)
                )

                observations[
                    persistent_code
                ].append(
                    local_id
                )

    # --------------------------------------------------------
    # Decide season mapping from observations.
    # --------------------------------------------------------

    for persistent_code, ids in (
        observations.items()
    ):

        if not ids:
            continue

        counts = defaultdict(int)

        for local_id in ids:
            counts[local_id] += 1

        ranked = sorted(
            counts.items(),
            key=lambda x: (
                -x[1],
                int(x[0]),
            )
        )

        best_id, best_count = ranked[0]
        total = sum(
            counts.values()
        )

        if total < 3:
            continue

        # We only persist mappings where at least 80%
        # of clean observations agree.
        if (
            best_count / total
        ) < 0.80:
            continue

        if (
            season,
            best_id,
        ) not in fixture_team_seasons:
            continue

        registry.append(
            {
                "team_season_id":
                    f"{season}:{persistent_code}",
                "season":
                    season,
                "club_id":
                    persistent_code,
                "canonical_name":
                    persistent_names[
                        persistent_code
                    ],
                "persistent_team_code":
                    persistent_code,
                "local_team_id":
                    best_id,
                "source_name":
                    persistent_names[
                        persistent_code
                    ],
                "mapping_status":
                    "VERIFIED",
                "mapping_source":
                    "Local PL events_stats + "
                    "fixtures_master",
            }
        )

    provenance.append(
        {
            "season": season,
            "method":
                "local_event_fixture_crosswalk",
            "source":
                "pl_stats/*/events_stats + "
                "fixtures_master.csv",
            "notes":
                "Persistent club identity from "
                "local _teams_index.json.",
        }
    )


# ============================================================
# FINAL VALIDATION
# ============================================================

print()
print("=" * 82)
print("VALIDATING REGISTRY")
print("=" * 82)
print()

keys = [
    (
        row["season"],
        row["local_team_id"],
    )
    for row in registry
]

unique_keys = set(
    keys
)

print(
    f"Registry rows: "
    f"{len(registry)}"
)

print(
    f"Unique season/local-ID keys: "
    f"{len(unique_keys)}"
)

if len(registry) != 200:
    missing = sorted(
        fixture_team_seasons
        - unique_keys,
        key=lambda x: (
            x[0],
            int(x[1]),
        )
    )

    print()
    print(
        "MISSING MAPPINGS:"
    )

    for season, local_id in missing:
        print(
            f"  {season}: local_team_id={local_id}"
        )

    raise RuntimeError(
        f"Expected 200 verified mappings, "
        f"got {len(registry)}."
    )

if len(unique_keys) != 200:
    raise RuntimeError(
        "Duplicate season/local-team mappings."
    )

# Exactly 20 teams per season.
for season in SEASONS:

    season_rows = [
        row
        for row in registry
        if row["season"] == season
    ]

    if len(season_rows) != 20:
        raise RuntimeError(
            f"{season}: expected 20 mappings, "
            f"got {len(season_rows)}"
        )

# Every mapping must refer to a valid persistent club code.
unknown_codes = [
    row["persistent_team_code"]
    for row in registry
    if row["persistent_team_code"]
    not in persistent_names
]

if unknown_codes:
    raise RuntimeError(
        f"Unknown persistent team codes: "
        f"{unknown_codes}"
    )


# ============================================================
# WRITE
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

registry.sort(
    key=lambda row: (
        row["season"],
        int(row["local_team_id"]),
    )
)

registry_fields = [
    "team_season_id",
    "season",
    "club_id",
    "canonical_name",
    "persistent_team_code",
    "local_team_id",
    "source_name",
    "mapping_status",
    "mapping_source",
]

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8",
    newline="",
) as handle:

    writer = csv.DictWriter(
        handle,
        fieldnames=registry_fields,
    )

    writer.writeheader()
    writer.writerows(
        registry
    )


provenance_fields = [
    "season",
    "method",
    "source",
    "notes",
]

with open(
    PROVENANCE_FILE,
    "w",
    encoding="utf-8",
    newline="",
) as handle:

    writer = csv.DictWriter(
        handle,
        fieldnames=provenance_fields,
    )

    writer.writeheader()
    writer.writerows(
        provenance
    )


print()
print("=" * 82)
print("V0.4 ACCEPTANCE CHECK: PASS")
print("=" * 82)
print()
print(
    "Team-season records : 200"
)
print(
    "Verified mappings    : 200"
)
print(
    "Unresolved mappings  : 0"
)
print(
    "Duplicate mappings   : 0"
)
print()
print(
    f"Registry:   {OUTPUT_FILE}"
)
print(
    f"Provenance: {PROVENANCE_FILE}"
)
print()
