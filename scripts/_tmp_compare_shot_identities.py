from __future__ import annotations

import argparse
from pathlib import Path

from audit_source_routes import SEASONS, direct_index, num


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pl-root", type=Path, required=True)
    args = parser.parse_args()

    print("season,fully_observed,three_way_exact,two_way_exact,total_minus_on_off_mean,total_minus_on_off_unique")
    for season in SEASONS:
        matches, _, _ = direct_index(args.pl_root, season)
        observed = three = two = 0
        diffs = []
        for sides in matches.values():
            for side in ("home", "away"):
                row = sides.get(side)
                if row is None:
                    continue
                total = num(row.get("totalScoringAtt"))
                on = num(row.get("ontargetScoringAtt"))
                off = num(row.get("shotOffTarget"))
                blocked = num(row.get("blockedScoringAtt"))
                if None in (total, on, off, blocked):
                    continue
                observed += 1
                three += abs(total - on - off - blocked) <= 1e-9
                two += abs(total - on - off) <= 1e-9
                diffs.append(total - on - off)
        mean = sum(diffs) / len(diffs) if diffs else 0.0
        unique = sorted(set(diffs))
        print(f"{season},{observed},{three},{two},{mean:.6f},{unique[:20]}")

    print("\n2025-26 blank SOT rows")
    matches, _, _ = direct_index(args.pl_root, "2025-26")
    for match_id, sides in matches.items():
        for side in ("home", "away"):
            row = sides.get(side)
            if row is None or num(row.get("ontargetScoringAtt")) is not None:
                continue
            total = num(row.get("totalScoringAtt"))
            off = num(row.get("shotOffTarget"))
            blocked = num(row.get("blockedScoringAtt"))
            print({
                "match_id": match_id,
                "team": row.get("team"),
                "venue": side,
                "total": total,
                "off": off,
                "blocked": blocked,
                "two_way_inferred_sot": None if None in (total, off) else total - off,
                "three_way_inferred_sot": None if None in (total, off, blocked) else total - off - blocked,
            })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
