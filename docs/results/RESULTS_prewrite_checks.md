# Pre-writing checks — results

*Six checks run before drafting (`prewrite_checks.py`). Both-importer politically-relevant dyads, w5 measure, full controls + peace-years + UNGA, dyad-clustered SEs, unless noted.*

## 1. The patron-selection alternative (patrons avoid arming both sides of a rivalry)

| test | result |
|---|---|
| Does an onset predict losing shared-patron status within 3 years? | No: 35.5% (onset) vs 37.8% (no onset); OR 1.26, p=0.20 |
| …within 1 year? | Mild: OR 1.62, p=0.04 — some short-run patron reaction exists |
| Effect among dyads at peace ≥20 years (patron cannot be reacting to recent conflict) | **stronger**: CW OR 0.547 (p=0.039); full 0.490 (p=0.001) |
| …at peace ≥10 years | CW 0.556 (p=0.003); full 0.562 (p<0.001) |
| Sharing already established ≥5 years before t | weaker/ns: CW 0.693 (p=0.107); full 0.794 (p=0.198) |

Reading: patrons do sometimes drop one client right after a dispute, so selection is not zero. But the association is strongest exactly where selection-on-conflict cannot operate (long-peace dyads). Selection does not account for the result. The weaker estimate for long-established sharing is worth a sentence (most identifying variation comes from sharing spells that began within the last few years) but does not reverse anything.

## 2. Coalition joiners

Originator-only dyads (drops 143 of 948 onsets): CW primary OR **0.692, p=0.020**; same-top 0.751 (p=0.049). The full-period shared-US result weakens to 0.756 (p=0.11) — the Gulf-War-type coalition dyads were contributing to it. Report the originator-only version as the main US-patron estimate or flag this.

## 3. Trade control (drops Eastern-bloc dyads)

Without trade: sd_w5 0.673 (p=0.004) vs 0.661 with; shared US 0.721 (p=0.066) vs 0.770; shared Soviet 0.674 (p=0.125) vs 0.564 (p=0.094). Main result unaffected; the Soviet-patron estimate stays directionally negative and short of significance either way.

## 4. Conditioning on both-importer

Full politically-relevant sample, shared patron coded 0 when not both importers, plus a both-importer dummy: sd_w5 CW **0.661 (p=0.005)**, full 0.710 (p=0.006). The sample restriction was not doing the work. (Both-importer dyads themselves have higher onset odds in the CW, OR 2.35 — arms-importing pairs are pairs with something to fight about.)

## 5. Year fixed effects

CW primary 0.701 (p=0.019); full-period shared US 0.697 (p=0.051). Survives.

## 6. Asia-Pacific

The shared-patron onsets are: Taiwan–Japan (6), ROK–Japan (6), China–India (5), Thailand–Laos (4), China–Vietnam, China–North Korea, Taiwan–Philippines. Two things this reveals. (i) The "shared US patron" pairs — Japan, Korea, Taiwan — are rich states with large domestic arms industries; their imports are a small part of their armament, so a 50% US share of imports is not 50% dependence. Domestic production is the ultimate outside option and our import-based measure cannot see it. (ii) China–India and China–Vietnam coded as "shared Soviet patron" are measurement noise: China's imports after 1960 were tiny, so a dominant supplier of a near-empty portfolio counts the same as Egypt's dependence. Fix for the paper: condition dominance on import intensity (imports / military expenditure, from NMC milex), so that patron dominance only counts where imports matter. This is a real refinement, not a patch.

## What this settles for the draft

- Primary result is robust to selection checks, joiner exclusion, trade control, sample conditioning and year FE.
- Present the originator-only CW estimate (0.69) alongside the all-dyad one (0.66); use originator-only for the US-patron claim.
- Add an import-intensity condition to the measure before finalizing tables (one more build step), and use it to explain Asia-Pacific.
- Selection alternative: address explicitly with checks 1a–1b; do not claim it is absent, claim it does not drive the result.
