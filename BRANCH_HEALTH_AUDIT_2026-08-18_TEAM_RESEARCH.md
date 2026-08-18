# Team Research redesign branch recovery — 2026-08-18

The existing `design/player-filter-tiles` branch is 5 commits behind `main` and 342 commits ahead, with merge base `1fbac1d`. The 5 commits unique to `main` concern Team Research and visualisation recovery (`FRL_ANALYTICAL_DATA_LAYOUT_V1.md`, `_tmp_visualisation_note.txt`, `frl_visualisations.py`, `gui/team_research_ui.py`).

Rather than merge or reset the diverged development branch blindly, preserve it as-is and base the next Team Research redesign branch on the current trusted `main` state.

Purpose: preserve a known-good recovery point before new Team Research presentation work.
