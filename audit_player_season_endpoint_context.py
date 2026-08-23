from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

TARGETS = ["goals", "playerName", "season", "totalShots"]
CACHE_FILES = [
    ROOT / "data" / "live_pl_api_cache" / "player_season_stats.json",
    ROOT / "data" / "live_pl_api_cache" / "player_leaderboard.json",
]


def flatten(obj, prefix=""):
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else str(k)
            if isinstance(v, (dict, list)):
                out.extend(flatten(v, p))
            else:
                out.append((p, v))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:3]):
            out.extend(flatten(v, f"{prefix}[{i}]"))
    return out


def main():
    print("FRL PLAYER-SEASON ENDPOINT CONTEXT AUDIT")
    print("=" * 80)
    for path in CACHE_FILES:
        print(f"FILE: {path}")
        if not path.exists():
            print("  EXISTS=False")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        print(f"  EXISTS=True type={type(data).__name__}")
        print(f"  TOP_KEYS={list(data.keys()) if isinstance(data, dict) else []}")
        if isinstance(data, dict):
            headers = data.get("headers", {})
            payload = data.get("payload", {})
            print(f"  HEADER_KEYS={sorted(headers.keys()) if isinstance(headers, dict) else []}")
            # Record any obvious URL/request/season/competition/player metadata, but do not infer.
            flat = flatten(payload, "payload")
            for key, value in flat:
                lk = key.lower()
                if any(token in lk for token in ("season", "competition", "player", "team", "url", "request", "query", "endpoint")):
                    if not any(f"{t}." in key for t in TARGETS):
                        print(f"  {key} = {value}")
            for key, value in flat:
                for target in TARGETS:
                    if key.endswith("." + target) or key == target:
                        print(f"  TARGET {target}: {key} = {value}")
        print()

    print("INTERPRETATION")
    print("  Endpoint/request context is evidence only.")
    print("  No Pulselive player.id -> FPL element equivalence is inferred.")
    print("  No season is inferred from currentTeam or player identity alone.")


if __name__ == "__main__":
    main()
