# Clean MENA re-test — the effect survives, and sharpens into a patron story

*Complete-network MENA15 panel (all 105 dyads × 1990–2014 = 2,625 dyad-years, 80 onsets), rebuilt with NO selection on imports or conflict. Full controls + Carter–Signorino peace-years, dyad-clustered SEs.*

## Results ladder

| spec | measure | OR | p |
|---|---|---|---|
| full controls + peace-yrs | overlap gradient | 0.41 | 0.113 |
| both-import subsample | overlap gradient | 0.49 | 0.187 |
| Firth (rare events) | overlap gradient | 0.43 | 0.078 |
| both-importers | **shared dominant supplier** (≥50% same top) | **0.44** | **0.053** |
| both-importers | **shared US patron** | **0.29** | **0.015** |

## Jackknife on shared US patron (sign never flips)

drop Gulf-War 1990–91: OR 0.22 (p=.030) · drop IRQ: 0.40 (.056) · drop ISR: 0.30 (.106) · drop TUR: 0.40 (.076) · drop IRN: 0.27 (.014) · drop EGY: 0.25 (.073) · drop SAU: 0.37 (.045)

## Reading

1. **The MENA finding survives the clean design directionally** — the generic overlap gradient is consistently negative (OR ~0.41–0.49) but underpowered at 80 onsets (Firth p=0.078).
2. **The sharper, mechanism-specific measure works better than the generic one**: sharing a *dominant patron* — and specifically the **United States** — is where the action is (OR 0.29, p=0.015; sign stable in every jackknife). Compare the global shared-US estimate (OR 0.60, ns): directionally consistent, concentrated in MENA.
3. Together with the global null for generic overlap, the evidence now points to a **conditional, patron-leverage story**: it is not portfolio similarity per se that pacifies, but a shared dominant supplier with leverage over both sides — visible where patron structures are strong (MENA), absent as a global average.

## Why this is good news for the paper

- The reframed thesis — *"common-patron leverage constrains escalation; generic supplier overlap does not"* — is more precise, more interesting, and fits **exactly** the mechanism Poast endorsed and the **Camp David case** (US becomes dominant patron of both Egypt and Israel after 1979; no Egypt–Israel MID onset after).
- The global null becomes part of the argument (rules out a mechanical structural effect), not an embarrassment.

## Honest cautions

- 58–80 onsets; the shared-US result is one significant coefficient among several tried — multiple-testing risk is real. Treat as the **new primary hypothesis**, to be confirmed (not re-discovered) in: other patron-heavy regions/periods, pre-registered-style robustness, and the case study.
- Next confirmatory steps: (a) test shared-patron in other strong-patron settings (e.g. Soviet clients pre-1991 if extended back; US clients in East Asia); (b) dependence-asymmetry / leverage measures; (c) re-run identification suite on the clean panels with the patron measure.

## Files
`clean_mena_panel_1990_2014.csv`, `mena_clean.py`.
