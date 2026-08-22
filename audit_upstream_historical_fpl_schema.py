"""Audit historical FPL CSV schemas published by the upstream repository.

Header-only discovery: downloads no data rows. Compares historical upstream
columns against the locally generated unresolved FPL queue.
"""
from __future__ import annotations

import csv
import io
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QUEUE = ROOT / "data" / "unmapped_variable_review_queue.csv"
OUTPUT = ROOT / "data" / "upstream_historical_fpl_schema_audit.csv"

API_BASE = "https://api.github.com/repos/imadeddine-belkat/Premier-League-Stats/contents/"
RAW_BASE = "https://raw.githubusercontent.com/imadeddine-belkat/Premier-League-Stats/main/"
MERGED_DIRS = (
    ("player", "fpl_scraper/fpl_stats/_merged/players"),
    ("team", "fpl_scraper/fpl_stats/_merged/teams"),
    ("fixture", "fpl_scraper/fpl_stats/_merged/fixtures"),
)


def fetch_json(url: str) -> object:
    request = urllib.request.Request(url, headers={"User-Agent": "FRL-historical-schema-audit"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def fetch_header(raw_url: str) -> list[str]:
    request = urllib.request.Request(raw_url, headers={"User-Agent": "FRL-historical-schema-audit"})
    with urllib.request.urlopen(request, timeout=60) as response:
        buf = bytearray()
        while True:
            chunk = response.read(8192)
            if not chunk:
                break
            buf.extend(chunk)
            if b"\n" in buf:
                break
    line = bytes(buf).splitlines()[0].decode("utf-8-sig")
    return next(csv.reader(io.StringIO(line)))


def terminal_name(field_name: str) -> str:
    text = (field_name or "").replace("[]", "")
    return text.split(".")[-1]


def discover_files() -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for grain, directory in MERGED_DIRS:
        payload = fetch_json(API_BASE + directory)
        if not isinstance(payload, list):
            continue
        for item in payload:
            if not isinstance(item, dict) or item.get("type") != "file":
                continue
            name = str(item.get("name", ""))
            if not name.endswith(".csv"):
                continue
            path = str(item.get("path", ""))
            out.append({
                "grain": grain,
                "season_file": name,
                "path": path,
                "raw_url": RAW_BASE + path,
            })
    return out


def load_queue(path: Path = QUEUE) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def audit(queue: list[dict[str, str]], files: list[dict[str, str]]) -> list[dict[str, str]]:
    header_cache: dict[str, list[str]] = {}
    rows: list[dict[str, str]] = []
    for file in files:
        header_cache[file["raw_url"]] = fetch_header(file["raw_url"])

    for row in queue:
        if row.get("source_surface") != "fpl":
            continue
        field = terminal_name(row.get("field_name", ""))
        matches: list[str] = []
        matched_grains: set[str] = set()
        for file in files:
            if field in header_cache[file["raw_url"]]:
                matches.append(file["season_file"])
                matched_grains.add(file["grain"])
        rows.append({
            "field_name": row.get("field_name", ""),
            "terminal_field": field,
            "historical_grains": ";".join(sorted(matched_grains)),
            "historical_season_files": ";".join(sorted(matches)),
            "historical_presence": "FOUND" if matches else "NOT_FOUND",
            "review_status": "OPEN",
            "resolution": "",
        })
    return rows


def run() -> int:
    queue = load_queue()
    files = discover_files()
    rows = audit(queue, files)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    columns = ["field_name", "terminal_field", "historical_grains", "historical_season_files", "historical_presence", "review_status", "resolution"]
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    found = sum(1 for r in rows if r["historical_presence"] == "FOUND")
    missing = len(rows) - found
    print("FRL UPSTREAM HISTORICAL FPL SCHEMA AUDIT")
    print("=" * 80)
    print(f"Unresolved FPL fields inspected: {len(rows)}")
    print(f"  FOUND_IN_HISTORICAL_SCHEMA {found}")
    print(f"  NOT_FOUND                 {missing}")
    print(f"Historical CSV files scanned: {len(files)}")
    print(f"Output: {OUTPUT}")
    print("Header-only evidence; no data rows downloaded or canonical promotion performed.")
    return len(rows)


if __name__ == "__main__":
    run()
