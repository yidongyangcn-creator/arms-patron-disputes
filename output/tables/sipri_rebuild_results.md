# SIPRI rebuild — results, 6 October 2026

Three builds, same code. Logs in `output/logs/rebuild_2026-10-06/`.

* **Old flows** — the previous `bilateral_tiv_by_year.csv` (per-deal export, multi-year replication). Reproduces the tracked 1955–2014 panel exactly, so every difference below comes from the data, not the code.
* **New, all deliveries** — per-delivery-year export (downloaded 6 Oct 2026, 60,789 rows, 1950–2025), every delivery counted. This is now the default (`--measure all`) and is what sits in `data/derived/`.
* **New, flagged local production removed** — same export, rows with `Local production = Yes` dropped (`--measure crossborder`; flows in `data/derived_crossborder/`).

Both new builds also carry the West Germany fix (below). Cell entries: odds ratio (cluster-robust p).

| Estimate | Old flows | New, all deliveries (default) | New, flagged local production removed |
|---|---|---|---|
| **Primary** — CW 1955–89, shared dominant (5-yr window), + UNGA | 0.66 (p=0.005) | **0.71 (p=0.014)** | 0.65 (p=0.006) |
| Same, no UNGA control | 0.64 (p=0.002) | 0.69 (p=0.007) | 0.63 (p=0.003) |
| Same, single-year measure (22) | 0.59 (p=0.001) | 0.66 (p=0.008) | 0.61 (p=0.006) |
| No-defence-pact subsample | 0.65 (p=0.032) | 0.76 (p=0.142) | 0.67 (p=0.052) |
| Drop dyads with a top-10 exporter | 0.71 (p=0.039) | 0.74 (p=0.060) | 0.74 (p=0.078) |
| + year fixed effects | 0.70 (p=0.019) | 0.76 (p=0.049) | 0.69 (p=0.018) |
| Originator dyads only | 0.69 (p=0.020) | 0.75 (p=0.055) | 0.70 (p=0.030) |
| Dyads at peace ≥10 yrs | 0.56 (p=0.003) | 0.60 (p=0.010) | 0.50 (p=0.001) |
| Full polrel sample, both-import dummy | 0.66 (p=0.005) | 0.71 (p=0.013) | 0.65 (p=0.006) |
| Dyad-FE conditional logit, CW (single-year) | 0.66 (p=0.041) | 0.77 (p=0.169) | 0.69 (p=0.069) |
| Dyad-FE conditional logit, 1955–2014 | 0.62 (p=0.002) | 0.73 (p=0.030) | 0.69 (p=0.013) |
| Dyad-FE, CW, 5-yr window | 0.85 (p=0.438) | 0.92 (p=0.684) | 0.91 (p=0.647) |
| CW shared US (w5) | 0.77 (p=0.154) | 0.76 (p=0.115) | 0.75 (p=0.113) |
| CW shared Soviet (w5) | 0.56 (p=0.094) | 0.71 (p=0.312) | 0.69 (p=0.281) |
| CW overlap gradient (w5) | 0.57 (p=0.002) | 0.61 (p=0.006) | 0.59 (p=0.006) |
| Post-1990 shared dominant (w5) | 0.83 (p=0.368) | 0.96 (p=0.846) | 0.86 (p=0.496) |
| Post-1990 shared US (w5) | 0.44 (p=0.040) | 0.48 (p=0.071) | 0.40 (p=0.024) |
| Full 1955–2014 (29) | 0.73 (p=0.027) | 0.80 (p=0.122) | 0.75 (p=0.059) |
| MENA post-1990 shared US (13) | 0.29 (p=0.015) | 0.46 (p=0.082) | 0.38 (p=0.025) |
| War given dispute, controls + era | 0.65 (p=0.430) | 0.35 (p=0.144) | 0.35 (p=0.147) |
| Financing: CW shared US baseline (27)* | 0.65 (p=0.013) | 0.66 (p=0.016) | 0.62 (p=0.006) |
\* Row 27 also reflects the Greenbook mapping fix, which applies to the two new builds only.

## What changed in the data

1. **Replication.** Old global TIV was 4.49 times the true total (9.53m against 2.12m TIV, 1950–2025). The new yearly totals line up with SIPRI's published world totals.
2. **West Germany.** SIPRI writes "Germany" for the FRG before 1990. Exact matching sent it to COW 255 rather than 260, so in the old build the FRG had no imports in any Cold War year and dropped out of the both-importer sample: 489 FRG dyad-years now enter it, 181 of them with a shared dominant patron. This was fixed with year-bounded crosswalk rows, and a membership check now lists any mapped row that falls outside its code's COW spell.
3. **Recoding.** Among Cold War both-importer dyad-years, 958 of 29,708 (3.2%) change `sd_w5` under the all-deliveries measure: 534 go from 0 to 1 and 424 from 1 to 0. Twelve of those are onset dyad-years, ten of which go from 0 to 1 (Egypt–Israel 1989, China–Taiwan 1987, China–South Korea 1985, China–India 1971, among others), and that is why the primary estimate moves towards 1. Under the local-production-removed measure, 1,776 (6.1%) change.
4. **The local-production flag is not a licensed-production marker.** SIPRI sets it for any deal with a local share, including component work-share: F-35A deliveries to Australia, Israel, Norway and Denmark are all flagged, although every one of those aircraft was assembled in Fort Worth. It also covers kit assembly (M1A1 to Egypt) and true licensed builds (F-15J, Su-30MKI, F-104G). In total it touches 26.7% of all TIV. Dropping every flagged row therefore also removes real cross-border deliveries, which is why "all deliveries" is the default and the cross-border-only build is a robustness check. Separating true licensed production would mean coding SIPRI's deal comments.

## Silent-drop fixes made along the way

* `27_financing_test.py`: 8.5% of Greenbook military aid had been dropped by `dropna()` with no warning, including Taiwan ($29bn, coded as "China (Taiwan)"), Yugoslavia, Bosnia, North Korea and several Caribbean states. They are now mapped, Germany before 1990 is now coded 260, and any unmapped country halts the script.
* The old `summary.json` recorded 707 unmapped SIPRI rows, also dropped silently. The new ingest has none, and any future unmapped name halts the build.

## Reading

The Cold War result holds on the corrected data, with a smaller effect and stronger dependence on how the treatment is measured: the primary OR is 0.71 (p=0.014) counting all deliveries and 0.65 (p=0.006) counting cross-border only. The checks that weaken most under all-deliveries are the no-defence-pact subsample (p=0.14), the single-year dyad-FE model (p=0.17) and the pooled 1955–2014 model (p=0.12). The post-1990 null and the null shift-share IV are unchanged.
