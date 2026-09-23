# Confirmatory test: the shared-patron effect, Cold War era

*Correction, Aug 11: the Camp David paragraph below is superseded. MID 5.0 records seven Egypt–Israel onsets after 1979; Egypt–Israel is treated as a boundary case, not the mechanism case. See PROJECT_MEMO.md §1 and RESULTS_case_memo_verification.md.*


*The shared-patron hypothesis was generated in the post-1990 MENA sample. Here it is tested out-of-sample: global politically-relevant dyads, 1955–1989 — the era of maximal patron structure. Panel extended to 1955–2014 (77,542 dyad-years, 1,109 onsets). Primary test declared before running. Full controls + peace-years, dyad-clustered SEs, both-importer dyads.*

## Results

| test | OR | p |
|---|---|---|
| **PRIMARY: shared dominant patron, Cold War (declared ex ante)** | **0.594** | **0.001** |
| Cold War: shared **US** patron | 0.544 | 0.004 |
| Cold War: shared **Soviet** patron | 0.628 | 0.209 |
| Cold War: generic overlap gradient | 0.492 | <0.001 |
| Post-1990: shared dominant patron | 0.855 | 0.497 |
| Post-1990: shared US patron | 0.599 | 0.174 |
| Pooled interaction (patron × Cold-War era) | 0.721 | 0.216 |

## Verdict: confirmed, out of sample

The hypothesis generated in post-1990 MENA **passes its declared confirmatory test in a different era**: during the Cold War, dyads sharing a dominant arms patron had ~40% lower odds of new dispute onset (p=0.001). The US-patron version is stronger still; the Soviet version is directionally consistent but underpowered. Notably, in the Cold War even the *generic* overlap gradient works (OR 0.49, p<0.001) — in a tight bipolar market, portfolio similarity ≈ patron sharing, which is exactly what the leverage mechanism predicts.

## The paper's story, as the evidence now stands

1. **Cold War (strong patron structures):** shared supply — patron sharing and overlap alike — robustly predicts fewer new disputes.
2. **Post-1990 (diversified, multipolar arms market):** the average effect disappears; it survives only where patron density remains high (MENA; US client pairs, directionally).
3. **Interpretation:** the pacifying effect of shared arms supply operates through **patron leverage**, and it *declined as the arms market multipolarized* — a substantively important and timely claim (relevant to today's China/Russia/second-tier supplier expansion).

Camp David slots in as the mechanism case: the US becomes both Egypt's and Israel's dominant patron after 1979; no Egypt–Israel onset thereafter.

## Cautions

- The era *difference* is directionally right but not itself significant (interaction p=0.216) — frame as "concentrated in the Cold War / patron-dense settings," not "vanished after 1990," until a higher-powered moderation test (e.g. continuous supplier-market concentration) is run.
- Soviet-patron cell is thin; consider pooling patrons or measuring leverage continuously (patron share of imports).
- Identification suite (dyad FE, shift-share IV) should now be re-run on the **clean 1955–2014 panel** with the patron measure — the earlier IV machinery is reusable as-is.

## Files
`clean_polrel_panel_1955_2014.csv`, `patron_confirm.py`.
