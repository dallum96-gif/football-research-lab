from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
MATRIX = DATA / "variable_entity_attachment_matrix.csv"
OUT = DATA / "variable_attachment_evidence_frontier.csv"


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        return rows, reader.fieldnames or []


def norm(v):
    return str(v or "").strip()


def index_by_field(path: Path):
    if not path.is_file():
        return {}
    rows, _ = read_csv(path)
    out = {}
    for row in rows:
        key = norm(row.get("field_name"))
        if key:
            out.setdefault(key, []).append(row)
    return out


def first_nonblank(row, names):
    for name in names:
        value = norm(row.get(name))
        if value:
            return value
    return ""


def explicit_evidence(field, sources):
    candidates = []
    for source_name, rows in sources.items():
        for row in rows:
            reason = first_nonblank(row, ("reason", "relationship_note", "notes", "decision_reason"))
            semantic = first_nonblank(row, ("semantic_status", "decision_status", "team_grain_decision", "capability_status"))
            contract = first_nonblank(row, ("identity_contract", "relationship_contract"))
            if reason or semantic or contract:
                candidates.append((source_name, semantic, reason or contract))
    if not candidates:
        return "", "NO_EXISTING_FIELD_REASON"
    source_name, semantic, reason = sorted(candidates)[0]
    return semantic, f"{source_name}: {reason}"


def main():
    if not MATRIX.is_file():
        raise SystemExit(f"Missing attachment matrix: {MATRIX}")

    rows, columns = read_csv(MATRIX)
    print("FRL VARIABLE ATTACHMENT EVIDENCE FRONTIER")
    print("=" * 100)
    print(f"Variables reviewed: {len(rows)}")
    print("MATRIX COLUMNS")
    for col in columns:
        print(f"  {col}")

    evidence_files = {
        "frl_variable_dictionary": DATA / "frl_variable_dictionary.csv",
        "relationship_matrix": DATA / "variable_entity_relationship_matrix.csv",
        "relationship_coverage": DATA / "variable_entity_relationship_coverage.csv",
        "team_capability_v2": DATA / "team_leaderboard_capability_map_v2.csv",
        "team_season_delta": DATA / "team_season_capability_delta.csv",
        "player_capability": DATA / "player_season_capability_map.csv",
        "player_semantic": DATA / "player_season_semantic_decisions.csv",
        "team_fixture_semantic": DATA / "team_leaderboard_fixture_semantic_audit.csv",
        "local_crosswalk": DATA / "local_identity_key_crosswalk.csv",
        "unmapped_grain": DATA / "unmapped_variable_grain_profile.csv",
    }
    indexes = {name: index_by_field(path) for name, path in evidence_files.items()}

    aliases = {
        "PLAYER": ("player_attachment", "player_status", "player_attachment_status"),
        "FIXTURE": ("fixture_attachment", "fixture_status", "fixture_attachment_status"),
        "TEAM": ("team_attachment", "team_status", "team_attachment_status", "club_attachment"),
    }
    resolved = {entity: next((c for c in names if c in columns), "") for entity, names in aliases.items()}

    print("\nSTATUS COLUMNS USED")
    for entity, col in resolved.items():
        print(f"  {entity:<8} {col or 'NONE_FOUND'}")

    counters = {e: Counter() for e in resolved}
    out_rows = []

    for row in rows:
        field = norm(row.get("field_name"))
        field_evidence = {name: idx.get(field, []) for name, idx in indexes.items()}
        base = dict(row)
        for entity, col in resolved.items():
            status = norm(row.get(col)) if col else ""
            if status == "REVIEW":
                code = "ATTACHMENT_REVIEW"
            elif status == "NOT_ESTABLISHED":
                code = "ATTACHMENT_NOT_ESTABLISHED"
            elif status:
                code = status
            else:
                code = "NO_STATUS_COLUMN"
            semantic, evidence = explicit_evidence(field, field_evidence)
            counters[entity][code] += 1
            base[f"{entity.lower()}_reason_code"] = code
            base[f"{entity.lower()}_evidence_semantic"] = semantic
            base[f"{entity.lower()}_evidence_source"] = evidence
        out_rows.append(base)

    print("\nSTATUS / EVIDENCE CODES")
    for entity, counter in counters.items():
        print(f"\n{entity}")
        for code, count in counter.most_common():
            print(f"  {count:4}  {code}")

    fields = list(dict.fromkeys([*columns] + [
        "player_reason_code", "player_evidence_semantic", "player_evidence_source",
        "fixture_reason_code", "fixture_evidence_semantic", "fixture_evidence_source",
        "team_reason_code", "team_evidence_semantic", "team_evidence_source",
    ]))
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"\nOutput: {OUT}")
    print("Evidence-only decomposition; existing field evidence only; no inferred attachment and no canonical promotion.")


if __name__ == "__main__":
    main()
