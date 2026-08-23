"""Read-only verified entity attachment audit for structurally eligible variables.

Uses only existing repository evidence and existing relationship contracts.
No inferred joins, no name-based joins, no canonical promotion.
"""
from __future__ import annotations
import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
ELIG = DATA / "variable_attachment_eligibility.csv"
OUT = DATA / "verified_entity_attachment_audit.csv"


def read(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        r = csv.DictReader(fh)
        return list(r)


def n(v): return str(v or "").strip()


def idx(rows):
    out = defaultdict(list)
    for r in rows:
        if n(r.get("field_name")):
            out[n(r["field_name"])].append(r)
    return out


def load(name):
    p = DATA / name
    return idx(read(p)) if p.is_file() else {}


def main():
    rows = read(ELIG)
    evidence = {
        "dictionary": load("frl_variable_dictionary.csv"),
        "relationship_matrix": load("variable_entity_relationship_matrix.csv"),
        "coverage": load("variable_entity_relationship_coverage.csv"),
        "team_v2": load("team_leaderboard_capability_map_v2.csv"),
        "team_delta": load("team_season_capability_delta.csv"),
        "player_map": load("player_season_capability_map.csv"),
        "player_semantic": load("player_season_semantic_decisions.csv"),
        "team_fixture": load("team_leaderboard_fixture_semantic_audit.csv"),
    }

    eligible = []
    for r in rows:
        p = n(r.get("player_eligibility"))
        f = n(r.get("fixture_eligibility"))
        t = n(r.get("team_eligibility"))
        if p == "GRAIN_COMPATIBLE" or f == "GRAIN_OR_CONTRACT_COMPATIBLE" or t == "GRAIN_OR_CONTRACT_COMPATIBLE":
            eligible.append(r)

    print("FRL VERIFIED ENTITY ATTACHMENT AUDIT")
    print("=" * 100)
    print(f"Eligibility rows: {len(rows)}")
    print(f"Structurally eligible rows: {len(eligible)}")
    print("Existing evidence only; verified means an existing explicit/contracted route is present in repository evidence.")

    counters = {e: Counter() for e in ("PLAYER", "FIXTURE", "TEAM")}
    out = []
    for r in eligible:
        field = n(r.get("field_name"))
        base = dict(r)
        for entity, elig_key, contracts in (
            ("PLAYER", "player_eligibility", {"player_season", "player_match"}),
            ("FIXTURE", "fixture_eligibility", {"team_match", "player_match", "fixture"}),
            ("TEAM", "team_eligibility", {"team_match", "team", "squad"}),
        ):
            eligibility = n(r.get(elig_key))
            if (entity == "PLAYER" and eligibility != "GRAIN_COMPATIBLE") or (entity != "PLAYER" and eligibility != "GRAIN_OR_CONTRACT_COMPATIBLE"):
                status = "NOT_STRUCTURALLY_ELIGIBLE"
                evidence_name = ""
            else:
                matches = []
                for name, ix in evidence.items():
                    for ev in ix.get(field, []):
                        relationship = n(ev.get("relationship_kind"))
                        contract = n(ev.get("identity_contract") or ev.get("relationship_contract"))
                        semantic = n(ev.get("semantic_status") or ev.get("decision_status") or ev.get("capability_status"))
                        status = n(ev.get("coverage_player_status" if entity == "PLAYER" else "coverage_fixture_status" if entity == "FIXTURE" else "coverage_club_status"))
                        if relationship or contract or semantic or status:
                            matches.append((name, relationship, contract, semantic, status))
                if not matches:
                    status = "ELIGIBLE_NO_EXPLICIT_EVIDENCE"
                    evidence_name = ""
                    contract = ""
                else:
                    explicit = [m for m in matches if m[2] or m[3] or m[4]]
                    if explicit:
                        m = sorted(explicit)[0]
                        contract, semantic, coverage = m[2], m[3], m[4]
                        status = "EXPLICIT_EVIDENCE_REQUIRES_REVIEW" if coverage in {"REVIEW", "UNSPECIFIED", ""} else "EXPLICIT_EVIDENCE_PRESENT"
                        evidence_name = m[0]
                    else:
                        status = "RELATIONSHIP_EVIDENCE_PRESENT_REVIEW"
                        evidence_name = sorted(matches)[0][0]
                        contract = sorted(matches)[0][2]
            counters[entity][status] += 1
            base[f"{entity.lower()}_verified_attachment_status"] = status
            base[f"{entity.lower()}_evidence_source"] = evidence_name
            if entity == "PLAYER": base["player_contract_evidence"] = contract if 'contract' in locals() else ""
            elif entity == "FIXTURE": base["fixture_contract_evidence"] = contract if 'contract' in locals() else ""
            else: base["team_contract_evidence"] = contract if 'contract' in locals() else ""
        out.append(base)

    print("\nPLAYER")
    for k,v in counters["PLAYER"].most_common(): print(f"  {v:4}  {k}")
    print("\nFIXTURE")
    for k,v in counters["FIXTURE"].most_common(): print(f"  {v:4}  {k}")
    print("\nTEAM")
    for k,v in counters["TEAM"].most_common(): print(f"  {v:4}  {k}")

    fields = sorted({k for r in out for k in r})
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader(); w.writerows(out)
    print(f"\nOutput: {OUT}")
    print("Evidence-only verified attachment audit; no inferred joins and no canonical promotion.")

if __name__ == "__main__": main()
