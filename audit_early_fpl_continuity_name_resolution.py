"""Read-only audit of early FPL element continuity with source-name resolution.

The FPL element is used only as an already-proven cross-season anchor. Because
an element can map to multiple source players across later seasons, an early
record is classified as resolved only when the early FPL name agrees with
exactly one candidate source player ID in that season. No canonical identity
is written or promoted.
"""
from __future__ import annotations

from collections import defaultdict
import unicodedata
import re

import player_identity_audit
import player_research

EARLY = ("2016-17", "2017-18", "2018-19", "2019-20")


def normalize(value: str | None) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.casefold().replace("'", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def distinct_fpl(season: str):
    out = {}
    for row in player_research._load_season_rows(season):
        element = str(row.get("element") or "").strip()
        if element:
            out.setdefault(element, row)
    return out


def later_anchor_map():
    report = player_identity_audit.run_audit()
    anchors = defaultdict(set)
    for result in report["seasons"].values():
        for item in result["exact"]:
            code = str(item.get("fpl_player_code") or "").strip()
            source = str(item.get("source_player_id") or "").strip()
            if code and source:
                anchors[code].add(source)
    return anchors


def early_source_names(season: str):
    by_id = defaultdict(set)
    for (_name, _team), values in player_identity_audit.source_player_index(season).items():
        for source_id, display in values:
            by_id[str(source_id)].add(str(display or ""))
    return by_id


def run():
    anchors = later_anchor_map()
    totals = defaultdict(int)

    print("=" * 96)
    print("FRL EARLY FPL ELEMENT CONTINUITY + NAME RESOLUTION AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 96)
    print(f"Later-season proven FPL elements: {len(anchors):,}")

    for season in EARLY:
        fpl = distinct_fpl(season)
        source_names = early_source_names(season)
        counts = defaultdict(int)
        examples = defaultdict(list)

        for element, row in fpl.items():
            ids = anchors.get(element, set())
            if not ids:
                counts["NO_ANCHOR"] += 1
                continue

            counts["ANCHORED"] += 1
            fpl_name = str(row.get("name") or player_research.display_player_name(row) or "").strip()
            fpl_norm = normalize(fpl_name)
            candidate_name_hits = []

            for source_id in sorted(ids):
                names = source_names.get(source_id, set())
                if any(normalize(name) == fpl_norm for name in names if name):
                    candidate_name_hits.append(source_id)

            if len(candidate_name_hits) == 1:
                counts["NAME_RESOLVED"] += 1
                if len(ids) > 1:
                    counts["AMBIGUOUS_BY_ELEMENT_RESOLVED_BY_NAME"] += 1
                if len(examples["RESOLVED_NAME"]) < 12:
                    examples["RESOLVED_NAME"].append((element, fpl_name, sorted(ids), candidate_name_hits[0]))
            elif len(candidate_name_hits) > 1:
                counts["NAME_AMBIGUOUS"] += 1
                if len(examples["NAME_AMBIGUOUS"]) < 8:
                    examples["NAME_AMBIGUOUS"].append((element, fpl_name, candidate_name_hits))
            else:
                counts["NO_NAME_RESOLUTION"] += 1
                if len(examples["NO_NAME_RESOLUTION"]) < 8:
                    examples["NO_NAME_RESOLUTION"].append((element, fpl_name, sorted(ids)))

        for key, value in counts.items():
            totals[key] += value
        totals["FPL"] += len(fpl)

        print(f"{season}: FPL={len(fpl):,} anchored={counts['ANCHORED']:,} name-resolved={counts['NAME_RESOLVED']:,} name-ambiguous={counts['NAME_AMBIGUOUS']:,} no-name-resolution={counts['NO_NAME_RESOLUTION']:,} no-anchor={counts['NO_ANCHOR']:,}")
        if examples["RESOLVED_NAME"]:
            print("  resolved sample:")
            for item in examples["RESOLVED_NAME"][:4]:
                print(f"    element={item[0]} | {item[1]} | anchored={item[2]} -> source={item[3]}")
        if examples["NAME_AMBIGUOUS"]:
            print("  ambiguous name sample:")
            for item in examples["NAME_AMBIGUOUS"][:4]:
                print(f"    element={item[0]} | {item[1]} | candidates={item[2]}")
        if examples["NO_NAME_RESOLUTION"]:
            print("  unresolved sample:")
            for item in examples["NO_NAME_RESOLUTION"][:4]:
                print(f"    element={item[0]} | {item[1]} | anchored={item[2]}")

    print("\nTOTALS:")
    print(f"  Early FPL identities:                     {totals['FPL']:,}")
    print(f"  Elements anchored elsewhere:              {totals['ANCHORED']:,}")
    print(f"  Name-resolved to one early source ID:     {totals['NAME_RESOLVED']:,}")
    print(f"  Ambiguous name among anchored IDs:        {totals['NAME_AMBIGUOUS']:,}")
    print(f"  Anchored but no name resolution:           {totals['NO_NAME_RESOLUTION']:,}")
    print(f"  No continuity anchor:                      {totals['NO_ANCHOR']:,}")
    print(f"  Ambiguous element anchors resolved by name:{totals['AMBIGUOUS_BY_ELEMENT_RESOLVED_BY_NAME']:,}")
    print("\nNo files were written or modified.")
    print("=" * 96)


if __name__ == "__main__":
    run()
