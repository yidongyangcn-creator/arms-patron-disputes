# Baseline hardening — major reassessment (read this first)

*Date: 2026-08-11. This memo supersedes RESULTS_region_logit.md, RESULTS_identification.md, and RESULTS_bartik_iv.md.*

## What we did

Ran the four "harden the baseline" checks: (1) zero-diagnostic (overlap gradient vs. import status), (2) Carter–Signorino peace-years controls, (3) standard politically-relevant sample (contiguous OR major power), (4) Firth rare-events logit. This required rebuilding the panel **unconditionally** — the original panel only kept dyad-years where both states imported arms *or* a MID occurred.

## The finding: the earlier global result was a sample-construction artifact

The old panel's inclusion rule ("both-import OR MID") meant that non-importing dyads entered **only when they were in conflict**. Those 410 conflict-loaded, zero-overlap rows produced the significant negative overlap coefficient (OR = 0.29). Diagnostics:

| spec (old panel) | overlap OR | p |
|---|---|---|
| A. original spec | 0.29 | 0.001 |
| B. + both-import indicator | 1.00 | 1.00 |
| C. both-import subsample only | 0.995 | 0.99 |

On the **clean, unconditional politically-relevant panel** (43,624 dyad-years, 522 onsets, no selection on imports or conflict):

| spec (clean panel) | OR | p |
|---|---|---|
| overlap gradient (+ controls + peace-years) | 0.99 | 0.97 |
| overlap + both-import indicator | 0.96 / 1.04 | 0.90 / 0.74 |
| gradient within both-importers | 1.03 | 0.93 |
| extensive margin alone (both-import) | 1.03 | 0.77 |
| Firth logit | 0.97 / 1.04 | 0.91 / 0.73 |
| shared dominant supplier (≥50% same top) | 0.86 | 0.50 |
| shared **US** patron specifically | 0.60 | 0.18 |

**Conclusion: in the properly constructed global panel, there is no robust evidence that arms-supplier overlap (any margin, any measure tried so far) reduces dispute onset.** The earlier identification suite (UNGA control, dyad FE, non-aligned subsample, Bartik IV) was estimated on the contaminated panel and is therefore void until re-run on the clean panel.

## Important context

- **This is the diagnostics working as intended.** We ran them precisely because they could overturn the result; better now than from a referee.
- **The original MENA writing-sample finding is a different design** (complete 15×15 network, no DV-based selection) and is *not* automatically invalidated. Whether a MENA-specific effect survives a clean design is now the key open question.
- The shared-US-patron estimate is directionally negative (OR 0.60) but underpowered — the mechanism-specific version of the hypothesis is not dead, just not confirmed globally.
- **The slides (overlap_conflict_slides.pdf) and earlier results memos now overstate the findings and must not be circulated until revised.**

## Paths forward (decision needed)

1. **Re-test MENA with a clean design** — unconditional 15×15 (or extended MENA) panel/network. If the effect is real there, the paper becomes a *conditional* story: supplier overlap constrains in tight regional arms markets with dominant patrons, not everywhere. Camp David case study slots in naturally as mechanism evidence.
2. **Mechanism-first measurement** — build sharper measures of patron leverage (dependence asymmetry, spare-parts lock-in, share of dominant supplier) instead of generic portfolio similarity, and test those.
3. **Honest null paper** — "supplier overlap does not pacify globally" with strong data and diagnostics; harder to place but defensible.
4. Re-run the IV/identification suite on the clean panel for completeness (likely null, but should be documented).

## Files
`clean_polrel_panel_1990_2014.csv` (the correct panel going forward), `clean_panel.py` (rebuild + ladder + Firth), `hardening.py` (diagnostics on old panel).
