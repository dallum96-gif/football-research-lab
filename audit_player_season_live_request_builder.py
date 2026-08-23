"""Read-only audit of the live Player-Season request construction.

Purpose:
    Trace how the FRL/source-audit code constructs or records the live
    ``player_season_stats`` / ``player_leaderboard`` requests, looking for
    explicit season, competition, player, team, and identifier parameters.

This audit does not call external APIs, create identity mappings, or promote
any relationship. It only scans local Python source under the audit root and
reports matching source lines plus cached payload metadata fields that may
encode request context.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "data" / "live_pl_api_cache"

TERMS = (
    "player_season_stats",
    "player_leaderboard",
    "playerSeason",
    "player_season",
    "season=",
    "season_id",
    "seasonId",
    "competition",
    "competition_id",
    "competitionId",
    "player_id",
    "playerId",
    "element",
    "team_id",
    "teamId",
    "https://",
)


def scan_python() -> list[tuple[str, int, str]]:
    hits: list[tuple[str, int, str]] = []
    for path in sorted(ROOT.rglob("*.py")):
        if any(part in {".git", "__pycache__"} for part in path.parts):
            continue
        try:
            lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            if any(term.casefold() in line.casefold() for term in TERMS):
                hits.append((str(path.relative_to(ROOT)), i, line.strip()))
    return hits


def payload_metadata(path: Path) -> dict:
    if not path.is_file():
        return {"exists": False}
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"exists": True, "json_error": str(exc)}

    out = {
        "exists": True,
        "top_keys": sorted(payload.keys()) if isinstance(payload, dict) else [],
    }
    if isinstance(payload, dict):
        headers = payload.get("headers")
        out["header_keys"] = sorted(headers.keys()) if isinstance(headers, dict) else []
        p = payload.get("payload")
        if isinstance(p, dict):
            out["payload_keys"] = sorted(p.keys())
            # Report only fields whose names look like explicit context.
            context = {}
            def walk(obj, prefix=""):
                if not isinstance(obj, dict):
                    return
                for key, value in obj.items():
                    full = f"{prefix}.{key}" if prefix else key
                    if any(x in key.casefold() for x in ("season", "competition", "player", "team", "element")):
                        if isinstance(value, (str, int, float, bool)) or value is None:
                            context[full] = value
                    if isinstance(value, dict):
                        walk(value, full)
            walk(p)
            out["context_fields"] = context
    return out


def main() -> None:
    print("=" * 96)
    print("FRL PLAYER-SEASON LIVE REQUEST BUILDER AUDIT")
    print("=" * 96)
    print(f"Audit root: {ROOT}")
    print()

    hits = scan_python()
    print(f"Python source hits: {len(hits)}")
    for path, line_no, line in hits:
        print(f"  {path}:{line_no} :: {line}")

    print()
    for name in ("player_season_stats.json", "player_leaderboard.json"):
        path = CACHE / name
        info = payload_metadata(path)
        print(f"CACHE {name}")
        print(f"  exists={info.get('exists')}")
        if info.get("header_keys"):
            print("  header_context_keys=" + ", ".join(k for k in info["header_keys"] if any(x in k.casefold() for x in ("season", "competition", "player", "team", "element", "request", "url"))))
        context = info.get("context_fields", {})
        if context:
            for key, value in sorted(context.items()):
                print(f"  context {key} = {value!r}")
        else:
            print("  context fields: NONE")
        print()

    print("INTERPRETATION")
    print("  This audit reports implementation evidence only.")
    print("  It does not infer season from currentTeam, name, or player.id.")
    print("  It does not create Pulselive -> FPL or Pulselive -> FRL identity edges.")


if __name__ == "__main__":
    main()
