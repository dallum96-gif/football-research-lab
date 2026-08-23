"""Evidence-first audit of the live Premier League public web-data API surface.

Representative GETs only. The audit records response keys/resource families and
never promotes fields into the canonical FRL model. It intentionally uses a
conservative request rate and local cache.
"""
from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "data" / "live_pl_api_cache"
OUTPUT = ROOT / "data" / "live_premier_league_api_surface.csv"
SDP = "https://sdp-prem-prod.premier-league-prod.pulselive.com"
EDITORIAL = "https://api.premierleague.com"
STATIC = "https://resources.premierleague.com"

# Complete-season representative IDs from the reverse-engineered public API map.
COMPETITION = 8
SEASON = 2025  # 2025/26: complete season at audit design time.
TEAM = 14      # Liverpool
PLAYER = 223094
MATCH = 2561895

ENDPOINTS = [
    ("competition", f"{SDP}/api/v1/competitions/{COMPETITION}"),
    ("competition_teams", f"{SDP}/api/v1/competitions/{COMPETITION}/teams?_limit=5"),
    ("season_teams", f"{SDP}/api/v1/competitions/{COMPETITION}/seasons/{SEASON}/teams?_limit=5"),
    ("standings", f"{SDP}/api/v5/competitions/{COMPETITION}/seasons/{SEASON}/standings?live=false"),
    ("matches", f"{SDP}/api/v2/matches?competition={COMPETITION}&season={SEASON}&_limit=1"),
    ("match_detail", f"{SDP}/api/v2/matches/{MATCH}"),
    ("match_events", f"{SDP}/api/v1/matches/{MATCH}/events"),
    ("match_lineups", f"{SDP}/api/v3/matches/{MATCH}/lineups"),
    ("match_stats", f"{SDP}/api/v3/matches/{MATCH}/stats"),
    ("match_officials", f"{SDP}/api/v1/matches/{MATCH}/officials"),
    ("match_commentary", f"{SDP}/api/v1/matches/{MATCH}/commentary?_limit=2&_sort=timestamp:desc"),
    ("team_squad", f"{SDP}/api/v2/competitions/{COMPETITION}/seasons/{SEASON}/teams/{TEAM}/squad"),
    ("team_form", f"{SDP}/api/v1/competitions/{COMPETITION}/seasons/{SEASON}/teams/{TEAM}/form?competitions={COMPETITION}&seasons={SEASON}"),
    ("team_stats", f"{SDP}/api/v1/competitions/{COMPETITION}/teams/{TEAM}/stats"),
    ("player_directory", f"{SDP}/api/v1/competitions/{COMPETITION}/seasons/{SEASON}/players?_limit=1"),
    ("player_basic", f"{SDP}/api/v1/players/{PLAYER}/basic"),
    ("player_career", f"{SDP}/api/v1/players/{PLAYER}"),
    ("player_season_stats", f"{SDP}/api/v1/competitions/{COMPETITION}/seasons/{SEASON}/players/{PLAYER}/stats"),
    ("player_season_info", f"{SDP}/api/v1/competitions/{COMPETITION}/seasons/{SEASON}/playerinfo/{PLAYER}"),
    ("player_leaderboard", f"{SDP}/api/v3/competitions/{COMPETITION}/seasons/{SEASON}/players/stats/leaderboard?_sort=goals:desc&_limit=1"),
    ("team_leaderboard", f"{SDP}/api/v2/competitions/{COMPETITION}/teams/stats/leaderboard?_sort=goals:desc&season={SEASON}&_limit=1"),
    ("season_awards", f"{SDP}/api/v1/competitions/{COMPETITION}/seasons/{SEASON}/awards"),
    ("season_structure", f"{SDP}/api/v1/competitions/{COMPETITION}/seasons/{SEASON}/structure"),
    ("broadcast_match_events", f"{EDITORIAL}/broadcasting/match-events?{urlencode({'sportDataId': MATCH, 'pageSize': 5})}"),
    ("player_profile_content", f"{EDITORIAL}/content/premierleague/TEXT/en?{urlencode({'referenceExpression': f'SDP_FOOTBALL_PLAYER:{PLAYER}', 'tagNames': 'player_profile_bio', 'detail': 'DETAILED'})}"),
    ("current_gameweek_config", f"{STATIC}/premierleague25/config/current-gameweek.json"),
    ("clubs_metadata", f"{STATIC}/premierleague25/config/clubs-metadata.json"),
]


def _request_json(url: str) -> tuple[int, Any, dict[str, str]]:
    req = Request(url, headers={"User-Agent": "FRL-live-api-audit/1.0", "Accept": "application/json"})
    with urlopen(req, timeout=30) as response:
        status = int(response.status)
        payload = json.loads(response.read().decode("utf-8"))
        headers = {k.lower(): v for k, v in response.headers.items()}
        return status, payload, headers


def _cached(name: str) -> tuple[int, Any, dict[str, str]] | None:
    path = CACHE / f"{name}.json"
    if not path.exists():
        return None
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
        return int(obj["status"]), obj["payload"], obj.get("headers", {})
    except Exception:
        return None


def _save(name: str, status: int, payload: Any, headers: dict[str, str]) -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / f"{name}.json").write_text(
        json.dumps({"status": status, "payload": payload, "headers": headers}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _flatten(value: Any, prefix: str = "") -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            kind = "object" if isinstance(child, (dict, list)) else type(child).__name__
            out.append((path, kind))
            if isinstance(child, dict):
                out.extend(_flatten(child, path))
            elif isinstance(child, list) and child and isinstance(child[0], dict):
                out.extend(_flatten(child[0], f"{path}[]"))
    return out


def run() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for name, url in ENDPOINTS:
        cached = _cached(name)
        if cached:
            status, payload, headers = cached
            source = "CACHE"
        else:
            try:
                status, payload, headers = _request_json(url)
                _save(name, status, payload, headers)
                source = "LIVE"
            except Exception as exc:
                rows.append({
                    "endpoint_name": name, "url": url, "http_status": "ERROR",
                    "field_path": "", "field_type": "", "x_pulse_sdp_endpoint": "",
                    "rate_limit_remaining": "", "observation_source": "ERROR",
                    "error": str(exc),
                })
                time.sleep(0.25)
                continue

        endpoint_template = headers.get("x-pulse-sdp-endpoint", "")
        remaining = headers.get("x-ratelimit-remaining", "")
        flattened = _flatten(payload)
        if not flattened:
            flattened = [("", type(payload).__name__)]
        for field_path, field_type in flattened:
            rows.append({
                "endpoint_name": name,
                "url": url,
                "http_status": str(status),
                "field_path": field_path,
                "field_type": field_type,
                "x_pulse_sdp_endpoint": endpoint_template,
                "rate_limit_remaining": remaining,
                "observation_source": source,
                "error": "",
            })
        if source == "LIVE":
            time.sleep(0.25)
    return rows


def main() -> None:
    rows = run()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else [
            "endpoint_name", "url", "http_status", "field_path", "field_type",
            "x_pulse_sdp_endpoint", "rate_limit_remaining", "observation_source", "error"
        ])
        writer.writeheader()
        writer.writerows(rows)
    successful = sorted({r["endpoint_name"] for r in rows if r["http_status"] == "200"})
    print("FRL LIVE PREMIER LEAGUE API SURFACE AUDIT")
    print("=" * 90)
    print(f"Representative endpoints: {len(ENDPOINTS)}")
    print(f"Successful endpoints observed: {len(successful)}")
    print(f"Observed endpoint fields: {len(rows)}")
    print(f"Output: {OUTPUT}")
    print("Representative/live API discovery only; no semantic/canonical promotion.")


if __name__ == "__main__":
    main()
