# Rebuilding the SIPRI flows

_October 2026. Read this before re-running anything._

> **STATUS 6 Oct 2026: DONE.** The rebuild was run on the per-delivery-year export (`../data/raw/trade-register.csv`, 60,789 rows). `data/derived/` now holds the new build, and the old build is kept in `data/derived_OLD/` and `output_OLD/`. Results and the old-vs-new comparison are in `output/tables/sipri_rebuild_results.md`. Three things differ from the plan below:
> 1. **The default measure is all deliveries, not cross-border only.** SIPRI's `Local production` flag also covers component work-share (for example, the F-35As delivered to Australia and Israel), so dropping flagged rows removes real transfers. Cross-border-only is `--measure crossborder` and serves as a robustness check (`data/derived_crossborder/`).
> 2. **West Germany fix.** SIPRI's "Germany" before 1990 is now mapped to COW 260 (the FRG), via year-bounded crosswalk rows (`yr_from`, `yr_to`).
> 3. **`27_financing_test.py`** silently dropped 8.5% of Greenbook aid, Taiwan included. That is fixed, and the script now halts on any unmapped country.
>
> The `data/raw/` links now point to files under `Middle East/` by relative path, so the pipeline runs on this Mac. The old absolute links pointed at a sandbox path that no longer exists.

## Why

The SIPRI flows that every panel in this repository is built from had three defects, and the pipeline has an ordering trap that would hide the fix.

**1. Multi-year deliveries were counted once per delivery year.** In the per-deal SIPRI export, `SIPRI TIV of delivered weapons` is the deal total across every listed delivery year (it equals TIV-per-unit × number delivered in 99.8% of multi-year deals). The old code in `11_integrate.py` exploded `Year(s) of delivery` by year and kept the full total on each year. A deal delivered over seven years was counted seven times. Because the multiplier is the number of delivery years, it does not wash out of shares — long programmes are overweighted in every year they touch.

Measured on the MENA export (15 recipients, 1990–2024), comparing the production build against the same data with TIV spread across delivery years:

| | |
|---|---|
| Total TIV inflation | 3.4–3.6× |
| Recipient-years whose dominant supplier changes | 14.9% |
| `shared_dominant` (paper definition) recoded | 5.8% of importing dyad-years (127 → 1, 49 → 0) |
| `shared_us` recoded | 4.8% |
| Overlap, correlation old–new | 0.955; 18% of dyad-years move by more than 0.10 |

A face-validity example: the production build has **Germany** as Israel's dominant supplier in 2010–2012 (shares 0.65–0.74). With deliveries spread correctly it is the **United States** (0.71–0.89). The Dolphin submarine programme was being counted once per delivery year.

The global effect is not yet measured and needs this rebuild. The production file's yearly totals run around 100,000–200,000 TIV; check one year against SIPRI's own published world total to confirm the inflation globally.

**2. Licensed production counted as a cross-border transfer.** SIPRI records units built under licence in the recipient country as transfers from the licensor, dated to the year each unit is completed. Nothing crosses a border and the licensor cannot withhold units already on someone else's production line — the opposite of the resupply-leverage mechanism the paper argues for. The per-deal export has no field for it.

**3. Unmatched names were dropped silently.** `sipri2ccode()` returned `None` and `dropna()` removed the rows. The production build happened to be complete, but only because its export named every state the way COW does. A filtered export of the same database writes `UAE` instead of `United Arab Emirates` and loses 12.2% of its TIV without a warning.

**4. The 1955–2014 panel will not rebuild on its own.** `clean_polrel_panel_1955_2014.csv` — the panel behind the primary test — is created by `code/02_analysis/22_patron_confirmation.py`, **only if the file does not exist**. Six later scripts (14, 16, 25, 27, 28, 29) read it, add columns and write it back. If you re-run the README's pipeline order without deleting the file, 22 silently reuses the old panel and every result comes from the old flows. If you delete it and follow the README order, 14 crashes because 22 has not run yet.

## What changed in the code

| File | Change |
|---|---|
| `code/01_build/10_sipri_ingest.py` | **New.** Detects the export schema, maps names through the crosswalk, halts on any unmatched name, separates licensed production, writes audited flows. |
| `data/reference/sipri_cow_crosswalk.csv` | **New.** The 20 hand overrides and 8 drops formerly hard-coded in `11_integrate.py`, plus `UAE`, each with a note. |
| `code/01_build/11_integrate.py` | Reads flows from step 10 instead of parsing SIPRI itself. Fixes `OUT=BASE+"/build"` (`BASE` was undefined after the `_paths` refactor, so the committed script could not run). Comments the outcome-selecting retention rule in section 8. |
| `code/03_diagnostics/32_sipri_rebuild_qa.py` | **New.** Old-vs-new comparison of TIV, dominant suppliers, `shared_dominant` / `shared_us` / `shared_soviet` under the paper's ≥50% definition, overlap, licensed share, and a Warsaw Pact check. |

`bilateral_tiv_by_year.csv` keeps its four columns (`rec_cc, sup_cc, yr, tiv`). Every downstream script reads it unchanged. `tiv` is now **cross-border only**.

## Step 1 — download SIPRI in the right format

You need the export with **one row per delivery year** and a **local-production field**. The target columns, from the export Mieke Löhrer used in 2026:

```
Supplier, Recipient, Delivery year, Numbers delivered, TIV delivery values,
Armament category, Local production
```

All suppliers, all recipients, 1950 to the latest year available. If the export form offers local production as an option, include it. Save as `data/raw/trade-register.csv`.

If you can only get the old per-deal format (`Year(s) of delivery`, `SIPRI TIV of delivered weapons`), step 10 will still run — it spreads TIV evenly across delivery years and prints a warning — but it cannot remove licensed production and the result is not for reporting.

## Step 2 — run in this order

```bash
cp -r data/derived data/derived_OLD                    # keep the old build for comparison
rm data/derived/clean_polrel_panel_1955_2014.csv       # otherwise 22 silently reuses it

python code/01_build/10_sipri_ingest.py                # will probably halt the first time — see below
python code/01_build/11_integrate.py
python code/01_build/12_clean_panel.py
python code/01_build/13_mena_panel.py
python code/02_analysis/22_patron_confirmation.py      # MOVED UP: creates the 1955-2014 panel
python code/01_build/14_window_measures.py             # adds columns to it
python code/01_build/15_ucdp_extension.py
python code/01_build/16_leverage_measures.py           # adds columns
python code/02_analysis/21_patron_identification.py
python code/02_analysis/23_region_era.py
python code/02_analysis/24_escalation_margin.py
python code/02_analysis/25_substitutability.py         # adds columns
python code/02_analysis/26_case_backbones.py
python code/02_analysis/27_financing_test.py           # adds columns
python code/02_analysis/28_prewrite_checks.py          # adds columns, drops three
python code/02_analysis/29_import_intensity.py         # adds columns

python code/03_diagnostics/32_sipri_rebuild_qa.py      # writes output/tables/sipri_rebuild_qa.md
```

**When step 10 halts**, it prints every name that matched neither the crosswalk nor the COW state list, with row counts and TIV. A new export will probably surface some — SIPRI does not apply its own asterisk convention consistently, so a non-state recipient like `Indonesia rebels` can appear without one. Add each to `sipri_cow_crosswalk.csv` as `map` (with a ccode) or `drop`, with a note saying why, and re-run. **Do not loosen the check to get past it.**

## Step 3 — what to look at

1. **`sipri_ingest_audit.json`**: schema should be `NEW`; `licensed_share_of_all_tiv` tells you how large the licensed-production problem is overall.
2. **Global TIV by year** in the QA report, against SIPRI's published world totals.
3. **Israel 2010–2012** should have the United States as dominant supplier, not Germany.
4. **The primary test in 22**: does `shared_dominant` for Cold War both-importers still give an odds ratio near 0.66? This is the number that matters.
5. **The licensed-share table**: India, Turkey, South Korea and Brazil should be near the top. If they are not, check that the local-production field parsed (`local_production_values` in the audit).
6. **Warsaw Pact**: expect the Soviet *share* to stay near 100% for Poland, Czechoslovakia, the GDR and Bulgaria — they bought almost everything from the USSR either way — but the cross-border *volume* to fall. That matters for the leverage and import-intensity measures (16, 29), less for `shared_soviet`.

## Step 4 — the test this makes possible

If licensed production is where a patron's resupply leverage is weakest, the restraint effect should be **weaker** for dyads where either side has a high licensed-production share. `licensed_share_by_recipient_year.csv` is the moderator. Merge it onto the 1955–2014 panel at t-1 for both sides, take the maximum or the mean, and interact it with `shared_dominant` in the primary specification. A negative interaction would be evidence for the mechanism from inside the data rather than a robustness check against it.
