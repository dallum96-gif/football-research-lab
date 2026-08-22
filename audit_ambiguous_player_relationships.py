"""Read-only audit of genuinely ambiguous FPL->source-player identities.

This report does not promote any identity. It surfaces only rows that the
canonical player_identity_audit classified as ambiguous, preserving all
candidate source IDs and names for evidence review.
"""
from __future__ import annotations

import player_identity_audit


def run():
    rows = []
    for season in player_identity_audit.SEASONS:
        report = player_identity_audit.audit_season(season)
        for item in report["ambiguous"]:
            rows.append(
                {
                    "season": season,
                    "fpl_player_code": str(item.get("fpl_player_code") or ""),
                    "fpl_name": str(item.get("fpl_name") or item.get("name") or ""),
                    "team_code": str(item.get("team_code") or ""),
                    "club": str(item.get("club") or ""),
                    "source_ids": tuple(item.get("source_ids") or ()),
                    "source_names": tuple(item.get("source_names") or ()),
                }
            )
    return rows


def print_report(rows):
    print("=" * 112)
    print("FRL AMBIGUOUS PLAYER RELATIONSHIP AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 112)
    print(f"Ambiguous relationships requiring review: {len(rows)}")
    print()
    for row in rows:
        print(
            f"{row['season']} | element={row['fpl_player_code']} | "
            f"FPL={row['fpl_name']} | team_code={row['team_code']} | "
            f"club={row['club']}"
        )
        print(f"  source IDs:   {list(row['source_ids'])}")
        print(f"  source names: {list(row['source_names'])}")
    print()
    print("No files were written or modified.")
    print("=" * 112)


if __name__ == "__main__":
    print_report(run())
