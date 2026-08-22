"""Enumerate the upstream historical PL/PulseLive CSV field universe.

Header-only discovery. Uses the recursive Git tree so file topology is audited
without downloading data rows. Identical blob SHAs are fetched once.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = ROOT / "data" / "upstream_pl_stats_variable_universe.csv"
CACHE = ROOT / "data" / ".cache_upstream_pl_stats_headers.json"

API_TREE = "https://api.github.com/repos/imadeddine-belkat/Premier-League-Stats/git/trees/main?recursive=1"
RAW_BASE = "https://raw.githubusercontent.com/imadeddine-belkat/Premier-League-Stats/main/"


def request_json(url: str) -> object:
    req = urllib.request.Request(url, headers={"User-Agent": "FRL-upstream-pl-stats-audit"})
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.load(response)


def classify_path(path: str) -> str | None:
    if not path.endswith(".csv"):
        return None
    if "/events_stats/" in path:
        return "team_match"
    if "/players_match_stats/" in path:
        return "player_match"
    if "/players_stats/" in path:
        return "player_season"
    if "/squad/" in path:
        return "squad"
    if "/_merged/events/" in path:
        return "team_match"
    return None


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
            "raw_url": RAW_BASE + path,
        })
    return rows


def fetch_header(url: str) -> list[str]:
    req = urllib.request.Request(url, headers={"User-Agent": "FRL-upstream-pl-stats-audit"})
    with urllib.request.urlopen(req, timeout=90) as response:
        data = bytearray()
        while b"\n" not in data:
            chunk = response.read(8192)
            if not chunk:
                break
            data.extend(chunk)
    if not data:
        return []
    line = bytes(data).splitlines()[0].decode("utf-8-sig")
    return next(csv.reader(io.StringIO(line)))


def load_cache() -> dict[str, list[str]]:
    if not CACHE.exists():
        return {}
    try:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_cache(cache: dict[str, list[str]]) -> None:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def audit(files: list[dict[str, str]], workers: int = 8) -> list[dict[str, str]]:
    cache = load_cache()
    by_sha: dict[str, dict[str, str]] = {}
    for item in files:
        by_sha.setdefault(item["sha"], item)

    missing = [(sha, item["raw_url"]) for sha, item in by_sha.items() if sha not in cache]
    if missing:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(fetch_header, url): sha for sha, url in missing}
            for future in as_completed(futures):
                sha = futures[future]
                try:
                    cache[sha] = future.result()
                except Exception:
                    cache[sha] = []
        save_cache(cache)

    grouped: dict[tuple[str, str], dict[str, object]] = {}
    for item in files:
        headers = cache.get(item["sha"], [])
        for field in headers:
            key = (item["grain"], field)
            bucket = grouped.setdefault(key, {
                "grain": item["grain"],
                "field_name": field,
                "paths": [],
                "file_count": 0,
                "blob_count": set(),
            })
            bucket["paths"].append(item["path"])
            bucket["file_count"] += 1
            bucket["blob_count"].add(item["sha"])

    out: list[dict[str, str]] = []
    for key in sorted(grouped):
        bucket = grouped[key]
        paths = sorted(set(bucket["paths"]))
        out.append({
            "source_surface": "PL_PULSELIVE_HISTORICAL",
            "resource": bucket["grain"],
            "grain": bucket["grain"],
            "field_name": bucket["field_name"],
            "file_count": str(bucket["file_count"]),
            "unique_blob_count": str(len(bucket["blob_count"])),
            "first_observed_path": paths[0] if paths else "",
            "last_observed_path": paths[-1] if paths else "",
            "observation_paths": " | ".join(paths),
            "semantic_status": "UNCATALOGUED",
        })
    return out


def run(output: Path = DEFAULT_OUTPUT, workers: int = 8) -> tuple[int, int, int]:
    tree = request_json(API_TREE)
    if not isinstance(tree, dict):
        raise ValueError("Unexpected Git tree payload")
    files = discover_files(tree)
    rows = audit(files, workers=workers)
    output.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0].keys()) if rows else [
        "source_surface", "resource", "grain", "field_name", "file_count",
        "unique_blob_count", "first_observed_path", "last_observed_path",
        "observation_paths", "semantic_status",
    ]
    with output.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    return len(files), len({f["sha"] for f in files}), len(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    files, blobs, variables = run(args.output, args.workers)
    print("FRL UPSTREAM PL_STATS VARIABLE-UNIVERSE AUDIT")
    print("=" * 90)
    print(f"CSV files discovered: {files}")
    print(f"Unique content blobs inspected: {blobs}")
    print(f"Deduplicated source variables: {variables}")
    print(f"Output: {args.output}")
    print("Counting is by grain + native field name; semantic equivalence is not assumed.")
    print("Header-only audit; no historical data rows downloaded.")


if __name__ == "__main__":
    main()
