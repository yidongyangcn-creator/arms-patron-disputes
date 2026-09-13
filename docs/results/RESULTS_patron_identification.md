# Identification suite on the clean 1955–2014 panel: mixed verdict

*Both-importer politically-relevant dyads; full controls + peace-years unless noted.*

## (1) Dyad fixed effects — PASSES

Conditional logit, within-dyad variation only (absorbs all stable alignment):

| sample | shared_dominant OR | p |
|---|---|---|
| Cold War 1955–89 | 0.655 | 0.041 |
| Full 1955–2014 | **0.617** | **0.002** |

When the *same pair* of countries comes to share a dominant patron, its onset risk falls; when patron-sharing dissolves, risk rises. The association is not just stable cross-dyad alignment.

## (2) Shift-share IV — DOES NOT CONFIRM

Instrument: predicted shared-dominance from predetermined base shares (1950–54 base for CW; 1980–89 for post-90) × leave-one-out global supplier shifts.

| sample | 1st-stage F | reduced form | 2SLS | OLS-LPM |
|---|---|---|---|---|
| Cold War 1957–89 | 117 | OR 0.99 (p=0.94) | +0.001 (p=0.93) | −0.007 (p=0.016) |
| Full 1957–2014 | 268 | OR 0.93 (p=0.52) | −0.008 (p=0.33) | −0.005 (p=0.008) |

The instrument is strong, but the **supply-shock-driven component of patron-sharing shows no pacifying effect**.

## How to read the mixed verdict (for the paper)

The IV strips patron-sharing down to its *mechanical market-share* component: a supplier surging globally can make two states' portfolios nominally "share a dominant supplier" without any real political-military relationship forming. That component doesn't pacify. The FE result says the *actual* (relational) patron-sharing does predict within-dyad de-escalation. Together they point to a refinement of the theory, not its refutation: **leverage is relational, not a mechanical function of market shares** — what pacifies is the political relationship that usually accompanies patron concentration, not the concentration itself.

But be honest about the alternative reading: the FE association could still reflect time-varying confounding (joint realignment), and the IV null is consistent with "no causal effect of the measurable market component." The quantitative evidence therefore establishes a **robust, timing-consistent association** — not a completed causal identification.

## Implications

1. **The case study is now load-bearing** (exactly Poast's advice): Camp David must trace the relational mechanism — US leverage over both Egypt and Israel via aid, spares, and conditionality — that the IV cannot capture.
2. Worth exploring: relational leverage measures (aid flows, patron share of imports, arms-embargo threat episodes) and event-based designs (supplier embargoes/cutoffs as shocks).
3. Frame the paper as: global null for generic overlap → patron-sharing association, out-of-sample confirmed, FE-robust → mechanism traced qualitatively; IV documents that nominal market overlap alone is not enough.

## Files
`patron_identification.py`; panels as before.
