"""Navigation model for the Football Research Laboratory UI."""

from dataclasses import dataclass


@dataclass(frozen=True)
class NavigationItem:
    key: str
    label: str
    section: str
    description: str = ""


# Primary navigation is intentionally smaller than the underlying application graph.
# Contextual/detail views and evidence tooling remain reachable by relationship links
# or deep links without becoming competing top-level workspaces.
NAVIGATION = (
    NavigationItem(
        "overview",
        "Home",
        "Primary",
        "The front door to the laboratory and its research entry points.",
    ),
    NavigationItem(
        "fixtures",
        "Fixtures & Results",
        "Primary",
        "Explore canonical fixtures, results and individual match research objects.",
    ),
    NavigationItem(
        "league-table",
        "League Table",
        "Primary",
        "Inspect current and historical competition standings and team context.",
    ),
    NavigationItem(
        "teams",
        "Teams",
        "Primary",
        "Explore club profiles, team statistics and connected fixture research.",
    ),
    NavigationItem(
        "players",
        "Players",
        "Primary",
        "Explore player profiles, statistics, research and match appearances.",
    ),
    NavigationItem(
        "analysis",
        "Analysis",
        "Primary",
        "Access Matchday, modelling and future research tools.",
    ),
)

SECTION_ORDER = ("Primary",)

# Existing keys remain valid for contextual/deep-link compatibility. They are not
# primary navigation destinations under the v1.0 organisation contract.
HIDDEN_WORKSPACES = (
    "head-to-head",
    "form",
    "prediction",
    "data-quality",
    "provenance",
)

# Future capabilities that are deliberately not treated as navigation until their
# user journeys are established.
FUTURE_WORKSPACES = (
    "player-profile",
    "player-history",
    "comparisons",
    "custom-query",
    "records",
    "combined-metrics",
)


def navigation_by_section():
    return {
        section: tuple(item for item in NAVIGATION if item.section == section)
        for section in SECTION_ORDER
    }


def navigation_item(key):
    for item in NAVIGATION:
        if item.key == key:
            return item
    raise KeyError(f"Unknown navigation item: {key}")
