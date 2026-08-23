import player_route_readiness as player
import squad_source_adapter as squad


def test_player_registry_is_contract_compliant():
    assert player.registry_is_contract_compliant()
    assert player.player_season_route_status() == "READY_FOR_VERIFICATION"
    assert player.player_match_route_status() == "REQUIRES_VERIFIED_PLAYER_IDENTITY"


def test_squad_fails_closed_without_materialised_source():
    assert squad.squad_route_status() in {
        "SOURCE_REQUIRED",
        "SOURCE_AVAILABLE_REQUIRES_VERIFICATION",
    }
