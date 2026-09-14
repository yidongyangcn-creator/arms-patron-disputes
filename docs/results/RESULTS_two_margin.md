# Two-margin main table: onset vs escalation — asymmetric verdict

*Margin 1: does shared patronage prevent new disputes (onset)? Margin 2: conditional on a dispute occurring, does it cap escalation to war / fatalities? Dispute-level data: 2,327 dyadic disputes 1955–2014 (134 wars, 529 with fatalities); covariates merged from the panel (73% coverage). Dyad-clustered SEs. Files: `two_margin_main_table.csv`, `dispute_level_1955_2014.csv`, `escalation_margin.py`.*

## Results

| margin | spec | OR | p |
|---|---|---|---|
| **onset** | CW: shared dominant patron (w5) | **0.661** | **0.005** |
| onset | CW: same top supplier | **0.704** | **0.010** |
| onset | post-90: shared US patron | **0.439** | **0.040** |
| onset | post-90: shared dominant patron | 0.835 | 0.368 |
| **escalation** | war \| dispute — bivariate | 0.483 | 0.138 |
| escalation | war \| dispute — + era | 0.499 | 0.153 |
| escalation | war \| dispute — **+ full controls + era** | **0.650** | **0.430** |
| escalation | war — Firth | 0.746 | 0.601 |
| escalation | war — shared US / same-top variants | 0.90 / 0.81 | 0.87 / 0.65 |
| escalation | fatality \| dispute — + controls | 0.804 | 0.342 |

## Verdict — the escalation margin does NOT survive

The earlier suggestive war-capping estimate (OR 0.50, p=0.094, near-bivariate) **attenuates to null once controls (distance, alliance, capabilities, era) enter** (OR 0.65, p=0.43; Firth p=0.60). No specification of the escalation margin is significant. Update to previous documents: the "suggestive escalation-capping" line in the stage report should be downgraded to **null/inconclusive** — and Yidong's original memo conclusion ("shared patronage does not cap escalation") stands closer to correct than our interim reading, though via different numbers.

## What the asymmetry means for the paper

The evidence now says: **restraint operates at dispute initiation (Cold-War onsets), not on intensity conditional on initiation.** That is theoretically coherent — patron leverage works ex ante (anticipated costs deter starting an incident) but once a crisis is underway, escalation dynamics (stakes, domestic politics, battlefield facts) swamp supply dependence. Consequences:

1. **Egypt–Israel stays a boundary case, full stop.** Its post-1979 war-free record cannot be generalized as a patron effect; discuss it as dyad-specific (Sinai demilitarization, MFO, US aid conditioned on the treaty — mechanisms adjacent to but distinct from arms supply).
2. The paper's DV is onset; escalation goes in as a **documented null side-test** (one table, one paragraph) — it sharpens rather than weakens the argument, and preempts the referee question.
3. Caveat to state: dispute-level covariate coverage is 73% (panel merge); wars are rare (53–70 in estimation samples), so power is limited — "no evidence," not "evidence of no effect."
