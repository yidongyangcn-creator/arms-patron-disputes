# Import-intensity condition — and what it says about Asia-Pacific

*`import_intensity.py`. Intensity = SIPRI TIV imported over the 5-yr window / military expenditure over the same window (NMC milex). A state below the 10th (or 25th) percentile of intensity among importers is treated as not import-dependent; shared dominance is switched off unless both sides are dependent. Panel gains `imp_int_i/j`, `dep10/25`, `sd_w5_int10/25`.*

## Main result with the condition

| spec | p10 cut | p25 cut |
|---|---|---|
| CW primary | 0.682 (p=0.018) | 0.682 (p=0.022) |
| CW primary, originator-only | 0.690 (p=0.035) | 0.682 (p=0.035) |
| full 1955–2014 | 0.729 (p=0.027) | 0.779 (p=0.089) |
| post-1990 | 0.866 (ns) | 1.117 (ns) |

Unconditioned CW primary for comparison: 0.661 (p=0.005). The condition costs a little precision (fewer shared-patron dyad-years) and changes nothing substantive. Good: the result was not riding on near-empty portfolios.

## Asia-Pacific: the measurement fix does not rescue it — it sharpens the anomaly

Expectation from the dyad list: Japan/Korea/Taiwan are big domestic producers, so their "US dependence" is overstated. The data disagree for the period that matters. Import intensity in 1975: Japan 2.97, ROK 3.29, Taiwan 1.50 — as import-dependent as Egypt (2.05) or Israel (1.36); it is only by 2005 that they fall (0.16–0.36). China 1975 = 0.0002, so the China–India / China–Vietnam "shared Soviet patron" codings are indeed noise and drop out.

With the condition, the Asia-Pacific coefficient goes the wrong way *more* strongly: OR 1.75 (p=0.001) at p10, 1.95 (p<0.001) at p25 (unconditioned: 1.41, p=0.07). Among genuinely US-dependent Asian clients — ROK–Japan, Taiwan–Japan, Taiwan–Philippines, Thailand–Laos — sharing the patron goes with *more* low-level disputes.

So this is not a measurement artifact. It is a real regional exception that the theory has to absorb. The plausible account, and one that fits the rest of our evidence: patron restraint requires the patron to *care* about client–client friction. In Europe the US built a multilateral alliance that internalized intra-client disputes (Greece–Turkey is the exception that proves it: NATO's one unresolved intra-alliance rivalry). In Asia it deliberately did not — the hub-and-spokes design kept clients bilateral to the hub (Cha's "powerplay"), left territorial and historical disputes among them unaddressed, and tolerated displays over islands as long as they did not threaten the hub. That is the same "patron indifference" condition the Iraq–Syria case raises for the Soviet side. Leverage existed; it was not spent on these disputes.

## For the draft

- Keep the intensity condition as a robustness spec (main tables: unconditioned sd_w5; footnote/appendix: dependent-only).
- Write Asia-Pacific as a theoretical boundary condition (patron indifference / alliance architecture), not as noise. It is now one of the more interesting things in the paper.
- The originator-only CW estimate with the condition (0.69, p=0.035) is the most conservative headline number; cite it alongside 0.66.
