# Project Memo — Arms Supply, Patron Leverage, and Dispute Onset

*Status memo, August 11, 2026. Yidong Yang & Jerry Zhang. Supersedes all earlier results documents; see file inventory at the end.*

---

## 1. One-paragraph summary

The project began as "arms-supplier overlap reduces militarized dispute onset" (MENA pilot, then global). Rigorous diagnostics overturned the original global result — it was an artifact of sample construction. What survived, sharpened, and was then confirmed out-of-sample is a more precise claim: **sharing a dominant arms patron (a single supplier providing >=50% of both sides' imports) is robustly associated with fewer new militarized disputes — where patron structures are strong: the Cold War era, patron–client (cross-region) dyads, and MENA. Generic portfolio overlap without a dominant patron does nothing, and the effect is absent in the diversified post-1990 market on average and in Asia-Pacific in particular.** The mechanism claim (relational patron leverage: aid, spare parts, conditionality) is supported by timing (dyad fixed effects) but not by a supply-shock IV — so the causal story rests on process evidence, making the case-study component load-bearing. **Correction (Aug 11): Camp David was initially proposed as the mechanism case but is retracted as a positive case — our own MID 5.0 data record seven Egypt–Israel onsets after 1979 (1983, 1989, 2004, 2006, 2009, 2011, 2014) under largely shared US patronage. What is true is narrower: wars (hostility level 5) stop after 1979; all later disputes are displays/limited force with ≤1 coded fatality. Egypt–Israel will be discussed as a boundary case the argument does not fully explain.**

## 2. How the argument evolved (keep this history — it disciplines the paper)

1. **Original pilot (writing sample):** MENA15, 1990–2014, TERGM; overlap negatively associated with onset.
2. **Global expansion:** full SIPRI bilateral register scraped (all suppliers × recipients, 1950–2025); MID 5.0, V-Dem, CINC, alliances, contiguity, capital distance (computed), COW trade, UNGA ideal points — all harmonized to COW codes.
3. **First global results (later voided):** overlap OR of about 0.29 with full controls; "identification suite" (UNGA control, dyad FE, non-aligned subsample, Bartik IV) all passed. *These were run on a panel whose inclusion rule ("both import OR MID present") turned out to select non-importing dyads into the sample only when in conflict.*
4. **Baseline hardening (the turning point):** zero-diagnostic, peace-years controls, standard politically-relevant sample, Firth. On the rebuilt unconditional panel, **generic overlap is null on every margin**. Original global finding: artifact.
5. **Clean MENA re-test:** complete-network design survives directionally; the sharp measure — **shared dominant patron, esp. shared US patron (OR 0.29, p=0.015, jackknife-stable)** — is where the action is.
6. **Out-of-sample confirmation (declared primary test):** Cold War 1955–89, global politically-relevant dyads: shared dominant patron **OR 0.594, p=0.001**; shared US patron 0.54 (p=0.004); generic overlap also works in the bipolar era (OR 0.49) — consistent with overlap being nearly equivalent to patron-sharing under bipolarity.
7. **Identification, clean panel:** dyad FE passes (full panel OR 0.617, p=0.002); **shift-share IV does not confirm** (strong first stage, null reduced form) → the market-share component of patron-sharing is not what pacifies; leverage is relational.
8. **Region × era map:** effect concentrated in cross-region (patron–client) dyads in the Cold War (OR 0.53, p=0.031) and directionally in MENA both eras; **Asia-Pacific is a consistent outlier** (null-to-positive).

## 3. The paper's thesis as it now stands

> Shared dependence on a dominant arms patron constrains the outbreak of militarized disputes between recipients. The constraint operates through the patron's relational leverage — aid, resupply, spare parts, conditionality — not through portfolio similarity per se. Accordingly it is visible where patrons dominate (Cold War, patron–client dyads, MENA) and vanishes where the arms market is diversified (post-1990 average, Asia-Pacific). The case section uses Iraq–Syria (off-the-line: shared Soviet patron, repeated onsets) and Warsaw Pact dyads (on-the-line: maximal patron concentration) as mechanism cases; Egypt–Israel after Camp David is discussed as a boundary case — wars end after 1979, but seven lower-level onsets occur under shared US patronage.

Contributions: (i) dyadic/network view of arms transfers; (ii) a null that matters (generic overlap does nothing — corrects the intuition the pilot started from); (iii) the patron-leverage conditional finding with out-of-sample confirmation; (iv) mechanism case study; (v) timely implication — as the market multipolarizes (China, second-tier suppliers), this restraint channel erodes.

## 4. Evidence inventory (what we can claim, at what strength)

| claim | evidence | strength |
|---|---|---|
| Generic overlap does not pacify (global) | clean panel, all margins, Firth | strong null |
| Shared dominant patron and fewer onsets, Cold War | declared primary test, p=0.001 | strong association |
| Same, MENA post-1990 (shared US) | complete network, p=0.015, jackknife-stable | moderate (small n, multiple testing) |
| Timing consistent within dyads | conditional logit FE, p=0.002 | moderate-strong |
| Era/market-structure moderation | CW vs post-90 contrast; interaction p=0.216 | directional only — do not overclaim |
| Causal (exogenous) effect | shift-share IV null | **not established**; frame as relational-leverage refinement |
| Asia-Pacific exception | every design/era | consistent pattern, explain in paper |

## 5. Honest limitations to state

Small onset counts in regional cells; shared-patron hypothesis was generated post-hoc in MENA (mitigated by declared out-of-sample confirmation); IV null admits two readings (relational mechanism vs. no causal effect); MID 5.0 ends 2014; alliance/CINC data end 2012 (forward-filled 2013–14).

## 6. Next steps (priority order)

1. **Case studies (load-bearing): Iraq–Syria + Warsaw Pact** (per the Aug 11 case-design memo, whose factual claims we verified against our data; its regression numbers — 5-yr trailing windows, escalation test, residual table — must be reproduced in our pipeline before anything goes to Poast). Egypt–Israel becomes a boundary-case discussion, not a positive case.
2. **Relational leverage measures:** patron share of imports (continuous), dependence asymmetry, aid flows; embargo/cutoff episodes as event-based shocks (better than Bartik here).
3. **Market-concentration moderator:** continuous test of "effect declines as market multipolarizes" (replaces the underpowered era interaction).
4. **Asia-Pacific paragraph:** why leverage fails there (rivalry pairs among same-patron clients).
5. Network robustness (TERGM on clean panels) — appendix.
6. Update Poast; revise the slide deck (current deck reflects the voided results — **do not circulate until revised**).

## 7. File inventory (`build/`)

- **Panels:** `clean_polrel_panel_1955_2014.csv` (primary), `clean_mena_panel_1990_2014.csv`, `clean_polrel_panel_1990_2014.csv`; `dyad_year_panel_1990_2014.csv` (**voided — do not use**).
- **Results memos (current):** `RESULTS_clean_reassessment.md`, `RESULTS_mena_clean.md`, `RESULTS_patron_confirmation.md`, `RESULTS_patron_identification.md`, `RESULTS_region_era.md`. (**Voided:** `RESULTS_region_logit.md`, `RESULTS_identification.md`, `RESULTS_bartik_iv.md`.)
- **Scripts:** `integrate.py`, `clean_panel.py`, `hardening.py`, `mena_clean.py`, `patron_confirm.py`, `patron_identification.py`, `region_era.py`, `bartik_iv.py`, `iv_estimation.py`, `build_panel.R`.
- **Figures:** `FIG_patron_by_region_era.png` (current), `FIG_data_overview.png` (descriptive, still valid); `FIG_overlap_by_region.png` (**voided**).
- **Slides:** `overlap_conflict_slides.tex/.pdf` (**needs revision before any circulation**).
- **Data acquired** (`data/`): global SIPRI register, MID 5.0, V-Dem v16, COW Trade 4.0, capital coordinates/distances, Voeten ideal points.
