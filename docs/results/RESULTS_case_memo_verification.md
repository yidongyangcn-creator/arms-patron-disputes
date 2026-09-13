# Verification of the Aug 11 case-design memo against our pipeline

*Every checkable claim in Yidong's case-design memo was re-derived from our own data (`window5_repro.py`). Verdict: the memo is substantially validated; one section (escalation test) must be rewritten; sample counts differ and should be standardized to our pipeline before anything goes to Poast.*

## Validated (use as-is, numbers now from our pipeline)

| memo claim | memo number | our reproduction |
|---|---|---|
| Egypt–Israel onsets after 1979 | 1983, 89, 04, 06, 09, 11, 14 | **identical** (MIDB); wars (hostlev 5) indeed stop after 1979 |
| Single-year dominance flips | 11.6% | **10.9%** (w5 measure flips only 4.8% — window measure justified) |
| CW estimate, w5 + UNGA control | OR 0.66, p=0.005 | **OR 0.661, p=0.005** (N=24,349, 434 onsets) |
| No-defense-pact subsample | OR 0.65, p=0.032 | **OR 0.647, p=0.032** |
| Survives dropping top-10-exporter dyads | "survives" | **OR 0.714, p=0.039** |
| Iraq–Syria worst-fitting shared-patron dyad | residual +4.70 | **+4.71** (7 onsets vs 2.29 predicted, patron-share 0.73) |
| Greece–Turkey next off-the-line | +4.18 | **+4.04** |
| ROK–Japan off-the-line | 4 onsets/24 yrs | **4/24 in estimation sample** (6 in raw MID) |
| Warsaw Pact pairs on-the-line, single 1968 onset | — | **confirmed** (HUN–CZE, POL–CZE: only 1968) |
| Iraq/Syria long Soviet dominance | 1959–2003 / 1955–1993 | confirmed in direction; exact spans measure-dependent (single-year series has gap years during Iraq's French purchases — their own point 2 anticipates this) |

## Must be rewritten before sending

**The escalation test.** Memo: 3,396 disputes, war OR=1.56 (p=0.49), fatality OR=0.90 (p=0.75) → "shared patronage does not cap escalation." Our pipeline: **2,181 dyadic disputes (1955–2014)**; war OR=**0.503 (p=0.094)**, fatality OR=0.829 (p=0.342). Both agree the effect is not significant at 5%, but our war estimate is *directionally protective and marginal* — the flat "It does not" overstates. Rewrite as: *"conditional on a dispute, evidence that shared patronage caps escalation is inconclusive (war OR 0.50, p=0.09 in our specification) — suggestive but not established; the Egypt–Israel war-cessation pattern may weakly generalize."* This actually softens the Camp David demotion slightly: it stays a boundary case, but the "wars stop" observation may not be purely dyad-specific.

**Sample counts.** Their "54,987 dyad-years, 828 onsets" is not our estimation sample (ours: 27,333/491 CW both-importers; 24,349/434 with UNGA). Standardize all Ns to our pipeline.

## Bottom line

The case-design memo's selection logic (Lieberman off/on-the-line), the Camp David retraction, and the headline w5 estimates all hold up in our data — the w5 (5-year trailing window) measure is an improvement we should adopt as the primary measure going forward. Fix the escalation section and the Ns, then it is safe to send to Poast.
