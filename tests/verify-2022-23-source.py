import csv
import urllib.request

LOCAL = r".\fixtures_master.csv"

def load_local():
    with open(
        LOCAL,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:
        return list(csv.DictReader(f))


def load_remote():
    url = (
        "https://raw.githubusercontent.com/"
        "vaastav/Fantasy-Premier-League/"
        "master/data/2022-23/fixtures.csv"
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


local = [
    r for r in load_local()
    if r["season"] == "2022-23"
]

remote = load_remote()

print()
print("=" * 90)
print("2022-23 LOCAL vs AUTHORITATIVE FPL CHECK")
print("=" * 90)
print()

print(f"Local rows:       {len(local)}")
print(f"Authoritative:    {len(remote)}")

def signature_local(row):
    return (
        row["fixture_id"],
        row["kickoff_time"],
        row["home_team_id"],
        row["away_team_id"],
        row["home_score"],
        row["away_score"],
        row["gameweek"],
    )

def signature_remote(row):
    return (
        row["id"],
        row["kickoff_time"],
        row["team_h"],
        row["team_a"],
        row["team_h_score"],
        row["team_a_score"],
        row["event"],
    )

local_sigs = {
    signature_local(r)
    for r in local
}

remote_sigs = {
    signature_remote(r)
    for r in remote
}

print(
    f"Exact signatures shared: "
    f"{len(local_sigs & remote_sigs)}"
)

print(
    f"Local-only signatures:   "
    f"{len(local_sigs - remote_sigs)}"
)

print(
    f"Remote-only signatures:  "
    f"{len(remote_sigs - local_sigs)}"
)

print()
print("=" * 90)
