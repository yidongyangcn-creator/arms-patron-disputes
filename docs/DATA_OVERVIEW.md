# Global expansion — data integration & overview

*Generated 2026-06-16. Modelling window 1990–2014 (MID 5.0 ends 2014).*

## What is now integrated

| Source | Role | Key / coverage |
|---|---|---|
| SIPRI Trade Register (global, 1950–2025) | **IV**: arms-supplier overlap | 29,916 deal rows → 22,914 bilateral recipient←supplier TIV flows after mapping to COW codes |
| MID 5.0 (MIDB participant-level) | **DV**: dyadic conflict / onset | dyads built by crossing side A × side B per dispute; 1,046 conflict dyad-pairs, **689 onsets** in 1990–2014 |
| V-Dem v16 | regime controls | `v2x_polyarchy` etc., joined on `COWcode`; ~97% dyad coverage |
| NMC 6.0 (CINC) | relative capability | `cinc_diff`; ~99% dyad coverage |
| COW Alliance v4.1 | defense pacts | `ally_defense` dummy |
| COW Direct Contiguity 3.2 | geography | available (stateabb) — wired in the R pipeline |
| Capital distance (computed) | geography control | great-circle capital-to-capital km, **100%** dyad coverage (`data/dyadic_capital_distance.csv`) |
| COW Bilateral Trade v4.0 | economic interdependence | `smoothtotrade` (lagged), **92%** dyad coverage / 86% of onset dyads (`data/COW_Trade_4.0/`) |

All sources are harmonised to **COW ccode** via a single crosswalk (`integrate.py`), including SIPRI-specific spellings (Turkiye, Soviet Union→365, DR Congo, Czechia, etc.). Non-state recipients (rebel groups, African Union) are dropped.

## Headline numbers

- **Panel**: 133,702 dyad-year rows (politically-relevant filter: a dyad is kept in year *t* if both sides imported arms in *t−1*, or a MID is present). Onset base rate **0.52%** — rare-events territory, as expected.
- Going from MENA-15 to global lifts the sample from a handful of onset events to **689**; the MENA-only writing sample was estimating on ~tens of events.

## The key coverage caveat (drives region choice)

Arms-import coverage is very uneven, so the overlap IV is only *informative* where countries actually import major arms:

| Region | MID onsets | …with overlap data (t−1) | usable share |
|---|---|---|---|
| MENA | 91 | 68 | **75%** |
| Asia-Pacific | 119 | 88 | **74%** |
| Europe / post-Soviet | 127 | 63 | 50% |
| Sub-Saharan Africa | 92 | 14 | **15%** ⚠ |
| Americas / S. America | 34 | 13 | ~38% |
| cross-region | 226 | 155 | 68% |

**Implication:** Sub-Saharan Africa has many onsets but almost no arms-import data — overlap there is mostly undefined, so a naïve global pooled model would silently drop those dyads or treat them as zero-overlap. MENA and Asia-Pacific are the strongest cells. This is the empirical case for **estimating region-by-region and comparing coefficients** rather than one global network.

## Recommended modelling plan

1. **Region-stratified TERGMs** (MENA, Asia-Pacific, Europe/post-Soviet as the well-covered cells) using `build_panel.R`, which produces conformable matrices for any country set. Compare the overlap coefficient across regions — heterogeneity is the contribution.
2. **Global politically-relevant-dyad model** as a pooled robustness check (not the headline), restricted to dyads with defined overlap.
3. **Controls — now complete**: the full "hard test" set is in the panel (`overlap_lag1`, `ally_defense`, `cinc_diff`, `regime_dist`, `ln_capdist`, `ln_trade_lag1`). The next step is simply to run it.
4. **Rare-events / scale**: with 0.5% base rate, complement btergm with a rare-events logit (King-Zeng) and/or AME latent-space model as workhorse robustness.

## Files in `build/`

- `dyad_year_panel_1990_2014.csv` — analysis-ready dyad-year panel (onset, overlap_lag1, ally, cinc_diff, regime_dist, region tags).
- `overlap_long_allyears.csv` — dyadic supplier-overlap, every year 1950–2025 (for any window/region).
- `bilateral_tiv_by_year.csv` — recipient←supplier TIV flows by year.
- `overview_yearly.csv`, `overview_by_region.csv`, `summary.json`, `FIG_data_overview.png`.
- `integrate.py` — reproducible build; `build_panel.R` — region-configurable matrix builder for btergm.
