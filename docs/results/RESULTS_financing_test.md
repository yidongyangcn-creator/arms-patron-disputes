# Financing test: is patron leverage about concessional money? — No (US side)

*Data: USAID Greenbook (US Overseas Loans & Grants, 1946–2020, constant 2020$; official copy withdrawn Jan 2025, obtained from the maintained mirror). Processed to `data/us_military_aid_greenbook.csv` / `us_economic_aid_greenbook.csv`; 176 countries mapped to COW codes. Validation: Egypt military aid 0 (1975) → $4.47B (1979, Camp David package); Israel $11.9B spike (1979); Turkey aid continues through the 1975–78 embargo.*

## The test

The Iraq–Syria case memo's candidate condition 1 holds that leverage runs through **concessional financing** — cash-paying clients (oil states) should be hardest to coerce. US-side quantitative version: the shared-US-patron effect should be concentrated among dyads where **both sides' arms relationship is aid-financed** (>$50m constant military aid in the 5-yr window; continuous version: ln min aid).

## Results (both-importers, 1955–2014, full controls + peace-yrs + UNGA)

| spec | OR | p |
|---|---|---|
| shared US patron (baseline, full period) | **0.646** | **0.013** |
| both-US-aid-financed alone | 1.002 | 0.988 |
| shared US × both-aid interaction | 1.042 | 0.902 |
| → effect when both aid-financed | 0.642 | — |
| → effect when NOT aid-financed | 0.616 | — |
| shared US × ln(min aid) | 1.012 | 0.557 |
| split: among both-aid dyads | 0.683 | 0.139 (78 onsets) |
| split: among not-both-aid | 0.617 | 0.022 |

## Verdict

**The financing condition fails on the US side.** The pacifying association of a shared US patron is the same for aid-financed and cash clients (interaction p≈0.9). Leverage — whatever carries it — is not (only) concessional money.

## Implications

1. **Iraq–Syria case:** the "they paid cash" explanation loses its quantitative footing. Weight shifts to condition 2 (**outside options** — Iraq's French relationship) and condition 3 (**patron indifference** — consistent with the delivery series showing no Soviet suspension bite). The case's archival focus should follow.
2. **Theory:** the leverage channel is more plausibly resupply dependence / spare parts / interoperability lock-in than financial terms.
3. Soviet-side financing (Egypt aid-financed vs Iraq/Syria oil-cash) cannot be tested quantitatively with existing datasets — it stays a hand-coded contrast inside the case study, now with the caveat that its US-side analogue finds nothing.
4. Bonus: full-period shared-US baseline is significant (OR 0.646, p=0.013) — a cleaner single-number headline for the US-patron story than the era splits.

*Files: `financing test` code inline in session; panel updated with `aid_i`, `aid_j`, `both_us_aid`, `ln_min_aid`.*
