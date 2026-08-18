"""Navigation model for the Football Research Laboratory UI."""

from dataclasses import dataclass


@dataclass(frozen=True)
class NavigationItem:
    key: str
    label: str
    section: str
    description: str = ""


# Primary navigation mirrors the way a researcher thinks about the laboratory:
# homepage -> general football evidence -> team/player research -> matchday work.
NAVIGATION = (
    NavigationItem(
        "overview",
        "Home",
        "Homepage",
        "The front door to the laboratory and its research entry points.",
    ),
    NavigationItem(
        "fixtures",
        "Fixtures",
        "General",
        "Explore canonical fixtures, results and individual match research objects.",
    ),
    NavigationItem(
        "league-table",
        "League Table",
        "General",
        "Inspect current and historical competition standings and team context.",
    ),
    NavigationItem(
        "team-profile",
        "Team Profile",
        "Teams",
        "Understand a club's identity, season story and recent evidence.",
    ),
    NavigationItem(
        "team-stats",
        "Team Stats",
        "Teams",
        "Interrogate team performance across seasons, splits and distributions.",
    ),
    NavigationItem(
        "player-profile",
        "Player Profile",
        "Players",
        "Explore a player's identity, roles, history and connected evidence.",
    ),
    NavigationItem(
        "player-stats",
        "Player Stats",
        "Players",
        "Compare player output and performance across seasons and contexts.",
    ),
    NavigationItem(
        "prediction",
        "Projection Lab",
        "Matchday Centre",
        "Apply current analytical and modelling tools to a match.",
    ),
    NavigationItem(
        "head-to-head",
        "H2H / Stats Pack",
        "Matchday Centre",
        "Build match-specific context from shared history and statistical evidence.",
    ),
)

SECTION_ORDER = (
    "Homepage",
    "General",
    "Teams",
    "Players",
    "Matchday Centre",
)

# Existing keys remain valid for contextual/deep-link compatibility.
HIDDEN_WORKSPACES = (
    "teams",
    "players",
    "analysis",
    "form",
    "data-quality",
    "provenance",
)

# Future capabilities that are deliberately not treated as navigation until their
# user journeys are established.
FUTURE_WORKSPACES = (
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
