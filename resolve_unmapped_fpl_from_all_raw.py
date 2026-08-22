"""Resolve remaining FPL structural cases from all captured raw FPL JSON payloads.

Structural only. No semantic promotion and no canonical identity inference.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
QUEUE = ROOT / "data" / "unmapped_variable_review_queue.csv"
RAW_ROOT = ROOT / "raw_upstream" / "fpl"
OUTPUT = ROOT / "data" / "unmapped_variable_resolution_fpl_all_raw.csv"


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def terminal_name(field_name: str) -> str:
    text = field_name.replace("[]", "")
    return text.split(".")[-1]


def normalise_path(value: str) -> str:
    return value.strip()


def walk(value: Any, path: str = "") -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            if isinstance(child, (dict, list)):
                rows.append((child_path, "object", path))
                rows.extend(walk(child, child_path))
            else:
                rows.append((child_path, type(child).__name__, path))
    elif isinstance(value, list):
        item_path = f"{path}[]"
        for child in value[:3]:
            if isinstance(child, (dict, list)):
                rows.extend(walk(child, item_path))
            else:
                rows.append((item_path, type(child).__name__, path))
    return rows


def infer_family(relative_path: Path) -> str:
    parts = relative_path.parts
    if not parts:
        return "unknown"
    if parts[0] == "bootstrap-static.json":
        return "bootstrap-static"
    if parts[0] == "fixtures.json":
        return "fixtures"
    if parts[0] == "event-live":
        return "event-live"
    if parts[0] == "element-summary":
        return "element-summary"
    return parts[0]


def candidate_grains(family: str, path: str) -> set[str]:
    lower = path.lower()
    grains: set[str] = set()
    if family == "bootstrap-static":
        for marker, grain in {
            "elements": "player", "teams": "team", "events": "gameweek",
            "element_types": "position_type", "phases": "phase",
            "game_settings": "game_settings", "scoring": "scoring_rules", "settings": "settings",
            "chips": "gameweek",
        }.items():
            if lower == marker or lower.startswith(marker + ".") or lower.startswith(marker + "[]"):
                grains.add(grain)
    elif family == "fixtures":
        grains.add("fixture")
    elif family == "event-live":
        grains.add("player_match")
    elif family == "element-summary":
        if lower.startswith("history") or lower.startswith("history[]"):
            grains.add("player_season")
        elif lower.startswith("fixtures") or lower.startswith("fixtures[]"):
            grains.add("player_match")
        else:
            grains.add("player")
    return grains


def _build_occurrence_maps(root: Path) -> tuple[dict[str, list[dict[str, str]]], dict[str, list[dict[str, str]]]]:
    by_terminal: dict[str, list[dict[str, str]]] = {}
    by_path: dict[str, list[dict[str, str]]] = {}
    for path in sorted(root.rglob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        relative = path.relative_to(root)
        family = infer_family(relative)
        for field_path, field_type, parent_path in walk(payload):
            grains = candidate_grains(family, field_path)
            if not grains:
                continue
            evidence = {
                "resource": family,
                "field_path": field_path,
                "parent_path": parent_path,
                "field_type": field_type,
                "sample": str(path.relative_to(root)),
            }
            by_path.setdefault(field_path, []).append(evidence)
            field = terminal_name(field_path)
            for grain in grains:
                item = dict(evidence)
                item["grain"] = grain
                by_terminal.setdefault(field, []).append(item)
    return by_terminal, by_path


def build_occurrences(root: Path) -> dict[str, list[dict[str, str]]]:
    """Backward-compatible terminal-field occurrence map."""
    return _build_occurrence_maps(root)[0]


def resolve(
    queue_rows: list[dict[str, str]],
    occurrences: dict[str, list[dict[str, str]]],
    by_path: dict[str, list[dict[str, str]]] | None = None,
) -> list[dict[str, str]]:
    """Resolve queue rows using path evidence first, terminal evidence second.

    ``by_path`` is optional for backward compatibility with earlier tests/callers.
    """
    if by_path is None:
        by_path = {}

    out: list[dict[str, str]] = []
    for row in queue_rows:
        if row.get("source_surface") != "fpl":
            continue

        field_path = normalise_path(row.get("field_name", ""))
        terminal = terminal_name(field_path)
        exact_matches = by_path.get(field_path, [])
        terminal_matches = occurrences.get(terminal, [])

        base = dict(row)
        if exact_matches:
            resource = exact_matches[0].get("resource", "")
            family_matches = [m for m in terminal_matches if m.get("resource") == resource]
            grains = sorted({m.get("grain", "") for m in family_matches if m.get("grain")})
        else:
            family_matches = terminal_matches
            grains = sorted({m.get("grain", "") for m in terminal_matches if m.get("grain")})

        if len(grains) == 1:
            base.update({
                "resolved_grain": grains[0],
                "resolution_status": "STRUCTURALLY_RESOLVED",
                "resolution_basis": "exact JSON field path observed in captured raw FPL payload" if exact_matches else "terminal field observed at a single captured raw FPL grain",
                "upstream_matches": ";".join(grains),
                "evidence_paths": " | ".join(sorted({m["resource"] + ":" + m["field_path"] for m in family_matches})),
            })
        elif len(grains) > 1:
            base.update({
                "resolved_grain": "UNMAPPED_REVIEW",
                "resolution_status": "AMBIGUOUS_RAW_FPL_GRAIN",
                "resolution_basis": "exact JSON path observed, but resource context maps to multiple grains" if exact_matches else "terminal field observed at multiple defensible FPL grains",
                "upstream_matches": ";".join(grains),
                "evidence_paths": " | ".join(sorted({m["resource"] + ":" + m["field_path"] for m in family_matches})),
            })
        else:
            base.update({
                "resolved_grain": "UNMAPPED_REVIEW",
                "resolution_status": "NOT_FOUND_IN_ALL_CAPTURED_RAW_FPL",
                "resolution_basis": "terminal field not observed in captured raw FPL payloads",
                "upstream_matches": "",
                "evidence_paths": "",
            })
        out.append(base)

    return out


def run() -> int:
    queue = load_csv(QUEUE)
    if not RAW_ROOT.exists():
        raise FileNotFoundError(f"Raw FPL archive not found: {RAW_ROOT}")
    by_terminal, by_path = _build_occurrence_maps(RAW_ROOT)
    rows = resolve(queue, by_terminal, by_path)
    if not rows:
        raise ValueError("No unresolved FPL rows found")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0].keys())
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["resolution_status"]] = counts.get(row["resolution_status"], 0) + 1
    print("FRL UNMAPPED FPL ALL-RAW STRUCTURAL RESOLUTION")
    print("=" * 80)
    print(f"FPL unresolved rows inspected: {len(rows)}")
    for key in ("STRUCTURALLY_RESOLVED", "AMBIGUOUS_RAW_FPL_GRAIN", "NOT_FOUND_IN_ALL_CAPTURED_RAW_FPL"):
        print(f"  {key:36s} {counts.get(key, 0)}")
    print(f"Output: {OUTPUT}")
    print("Captured raw payloads only; no semantic/canonical promotion.")
    return len(rows)


if __name__ == "__main__":
    run()
