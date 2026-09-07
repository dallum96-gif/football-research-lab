from pathlib import Path
from datetime import datetime
import argparse
import csv
import os
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import query_lab
import source_family_adapters as sfa


SEASON = "2026-27"

STAGING = (
    ROOT
    / "data"
    / "staging"
    / "rich_player_season_stats_2026-27_gw3.csv"
)

PRODUCTION = (
    ROOT
    / "data"
    / "rich_player_season_stats.csv"
)

EXPECTED_FIXTURES = 30
EXPECTED_PARTICIPANTS = 387

CARRY_QUARTET = {
    "ball_carries",
    "progressive_carries",
    "progressive_carry_distance",
    "total_progression",
}


def read_csv(path: Path) -> tuple[list[dict], list[str]]:
    if not path.is_file():
        raise RuntimeError(
            f"Required CSV not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:

        reader = csv.DictReader(handle)

        return (
            [dict(row) for row in reader],
            list(reader.fieldnames or []),
        )


def number(value):
    if value in (None, ""):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def staging_state():
    rows, fields = read_csv(STAGING)

    current = [
        row
        for row in rows
        if str(
            row.get("season") or ""
        ).strip() == SEASON
    ]

    if len(current) != EXPECTED_PARTICIPANTS:
        raise RuntimeError(
            "Staging row count is "
            f"{len(current)}, expected "
            f"{EXPECTED_PARTICIPANTS}."
        )

    player_codes = [
        str(
            row.get("player_code")
            or ""
        ).strip()
        for row in current
    ]

    source_ids = [
        str(
            row.get("source_player_id")
            or ""
        ).strip()
        for row in current
    ]

    if (
        "" in player_codes
        or "" in source_ids
    ):
        raise RuntimeError(
            "Blank current player identity "
            "found in staging."
        )

    if len(set(player_codes)) != EXPECTED_PARTICIPANTS:
        raise RuntimeError(
            "Staged player_code values are "
            "not unique."
        )

    if len(set(source_ids)) != EXPECTED_PARTICIPANTS:
        raise RuntimeError(
            "Staged source_player_id values "
            "are not unique."
        )

    if set(player_codes) != set(source_ids):
        raise RuntimeError(
            "Staged player_code and "
            "source_player_id universes differ."
        )

    for metric in CARRY_QUARTET:

        if metric not in fields:
            raise RuntimeError(
                f"Staging is missing expected "
                f"column {metric}."
            )

        populated = [
            row
            for row in current
            if row.get(metric) not in (
                None,
                "",
            )
        ]

        if populated:
            raise RuntimeError(
                f"{metric} unexpectedly contains "
                "current values."
            )

    xgot_observed = sum(
        number(
            row.get("xgot")
        )
        is not None
        for row in current
    )

    return {
        "rows": current,
        "fields": fields,
        "codes": set(player_codes),
        "xgot_observed": xgot_observed,
    }


def expected_fixture_codes():

    codes = set()

    for fixture_id in range(
        1,
        EXPECTED_FIXTURES + 1,
    ):

        fixture = sfa.canonical_fixture(
            SEASON,
            str(fixture_id),
        )

        if fixture is None:
            raise RuntimeError(
                "Canonical fixture missing: "
                f"{fixture_id}"
            )

        code = str(
            fixture.get("fixture_code")
            or ""
        ).strip()

        if not code:
            raise RuntimeError(
                "Canonical fixture has no "
                f"fixture_code: {fixture_id}"
            )

        codes.add(code)

    if len(codes) != EXPECTED_FIXTURES:
        raise RuntimeError(
            "Canonical current fixture-code "
            f"universe is {len(codes)}, "
            f"expected {EXPECTED_FIXTURES}."
        )

    return codes


def fpl_state():

    rows, source_file, _ = (
        query_lab.load_player_rows(
            SEASON
        )
    )

    fixture_codes = {
        str(
            row.get("fixture_code")
            or ""
        ).strip()
        for row in rows
        if str(
            row.get("fixture_code")
            or ""
        ).strip()
    }

    participants = {
        str(
            row.get("player_code")
            or ""
        ).strip()
        for row in rows
        if (
            number(
                row.get("minutes")
            )
            or 0
        ) > 0
        and str(
            row.get("player_code")
            or ""
        ).strip()
    }

    all_codes = {
        str(
            row.get("player_code")
            or ""
        ).strip()
        for row in rows
        if str(
            row.get("player_code")
            or ""
        ).strip()
    }

    return {
        "rows": rows,
        "source_file": source_file,
        "fixtures": fixture_codes,
        "participants": participants,
        "all_codes": all_codes,
    }


def readiness():

    staging = staging_state()
    fpl = fpl_state()

    expected_fixtures = (
        expected_fixture_codes()
    )

    matched_fixtures = (
        expected_fixtures
        & fpl["fixtures"]
    )

    missing_fixtures = (
        expected_fixtures
        - fpl["fixtures"]
    )

    missing_participants = (
        staging["codes"]
        - fpl["participants"]
    )

    extra_participants = (
        fpl["participants"]
        - staging["codes"]
    )

    reasons = []

    if missing_fixtures:

        reasons.append(
            "FPL data does not yet contain all "
            "30 completed GW1-3 fixtures."
        )

    if missing_participants:

        reasons.append(
            "FPL participant universe is missing "
            f"{len(missing_participants)} "
            "PulseLive participants."
        )

    if extra_participants:

        reasons.append(
            "FPL participant universe contains "
            f"{len(extra_participants)} "
            "participants outside the staged "
            "PulseLive universe."
        )

    ready = not reasons

    print(
        "=== CURRENT PLAYER PROMOTION GATE ==="
    )

    print()
    print(
        "staged rich players =",
        len(staging["codes"]),
    )

    print(
        "staged xGOT observed =",
        f"{staging['xgot_observed']}/"
        f"{EXPECTED_PARTICIPANTS}",
    )

    print(
        "FPL source =",
        fpl["source_file"],
    )

    print(
        "FPL player codes =",
        len(fpl["all_codes"]),
    )

    print(
        "FPL participants =",
        len(fpl["participants"]),
    )

    print(
        "FPL GW1-3 fixture coverage =",
        f"{len(matched_fixtures)}/"
        f"{EXPECTED_FIXTURES}",
    )

    print(
        "staged participants missing "
        "from FPL =",
        len(missing_participants),
    )

    print(
        "extra FPL participants =",
        len(extra_participants),
    )

    if missing_participants:

        print()
        print(
            "Missing participant IDs:"
        )

        print(
            "  "
            + ", ".join(
                sorted(
                    missing_participants
                )
            )
        )

    print()

    if ready:

        print(
            "PROMOTION READY: YES"
        )

        print(
            "FPL and PulseLive are aligned "
            "on the GW1-3 analytical window."
        )

    else:

        print(
            "PROMOTION READY: NO"
        )

        for reason in reasons:
            print(
                "  -",
                reason,
            )

        print()
        print(
            "Production rich-player package "
            "remains untouched."
        )

    return {
        "ready": ready,
        "staging": staging,
        "fpl": fpl,
    }


def promote(state):

    if not state["ready"]:
        raise RuntimeError(
            "Promotion requested while "
            "readiness gate is closed."
        )

    import rich_player_projection as rpp
    import player_research as pr
    import player_analysis_kernel as pak

    staged_rows = (
        state["staging"]["rows"]
    )

    existing, _ = (
        read_csv(PRODUCTION)
        if PRODUCTION.is_file()
        else ([], [])
    )

    preserved = [
        row
        for row in existing
        if str(
            row.get("season")
            or ""
        ).strip() != SEASON
    ]

    fieldnames = [
        "season",
        "player_code",
        "source_player_id",
        *rpp.RICH_PLAYER_METRICS,
    ]

    output = (
        preserved
        + staged_rows
    )

    stamp = (
        datetime.now()
        .strftime(
            "%Y%m%d-%H%M%S"
        )
    )

    backup = (
        PRODUCTION.with_name(
            PRODUCTION.name
            + ".pre-current-player-promotion-"
            + stamp
            + ".bak"
        )
    )

    production_before = (
        PRODUCTION.read_bytes()
        if PRODUCTION.is_file()
        else None
    )

    if PRODUCTION.is_file():

        shutil.copy2(
            PRODUCTION,
            backup,
        )

        print()
        print(
            "BACKUP:",
            backup,
        )

    temporary = (
        PRODUCTION.with_name(
            PRODUCTION.name
            + ".promoting"
        )
    )

    try:

        PRODUCTION.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with temporary.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as handle:

            writer = csv.DictWriter(
                handle,
                fieldnames=fieldnames,
                extrasaction="ignore",
            )

            writer.writeheader()
            writer.writerows(
                output
            )

        os.replace(
            temporary,
            PRODUCTION,
        )

        # -----------------------------------------
        # Runtime reload.
        # -----------------------------------------

        rpp.clear_caches()

        pr._load_season_rows.cache_clear()
        pr.season_players.cache_clear()
        pr.multi_season_players.cache_clear()

        pak.season_position_analysis.cache_clear()

        players = pr.season_players(
            SEASON
        )

        eligible = [
            player
            for player in players
            if (
                number(
                    player.get("minutes")
                )
                or 0
            ) > 0
        ]

        runtime_codes = {
            str(
                player.get("player_code")
                or ""
            ).strip()
            for player in eligible
        }

        if (
            len(eligible)
            != EXPECTED_PARTICIPANTS
        ):
            raise RuntimeError(
                "Runtime population after "
                f"promotion is {len(eligible)}, "
                f"expected "
                f"{EXPECTED_PARTICIPANTS}."
            )

        if (
            runtime_codes
            != state["staging"]["codes"]
        ):
            raise RuntimeError(
                "Runtime current-player identity "
                "universe differs from staging."
            )

        # -----------------------------------------
        # Original 50-gap RUNTIME audit.
        # Uses position-specific cohorts from
        # player_analysis_kernel.
        # -----------------------------------------

        gap_keys = (
            "shots",
            "shots_on_target",
            "shots_off_target",
            "blocked_shots",
            "xgot",
            "hit_woodwork",

            "key_passes",
            "big_chances_created",
            "crosses",
            "successful_crosses",
            "accurate_opposition_half_passes",

            "attempted_passes",
            "completed_passes",
            "pass_completion",
            "passes",
            "accurate_passes",
            "rich_pass_accuracy",
            "long_balls",
            "accurate_long_balls",
            "long_ball_accuracy",

            "touches",
            "dribbles",
            "successful_dribbles",
            "unsuccessful_dribbles",

            "ball_carries",
            "progressive_carries",
            "progressive_carry_distance",
            "total_progression",

            "possession_lost",

            "tackles_won",
            "interceptions_won",
            "clearances",
            "blocks",
            "aerial_duels_won",
            "aerial_duels_lost",
            "duels_won",
            "duels_lost",
            "contests_won",
            "errors_leading_to_shot",
            "errors_leading_to_goal",

            "fouls_won",
            "fouls_conceded",
            "penalties_won",
            "penalties_conceded",

            "saves_inside_box",
            "high_claims",
            "keeper_sweeper_actions",
            "accurate_keeper_sweeper_actions",
            "keeper_sweeper_accuracy",
            "penalties_faced",
        )

        unavailable = []
        partial = []
        available = []

        print()
        print(
            "=== RUNTIME 50-GAP AUDIT ==="
        )

        for key in gap_keys:

            definition = (
                pak.DEFINITIONS_BY_KEY.get(
                    key
                )
            )

            if definition is None:
                raise RuntimeError(
                    f"No player-analysis "
                    f"definition for {key}."
                )

            cohort = [
                player
                for player in eligible
                if str(
                    player.get("position")
                    or ""
                ) in definition.positions
            ]

            values = [
                pak.metric_value(
                    player,
                    definition,
                )
                for player in cohort
            ]

            observed = sum(
                value is not None
                for value in values
            )

            if observed == 0:
                status = "UNAVAILABLE"
                unavailable.append(key)

            elif observed == len(cohort):
                status = "AVAILABLE"
                available.append(key)

            else:
                status = "PARTIAL"
                partial.append(key)

            print(
                f"{key:40} "
                f"{status:11} "
                f"{observed:3}/"
                f"{len(cohort):3}"
            )

        if set(unavailable) != CARRY_QUARTET:
            raise RuntimeError(
                "Unexpected runtime unavailable "
                "metric set: "
                + ", ".join(
                    unavailable
                )
            )

        print()
        print(
            "RUNTIME ORIGINAL-GAP SUPPORT = "
            "46 / 50"
        )

        print(
            "RUNTIME UNAVAILABLE = "
            "carry/progression quartet only"
        )

        print()
        print(
            "CURRENT PLAYER RICH PROJECTION "
            "PROMOTION: PASS"
        )

        print(
            "Source capability remains "
            "79 / 83."
        )

    except Exception:

        if temporary.exists():
            temporary.unlink()

        if production_before is None:

            if PRODUCTION.exists():
                PRODUCTION.unlink()

        else:

            PRODUCTION.write_bytes(
                production_before
            )

        print()
        print(
            "PROMOTION FAILED — "
            "PRODUCTION PACKAGE RESTORED"
        )

        raise


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Check whether current FPL and "
            "staged PulseLive windows align."
        ),
    )

    parser.add_argument(
        "--promote",
        action="store_true",
        help=(
            "Promote staging to runtime only "
            "if all readiness gates pass."
        ),
    )

    args = parser.parse_args()

    if (
        args.check
        and args.promote
    ):
        raise RuntimeError(
            "Choose either --check or --promote."
        )

    state = readiness()

    if args.promote:
        promote(state)

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
