# Football Research Lab — GUI Design Contract

The Overview page is the visual benchmark for the entire application.

Preserve:
- FRL colour variables and theme
- typography hierarchy
- spacing rhythm
- white/surface backgrounds
- subtle borders
- restrained use of accent colours
- compact analytical layouts
- clear information hierarchy
- consistent selectors across workspaces

## Functional/UI principles

- Useful football data appears before advanced configuration.
- Advanced filters belong in collapsed expanders.
- Tables are first-class analytical components.
- Never replace an approved table design merely to add functionality.
- Never introduce native Streamlit widgets where an existing custom component already establishes the visual language, unless the widget is explicitly requested.
- A behavioural change must not alter font, size, colour, spacing, background, alignment or border styling unless requested.
- Prefer shared components and theme variables over page-specific styling.
- Fix classes of UI problems, not individual symptoms.
- Never duplicate navigation headers, section labels or workspace identities.
- Every page must have a clear primary purpose visible immediately.

## Change protocol

Before modifying an existing page:
1. Identify the current approved state.
2. Identify exactly what is changing.
3. Preserve everything else.
4. Check whether the requested behaviour can be implemented using the existing component.
5. Do not redesign surrounding UI.

After modifying:
- Verify Python syntax.
- Verify route still exists.
- Verify existing data still renders.
- Verify controls still work.
- Verify no deprecated Streamlit APIs were introduced.
- Verify the visual contract has not changed unintentionally.

## Players regression tests

The following must remain true:
- Season & scope starts collapsed.
- Advanced conditions starts collapsed.
- Player data appears before advanced filters.
- Table has white/surface background.
- Table heading typography matches approved Players design.
- Table heading colour matches approved Players design.
- Table row typography matches approved Players design.
- No separate Sort By control exists.
- Clicking a sortable statistic changes row ordering only.
- Clicking the same statistic again reverses ordering.
- Player detail remains collapsed.
- Deprecated use_container_width is absent.
