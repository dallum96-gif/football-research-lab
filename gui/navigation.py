"""Navigation model for the Football Research Laboratory UI.

This module intentionally contains presentation/navigation metadata only.
It does not import Streamlit, query functions, or research/data modules.
That keeps the UI redesign decoupled from the trusted research layer while
we migrate the legacy interface workspace-by-workspace.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class NavigationItem:
    key: str
    label: str
    section: str
    description: str = ""


NAVIGATION = (
    NavigationItem(
        key="overview",
        label="Overview",
        section="Explore",
        description="Start at the laboratory overview and choose a research workspace.",
    ),
    NavigationItem(
        key="fixtures",
        label="Fixtures",
        section="Explore",
        description="Explore canonical Premier League fixtures and open individual match pages.",
    ),
    NavigationItem(
        key="teams",
        label="Teams",
        section="Explore",
        description="Inspect league performance and historical team comparisons.",
    ),
    NavigationItem(
        key="players",
        label="Players",
        section="Research",
        description="Search and filter player research across the available seasons.",
    ),
    NavigationItem(
        key="head-to-head",
        label="Head-to-Head",
        section="Analysis",
        description="Compare two clubs across their shared Premier League history.",
    ),
    NavigationItem(
        key="form",
        label="Form & Streaks",
        section="Analysis",
        description="Inspect recent form, match ranges and current streaks.",
    ),
    NavigationItem(
        key="prediction",
        label="Prediction Lab",
        section="Modelling",
        description="Explore the current experimental prediction models.",
    ),
    NavigationItem(
        key="data-quality",
        label="Data Quality",
        section="Data & Evidence",
        description="Inspect data completeness and quality controls.",
    ),
    NavigationItem(
        key="provenance",
        label="Provenance",
        section="Data & Evidence",
        description="Inspect the sources and lineage behind research outputs.",
    ),
)


SECTION_ORDER = (
    "Explore",
    "Research",
    "Analysis",
    "Modelling",
    "Data & Evidence",
)


FUTURE_WORKSPACES = (
    "player-profile",
    "player-history",
    "comparisons",
    "custom-query",
)


def navigation_by_section():
    """Return navigation items grouped in the deliberate UI order."""
    return {
        section: tuple(
            item
            for item in NAVIGATION
            if item.section == section
        )
        for section in SECTION_ORDER
    }


def navigation_item(key):
    """Resolve a navigation key without coupling callers to list positions."""
    for item in NAVIGATION:
        if item.key == key:
            return item

    raise KeyError(
        f"Unknown navigation item: {key}"
    )
