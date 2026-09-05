from __future__ import annotations

from datetime import datetime, timezone

import head_to_head


def _dt(value: object) -> datetime:
    text = str(value)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def test_head_to_head_v1_builds_fixed_two_sided_betbuilder_pack():
    pack = head_to_head.build_head_to_head_pack("2026-27", "29")

    assert pack["pack_version"] == "head-to-head-v1"
    assert pack["fixture"]["season"] == "2026-27"
    assert pack["fixture"]["fixture_id"] == "29"
    assert pack["betbuilder"]["status"] == "EVIDENCE_PACK_NOT_BETTING_ADVICE"

    entries = pack["betbuilder"]["entries"]
    assert len(entries) == 10
    assert {entry["side"] for entry in entries} == {"home", "away"}
    assert {entry["source_key"] for entry in entries} == {
        "goals_for",
        "Shots",
        "Shots on target",
        "Corners",
        "Yellow cards",
    }

    for entry in entries:
        assert entry["evidence_label"] in {"STRONG", "FAVOURABLE", "MIXED", "WEAK", "UNAVAILABLE"}
        if entry["evidence_index"] is not None:
            assert 0.0 <= entry["evidence_index"] <= 1.0
        for key in ("team_recent", "opponent_allowance"):
            summary = entry[key]
            assert summary["hits"] <= summary["observed_matches"] <= summary["eligible_matches"]
            assert summary["coverage_status"] in {"COMPLETE", "PARTIAL", "UNAVAILABLE"}


def test_head_to_head_uses_frozen_adaptive_dc_control_without_future_results():
    pack = head_to_head.build_head_to_head_pack("2026-27", "29")
    forecast = pack["forecast"]

    assert forecast["status"] == "AVAILABLE"
    assert forecast["model"] == "Adaptive Dixon-Coles V1.0"
    assert forecast["control_status"] == "FROZEN_EXPERIMENTAL_CONTROL"
    assert forecast["temporal_contract"]["future_results_used"] is False
    assert forecast["temporal_contract"]["training_results_strictly_before_target_kickoff"] is True

    probabilities = forecast["probabilities"]
    assert abs(
        probabilities["home_win"] + probabilities["draw"] + probabilities["away_win"] - 1.0
    ) < 1e-9
    assert 0.0 <= probabilities["over_2_5"] <= 1.0
    assert 0.0 <= probabilities["btts"] <= 1.0


def test_head_to_head_recent_profile_evidence_is_strictly_pre_fixture():
    pack = head_to_head.build_head_to_head_pack("2026-27", "29")
    cutoff = _dt(pack["fixture"]["kickoff_time"])

    for side in ("home", "away"):
        for match in pack["profiles"][side]["matches"]:
            assert _dt(match["kickoff_time"]) < cutoff
