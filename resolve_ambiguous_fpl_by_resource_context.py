"""Resolve ambiguous FPL structural cases using observed resource/path context.

Read-only reconciliation. A field is structurally resolved only when every
observed evidence path maps to one defensible grain. No semantic or canonical
promotion is performed.
"""
from __future__ import annotations

import csv
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "ambiguous_fpl_variable_audit.csv"
OUTPUT = ROOT / "data" / "ambiguous_fpl_resource_context_resolution.csv"


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def grain_from_evidence(resource: str, field_path: str) -> str:
    resource = resource.strip()
    path = (field_path or "").strip().lower()

    if resource == "fixtures":
        return "fixture"
    if resource == "event-live":
        return "player_match"
    if resource == "element-summary":
        if path.startswith("history"):
            return "player_season"
        if path.startswith("fixtures"):
            return "player_match"
        return "player"
    if resource == "bootstrap-static":
        root = path.replace("[]", "").split(".", 1)[0]
        return {
            "elements": "player",
            "teams": "team",
            "events": "gameweek",
            "element_types": "position_type",
            "phases": "phase",
            "chips": "gameweek",
            "game_settings": "game_settings",
            "game_config": "game_config",
            "scoring": "scoring_rules",
            "settings": "settings",
        }.get(root, "")
    return ""


def parse_evidence_paths(raw: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for token in (raw or "").split(" | "):
        token = token.strip()
        if not token or ":" not in token:
            continue
        resource, path = token.split(":", 1)
        pairs.append((resource, path))
    return pairs


def resolve(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in rows:
        pairs = parse_evidence_paths(row.get("evidence_paths", ""))
        grains = sorted({g for r, p in pairs if (g := grain_from_evidence(r, p))})
        base = dict(row)
        if len(grains) == 1:
            base.update({
                "resolved_grain": grains[0],
                "resolution_status": "STRUCTURALLY_RESOLVED",
                "resolution_basis": "observed resource/path context maps to one grain",
                "context_grains": ";".join(grains),
            })
        elif len(grains) > 1:
            base.update({
                "resolved_grain": "UNMAPPED_REVIEW",
                "resolution_status": "AMBIGUOUS_RESOURCE_CONTEXT",
                "resolution_basis": "observed resource/path context maps to multiple grains",
                "context_grains": ";".join(grains),
            })
        else:
            base.update({
                "resolved_grain": "UNMAPPED_REVIEW",
                "resolution_status": "NO_RESOLVABLE_RESOURCE_CONTEXT",
                "resolution_basis": "no recognised resource/path grain evidence",
                "context_grains": "",
            })
        out.append(base)
    return out


def run() -> int:
    rows = resolve(load_csv(INPUT))
    if not rows:
        raise ValueError("No ambiguous FPL rows found.")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0].keys())
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(r["resolution_status"] for r in rows)
    print("FRL AMBIGUOUS FPL RESOURCE-CONTEXT RESOLUTION")
    print("=" * 80)
    print(f"Ambiguous FPL fields inspected: {len(rows)}")
    for key in ("STRUCTURALLY_RESOLVED", "AMBIGUOUS_RESOURCE_CONTEXT", "NO_RESOLVABLE_RESOURCE_CONTEXT"):
        print(f"  {key:34s} {counts.get(key, 0)}")
    print(f"Output: {OUTPUT}")
    print("Resource/path evidence only; no semantic/canonical promotion.")
    return len(rows)


if __name__ == "__main__":
    run()
