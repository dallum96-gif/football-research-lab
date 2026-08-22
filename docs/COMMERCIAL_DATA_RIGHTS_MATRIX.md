# FRL Commercial Data Rights Matrix

## Purpose

Track whether discovered FRL data has an established right/licence/permission for commercial redistribution or commercial product use.

This is a rights/provenance classification, not legal advice. A source being technically accessible, publicly visible, or present in an MIT-licensed wrapper repository does not by itself establish redistribution rights for the underlying data.

## Decision standard

A variable/dataset is counted as **COMMERCIAL_CLEAR_NOW** only when FRL has an identifiable legal basis supporting the intended commercial use/redistribution.

Other states:

- `LICENCE_REQUIRED` — technically useful, but current evidence indicates a licence/permission is required before commercial redistribution/use.
- `RIGHTS_UNCONFIRMED` — source/rightsholder position is not sufficiently established yet.
- `FRL_ORIGINAL` — created by FRL rather than copied from a third-party source; commercial use depends on the inputs and methodology used.
- `EXTERNAL_OPEN_LICENSE` — source explicitly grants commercial reuse under an open licence, subject to that licence's conditions.

## Current source-level findings

| Source / family | Current evidence | Commercial status now | Notes |
|---|---|---|---|
| Premier League website/app content | Premier League Terms of Use reserve copyright/database rights and prohibit commercial use/reproduction/re-utilisation/redistribution, including creating a database from website material, without prior written approval. | `LICENCE_REQUIRED` | This applies to content obtained from the Website/App. |
| Premier League / Opta / Football DataCo match data | Premier League states match data is gathered using Opta and directs permission for match data, including fixture feeds, to Football DataCo. Football DataCo is identified as a data-rights holder and official-data licensor. | `LICENCE_REQUIRED` | Do not treat public accessibility as a redistribution licence. |
| FPL data/API | Current official FPL-related terms identified prohibit commercial exploitation of information/material obtained through the game without provider permission; exact API redistribution terms still require dedicated verification. | `RIGHTS_UNCONFIRMED` / likely `LICENCE_REQUIRED` | Keep conservative until the exact governing API/data terms are pinned down. |
| `imadeddine-belkat/Premier-League-Stats` repository code | Repository README states MIT format/licensing and describes the repository as an unofficial dataset. | `RIGHTS_UNCONFIRMED` for underlying data | MIT on the wrapper repository must not be assumed to grant rights in Premier League/FPL/Opta data supplied by third parties. |
| FRL-created taxonomy / relationship metadata | Created by FRL. | `FRL_ORIGINAL` | Does not automatically confer commercial rights to the underlying source data. |
| FRL-derived analytics / models | Created/calculated by FRL from source data. | `FRL_ORIGINAL` subject to input-data rights | Must be reviewed alongside source licences and any contractual restrictions. |

## Interim commercial reading

At this stage, **none of the third-party Premier League/FPL/Opta-derived source universe has been marked commercially cleared by FRL**. This is deliberately conservative and does not mean the data can never be commercialised; it means we have not yet established a right permitting that use.

The eventual commercial percentage will be calculated only after the full variable universe is inventoried and each variable is assigned a rights status. The denominator will be the set of third-party source variables FRL proposes to preserve/use commercially, not FRL-original software or methodology.

## Commercial pathway

1. Finish upstream discovery and variable inventory.
2. Map every retained variable to its source/rightsholder.
3. Separate open/licensed/uncertain/restricted data.
4. Identify which datasets require Football DataCo, Premier League, FPL or other provider licences.
5. Build a commercial-safe FRL product surface around cleared/licensed inputs and FRL-original analysis.
6. Recalculate the commercial viability percentage whenever licence scope changes.
