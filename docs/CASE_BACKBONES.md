# Case-study quantitative backbones — figures, selection table, and what the delivery data show

*All from our SIPRI series (`case_backbones.py`). Figures: `CASE_iraq_syria.png`, `CASE_hungary_romania.png`, `CASE_greece_turkey.png`, `CASE_egypt_israel.png`; table: `case_selection_table.csv`.*

## Final case slate (model-based selection, corrected)

| role | dyad | years (in sample) | onsets | predicted | patron-conc | residual |
|---|---|---|---|---|---|---|
| **Case A — off-the-line** | Iraq–Syria | 45 | 7 | 2.29 | 0.73 | **+4.71** |
| **Case B — on-the-line** | **Hungary–Romania** | 58 | 1 | 1.43 | 0.64 | **−0.43** |
| shadow (US patron) | Greece–Turkey | 59 | 8 | 3.96 | 0.58 | +4.04 |
| boundary | Egypt–Israel | — | 7 post-1979 | — | shared US ~1980–2005 | model under-predicts |

Hungary–Romania replaces the Warsaw-Pact–vs-Czechoslovakia pairs as Case B: it combines genuine latent conflict (Transylvania; wars in 1919/1944), 6 decades of shared Soviet patronage, and near-zero militarization (one display-level incident, 1971) — and it *fits the model* (residual −0.43). Note: HUN–CZE / POL–CZE lose their 1968 rows from the estimation sample through missing trade covariates (echoes Yidong's memo); a no-trade-control robustness run is on the to-do list.

## What the delivery series show (key facts for the case texts)

**Iraq–Syria — the reported 1980–82 Soviet "suspension" of Iraq is NOT visible in deliveries.** USSR→Iraq TIV 1978–84: 7470, 7000, 7776, 7454, **10342**, 9319, 11359 — deliveries *rose* through the alleged suspension window (figure confirms visually). Two readings, both usable: (i) the suspension (if real) applied to new agreements, not pipeline deliveries — i.e. the lever's bite was shallow; (ii) the patron never seriously pulled the lever between these clients. Either way this **strengthens the off-the-line reading**: Soviet leverage over Iraq/Syria was available in principle and unused/ineffective in practice. The archival task is now sharper: find what (if anything) Moscow actually withheld in 1980–82.

**Greece–Turkey — the US embargo IS visible.** USA→Turkey TIV: 1916 (1974) → **575, 443, 443** (1975–77) → 1523, 1499 (1978–79). A documented, data-visible instance of the lever being pulled — after the invasion it failed to prevent, and its aftermath (Turkish domestic arms industry) illustrates the outside-option escape. Perfect shadow case.

**Egypt — the patron switch is textbook.** USSR→Egypt: 10072 (1972) → 2658 (1974) → 35 (1976–77) → 0 (1978 on). USA→Egypt: 0 → 896 (1979) → 2378 (1982). Combined with the onset record (wars end 1979; display-level onsets 1983–2014), Egypt–Israel illustrates the **escalation-capping margin** rather than onset prevention.

**Hungary–Romania.** Both under Soviet supply throughout; single 1971 display incident across 60 dyad-years despite genuine antagonism — the "dog that didn't bark" the mechanism predicts. Romania's post-1968 partial defection (reduced dependence, more autonomous behavior) provides within-case variation.

## To-do hooks

1. Archival verification: 1972 Soviet–Iraqi & 1980 Soviet–Syrian treaties' supply annexes; what Moscow actually did 1980–82; Warsaw Pact spare-part/licensing architecture; Romania's procurement autonomy path.
2. Robustness: re-run main spec without the trade control so Eastern-bloc dyads (incl. 1968) stay in sample.
3. Financing condition (cash vs aid clients): needs USAID Greenbook + Soviet aid estimates — next data acquisition.
