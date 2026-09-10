from __future__ import annotations

import csv
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import query_api
from fixture_context_research import (
    FixtureContextUnavailableError,
    fixture_tactical_context,
)
from pulselive_fixture_evidence import (
    load_snapshot,
    normalise_lineups,
    resource_payload,
)
from source_family_adapters import resolve_source_match


REGISTRY = ROOT / "data" / "reference" / "club_profiles_v1.json"
IDENTITY = ROOT / "identity" / "team_seasons.csv"
IMAGE_DIR = ROOT / "web" / "public" / "club-profile"
REPORT = ROOT / "data" / "reference" / "club_profile_context_backfill_v2.json"
CSS_PATH = (
    ROOT
    / "web"
    / "src"
    / "app"
    / "teams"
    / "[season]"
    / "[teamCode]"
    / "TeamProfile.module.css"
)

IMAGE_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = "Football Research Laboratory/1.0"


def season_start(season: str) -> int:
    try:
        return int(str(season)[:4])
    except ValueError:
        return 9999


def clean_name(value: object) -> str:
    return str(value or "").replace("_", " ").strip()


def get_list(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]

    if isinstance(value, dict):
        for key in ("content", "items", "data", "players"):
            candidate = value.get(key)

            if isinstance(candidate, list):
                return [
                    item
                    for item in candidate
                    if isinstance(item, dict)
                ]

    return []


def normalise_key(value: str) -> str:
    return re.sub(r"[^a-z]", "", value.casefold())


def truthy_captain(value: Any) -> bool:
    if value is True:
        return True

    if isinstance(value, int) and value == 1:
        return True

    text = str(value or "").strip().casefold()

    return text in {
        "1",
        "true",
        "yes",
        "captain",
        "team captain",
        "c",
    }


def player_source_id(player: dict[str, Any]) -> str | None:
    value = (
        player.get("playerId")
        or player.get("player_id")
        or player.get("id")
    )

    text = str(value or "").strip()
    return text or None


def raw_player_name(player: dict[str, Any]) -> str | None:
    display = player.get("displayName")

    if isinstance(display, str) and display.strip():
        return display.strip()

    raw_name = player.get("name")

    if isinstance(raw_name, str) and raw_name.strip():
        return raw_name.strip()

    first = str(player.get("firstName") or "").strip()
    last = str(player.get("lastName") or "").strip()

    name = " ".join(
        part
        for part in (first, last)
        if part
    ).strip()

    return name or None


def player_has_captain_flag(player: dict[str, Any]) -> bool:
    explicit_keys = {
        "captain",
        "iscaptain",
        "captainflag",
        "teamcaptain",
    }

    for key, value in player.items():
        if normalise_key(str(key)) in explicit_keys:
            if truthy_captain(value):
                return True

    role = str(
        player.get("role")
        or player.get("type")
        or ""
    ).strip().casefold()

    return role in {
        "captain",
        "team captain",
    }


def explicit_captains(
    team: dict[str, Any],
    normalised_players: list[dict[str, Any]],
    side: str,
) -> list[dict[str, str | None]]:
    by_id: dict[str, str] = {}

    for item in normalised_players:
        if item.get("side") != side:
            continue

        source_id = str(
            item.get("source_player_id")
            or ""
        ).strip()

        name = str(item.get("name") or "").strip()

        if source_id and name:
            by_id[source_id] = name

    found: list[dict[str, str | None]] = []

    for player in get_list(team.get("players")):
        if not player_has_captain_flag(player):
            continue

        source_id = player_source_id(player)

        name = (
            by_id.get(source_id or "")
            or raw_player_name(player)
        )

        found.append(
            {
                "source_player_id": source_id,
                "name": name,
            }
        )

    # Also accept an explicit team-level captain/player reference.
    for key, value in team.items():
        normalised = normalise_key(str(key))

        if normalised not in {
            "captain",
            "captainid",
            "captainplayerid",
            "teamcaptain",
            "teamcaptainid",
        }:
            continue

        if isinstance(value, dict):
            source_id = player_source_id(value)
            name = (
                by_id.get(source_id or "")
                or raw_player_name(value)
            )

            if source_id or name:
                found.append(
                    {
                        "source_player_id": source_id,
                        "name": name,
                    }
                )

        elif not isinstance(value, bool):
            text = str(value or "").strip()

            if not text:
                continue

            if text in by_id:
                found.append(
                    {
                        "source_player_id": text,
                        "name": by_id[text],
                    }
                )
            else:
                for source_id, name in by_id.items():
                    if text.casefold() == name.casefold():
                        found.append(
                            {
                                "source_player_id": source_id,
                                "name": name,
                            }
                        )

    unique: dict[str, dict[str, str | None]] = {}

    for item in found:
        key = (
            str(item.get("source_player_id") or "")
            or str(item.get("name") or "").casefold()
        )

        if key:
            unique[key] = item

    return list(unique.values())


def manager_name(item: dict[str, Any]) -> str | None:
    first = str(item.get("first_name") or "").strip()
    last = str(item.get("last_name") or "").strip()

    name = " ".join(
        part
        for part in (first, last)
        if part
    ).strip()

    return name or None


def manager_rank(value: object) -> int:
    text = str(value or "").casefold()

    if "assistant" in text:
        return 0

    if "manager" in text or "head" in text:
        return 4

    if "coach" in text:
        return 3

    return 2


def choose_final_manager(
    observations: list[dict[str, Any]],
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    if not observations:
        return None, []

    fixture_counts = Counter(
        observation["name"]
        for observation in observations
    )

    history: list[dict[str, Any]] = []

    for name in sorted(fixture_counts):
        rows = [
            row
            for row in observations
            if row["name"] == name
        ]

        rows.sort(
            key=lambda row: (
                row["kickoff_time"],
                row["fixture_id"],
            )
        )

        history.append(
            {
                "name": name,
                "first_observed": rows[0]["kickoff_time"],
                "last_observed": rows[-1]["kickoff_time"],
                "fixtures_observed": len(
                    {
                        row["fixture_id"]
                        for row in rows
                    }
                ),
            }
        )

    ordered = sorted(
        observations,
        key=lambda row: (
            row["kickoff_time"],
            row["fixture_id"],
        ),
    )

    final_fixture = ordered[-1]["fixture_id"]

    candidates = [
        row
        for row in ordered
        if row["fixture_id"] == final_fixture
    ]

    distinct: dict[str, dict[str, Any]] = {}

    for candidate in candidates:
        name = candidate["name"]

        current = distinct.get(name)

        if (
            current is None
            or manager_rank(candidate.get("type"))
            > manager_rank(current.get("type"))
        ):
            distinct[name] = candidate

    ranked = sorted(
        distinct.values(),
        key=lambda row: (
            manager_rank(row.get("type")),
            fixture_counts[row["name"]],
        ),
        reverse=True,
    )

    if not ranked:
        return None, history

    if len(ranked) > 1:
        first_score = (
            manager_rank(ranked[0].get("type")),
            fixture_counts[ranked[0]["name"]],
        )

        second_score = (
            manager_rank(ranked[1].get("type")),
            fixture_counts[ranked[1]["name"]],
        )

        if first_score == second_score:
            return None, history

    return ranked[0], history


def choose_season_captain(
    observations: list[dict[str, Any]],
) -> tuple[dict[str, Any] | None, dict[str, int]]:
    if not observations:
        return None, {}

    by_fixture: dict[str, str] = {}

    for observation in observations:
        name = str(observation.get("name") or "").strip()

        if not name:
            continue

        fixture_id = observation["fixture_id"]

        current = by_fixture.get(fixture_id)

        if current is None:
            by_fixture[fixture_id] = name
        elif current != name:
            # Conflicting explicit captain evidence in one team fixture.
            by_fixture.pop(fixture_id, None)

    counts = Counter(by_fixture.values())

    if not counts:
        return None, {}

    ordered = counts.most_common()

    if (
        len(ordered) > 1
        and ordered[0][1] == ordered[1][1]
    ):
        return None, dict(counts)

    winner, count = ordered[0]

    return (
        {
            "name": winner,
            "count": count,
            "total": sum(counts.values()),
        },
        dict(counts),
    )


def http_json(
    endpoint: str,
    params: dict[str, object],
) -> dict[str, Any] | None:
    url = endpoint + "?" + urllib.parse.urlencode(params)

    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT},
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=25,
        ) as response:
            return json.loads(
                response.read().decode("utf-8")
            )
    except Exception:
        return None


def clean_html(value: object) -> str:
    text = str(value or "")

    text = re.sub(
        r"<[^>]+>",
        "",
        text,
    )

    return html.unescape(text).strip()


def licence_allowed(value: str) -> bool:
    text = value.casefold()

    return (
        text.startswith("cc ")
        or "creative commons" in text
        or "public domain" in text
    )


def commons_file_info(
    file_name: str,
) -> dict[str, Any] | None:
    title = (
        file_name
        if file_name.casefold().startswith("file:")
        else "File:" + file_name
    )

    payload = http_json(
        "https://commons.wikimedia.org/w/api.php",
        {
            "action": "query",
            "titles": title,
            "prop": "imageinfo",
            "iiprop": "url|mime|size|extmetadata",
            "iiurlwidth": 1600,
            "format": "json",
            "formatversion": 2,
        },
    )

    if not payload:
        return None

    pages = (
        payload.get("query", {})
        .get("pages", [])
    )

    if not pages:
        return None

    infos = pages[0].get("imageinfo") or []

    if not infos:
        return None

    info = infos[0]

    mime = str(info.get("mime") or "")

    if mime not in {
        "image/jpeg",
        "image/png",
        "image/webp",
    }:
        return None

    metadata = info.get("extmetadata") or {}

    licence = str(
        metadata.get(
            "LicenseShortName",
            {},
        ).get("value")
        or ""
    )

    if not licence_allowed(licence):
        return None

    artist = clean_html(
        metadata.get(
            "Artist",
            {},
        ).get("value")
    )

    licence_url = str(
        metadata.get(
            "LicenseUrl",
            {},
        ).get("value")
        or ""
    )

    if licence_url.startswith("//"):
        licence_url = "https:" + licence_url

    return {
        "url": info.get("thumburl") or info.get("url"),
        "source": info.get("descriptionurl"),
        "mime": mime,
        "width": info.get("width"),
        "height": info.get("height"),
        "credit": artist or "Wikimedia Commons contributor",
        "licence": licence,
        "licence_url": licence_url or None,
        "title": title,
    }


STADIUM_ARTICLE_ALIASES = {
    "Vitality Stadium": "Dean Court",
    "Gtech Community Stadium": "Brentford Community Stadium",
    "American Express Stadium": "Falmer Stadium",
    "Etihad Stadium": "City of Manchester Stadium",
    "Hill Dickinson Stadium": "Everton Stadium",
    "John Smith's Stadium": "Kirklees Stadium",
    "bet365 Stadium": "Bet365 Stadium",
}


def wikipedia_stadium_image(
    stadium: str,
) -> dict[str, Any] | None:
    title = STADIUM_ARTICLE_ALIASES.get(
        stadium,
        stadium,
    )

    payload = http_json(
        "https://en.wikipedia.org/w/api.php",
        {
            "action": "query",
            "titles": title,
            "redirects": 1,
            "prop": "pageimages",
            "piprop": "name|thumbnail|original",
            "pithumbsize": 1600,
            "format": "json",
            "formatversion": 2,
        },
    )

    if payload:
        pages = (
            payload.get("query", {})
            .get("pages", [])
        )

        if pages:
            file_name = pages[0].get("pageimage")

            if file_name:
                result = commons_file_info(
                    str(file_name)
                )

                if result:
                    return result

    return None


def commons_search_image(
    stadium: str,
    club: str,
) -> dict[str, Any] | None:
    payload = http_json(
        "https://commons.wikimedia.org/w/api.php",
        {
            "action": "query",
            "generator": "search",
            "gsrsearch": f'"{stadium}" {club} football stadium',
            "gsrnamespace": 6,
            "gsrlimit": 20,
            "prop": "imageinfo",
            "iiprop": "url|mime|size|extmetadata",
            "iiurlwidth": 1600,
            "format": "json",
            "formatversion": 2,
        },
    )

    if not payload:
        return None

    blocked = {
        "logo",
        "badge",
        "crest",
        "map",
        "diagram",
        "plan",
        "kit",
        "shirt",
        "flag",
        "drawing",
        "render",
    }

    stadium_tokens = {
        token
        for token in re.findall(
            r"[a-z0-9]+",
            stadium.casefold(),
        )
        if len(token) >= 4
        and token not in {"stadium"}
    }

    candidates: list[tuple[int, dict[str, Any]]] = []

    for page in (
        payload.get("query", {})
        .get("pages", [])
    ):
        title = str(page.get("title") or "")

        title_lower = title.casefold()

        if any(word in title_lower for word in blocked):
            continue

        infos = page.get("imageinfo") or []

        if not infos:
            continue

        info = infos[0]

        mime = str(info.get("mime") or "")

        if mime not in {
            "image/jpeg",
            "image/png",
            "image/webp",
        }:
            continue

        metadata = info.get("extmetadata") or {}

        licence = str(
            metadata.get(
                "LicenseShortName",
                {},
            ).get("value")
            or ""
        )

        if not licence_allowed(licence):
            continue

        score = 0

        for token in stadium_tokens:
            if token in title_lower:
                score += 3

        width = int(info.get("width") or 0)
        height = int(info.get("height") or 0)

        if width > height:
            score += 2

        if "stadium" in title_lower:
            score += 1

        artist = clean_html(
            metadata.get(
                "Artist",
                {},
            ).get("value")
        )

        licence_url = str(
            metadata.get(
                "LicenseUrl",
                {},
            ).get("value")
            or ""
        )

        if licence_url.startswith("//"):
            licence_url = "https:" + licence_url

        candidates.append(
            (
                score,
                {
                    "url": (
                        info.get("thumburl")
                        or info.get("url")
                    ),
                    "source": info.get("descriptionurl"),
                    "mime": mime,
                    "credit": (
                        artist
                        or "Wikimedia Commons contributor"
                    ),
                    "licence": licence,
                    "licence_url": licence_url or None,
                    "title": title,
                },
            )
        )

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return candidates[0][1]


def download_image(
    image: dict[str, Any],
    club: str,
) -> str | None:
    url = str(image.get("url") or "")

    if not url:
        return None

    mime = image["mime"]

    extension = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }.get(mime)

    if not extension:
        return None

    slug = re.sub(
        r"[^a-z0-9]+",
        "-",
        club.casefold(),
    ).strip("-")

    file_name = slug + "-stadium" + extension
    destination = IMAGE_DIR / file_name

    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT},
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=40,
        ) as response:
            content = response.read()

        if len(content) < 20000:
            return None

        destination.write_bytes(content)

        return "/club-profile/" + file_name
    except Exception:
        return None


with REGISTRY.open("r", encoding="utf-8") as handle:
    document = json.load(handle)

profiles = document.get("profiles") or []

profile_by_code = {
    str(profile.get("persistent_team_code") or "").strip(): profile
    for profile in profiles
}

with IDENTITY.open(
    "r",
    encoding="utf-8-sig",
    newline="",
) as handle:
    identity_rows = list(csv.DictReader(handle))

identity_by_local: dict[
    tuple[str, str],
    tuple[str, str],
] = {}

historical_team_seasons: set[
    tuple[str, str],
] = set()

for row in identity_rows:
    season = str(row.get("season") or "").strip()
    local_id = str(row.get("local_team_id") or "").strip()
    persistent_code = str(
        row.get("persistent_team_code")
        or ""
    ).strip()

    canonical_name = clean_name(
        row.get("canonical_name")
    )

    if not (
        season
        and local_id
        and persistent_code
    ):
        continue

    identity_by_local[
        (season, local_id)
    ] = (
        persistent_code,
        canonical_name,
    )

    if season_start(season) <= 2025:
        historical_team_seasons.add(
            (season, persistent_code)
        )


manager_observations: dict[
    tuple[str, str],
    list[dict[str, Any]],
] = defaultdict(list)

captain_observations: dict[
    tuple[str, str],
    list[dict[str, Any]],
] = defaultdict(list)

context_failures: list[dict[str, str]] = []

historical_seasons = sorted(
    {
        season
        for season, _ in historical_team_seasons
    }
)

fixture_count = 0
captain_flag_fixture_count = 0

print()
print("BACKFILLING HISTORICAL LEADERSHIP")
print("=" * 52)

for season in historical_seasons:
    payload = query_api.fixtures(
        season=season,
        limit=1000,
    )

    fixtures = payload.get("results") or []

    print(
        f"{season}: {len(fixtures)} fixtures"
    )

    for fixture in fixtures:
        fixture_id = str(
            fixture.get("fixture_id")
            or ""
        ).strip()

        if not fixture_id:
            continue

        fixture_count += 1

        kickoff_time = str(
            fixture.get("kickoff_time")
            or ""
        )

        try:
            context = fixture_tactical_context(
                season,
                fixture_id,
            )
        except (
            FixtureContextUnavailableError,
            FileNotFoundError,
            ValueError,
        ) as exc:
            context_failures.append(
                {
                    "season": season,
                    "fixture_id": fixture_id,
                    "error": str(exc),
                }
            )
            continue

        for manager in (
            context.get("managers", {})
            .get("items", [])
        ):
            local_id = str(
                manager.get("frl_team_id")
                or ""
            ).strip()

            identity = identity_by_local.get(
                (season, local_id)
            )

            name = manager_name(manager)

            if not identity or not name:
                continue

            persistent_code, _ = identity

            manager_observations[
                (season, persistent_code)
            ].append(
                {
                    "fixture_id": fixture_id,
                    "kickoff_time": kickoff_time,
                    "name": name,
                    "source_manager_id": manager.get(
                        "source_manager_id"
                    ),
                    "type": manager.get("type"),
                }
            )

        # Captain evidence: inspect the preserved source payload,
        # but only accept an explicit captain marker.
        try:
            resolved = resolve_source_match(
                season,
                fixture_id,
            )

            source_match_id = str(
                resolved["source_match_id"]
            )

            snapshot, _ = load_snapshot(
                source_match_id
            )

            if snapshot is None:
                continue

            lineup_payload = resource_payload(
                snapshot,
                "lineups",
            )

            if not isinstance(
                lineup_payload,
                dict,
            ):
                continue

            normalised = normalise_lineups(
                lineup_payload
            )

            side_data = (
                (
                    "home",
                    lineup_payload.get("homeTeam")
                    or lineup_payload.get("home_team"),
                    str(
                        fixture.get("home_team_id")
                        or ""
                    ).strip(),
                ),
                (
                    "away",
                    lineup_payload.get("awayTeam")
                    or lineup_payload.get("away_team"),
                    str(
                        fixture.get("away_team_id")
                        or ""
                    ).strip(),
                ),
            )

            for side, team, local_id in side_data:
                if not isinstance(team, dict):
                    continue

                identity = identity_by_local.get(
                    (season, local_id)
                )

                if not identity:
                    continue

                captains = explicit_captains(
                    team,
                    normalised.get("players") or [],
                    side,
                )

                if len(captains) != 1:
                    continue

                captain = captains[0]

                if not captain.get("name"):
                    continue

                captain_flag_fixture_count += 1

                persistent_code, _ = identity

                captain_observations[
                    (season, persistent_code)
                ].append(
                    {
                        "fixture_id": fixture_id,
                        "kickoff_time": kickoff_time,
                        "name": captain["name"],
                        "source_player_id": captain.get(
                            "source_player_id"
                        ),
                    }
                )

        except Exception:
            # Captain evidence is optional. A failure here does not
            # invalidate the manager evidence already collected.
            pass


manager_backfilled = 0
manager_existing = 0
manager_unresolved: list[dict[str, str]] = []

captain_backfilled = 0
captain_existing = 0
captain_unresolved: list[dict[str, str]] = []


for season, persistent_code in sorted(
    historical_team_seasons
):
    profile = profile_by_code.get(
        persistent_code
    )

    if not profile:
        continue

    leadership_by_season = profile.get(
        "leadership_by_season"
    )

    if not isinstance(
        leadership_by_season,
        dict,
    ):
        leadership_by_season = {}
        profile["leadership_by_season"] = (
            leadership_by_season
        )

    season_leadership = (
        leadership_by_season.get(season)
    )

    if not isinstance(
        season_leadership,
        dict,
    ):
        season_leadership = {}
        leadership_by_season[season] = (
            season_leadership
        )

    manager, manager_history = (
        choose_final_manager(
            manager_observations.get(
                (season, persistent_code),
                [],
            )
        )
    )

    existing_manager = (
        season_leadership.get("manager")
    )

    if (
        isinstance(existing_manager, dict)
        and existing_manager.get("name")
    ):
        manager_existing += 1
    elif manager:
        season_leadership["manager"] = {
            "name": manager["name"],
            "detail": (
                "Season-ending manager - observed in "
                "the final preserved league fixture"
            ),
        }

        manager_backfilled += 1

    else:
        _, club = next(
            (
                value
                for key, value
                in identity_by_local.items()
                if key[0] == season
                and value[0] == persistent_code
            ),
            (persistent_code, persistent_code),
        )

        manager_unresolved.append(
            {
                "season": season,
                "club": club,
            }
        )

    if manager_history:
        season_leadership[
            "manager_history"
        ] = manager_history

        season_leadership[
            "manager_evidence"
        ] = {
            "status": "OBSERVED",
            "source_family": (
                "PulseLive preserved match-centre snapshot"
            ),
            "selection": (
                "Manager attached to the final "
                "preserved league fixture"
            ),
        }

    captain, captain_counts = (
        choose_season_captain(
            captain_observations.get(
                (season, persistent_code),
                [],
            )
        )
    )

    existing_captain = (
        season_leadership.get("captain")
    )

    if (
        isinstance(existing_captain, dict)
        and existing_captain.get("name")
    ):
        captain_existing += 1
    elif captain:
        season_leadership["captain"] = {
            "name": captain["name"],
            "detail": (
                "Most frequent observed match captain "
                f"- {captain['count']}/"
                f"{captain['total']} explicit observations"
            ),
        }

        season_leadership[
            "captain_evidence"
        ] = {
            "status": "OBSERVED",
            "source_family": (
                "PulseLive preserved match-centre snapshot"
            ),
            "meaning": (
                "Most frequently explicitly flagged "
                "match captain; not asserted as a "
                "separately sourced official club captain"
            ),
            "observations": [
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
        }

        captain_backfilled += 1
    else:
        _, club = next(
            (
                value
                for key, value
                in identity_by_local.items()
                if key[0] == season
                and value[0] == persistent_code
            ),
            (persistent_code, persistent_code),
        )

        captain_unresolved.append(
            {
                "season": season,
                "club": club,
            }
        )


print()
print("RECOVERING STADIUM IMAGERY")
print("=" * 52)

images_downloaded = 0
images_existing = 0
images_missing: list[str] = []
image_details: list[dict[str, str]] = []

for profile in profiles:
    club = clean_name(
        profile.get("canonical_name")
    )

    stadium_data = profile.get("stadium")

    if not isinstance(
        stadium_data,
        dict,
    ):
        continue

    stadium = str(
        stadium_data.get("name")
        or ""
    ).strip()

    if not stadium:
        continue

    visual = profile.get("visual")

    if not isinstance(visual, dict):
        visual = {}
        profile["visual"] = visual

    existing_path = str(
        visual.get("hero_image")
        or ""
    ).strip()

    existing_file = None

    if existing_path.startswith(
        "/club-profile/"
    ):
        existing_file = (
            ROOT
            / "web"
            / "public"
            / existing_path.lstrip("/")
        )

    if (
        existing_path
        and (
            existing_file is None
            or existing_file.is_file()
        )
    ):
        images_existing += 1
        continue

    print(f"  {club}: {stadium}")

    image = wikipedia_stadium_image(
        stadium
    )

    method = "Wikipedia stadium article -> Commons"

    if image is None:
        image = commons_search_image(
            stadium,
            club,
        )
        method = "Commons search fallback"

    if image is None:
        images_missing.append(club)
        continue

    local_path = download_image(
        image,
        club,
    )

    if local_path is None:
        images_missing.append(club)
        continue

    visual.update(
        {
            "hero_image": local_path,
            "hero_image_credit": (
                image["credit"]
                + " / Wikimedia Commons"
            ),
            "hero_image_licence": image[
                "licence"
            ],
            "hero_image_licence_url": image[
                "licence_url"
            ],
            "hero_image_source": image[
                "source"
            ],
        }
    )

    image_details.append(
        {
            "club": club,
            "stadium": stadium,
            "source_file": str(
                image.get("title")
                or ""
            ),
            "method": method,
        }
    )

    images_downloaded += 1


document["context_backfill"] = {
    "version": "2.0.0",
    "date": "2026-09-10",
    "historical_manager_method": (
        "Season-ending manager from governed "
        "preserved PulseLive fixture context"
    ),
    "captain_method": (
        "Most frequent explicitly flagged match captain; "
        "no inference where the source does not expose a marker"
    ),
    "stadium_image_method": (
        "Wikipedia stadium article used for discovery, "
        "with licence verified against Wikimedia Commons "
        "before local acquisition"
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


greyscale_css_present = False

if CSS_PATH.is_file():
    css = CSS_PATH.read_text(
        encoding="utf-8"
    )

    greyscale_css_present = (
        "grayscale(1)" in css
    )


report = {
    "version": "2.0.0",
    "date": "2026-09-10",
    "fixtures_inspected": fixture_count,
    "context_failures": context_failures,
    "manager": {
        "historical_team_seasons": len(
            historical_team_seasons
        ),
        "backfilled": manager_backfilled,
        "already_present": manager_existing,
        "unresolved": manager_unresolved,
    },
    "captain": {
        "explicit_team_fixture_observations": (
            captain_flag_fixture_count
        ),
        "backfilled": captain_backfilled,
        "already_present": captain_existing,
        "unresolved": captain_unresolved,
        "note": (
            "Unresolved means FRL did not find "
            "sufficient explicit captain evidence; "
            "no captain was guessed."
        ),
    },
    "stadium_imagery": {
        "already_present": images_existing,
        "downloaded": images_downloaded,
        "still_missing": images_missing,
        "downloads": image_details,
        "greyscale_css_present": (
            greyscale_css_present
        ),
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
print("CONTEXT BACKFILL COMPLETE")
print("=" * 52)

print(
    "Historical managers backfilled: "
    f"{manager_backfilled}"
)

print(
    "Historical managers already present: "
    f"{manager_existing}"
)

print(
    "Historical manager gaps: "
    f"{len(manager_unresolved)}"
)

print(
    "Captain team-fixture observations: "
    f"{captain_flag_fixture_count}"
)

print(
    "Historical captains backfilled: "
    f"{captain_backfilled}"
)

print(
    "Historical captain gaps: "
    f"{len(captain_unresolved)}"
)

print(
    "Stadium images downloaded: "
    f"{images_downloaded}"
)

print(
    "Stadium images already present: "
    f"{images_existing}"
)

print(
    "Stadium images still missing: "
    f"{len(images_missing)}"
)

print(
    "Greyscale CSS present: "
    f"{greyscale_css_present}"
)

print()
print(f"Report: {REPORT}")