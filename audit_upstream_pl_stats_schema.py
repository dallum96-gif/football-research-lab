"""Fast, evidence-first audit of upstream historical PL/PulseLive CSV schemas.

The first pass deliberately samples representative files by grain/season instead
of making one HTTP request per historical file. If schema drift is discovered,
the drift report tells us exactly which seasons/grains need widening.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = ROOT / "data" / "upstream_pl_stats_variable_universe.csv"
API_TREE = "https://api.github.com/repos/imadeddine-belkat/Premier-League-Stats/git/trees/main?recursive=1"
RAW_BASE = "https://raw.githubusercontent.com/imadeddine-belkat/Premier-League-Stats/main/"

GRAIN_ORDER = ("team_match", "player_match", "player_season", "squad")


def request_json(url: str) -> object:
    req = urllib.request.Request(url, headers={"User-Agent": "FRL-upstream-pl-stats-audit"})
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.load(response)


def fetch_header(url: str) -> list[str]:
    req = urllib.request.Request(url, headers={"User-Agent": "FRL-upstream-pl-stats-audit"})
    with urllib.request.urlopen(req, timeout=30) as response:
        data = bytearray()
        while b"\n" not in data:
            chunk = response.read(16384)
            if not chunk:
                break
            data.extend(chunk)
            if len(data) > 1024 * 1024:
                break
    if not data:
        return []
    line = bytes(data).splitlines()[0].decode("utf-8-sig")
    return next(csv.reader(io.StringIO(line)))


def classify_path(path: str) -> str | None:
    if not path.endswith(".csv"):
        return None
    if "/events_stats/" in path or "/_merged/events/" in path:
        return "team_match"
    if "/players_match_stats/" in path:
        return "player_match"
    if "/players_stats/" in path:
        return "player_season"
    if "/squad/" in path:
        return "squad"
    return None


def season_from_path(path: str) -> str:
    for token in path.split("/"):
        if len(token) >= 7 and token[4] == "-":
            return token[:7]
    return "UNKNOWN"


def is_merged(path: str) -> bool:
    return "/_merged/" in path


def discover_files(tree_payload: dict) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in tree_payload.get("tree", []):
        if item.get("type") != "blob":
            continue
        path = str(item.get("path", ""))
        grain = classify_path(path)
        if not grain:
            continue
        rows.append({
            "path": path,
            "sha": str(item.get("sha", "")),
            "grain": grain,
            "season": season_from_path(path),
            "merged": "1" if is_merged(path) else "0",
            "raw_url": RAW_BASE + path,
        })
    return rows


def choose_representatives(files: list[dict[str, str]]) -> list[dict[str, str]]:
    """Choose a small but coverage-aware schema sample.

    For each grain we sample the earliest, middle, and latest seasons present,
    preferring merged files when available. We also include one non-merged file
    from the latest season to detect per-club shaping differences.
    """
    chosen: list[dict[str, str]] = []
    by_grain: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in files:
        by_grain[row["grain"]].append(row)

    for grain in GRAIN_ORDER:
        pool = sorted(by_grain.get(grain, []), key=lambda r: (r["season"], r["merged"], r["path"]))
        if not pool:
            continue
        seasons = sorted({r["season"] for r in pool if r["season"] != "UNKNOWN"})
        targets = []
        if seasons:
            targets = [seasons[0], seasons[len(seasons) // 2], seasons[-1]]
        for season in dict.fromkeys(targets):
            candidates = [r for r in pool if r["season"] == season]
            merged = [r for r in candidates if r["merged"] == "1"]
            chosen.append((merged or candidates)[0])
        latest_nonmerged = [r for r in pool if r["merged"] == "0" and r["season"] == seasons[-1]] if seasons else []
        if latest_nonmerged:
            chosen.append(latest_nonmerged[0])

    deduped = {}
    for row in chosen:
        deduped[row["path"]] = row
    return [deduped[k] for k in sorted(deduped)]


def audit(files: list[dict[str, str]], chosen: list[dict[str, str]]) -> list[dict[str, str]]:
    headers_by_path: dict[str, list[str]] = {}
    for row in chosen:
        try:
            headers_by_path[row["path"]] = fetch_header(row["raw_url"])
        except Exception:
            headers_by_path[row["path"]] = []

    grouped: dict[tuple[str, str], dict[str, object]] = {}
    for row in chosen:
        for field in headers_by_path[row["path"]]:
            key = (row["grain"], field)
            bucket = grouped.setdefault(key, {
                "grain": row["grain"],
                "field_name": field,
                "sampled_seasons": set(),
                "sampled_paths": [],
            })
            bucket["sampled_seasons"].add(row["season"])
            bucket["sampled_paths"].append(row["path"])

    out: list[dict[str, str]] = []
    for key in sorted(grouped):
        bucket = grouped[key]
        paths = sorted(set(bucket["sampled_paths"]))
        out.append({
            "source_surface": "PL_PULSELIVE_HISTORICAL",
            "resource": bucket["grain"],
            "grain": bucket["grain"],
            "field_name": bucket["field_name"],
            "sampled_seasons": ";".join(sorted(bucket["sampled_seasons"])),
            "sampled_paths": " | ".join(paths),
            "semantic_status": "UNCATALOGUED",
        })
    return out


def run(output: Path = DEFAULT_OUTPUT) -> tuple[int, int, int, int]:
    tree = request_json(API_TREE)
    if not isinstance(tree, dict):
        raise ValueError("Unexpected Git tree payload")
    files = discover_files(tree)
    chosen = choose_representatives(files)
    rows = audit(files, chosen)

    output.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0].keys()) if rows else [
        "source_surface", "resource", "grain", "field_name",
        "sampled_seasons", "sampled_paths", "semantic_status",
    ]
    with output.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    return len(files), len(chosen), len(rows), len({r["grain"] for r in chosen})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    files, sampled, variables, grains = run(args.output)
    print("FRL UPSTREAM PL_STATS VARIABLE-UNIVERSE AUDIT")
    print("=" * 90)
    print(f"CSV files discovered in Git tree: {files}")
    print(f"Representative CSV files sampled: {sampled}")
    print(f"Grains sampled: {grains}")
    print(f"Observed variables in sample: {variables}")
    print(f"Output: {args.output}")
    print("Header-only, stratified first pass; no historical data rows downloaded.")


if __name__ == "__main__":
    main()
