# Region × era analysis (clean panel) — replaces the voided regional forest plot

*Clean politically-relevant panel 1955–2014, both-importer dyads. `shared_dominant` and `overlap` per region × era; full controls + peace-years (lean fallback flagged where cells are tiny). Same-region cells contain within-region pairs only; "cross-region" is dominated by major↔minor (patron–client-type) dyads.*

## Shared dominant patron, by cell

| region | Cold War OR (p) | Post-1990 OR (p) |
|---|---|---|
| **cross-region** | **0.53 (0.031)** | 0.57 (0.220) |
| MENA | 0.54 (0.205) | 0.50 (0.191) |
| Asia-Pacific | 0.92 (0.79) | 1.45 (0.27) |
| Europe | 1.26 (0.60) | 0.48 (0.30) |
| Sub-Sah. Africa | 0.57 (0.41) | 1.12 (0.90) |
| S. America | 1.47 (0.61) | *(separation, n=9 — unreliable)* |

Cold-War generic overlap in cross-region dyads: OR 0.39 (p=0.008). Post-90 Asia-Pacific overlap is *positive* (OR 2.43, p=0.034) — the one cell going the other way (26 tests; treat with multiple-testing caution, but Asia-Pacific is consistently the outlier).

## Reading

1. **The Cold-War patron effect is carried above all by cross-region dyads** — precisely the pairs that include a major power or span patron systems. That is where patron leverage should operate, and it does (both the patron dummy and the overlap gradient significant).
2. **MENA is directionally negative in both eras** (~OR 0.5) in these narrow contiguous-pair cells; the complete-network MENA test (RESULTS_mena_clean.md) remains the sharper regional design and its shared-US result stands.
3. **Asia-Pacific is a genuine, consistent outlier** (null-to-positive in every design and era) — worth a paragraph in the paper: rivalry pairs there (e.g. both-US-clients with active disputes) may break the leverage logic.
4. Within-region cells are individually underpowered (9–85 onsets); the pattern, not any single cell, is the evidence.

## Status of deliverables

- `FIG_patron_by_region_era.png` **replaces** the old `FIG_overlap_by_region.png` (voided with the old panel).
- Files: `region_era.py`, `region_era_patron_results.csv`.
