from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IDENTITY_PATH = ROOT / "identity" / "team_seasons.csv"
REGISTRY_PATH = ROOT / "data" / "reference" / "club_profiles_v1.json"


with IDENTITY_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
    rows = list(csv.DictReader(handle))

identity_codes = {
    str(row["persistent_team_code"]).strip()
    for row in rows
    if str(row.get("persistent_team_code") or "").strip()
}

with REGISTRY_PATH.open("r", encoding="utf-8") as handle:
    document = json.load(handle)

profiles = document.get("profiles") or []

registry_codes = [
    str(profile.get("persistent_team_code") or "").strip()
    for profile in profiles
]

duplicates = sorted(
    {
        code
        for code in registry_codes
        if registry_codes.count(code) > 1
    }
)

missing = sorted(identity_codes - set(registry_codes))
extra = sorted(set(registry_codes) - identity_codes)

if duplicates:
    raise SystemExit(
        f"Duplicate persistent club profiles: {duplicates}"
    )

if missing:
    raise SystemExit(
        f"Persistent clubs missing from registry: {missing}"
    )

if extra:
    raise SystemExit(
        f"Registry contains unknown persistent clubs: {extra}"
    )

curated = [
    profile
    for profile in profiles
    if profile.get("status") == "CURATED"
]

pending = [
    profile
    for profile in profiles
    if profile.get("status") != "CURATED"
]

print(
    f"CLUB PROFILE REGISTRY: "
    f"{len(registry_codes)}/{len(identity_codes)} "
    f"persistent clubs registered"
)

print(
    f"CURATED: {len(curated)} | "
    f"PENDING CURATION: {len(pending)}"
)