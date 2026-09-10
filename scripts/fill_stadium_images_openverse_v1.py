from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

REGISTRY = ROOT / "data" / "reference" / "club_profiles_v1.json"
IMAGE_DIR = ROOT / "web" / "public" / "club-profile"
REPORT = ROOT / "data" / "reference" / "stadium_image_openverse_report_v1.json"

OPENVERSE = "https://api.openverse.engineering/v1/images/"

USER_AGENT = (
    "Football Research Laboratory/1.0 "
    "(private football research project)"
)

IMAGE_DIR.mkdir(parents=True, exist_ok=True)


TARGETS = {
    "Hull City": {
        "stadium": "MKM Stadium",
        "aliases": [
            "MKM Stadium",
            "KCOM Stadium",
            "KC Stadium",
        ],
    },
    "Liverpool": {
        "stadium": "Anfield",
        "aliases": ["Anfield"],
    },
    "Luton Town": {
        "stadium": "Kenilworth Road",
        "aliases": ["Kenilworth Road"],
    },
    "Manchester United": {
        "stadium": "Old Trafford",
        "aliases": ["Old Trafford"],
    },
    "Middlesbrough": {
        "stadium": "Riverside Stadium",
        "aliases": ["Riverside Stadium Middlesbrough"],
    },
    "Newcastle United": {
        "stadium": "St James' Park",
        "aliases": [
            "St James Park Newcastle",
            "St James' Park Newcastle",
        ],
    },
    "Norwich City": {
        "stadium": "Carrow Road",
        "aliases": ["Carrow Road"],
    },
    "Nottingham Forest": {
        "stadium": "City Ground",
        "aliases": [
            "City Ground Nottingham Forest",
            "Nottingham Forest City Ground",
        ],
    },
    "Sheffield United": {
        "stadium": "Bramall Lane",
        "aliases": ["Bramall Lane"],
    },
    "Southampton": {
        "stadium": "St Mary's Stadium",
        "aliases": [
            "St Mary's Stadium Southampton",
            "St Marys Stadium Southampton",
        ],
    },
    "Stoke City": {
        "stadium": "bet365 Stadium",
        "aliases": [
            "bet365 Stadium Stoke",
            "Britannia Stadium Stoke",
        ],
    },
    "Sunderland": {
        "stadium": "Stadium of Light",
        "aliases": [
            "Stadium of Light Sunderland",
        ],
    },
    "Swansea City": {
        "stadium": "Swansea.com Stadium",
        "aliases": [
            "Liberty Stadium Swansea",
            "Swansea.com Stadium",
        ],
    },
    "Tottenham Hotspur": {
        "stadium": "Tottenham Hotspur Stadium",
        "aliases": ["Tottenham Hotspur Stadium"],
    },
    "Watford": {
        "stadium": "Vicarage Road",
        "aliases": ["Vicarage Road Watford"],
    },
    "West Bromwich Albion": {
        "stadium": "The Hawthorns",
        "aliases": [
            "The Hawthorns West Bromwich",
            "Hawthorns West Brom",
        ],
    },
    "West Ham United": {
        "stadium": "London Stadium",
        "aliases": [
            "London Stadium West Ham",
            "Olympic Stadium West Ham",
        ],
    },
    "Wolverhampton Wanderers": {
        "stadium": "Molineux",
        "aliases": [
            "Molineux Stadium",
            "Molineux Wolverhampton",
        ],
    },
}


ALLOWED_LICENSES = {
    "by",
    "by-sa",
    "cc0",
    "pdm",
}


BLOCKED_TITLE_WORDS = {
    "logo",
    "badge",
    "crest",
    "shirt",
    "kit",
    "flag",
    "diagram",
    "map",
    "plan",
    "drawing",
    "render",
    "video game",
}


def club_name(profile: dict[str, Any]) -> str:
    return str(
        profile.get("canonical_name") or ""
    ).replace("_", " ").strip()


def words(value: str) -> set[str]:
    ignored = {
        "stadium",
        "football",
        "club",
        "city",
        "united",
        "the",
        "fc",
        "afc",
    }

    return {
        token
        for token in re.findall(
            r"[a-z0-9]+",
            value.casefold(),
        )
        if len(token) >= 3
        and token not in ignored
    }


def api_request(params: dict[str, Any]) -> dict[str, Any]:
    query = urllib.parse.urlencode(params)

    url = OPENVERSE + "?" + query

    waits = [2, 5, 15, 30, 60]

    for attempt, wait in enumerate(waits, start=1):
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=40,
            ) as response:
                return json.loads(
                    response.read().decode("utf-8")
                )

        except urllib.error.HTTPError as exc:
            if exc.code == 429 or 500 <= exc.code < 600:
                retry_after = exc.headers.get(
                    "Retry-After"
                )

                if retry_after:
                    try:
                        wait = max(
                            wait,
                            int(retry_after),
                        )
                    except ValueError:
                        pass

                print(
                    f"    Openverse HTTP {exc.code}; "
                    f"waiting {wait}s..."
                )

                time.sleep(wait)
                continue

            raise

        except Exception as exc:
            if attempt == len(waits):
                raise

            print(
                f"    Openverse request failed: {exc}; "
                f"waiting {wait}s..."
            )

            time.sleep(wait)

    raise RuntimeError(
        "Openverse request failed after retries."
    )


def result_score(
    result: dict[str, Any],
    club: str,
    aliases: list[str],
) -> int:
    title = str(
        result.get("title") or ""
    ).casefold()

    if any(
        blocked in title
        for blocked in BLOCKED_TITLE_WORDS
    ):
        return -1000

    license_code = str(
        result.get("license") or ""
    ).casefold()

    if license_code not in ALLOWED_LICENSES:
        return -1000

    if not result.get("license_url"):
        return -1000

    if not result.get("foreign_landing_url"):
        return -1000

    if not (
        result.get("url")
        or result.get("thumbnail")
    ):
        return -1000

    score = 0

    source = str(
        result.get("source") or ""
    ).casefold()

    if source == "geographorguk":
        score += 15
    elif source == "flickr":
        score += 7

    if str(
        result.get("category") or ""
    ).casefold() == "photograph":
        score += 5

    alias_match = False

    for alias in aliases:
        alias_lower = alias.casefold()

        if alias_lower in title:
            score += 35
            alias_match = True

        alias_tokens = words(alias)

        overlap = len(
            alias_tokens.intersection(
                words(title)
            )
        )

        score += overlap * 5

        if (
            alias_tokens
            and overlap == len(alias_tokens)
        ):
            alias_match = True

    club_tokens = words(club)

    score += (
        len(
            club_tokens.intersection(
                words(title)
            )
        )
        * 3
    )

    matched = {
        str(item).casefold()
        for item in (
            result.get("fields_matched")
            or []
        )
    }

    if "title" in matched:
        score += 5

    width = result.get("width")
    height = result.get("height")

    try:
        width = int(width or 0)
        height = int(height or 0)
    except (TypeError, ValueError):
        width = 0
        height = 0

    if width >= 1200:
        score += 4

    if width and height and width > height:
        score += 5

    if result.get("watermarked") is True:
        score -= 50

    # Avoid accepting a merely adjacent football image.
    if not alias_match:
        score -= 15

    return score


def search_target(
    club: str,
    aliases: list[str],
) -> tuple[dict[str, Any] | None, int]:
    candidates: dict[str, dict[str, Any]] = {}

    for alias in aliases:
        query = f"{alias} {club} football"

        payload = api_request(
            {
                "q": query,
                "source": "geographorguk,flickr",
                "page_size": 20,
                "page": 1,
            }
        )

        for result in payload.get(
            "results",
            [],
        ):
            identifier = str(
                result.get("id") or ""
            )

            if identifier:
                candidates[identifier] = result

        time.sleep(0.8)

    ranked = sorted(
        (
            (
                result_score(
                    result,
                    club,
                    aliases,
                ),
                result,
            )
            for result in candidates.values()
        ),
        key=lambda item: item[0],
        reverse=True,
    )

    if not ranked:
        return None, 0

    score, result = ranked[0]

    # Deliberately conservative.
    if score < 15:
        return None, score

    return result, score


def extension_from_type(
    content_type: str,
    url: str,
) -> str:
    content_type = content_type.casefold()

    if "png" in content_type:
        return ".png"

    if "webp" in content_type:
        return ".webp"

    if (
        "jpeg" in content_type
        or "jpg" in content_type
    ):
        return ".jpg"

    suffix = Path(
        urllib.parse.urlparse(url).path
    ).suffix.casefold()

    if suffix in {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }:
        return (
            ".jpg"
            if suffix == ".jpeg"
            else suffix
        )

    return ".jpg"


def download(
    result: dict[str, Any],
    club: str,
) -> str | None:
    urls = []

    if result.get("url"):
        urls.append(
            str(result["url"])
        )

    if result.get("thumbnail"):
        urls.append(
            str(result["thumbnail"])
        )

    slug = re.sub(
        r"[^a-z0-9]+",
        "-",
        club.casefold(),
    ).strip("-")

    for url in urls:
        waits = [2, 5, 15]

        for wait in waits:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                },
            )

            try:
                with urllib.request.urlopen(
                    request,
                    timeout=50,
                ) as response:
                    content = response.read()

                    if len(content) < 15000:
                        raise ValueError(
                            "Image was unexpectedly small."
                        )

                    extension = extension_from_type(
                        str(
                            response.headers.get(
                                "Content-Type",
                                "",
                            )
                        ),
                        url,
                    )

                filename = (
                    slug
                    + "-stadium"
                    + extension
                )

                destination = (
                    IMAGE_DIR
                    / filename
                )

                destination.write_bytes(content)

                return (
                    "/club-profile/"
                    + filename
                )

            except Exception:
                time.sleep(wait)

    return None


def license_label(
    result: dict[str, Any],
) -> str:
    code = str(
        result.get("license") or ""
    ).casefold()

    version = str(
        result.get("license_version") or ""
    ).strip()

    labels = {
        "by": "CC BY",
        "by-sa": "CC BY-SA",
        "cc0": "CC0",
        "pdm": "Public Domain Mark",
    }

    label = labels.get(
        code,
        code.upper(),
    )

    if (
        version
        and code not in {"pdm"}
    ):
        label += " " + version

    return label


with REGISTRY.open(
    "r",
    encoding="utf-8",
) as handle:
    document = json.load(handle)


profiles = document.get("profiles") or []

by_name = {
    club_name(profile): profile
    for profile in profiles
}


successes: list[dict[str, Any]] = []
failures: list[dict[str, Any]] = []


print()
print("OPENVERSE STADIUM IMAGE PASS")
print("=" * 56)


for club, target in TARGETS.items():
    profile = by_name.get(club)

    if not profile:
        failures.append(
            {
                "club": club,
                "reason": "Profile missing",
            }
        )
        continue

    visual = profile.get("visual")

    if not isinstance(visual, dict):
        visual = {}
        profile["visual"] = visual

    existing = str(
        visual.get("hero_image") or ""
    ).strip()

    if existing:
        print(
            f"{club}: already covered"
        )
        continue

    print()
    print(
        f"{club} - {target['stadium']}"
    )

    try:
        result, score = search_target(
            club,
            target["aliases"],
        )
    except Exception as exc:
        failures.append(
            {
                "club": club,
                "reason": (
                    "Openverse search failed: "
                    + str(exc)
                ),
            }
        )

        print("  SEARCH FAILED")
        continue

    if result is None:
        failures.append(
            {
                "club": club,
                "reason": (
                    "No sufficiently confident "
                    f"candidate; best score={score}"
                ),
            }
        )

        print(
            "  NO CONFIDENT CANDIDATE"
        )
        continue

    print(
        "  Candidate: "
        + str(result.get("title") or "")
    )

    print(
        "  Source: "
        + str(result.get("source") or "")
    )

    print(
        "  Creator: "
        + str(result.get("creator") or "")
    )

    print(
        "  License: "
        + license_label(result)
    )

    print(
        "  Score: "
        + str(score)
    )

    local_path = download(
        result,
        club,
    )

    if not local_path:
        failures.append(
            {
                "club": club,
                "reason": (
                    "Candidate found but image "
                    "download failed"
                ),
                "title": result.get("title"),
                "landing_page": result.get(
                    "foreign_landing_url"
                ),
            }
        )

        print("  DOWNLOAD FAILED")
        continue

    source = str(
        result.get("source") or ""
    )

    provider = str(
        result.get("provider") or ""
    )

    creator = str(
        result.get("creator") or ""
    ).strip()

    if not creator:
        creator = (
            "Source contributor"
        )

    visual.update(
        {
            "hero_image":
                local_path,

            "hero_image_credit":
                (
                    creator
                    + " / "
                    + source
                ),

            "hero_image_licence":
                license_label(result),

            "hero_image_licence_url":
                result.get("license_url"),

            "hero_image_source":
                result.get(
                    "foreign_landing_url"
                ),

            "hero_image_provider":
                provider,

            "hero_image_openverse_id":
                result.get("id"),

            "hero_image_review_status":
                (
                    "GEOGRAPH_SOURCE_CONFIRMED"
                    if source == "geographorguk"
                    else
                    "OPENVERSE_LICENSE_METADATA"
                ),

            "hero_image_retrieved":
                "2026-09-10",
        }
    )

    successes.append(
        {
            "club": club,
            "stadium": target[
                "stadium"
            ],
            "title": result.get(
                "title"
            ),
            "creator": creator,
            "source": source,
            "provider": provider,
            "license": license_label(
                result
            ),
            "license_url": result.get(
                "license_url"
            ),
            "landing_page": result.get(
                "foreign_landing_url"
            ),
            "score": score,
            "local_path": local_path,
        }
    )

    print("  DOWNLOADED")

    time.sleep(1.2)


document["openverse_stadium_pass"] = {
    "version": "1.0.0",
    "date": "2026-09-10",
    "sources": [
        "geographorguk",
        "flickr",
    ],
    "license_policy": [
        "by",
        "by-sa",
        "cc0",
        "pdm",
    ],
    "presentation": (
        "Existing FRL greyscale "
        "stadium treatment"
    ),
}


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
        profile["stadium"].get(
            "name"
        )
        or ""
    ).strip()
]


still_missing = [
    {
        "club": club_name(profile),
        "stadium": profile[
            "stadium"
        ].get("name"),
    }
    for profile in stadium_profiles
    if not str(
        (
            profile.get("visual")
            or {}
        ).get("hero_image")
        or ""
    ).strip()
]


report = {
    "version": "1.0.0",
    "date": "2026-09-10",
    "success_count": len(successes),
    "successes": successes,
    "failure_count": len(failures),
    "failures": failures,
    "coverage": {
        "covered": (
            len(stadium_profiles)
            - len(still_missing)
        ),
        "total": len(
            stadium_profiles
        ),
        "still_missing": still_missing,
    },
}


with REPORT.open(
    "w",
    encoding="utf-8",
) as handle:
    json.dump(
        report,
        handle,
        indent=2,
        ensure_ascii=False,
    )

    handle.write("\n")


print()
print("=" * 56)

print(
    "OPENVERSE IMAGES ADDED: "
    + str(len(successes))
)

print(
    "OPENVERSE FAILURES: "
    + str(len(failures))
)

print(
    "TOTAL STADIUM COVERAGE: "
    + str(
        len(stadium_profiles)
        - len(still_missing)
    )
    + "/"
    + str(len(stadium_profiles))
)

if still_missing:
    print()
    print(
        "STILL REQUIRING MANUAL REVIEW:"
    )

    for item in still_missing:
        print(
            "  "
            + item["club"]
            + " - "
            + str(item["stadium"])
        )

print()
print(
    "Report: "
    + str(REPORT)
)