from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REGISTRY = (
    ROOT
    / "data"
    / "reference"
    / "club_profiles_v1.json"
)

BACKFILL = (
    ROOT
    / "scripts"
    / "backfill_club_profile_context_v2.py"
)


with REGISTRY.open("r", encoding="utf-8") as handle:
    document = json.load(handle)


repaired_blocks = 0
merged_names = 0


def normalise_counts(counts: dict) -> list[dict]:
    global merged_names

    grouped: dict[str, dict] = {}

    for raw_name, raw_count in counts.items():
        name = str(raw_name).strip()

        if not name:
            continue

        try:
            count = int(raw_count)
        except (TypeError, ValueError):
            continue

        key = name.casefold()

        if key not in grouped:
            grouped[key] = {
                "name": name,
                "count": count,
            }
        else:
            grouped[key]["count"] += count
            merged_names += 1

    return sorted(
        grouped.values(),
        key=lambda item: (
            -item["count"],
            item["name"].casefold(),
        ),
    )


for profile in document.get("profiles") or []:
    leadership = (
        profile.get("leadership_by_season")
        or {}
    )

    if not isinstance(leadership, dict):
        continue

    for season_data in leadership.values():
        if not isinstance(season_data, dict):
            continue

        evidence = season_data.get(
            "captain_evidence"
        )

        if not isinstance(evidence, dict):
            continue

        counts = evidence.get("counts")

        if isinstance(counts, dict):
            evidence["observations"] = (
                normalise_counts(counts)
            )

            evidence.pop("counts", None)

            repaired_blocks += 1


# Pin reviewed Manchester City stadium image.
city = next(
    (
        profile
        for profile in document.get("profiles") or []
        if str(
            profile.get("canonical_name") or ""
        ).replace("_", " ").strip()
        == "Manchester City"
    ),
    None,
)

if city is None:
    raise SystemExit(
        "Manchester City profile not found."
    )


visual = city.get("visual")

if not isinstance(visual, dict):
    visual = {}
    city["visual"] = visual


visual.update(
    {
        "hero_image":
            "/club-profile/manchester-city-stadium.jpg",

        "hero_image_credit":
            (
                "Vojta.zurek / Wikimedia Commons "
                "- greyscale presentation by FRL"
            ),

        "hero_image_licence":
            "CC BY-SA 4.0",

        "hero_image_licence_url":
            (
                "https://creativecommons.org/"
                "licenses/by-sa/4.0/"
            ),

        "hero_image_source":
            (
                "https://commons.wikimedia.org/wiki/"
                "File:Etihad_Man._City_Stadium.jpg"
            ),
    }
)


# Verify that no JSON object anywhere still contains keys
# that collide case-insensitively. This ensures PowerShell
# ConvertFrom-Json can read the registry again.
collisions: list[str] = []


def audit_case_collisions(
    value,
    path: str = "$",
) -> None:
    if isinstance(value, dict):
        seen: dict[str, str] = {}

        for key, child in value.items():
            folded = str(key).casefold()

            if (
                folded in seen
                and seen[folded] != key
            ):
                collisions.append(
                    (
                        f"{path}: "
                        f"{seen[folded]!r} / "
                        f"{key!r}"
                    )
                )

            else:
                seen[folded] = key

            audit_case_collisions(
                child,
                f"{path}.{key}",
            )

    elif isinstance(value, list):
        for index, child in enumerate(value):
            audit_case_collisions(
                child,
                f"{path}[{index}]",
            )


audit_case_collisions(document)

if collisions:
    print(
        "Remaining case-insensitive key collisions:"
    )

    for collision in collisions:
        print("  " + collision)

    raise SystemExit(1)


with REGISTRY.open(
    "w",
    encoding="utf-8",
) as handle:
    json.dump(
        document,
        handle,
        indent=2,
        ensure_ascii=False,
    )
    handle.write("\n")


# Also repair the generator so a future rerun cannot
# recreate captain_evidence.counts.
if BACKFILL.is_file():
    source = BACKFILL.read_text(
        encoding="utf-8"
    )

    old = '''            "counts": captain_counts,
'''

    new = '''            "observations": [
                {
                    "name": name,
                    "count": count,
                }
                for name, count
                in sorted(
                    captain_counts.items(),
                    key=lambda item: (
                        -item[1],
                        item[0].casefold(),
                    ),
                )
            ],
'''

    if old in source:
        source = source.replace(
            old,
            new,
            1,
        )

        BACKFILL.write_text(
            source,
            encoding="utf-8",
        )


print(
    "Captain evidence blocks repaired: "
    f"{repaired_blocks}"
)

print(
    "Case-variant player names merged: "
    f"{merged_names}"
)

print(
    "Manchester City stadium image: PINNED"
)