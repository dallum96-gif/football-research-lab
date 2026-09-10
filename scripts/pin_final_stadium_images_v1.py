from __future__ import annotations

import html
import json
import re
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REGISTRY = ROOT / "data" / "reference" / "club_profiles_v1.json"
IMAGE_DIR = ROOT / "web" / "public" / "club-profile"

IMAGE_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = (
    "Mozilla/5.0 "
    "(Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "Chrome/142 Safari/537.36 "
    "Football Research Laboratory/1.0"
)


TARGETS = [
    {
        "club": "Southampton",
        "stadium": "St Mary's Stadium",
        "page": "https://www.geograph.org.uk/photo/6950611",
        "photographer": "Robin Webster",
        "license": "CC BY-SA 2.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/2.0/",
        "geograph_id": "6950611",
    },
    {
        "club": "Swansea City",
        "stadium": "Swansea.com Stadium",
        "page": "https://www.geograph.org.uk/photo/4996438",
        "photographer": "Bill Boaden",
        "license": "CC BY-SA 2.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/2.0/",
        "geograph_id": "4996438",
    },
    {
        "club": "Tottenham Hotspur",
        "stadium": "Tottenham Hotspur Stadium",
        "page": "https://www.geograph.org.uk/photo/7398185",
        "photographer": "Bryn Holmes",
        "license": "CC BY-SA 2.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/2.0/",
        "geograph_id": "7398185",
    },
]


def fetch(url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=45,
    ) as response:
        return (
            response.read(),
            str(
                response.headers.get(
                    "Content-Type",
                    "",
                )
            ),
        )


def extract_image_url(
    page_html: str,
) -> str | None:
    patterns = [
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
        r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']twitter:image["\']',
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            page_html,
            flags=re.IGNORECASE,
        )

        if match:
            return html.unescape(
                match.group(1)
            )

    return None


with REGISTRY.open(
    "r",
    encoding="utf-8",
) as handle:
    document = json.load(handle)


profiles = document.get("profiles") or []


def profile_name(profile: dict) -> str:
    return str(
        profile.get("canonical_name") or ""
    ).replace("_", " ").strip()


successes = []


for target in TARGETS:
    club = target["club"]

    print()
    print(
        f"{club} - {target['stadium']}"
    )

    profile = next(
        (
            item
            for item in profiles
            if profile_name(item) == club
        ),
        None,
    )

    if profile is None:
        raise RuntimeError(
            f"Profile not found: {club}"
        )

    page_bytes, _ = fetch(
        target["page"]
    )

    page_html = page_bytes.decode(
        "utf-8",
        errors="replace",
    )

    image_url = extract_image_url(
        page_html
    )

    if not image_url:
        raise RuntimeError(
            f"Could not resolve Geograph image for {club}"
        )

    print(
        "  Geograph image resolved"
    )

    image_bytes, content_type = fetch(
        image_url
    )

    if len(image_bytes) < 15000:
        raise RuntimeError(
            f"Downloaded image too small for {club}: "
            f"{len(image_bytes)} bytes"
        )

    if "png" in content_type.casefold():
        extension = ".png"
    elif "webp" in content_type.casefold():
        extension = ".webp"
    else:
        extension = ".jpg"

    slug = re.sub(
        r"[^a-z0-9]+",
        "-",
        club.casefold(),
    ).strip("-")

    filename = (
        slug
        + "-stadium"
        + extension
    )

    destination = (
        IMAGE_DIR
        / filename
    )

    destination.write_bytes(
        image_bytes
    )

    visual = profile.get("visual")

    if not isinstance(visual, dict):
        visual = {}
        profile["visual"] = visual

    visual.update(
        {
            "hero_image":
                "/club-profile/" + filename,

            "hero_image_credit":
                (
                    target["photographer"]
                    + " / Geograph Britain and Ireland"
                ),

            "hero_image_licence":
                target["license"],

            "hero_image_licence_url":
                target["license_url"],

            "hero_image_source":
                target["page"],

            "hero_image_provider":
                "Geograph Britain and Ireland",

            "hero_image_geograph_id":
                target["geograph_id"],

            "hero_image_review_status":
                "PINNED_GEOGRAPH_DIRECT",

            "hero_image_retrieved":
                "2026-09-10",
        }
    )

    successes.append(club)

    print(
        f"  SAVED - {len(image_bytes):,} bytes"
    )


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


stadium_profiles = [
    profile
    for profile in profiles
    if isinstance(
        profile.get("stadium"),
        dict,
    )
    and str(
        profile["stadium"].get("name")
        or ""
    ).strip()
]


missing = [
    profile
    for profile in stadium_profiles
    if not str(
        (
            profile.get("visual")
            or {}
        ).get("hero_image")
        or ""
    ).strip()
]


print()
print("=" * 56)
print(
    "FINAL IMAGES ADDED: "
    + str(len(successes))
)
print(
    "TOTAL STADIUM COVERAGE: "
    + str(
        len(stadium_profiles)
        - len(missing)
    )
    + "/"
    + str(len(stadium_profiles))
)

if missing:
    print()
    print("STILL MISSING:")

    for profile in missing:
        print(
            "  "
            + profile_name(profile)
        )
else:
    print()
    print(
        "ALL 35 CLUB PROFILES NOW HAVE STADIUM IMAGERY."
    )