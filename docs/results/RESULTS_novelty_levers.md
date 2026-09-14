# Novelty levers: UCDP extension & substitutability — honest results

*Two additions aimed at raising the paper's ceiling. One mostly fails for data reasons, one yields a new finding (not the one expected). Files: `ucdp_extension.py`, `substitutability.py`, `extension_panel_2015_2024.csv`; panel gains `onset_ucdp`, `out_i/out_j/locked/out_min`.*

## Lever 1 — UCDP post-2014 extension: NOT VIABLE as a test

UCDP's ≥25-battle-deaths threshold captures shooting wars only, not the threats/displays that make up most MIDs. Consequences: 1955–2014 UCDP onsets in our sample = 30–37 (vs 434–768 MID onsets) → direction consistent with the MID results (OR 0.65–0.70) but hopelessly underpowered (p≈0.5); 2015–2024 politically-relevant both-importer panel contains **4 onsets** → no estimation possible (Iran–Israel drops out: non-contiguous, no major); extended HHI moderation with UCDP DV: null (59 events).

**Salvage:** (i) alternative-DV footnote (direction consistent); (ii) **HHI series to 2023 shows multipolarization *reversing* after 2022** (0.18 → 0.23 as Russian exports collapse and the market re-concentrates on the US) — strong intro/conclusion material; (iii) qualitative discussion of the 12 recent interstate onsets (e.g., Kyrgyzstan–Tajikistan 2021–22: two Russian clients fighting while the patron is consumed by Ukraine — a "patron capacity" vignette). A MID-type post-2014 dataset does not exist yet; when MID 6 releases, this becomes a ready-made follow-up.

## Lever 2 — Substitutability / outside options: measure works, hypothesis flips

**Measure:** `outside_i` = number of suppliers besides the patron delivering >5% of i's imports (w5 window). **Validation is textbook** — Iraq: 0 alternatives in 1974/78 (pure Soviet), 1 by 1982 (France 12%), 2 by 1986 (China 20%, France 16%) — exactly the historical diversification path.

**Expected:** patron effect concentrated among "locked" dyads (both sides no alternatives). **Found:**

| spec (CW / full) | OR | p |
|---|---|---|
| sd_w5 × locked interaction | 1.30 / 1.01 | 0.45 / 0.97 — **no concentration among locked** |
| sd_w5 among locked only | 1.45 / 0.69 | ns (41 / 61 events — thin) |
| sd_w5 among dyads with options | 0.64 / 0.72 | **0.008 / 0.013** |
| **out_min (continuous outside options)** | **1.21 / 1.11** | **0.005 / 0.027** |
| sd_w5 alongside out_min | 0.72 / 0.74 | 0.023 / 0.016 |

**Two takeaways:**
1. The lock-in interaction is null — patron restraint (as measured) does not require exclusivity. Possible readings: the >5% threshold is crude; locked cell is small (11% of dyad-years); or restraint works through the *relationship*, not monopoly per se (consistent with the IV/financing nulls).
2. **New finding: outside options independently predict MORE onsets** (each additional alternative supplier ≈ +10–20% onset odds), with the patron effect surviving alongside. Two readings, both paper-worthy: *options free hands* (states with supplier alternatives are harder to restrain) vs *war-preparers diversify* (reverse causality — anticipating conflict, states hedge suppliers; Iraq diversified exactly while fighting Iran). Present as an association with both interpretations; the Iraq case can adjudicate qualitatively.

## Net effect on the paper

The novelty package is now: (i) the dyadic shared-patron design itself (gap confirmed vs Kinsella-era work); (ii) the **outside-options measure and its independent association with conflict**; (iii) restrain-vs-discipline + the mechanism "negative space"; (iv) contemporary hook: multipolarization-then-reconcentration of the arms market (HHI to 2023) + Kyrgyzstan–Tajikistan vignette. The post-2014 quantitative test waits for MID 6 — say so in the conclusion; it reads as a research program, not a gap.
