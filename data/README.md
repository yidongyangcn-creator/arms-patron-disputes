# Data

`derived/` is tracked, so everything under `code/02_analysis/` runs on a fresh clone.
`raw/` is git-ignored — the sources are large and carry their own redistribution terms.
`docs/DATA_OVERVIEW.md` has the integration detail and the coverage caveat that drives
the region-by-region design; this file is just the shopping list.

## Tracked

| File | Size | What it is |
|---|---|---|
| `derived/clean_polrel_panel_1955_2014.csv` | 18 MB | **Primary panel.** Politically-relevant dyad-years, 1955–2014. 77,542 rows, 1,109 onsets. Rebuilt after the August 2026 diagnostics. |
| `derived/clean_polrel_panel_1990_2014.csv` | 5.5 MB | Post-Cold-War slice of the same build. |
| `derived/clean_mena_panel_1990_2014.csv` | 350 KB | MENA complete-network panel, where the shared-patron hypothesis was generated. |
| `derived/dispute_level_1955_2014.csv` | 288 KB | Dispute-level file behind the escalation-margin test. |
| `derived/extension_panel_2015_2024.csv` | 1.1 MB | UCDP-based extension past the end of MID 5.0. |
| `derived/bilateral_tiv_by_year.csv` | 422 KB | Recipient←supplier TIV flows by year, from the SIPRI register. |
| `derived/overlap_long_allyears.csv` | 6.3 MB | Dyadic supplier-overlap, every year 1950–2025. |
| `reference/statelist2024.csv` | 11 KB | COW state list — the crosswalk spine. |

## To download into `raw/`

Everything is harmonised to **COW ccode** by `code/01_build/11_integrate.py`, including
SIPRI-specific spellings (Türkiye, Soviet Union → 365, DR Congo, Czechia). Non-state
recipients — rebel groups, the African Union — are dropped.

| Source | Path under `raw/` | Where |
|---|---|---|
| **SIPRI Arms Transfers Database** — trade register, global, 1950–2025 | `trade-register.csv` | <https://armstrade.sipri.org/> — export the full register, all suppliers × recipients. 29,916 deal rows → 22,914 bilateral flows after mapping. |
| **MID 5.0** (participant-level MIDB) | `MID-5-Data-and-Supporting-Materials/` | <https://correlatesofwar.org/data-sets/mids/> — dyads are built by crossing side A × side B per dispute. Ends 2014, which sets the modelling window. |
| **V-Dem v16** | `V-Dem-CY-FullOthers-v16_csv/` | <https://v-dem.net/data/the-v-dem-dataset/> — 406 MB CSV. Only `v2x_polyarchy` is used; consider slicing it once and keeping the slice. |
| **NMC 6.0** (CINC) | `NMC_Documentation-6.0/` | <https://correlatesofwar.org/data-sets/national-material-capabilities/> — ends 2012, forward-filled to 2014. |
| **COW Formal Alliances v4.1** | `version4.1_csv/` | <https://correlatesofwar.org/data-sets/formal-alliances/> — `ally_defense` dummy. Also ends 2012. |
| **COW Direct Contiguity 3.2** | `DirectContiguity320/` | <https://correlatesofwar.org/data-sets/direct-contiguity/> |
| **COW Bilateral Trade v4.0** | `COW_Trade_4.0/` | <https://correlatesofwar.org/data-sets/bilateral-trade/> — 82 MB dyadic file. 92% dyad coverage. |
| **Voeten UNGA ideal points** | `ideal_points_voeten.csv` | <https://dataverse.harvard.edu/dataverse/Voeten> |
| **UCDP Dyadic v26.1** | `Dyadic_v26_1.csv` | <https://ucdp.uu.se/downloads/> — for the 2015–2024 extension only. |
| **US Greenbook aid** | `us_military_aid_greenbook.csv`, `us_economic_aid_greenbook.csv` | <https://foreignassistance.gov/> — for the relational-leverage measures. |
| Capital coordinates / distances | `capital_coordinates.csv`, `dyadic_capital_distance.csv` | Computed great-circle capital-to-capital km, 100% dyad coverage. Regenerate with `11_integrate.py` or copy from the working folder. |

Two duplicate-by-content files in the original folder were not carried over:
`IdealpointestimatesAll_Apr2020 (1).csv` is byte-identical to `ideal_points_voeten.csv`,
and four identically-named `import-export-values_*.csv` exports differ only in how many
year ranges got appended to the filename.
