"""Navigation model for the Football Research Laboratory UI."""

from dataclasses import dataclass


@dataclass(frozen=True)
class NavigationItem:
    key: str
    label: str
    section: str
    description: str = ""


NAVIGATION = (
    NavigationItem("overview", "Overview", "Explore", "Start at the laboratory overview and choose a research workspace."),
    NavigationItem("fixtures", "Fixtures", "Explore", "Explore canonical Premier League fixtures and open individual match pages."),
    NavigationItem("league-table", "League Table", "Explore", "Inspect a season's league table and team performance."),
    NavigationItem("players", "Players", "Research", "Search and filter player research across the available seasons."),
    NavigationItem("head-to-head", "Head-to-Head", "Analysis", "Compare two clubs across their shared Premier League history."),
    NavigationItem("form", "Form & Streaks", "Analysis", "Inspect recent form, match ranges and current streaks."),
    NavigationItem("prediction", "Projection Lab", "Analysis", "Explore prospective fixtures using the current Poisson projection model."),
    NavigationItem("data-quality", "Data Quality", "Data & Evidence", "Inspect data completeness and quality controls."),
    NavigationItem("provenance", "Provenance", "Data & Evidence", "Inspect the sources and lineage behind research outputs."),
)

SECTION_ORDER = ("Explore", "Research", "Analysis", "Data & Evidence")
FUTURE_WORKSPACES = ("player-profile", "player-history", "comparisons", "custom-query")


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
