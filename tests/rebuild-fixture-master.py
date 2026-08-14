import csv
import urllib.request
from pathlib import Path

ROOT = Path(r".")
RAW = ROOT / "fixtures_master.csv"
OUTPUT = ROOT / "fixtures_master_corrected.csv"

SEASONS_TO_REPLACE = {
    "2020-21",
    "2021-22",
}

URL_BASE = (
    "https://raw.githubusercontent.com/"
    "vaastav/Fantasy-Premier-League/"
    "master/data"
)

def load_local(path):
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with path.open(
                "r",
                encoding=enc,
                newline=""
            ) as f:
                return list(csv.DictReader(f))
        except UnicodeDecodeError:
            continue
    raise RuntimeError(f"Could not decode {path}")


def load_remote(season):
    url = (
        f"{URL_BASE}/{season}/fixtures.csv"
    )

    with urllib.request.urlopen(
        url,
        timeout=30
    ) as response:
        text = response.read().decode(
            "utf-8-sig"
        )

    return list(
        csv.DictReader(
            text.splitlines()
        )
    )


def convert_remote(season, rows):
    output = []

    if len(rows) != 380:
        raise RuntimeError(
            f"{season}: expected 380 remote fixtures, "
            f"got {len(rows)}"
        )

    for row in rows:

        output.append({
            "season": season,
            "fixture_id": row["id"],
            # Historical local master deliberately leaves
            # fixture_code blank; modern 2025-26 has its
            # own populated fixture_code generation.
            "fixture_code": "",
            "kickoff_time": row["kickoff_time"],
            "gameweek": row["event"],
            "home_team_id": row["team_h"],
            "away_team_id": row["team_a"],
            "home_score": (
                ""
                if row["team_h_score"] == ""
                else row["team_h_score"]
            ),
            "away_score": (
                ""
                if row["team_a_score"] == ""
                else row["team_a_score"]
            ),
        })

    return output


raw = load_local(RAW)

required = [
    "season",
    "fixture_id",
    "fixture_code",
    "kickoff_time",
    "gameweek",
    "home_team_id",
    "away_team_id",
    "home_score",
    "away_score",
]

if not raw:
    raise RuntimeError("Raw fixture master is empty.")

if any(
    column not in raw[0]
    for column in required
):
    raise RuntimeError(
        "Raw fixture master does not have "
        "the expected schema."
    )

replacement_rows = {}

for season in sorted(SEASONS_TO_REPLACE):

    print(
        f"Fetching authoritative {season}..."
    )

    remote = load_remote(season)

    replacement_rows[season] = (
        convert_remote(
            season,
            remote
        )
    )

    print(
        f"  {season}: "
        f"{len(replacement_rows[season])} rows"
    )


# Preserve all unaffected seasons exactly.
corrected = [
    row
    for row in raw
    if row["season"]
    not in SEASONS_TO_REPLACE
]

# Add corrected historical blocks.
for season in (
    "2020-21",
    "2021-22",
):
    corrected.extend(
        replacement_rows[season]
    )


# Stable sort.
corrected.sort(
    key=lambda row: (
        row["season"],
        int(row["fixture_id"]),
    )
)


if len(corrected) != len(raw):
    raise RuntimeError(
        "Corrected master row count changed."
    )

# Validate every season is exactly 380.
for season in sorted(
    {
        row["season"]
        for row in corrected
    }
):

    count = sum(
        1
        for row in corrected
        if row["season"] == season
    )

    if count != 380:
        raise RuntimeError(
            f"{season}: expected 380 rows, "
            f"got {count}"
        )


with OUTPUT.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=required
    )

    writer.writeheader()
    writer.writerows(corrected)


print()
print("=" * 90)
print("CORRECTED FIXTURE MASTER BUILT")
print("=" * 90)
print()
print(f"Raw rows:       {len(raw)}")
print(f"Corrected rows: {len(corrected)}")
print()
print(
    f"Replaced: 2020-21 and 2021-22 "
    f"from authoritative historical FPL fixtures"
)
print(
    f"Output: {OUTPUT}"
)
print()
print("Raw fixtures_master.csv was not modified.")
