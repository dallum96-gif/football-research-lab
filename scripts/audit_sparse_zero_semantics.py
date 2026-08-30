from __future__ import annotations

import argparse
import json
from pathlib import Path

from audit_source_routes import PAIR_CONFIG, SEASONS, direct_index, num, player_index


ZERO_EPSILON = 1e-9


def participating_rows(rows: list[dict] | tuple[dict, ...]) -> tuple[dict, ...]:
    result = []
    for row in rows:
        minutes = num(row.get("minutesPlayed"))
        if minutes is not None and minutes > 0:
            result.append(row)
    return tuple(result)


def strict_player_observation(rows, field: str) -> float | None:
    """Return a player-summed observation only when numeric player evidence exists.

    Unlike the general route audit, this function does not turn every blank
    player cell into zero. At least one participating player must contain an
    explicit numeric value for the field. Remaining blank participating-player
    cells are left implicit in the source representation; the result is used
    only as corroborating evidence, never as a production value.
    """
    active = participating_rows(rows)
    if not active or not any(field in row for row in active):
        return None

    observed = [num(row.get(field)) for row in active]
    numeric = [value for value in observed if value is not None]
    if not numeric:
        return None
    return sum(numeric)


def season_blank_audit(root: Path, season: str) -> dict[str, dict]:
    direct, direct_pairs, _ = direct_index(root, season)
    player, player_pairs, _ = player_index(root, season)
    result: dict[str, dict] = {}

    for direct_field, config in PAIR_CONFIG.items():
        if config["kind"] != "sparse_count":
            continue

        player_field = config["player"]
        blank_sides = 0
        independently_observed = 0
        corroborated_zero = 0
        contradicted_nonzero = 0
        unresolved = 0
        max_nonzero = 0.0
        contradiction_examples = []

        for pair, direct_match_id in direct_pairs.items():
            player_match_id = player_pairs.get(pair)
            for side in ("home", "away"):
                direct_row = direct[direct_match_id].get(side)
                if direct_row is None or direct_field not in direct_row:
                    continue
                if num(direct_row.get(direct_field)) is not None:
                    continue

                blank_sides += 1
                if player_match_id is None:
                    unresolved += 1
                    continue

                team_id = str(direct_row.get("team_id", "")).strip()
                player_value = strict_player_observation(
                    player[player_match_id].get(team_id, []),
                    player_field,
                )
                if player_value is None:
                    unresolved += 1
                    continue

                independently_observed += 1
                if abs(player_value) <= ZERO_EPSILON:
                    corroborated_zero += 1
                else:
                    contradicted_nonzero += 1
                    max_nonzero = max(max_nonzero, abs(player_value))
                    if len(contradiction_examples) < 8:
                        contradiction_examples.append(
                            {
                                "direct_match_id": direct_match_id,
                                "player_match_id": player_match_id,
                                "team_id": team_id,
                                "venue": side,
                                "player_sum": player_value,
                            }
                        )

        rate = (
            corroborated_zero / independently_observed
            if independently_observed
            else None
        )
        result[direct_field] = {
            "player_field": player_field,
            "direct_blank_team_sides": blank_sides,
            "independently_observed_player_sides": independently_observed,
            "corroborated_zero": corroborated_zero,
            "contradicted_nonzero": contradicted_nonzero,
            "unresolved": unresolved,
            "zero_corroboration_rate": rate,
            "max_contradicting_player_sum": max_nonzero,
            "contradiction_examples": contradiction_examples,
        }

    return result


def field_summary(seasons: dict[str, dict], field: str) -> dict:
    items = [seasons[season][field] for season in SEASONS]
    blanks = sum(item["direct_blank_team_sides"] for item in items)
    observed = sum(item["independently_observed_player_sides"] for item in items)
    zero = sum(item["corroborated_zero"] for item in items)
    contradictions = sum(item["contradicted_nonzero"] for item in items)
    unresolved = sum(item["unresolved"] for item in items)
    rate = zero / observed if observed else None

    if observed < 10:
        diagnostic = "INSUFFICIENT_INDEPENDENT_EVIDENCE"
    elif rate is not None and rate >= 0.995:
        diagnostic = "ZERO_STRONGLY_CORROBORATED"
    elif rate is not None and rate >= 0.95:
        diagnostic = "ZERO_MOSTLY_CORROBORATED_WITH_EXCEPTIONS"
    else:
        diagnostic = "MIXED_OR_CONTRADICTED"

    return {
        "direct_blank_team_sides": blanks,
        "independently_observed_player_sides": observed,
        "corroborated_zero": zero,
        "contradicted_nonzero": contradictions,
        "unresolved": unresolved,
        "zero_corroboration_rate": rate,
        "diagnostic": diagnostic,
        "production_rule_approved": False,
    }


def markdown(report: dict) -> str:
    lines = [
        "# FRL sparse-zero semantics audit",
        "",
        "Diagnostic corroboration only. This report does **not** approve blank-as-zero production semantics.",
        "",
        "The test asks a narrower question than the general route audit: when a direct team-match count field is blank, does the independent player-match representation contain explicit numeric evidence whose team sum is zero?",
        "",
        "## Decade summary",
        "",
        "| Direct field | Blank team-sides | Independently observed | Player sum = 0 | Player sum > 0 | Unresolved | Zero corroboration | Diagnostic |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]

    for field, item in report["summary"].items():
        rate = item["zero_corroboration_rate"]
        rate_text = "" if rate is None else f"{rate:.2%}"
        lines.append(
            f"| `{field}` | {item['direct_blank_team_sides']} | "
            f"{item['independently_observed_player_sides']} | {item['corroborated_zero']} | "
            f"{item['contradicted_nonzero']} | {item['unresolved']} | {rate_text} | "
            f"`{item['diagnostic']}` |"
        )

    lines += ["", "## By season", ""]
    lines.append(
        "| Field | Season | Direct blanks | Independent observations | Zero | Non-zero | Unresolved | Zero rate |"
    )
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for field in report["summary"]:
        for season in SEASONS:
            item = report["seasons"][season][field]
            if not item["direct_blank_team_sides"]:
                continue
            rate = item["zero_corroboration_rate"]
            rate_text = "" if rate is None else f"{rate:.2%}"
            lines.append(
                f"| `{field}` | {season} | {item['direct_blank_team_sides']} | "
                f"{item['independently_observed_player_sides']} | {item['corroborated_zero']} | "
                f"{item['contradicted_nonzero']} | {item['unresolved']} | {rate_text} |"
            )

    lines += [
        "",
        "## Interpretation rule",
        "",
        "`ZERO_STRONGLY_CORROBORATED` means the preserved player-match representation strongly supports the zero hypothesis for the direct blanks it can independently observe. It is still not a production missingness contract. Source-version disagreement, participant-level sparsity and field semantics must be reviewed before governance.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Corroborate candidate blank-as-zero semantics using preserved player-match evidence."
    )
    parser.add_argument("--pl-root", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, default=Path("sparse_zero_semantics.json"))
    parser.add_argument("--md-out", type=Path, default=Path("sparse_zero_semantics.md"))
    args = parser.parse_args()

    if not args.pl_root.is_dir():
        raise SystemExit(f"PL source root not found: {args.pl_root}")

    seasons = {
        season: season_blank_audit(args.pl_root, season)
        for season in SEASONS
    }
    fields = tuple(
        field
        for field, config in PAIR_CONFIG.items()
        if config["kind"] == "sparse_count"
    )
    report = {
        "schema_version": "1.0.0",
        "scope": "2016-17_to_2025-26",
        "live_api_calls": False,
        "method": "direct_blank_vs_strict_numeric_player_sum",
        "seasons": seasons,
        "summary": {
            field: field_summary(seasons, field)
            for field in fields
        },
        "warning": (
            "This is corroborating evidence only. No blank-as-zero production rule is approved by this audit."
        ),
    }

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    args.md_out.write_text(markdown(report), encoding="utf-8")

    print("FRL SPARSE-ZERO SEMANTICS AUDIT")
    for field, item in report["summary"].items():
        rate = item["zero_corroboration_rate"]
        rate_text = "n/a" if rate is None else f"{rate:.2%}"
        print(
            f"{field}: blanks={item['direct_blank_team_sides']} "
            f"observed={item['independently_observed_player_sides']} "
            f"zero={item['corroborated_zero']} nonzero={item['contradicted_nonzero']} "
            f"rate={rate_text} {item['diagnostic']}"
        )
    print(f"JSON: {args.json_out}")
    print(f"Markdown: {args.md_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
