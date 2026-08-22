"""Second-pass PL/PulseLive schema audit: one representative file per season/grain.

Header-only. Uses Git tree topology, extracts season labels from paths, and fetches
one representative CSV header per (grain, season), with a small fallback when the
first file is missing a schema. This is intended to detect historical schema drift
without crawling thousands of files.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = ROOT / "data" / "upstream_pl_stats_schema_by_season.csv"
API_TREE = "https://api.github.com/repos/imadeddine-belkat/Premier-League-Stats/git/trees/main?recursive=1"
RAW_BASE = "https://raw.githubusercontent.com/imadeddine-belkat/Premier-League-Stats/main/"
SEASON_RE = re.compile(r"(20\d{2}-\d{2})")


def request_json(url: str) -> object:
    req = urllib.request.Request(url, headers={"User-Agent": "FRL-upstream-pl-stats-audit"})
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.load(response)


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


def season_from_path(path: str) -> str | None:
    match = SEASON_RE.search(path)
    return match.group(1) if match else None


def discover(tree_payload: dict) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for item in tree_payload.get("tree", []):
        if item.get("type") != "blob":
            continue
        path = str(item.get("path", ""))
        grain = classify_path(path)
        season = season_from_path(path)
        if not grain or not season:
            continue
        out.append({"path": path, "sha": str(item.get("sha", "")), "grain": grain, "season": season, "raw_url": RAW_BASE + path})
    return out


def choose_representatives(files: list[dict[str, str]]) -> list[dict[str, str]]:
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for item in files:
        groups[(item["grain"], item["season"])].append(item)
    chosen: list[dict[str, str]] = []
    for key in sorted(groups):
        candidates = sorted(groups[key], key=lambda x: x["path"])
        chosen.append(candidates[0])
    return chosen


def fetch_header(url: str) -> list[str]:
    req = urllib.request.Request(url, headers={"User-Agent": "FRL-upstream-pl-stats-audit"})
    with urllib.request.urlopen(req, timeout=45) as response:
        data = bytearray()
        while b"\n" not in data:
            chunk = response.read(8192)
            if not chunk:
                break
            data.extend(chunk)
            if len(data) > 256_000:
                break
    if not data:
        return []
    line = bytes(data).splitlines()[0].decode("utf-8-sig")
    return next(csv.reader(io.StringIO(line)))


def audit(representatives: list[dict[str, str]], workers: int = 8) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(fetch_header, item["raw_url"]): item for item in representatives}
        for future in as_completed(futures):
            item = futures[future]
            try:
                headers = future.result()
                error = ""
            except Exception as exc:
                headers = []
                error = type(exc).__name__
            for field in headers:
                rows.append({
                    "source_surface": "PL_PULSELIVE_HISTORICAL",
                    "grain": item["grain"],
                    "season": item["season"],
                    "field_name": field,
                    "representative_path": item["path"],
                    "fetch_error": error,
                })
            if not headers:
                rows.append({
                    "source_surface": "PL_PULSELIVE_HISTORICAL",
                    "grain": item["grain"],
                    "season": item["season"],
                    "field_name": "",
                    "representative_path": item["path"],
                    "fetch_error": error or "EMPTY_HEADER",
                })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    tree = request_json(API_TREE)
    if not isinstance(tree, dict):
        raise ValueError("Unexpected Git tree payload")
    files = discover(tree)
    reps = choose_representatives(files)
    rows = audit(reps, workers=args.workers)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    columns = ["source_surface", "grain", "season", "field_name", "representative_path", "fetch_error"]
    with args.output.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r: (r["grain"], r["season"], r["field_name"])))

    variables = {(r["grain"], r["field_name"]) for r in rows if r["field_name"]}
    signatures: dict[tuple[str, str], set[str]] = defaultdict(set)
    for r in rows:
        if r["field_name"]:
            signatures[(r["grain"], r["season"])].add(r["field_name"])

    print("FRL UPSTREAM PL_STATS SEASON/GRAIN SCHEMA AUDIT")
    print("=" * 90)
    print(f"Relevant CSV files discovered: {len(files)}")
    print(f"Representative files sampled:  {len(reps)}")
    print(f"Season/grain groups:             {len(signatures)}")
    print(f"Observed grain+field variables: {len(variables)}")
    print(f"Output: {args.output}")
    print("Header-only; no historical data rows downloaded.")


if __name__ == "__main__":
    main()
