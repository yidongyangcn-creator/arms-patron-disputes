import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _paths import RAW, REFERENCE, DERIVED

#!/usr/bin/env python3
"""10_sipri_ingest.py — SIPRI Trade Register -> audited bilateral TIV flows.

This step used to live inline at the top of 11_integrate.py. It was split out
because the defects in that code all sat here:

  1. MULTI-YEAR REPLICATION. In the per-deal export, "SIPRI TIV of delivered
     weapons" is the deal total across every listed delivery year. The old code
     exploded "Year(s) of delivery" by year and kept the full total on each year,
     so a deal delivered over seven years was counted seven times. Global
     inflation 4.49x (MENA export 3.42x).
  2. SILENT DROPS. Names that failed to map returned None and were removed by
     dropna() with no warning.
  3. WEST GERMANY. SIPRI writes "Germany" for the FRG before 1990. Exact match to
     the COW state list sent it to 255 (unified Germany) instead of 260 (German
     Federal Republic, 1955-1990), so the FRG had no imports in any COW-coded
     Cold War panel. Fixed with year-bounded crosswalk rows.

LOCAL PRODUCTION. The per-delivery-year export carries a "Local production"
Yes/No flag. It is NOT a clean licensed-production marker: it is set for whole
deals with any local share, including component work-share (F-35A to Australia,
Israel, Norway and Denmark — all assembled in Fort Worth — are flagged Yes) as
well as kit assembly (M1A1 to Egypt) and true licensed builds (F-15J, Su-30MKI).
It covers 26.5% of all TIV 1950-2025. Dropping every flagged row therefore
removes real cross-border deliveries. Hence:
  --measure all          (DEFAULT) every delivery, SIPRI's own convention
  --measure crossborder  drop rows flagged Local production = Yes (robustness)
Both columns are always written to bilateral_tiv_by_year_full.csv, and the
recipient-year flagged share is written for use as a moderator.

SCHEMA. The script detects which SIPRI export it has been given:
  NEW  one row per delivery year: "Delivery year", "TIV delivery values",
       "Local production". Exact per-year TIV. USE THIS ONE.
  OLD  one row per deal: "Year(s) of delivery", "SIPRI TIV of delivered weapons".
       TIV is split evenly across the listed years — an approximation — and the
       local-production flag is absent. A warning is printed. Fine for testing
       the crosswalk; not for results.

NAMES. Mapped through data/reference/sipri_cow_crosswalk.csv first (rows may be
bounded by yr_from / yr_to), then by exact match to the COW state list. Names
ending in "**" (international organisations) and names containing "*"
(non-state recipients) are dropped by rule. ANY OTHER NAME THAT DOES NOT MAP
HALTS THE BUILD and is printed with its row count and TIV. There is no flag to
suppress this. Add the name to the crosswalk as map or drop, with a note.

MEMBERSHIP CHECK. Mapped rows dated outside the COW membership spell of their
code (e.g. Kuwait 1953, Brunei 1965-83) are listed in
sipri_ingest_outside_membership.csv. They do not halt the build — they cannot
enter a COW dyad in those years — but a large entry there means a wrong code.

OUTPUTS (to DERIVED unless --out is given)
  bilateral_tiv_by_year.csv            rec_cc, sup_cc, yr, tiv   (tiv = --measure)
  bilateral_tiv_by_year_full.csv       + tiv_all, tiv_local, tiv_crossborder
  licensed_share_by_recipient_year.csv rec_cc, yr, tiv_all, tiv_local, licensed_share
  sipri_ingest_dropped.csv             every dropped name, side, reason, rows, TIV
  sipri_ingest_outside_membership.csv  mapped rows outside the code's COW spell
  sipri_ingest_audit.json              schema, measure, counts, drops, TIV totals

USAGE
  python code/01_build/10_sipri_ingest.py
  python code/01_build/10_sipri_ingest.py --measure crossborder --out /tmp/xb
"""
import argparse, io, json, re
import numpy as np, pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--input", default=str(RAW / "trade-register.csv"))
ap.add_argument("--out", default=str(DERIVED))
ap.add_argument("--crosswalk", default=str(REFERENCE / "sipri_cow_crosswalk.csv"))
ap.add_argument("--statelist", default=str(REFERENCE / "statelist2024.csv"))
ap.add_argument("--measure", choices=["all", "crossborder"], default="all")
args = ap.parse_args()
OUT = pathlib.Path(args.out); OUT.mkdir(parents=True, exist_ok=True)

def banner(msg):
    print("\n" + "=" * 78 + "\n" + msg + "\n" + "=" * 78)

# ----------------------------------------------------------------------------
# 1. Read, skipping SIPRI's preamble
# ----------------------------------------------------------------------------
raw = open(args.input, encoding="utf-8-sig", errors="replace").read().splitlines()
hdr = next(i for i, l in enumerate(raw) if "Recipient" in l and "Supplier" in l)
reg = pd.read_csv(io.StringIO("\n".join(raw[hdr:])), dtype=str, keep_default_na=False)
reg.columns = [c.strip() for c in reg.columns]
for c in ("Recipient", "Supplier"):
    reg[c] = reg[c].astype(str).str.strip()
n_in = len(reg)

cols = set(reg.columns)
if {"Delivery year", "TIV delivery values"} <= cols:
    SCHEMA = "NEW"
elif {"Year(s) of delivery", "SIPRI TIV of delivered weapons"} <= cols:
    SCHEMA = "OLD"
else:
    sys.exit(f"Unrecognised SIPRI export. Columns found:\n  {sorted(cols)}")
print(f"input   : {args.input}\nschema  : {SCHEMA}\nmeasure : {args.measure}\nrows    : {n_in:,}")

# ----------------------------------------------------------------------------
# 2. One row per (recipient, supplier, delivery year) with that year's TIV
# ----------------------------------------------------------------------------
num = lambda s: pd.to_numeric(s.astype(str).str.strip().replace({"": np.nan, "?": np.nan}), errors="coerce")

if SCHEMA == "NEW":
    lp_col = next((c for c in reg.columns if c.lower().startswith("local production")), None)
    long = pd.DataFrame({
        "Recipient": reg["Recipient"], "Supplier": reg["Supplier"],
        "yr": num(reg["Delivery year"]),
        "tiv": num(reg["TIV delivery values"]).fillna(0.0),
    })
    if lp_col is None:
        banner("WARNING: NEW-schema export has no 'Local production' column.\n"
               "Local production cannot be separated. Re-export with it included.")
        long["local"] = np.nan
        lp_counts = {}
    else:
        lp = reg[lp_col].astype(str).str.strip().str.rstrip(";").str.strip().str.lower()
        lp_counts = lp.replace({"": "(blank)"}).value_counts().to_dict()
        print(f"'{lp_col}' values: {lp_counts}")
        long["local"] = lp.eq("yes")
    replication = 1.0
else:
    banner("WARNING: OLD (per-deal) SIPRI export.\n"
           "  * TIV is split evenly across listed delivery years. This approximates\n"
           "    the true per-year schedule and is not suitable for reported results.\n"
           "  * The local-production flag is absent in this format.\n"
           "Re-export in the per-delivery-year format.")
    d = reg.assign(tiv_deal=num(reg["SIPRI TIV of delivered weapons"]).fillna(0.0),
                   _yrs=reg["Year(s) of delivery"].astype(str).str.split(";"))
    d = d.explode("_yrs")
    d["yr"] = num(d["_yrs"])
    d = d.dropna(subset=["yr"])
    n_years = d.groupby(level=0)["yr"].transform("size")       # valid years per deal
    long = pd.DataFrame({"Recipient": d["Recipient"], "Supplier": d["Supplier"],
                         "yr": d["yr"], "tiv": d["tiv_deal"] / n_years, "local": np.nan})
    legacy_total = d["tiv_deal"].sum()                           # what the old code produced
    replication = float(legacy_total / max(long["tiv"].sum(), 1e-9))
    print(f"legacy method would have inflated TIV {replication:.2f}x")
    lp_counts = {}

if args.measure == "crossborder" and long["local"].isna().all():
    sys.exit("--measure crossborder needs the 'Local production' column.")

long = long.dropna(subset=["yr"]).copy()
long["yr"] = long["yr"].astype(int)

# ----------------------------------------------------------------------------
# 3. Name (and year) -> COW code, with an explicit reason for every outcome
# ----------------------------------------------------------------------------
xw = pd.read_csv(args.crosswalk, dtype=str, keep_default_na=False)
for c in ("yr_from", "yr_to"):
    if c not in xw.columns: xw[c] = ""
xw["sipri_name"] = xw["sipri_name"].str.strip()
xw["lo"] = pd.to_numeric(xw.yr_from, errors="coerce").fillna(-1e9)
xw["hi"] = pd.to_numeric(xw.yr_to,   errors="coerce").fillna( 1e9)
for nm, g in xw.groupby("sipri_name"):
    g = g.sort_values("lo")
    if (g.lo.values[1:] <= g.hi.values[:-1]).any():
        sys.exit(f"Crosswalk rows for {nm!r} have overlapping year ranges:\n"
                 f"{g[['sipri_name','ccode','action','yr_from','yr_to']].to_string(index=False)}")
XW = {nm: g for nm, g in xw.groupby("sipri_name")}
sl = pd.read_csv(args.statelist)
cow = {str(n).strip(): int(c) for n, c in zip(sl.statenme, sl.ccode)}

def resolve(name, yr):
    if name in XW:
        g = XW[name]; g = g[(g.lo <= yr) & (yr <= g.hi)]
        if g.empty: return None, "UNMATCHED"            # in crosswalk, but not for this year
        r = g.iloc[0]
        if r.action == "map":  return int(r.ccode), "crosswalk"
        if r.action == "drop": return None, "drop: crosswalk"
        sys.exit(f"Crosswalk action must be map or drop, got {r.action!r} for {name!r}")
    if name.endswith("**"): return None, "drop: international organisation (**)"
    if "*" in name:         return None, "drop: non-state recipient (*)"
    if name in cow:         return cow[name], "statelist"
    return None, "UNMATCHED"

names = pd.unique(pd.concat([long.Recipient, long.Supplier]))
for side, key in (("Recipient", "rec"), ("Supplier", "sup")):
    pairs = long[[side, "yr"]].drop_duplicates()
    res = {(n, y): resolve(n, y) for n, y in zip(pairs[side], pairs.yr)}
    k = list(zip(long[side], long.yr))
    long[f"{key}_cc"]  = [res[x][0] for x in k]
    long[f"{key}_why"] = [res[x][1] for x in k]

side = pd.concat([
    long[["Recipient", "rec_why", "tiv"]].set_axis(["name", "reason", "tiv"], axis=1).assign(side="recipient"),
    long[["Supplier",  "sup_why", "tiv"]].set_axis(["name", "reason", "tiv"], axis=1).assign(side="supplier"),
])
dropped = (side[side.reason.str.startswith(("drop", "UNMATCHED"))]
           .groupby(["reason", "side", "name"]).agg(rows=("tiv", "size"), tiv=("tiv", "sum"))
           .reset_index().sort_values(["reason", "tiv"], ascending=[True, False]))
dropped.to_csv(OUT / "sipri_ingest_dropped.csv", index=False)

unmatched = dropped[dropped.reason == "UNMATCHED"]
if not unmatched.empty:
    banner("BUILD HALTED — SIPRI names that match neither the crosswalk nor the COW state list")
    print(unmatched[["side", "name", "rows", "tiv"]].to_string(index=False))
    share = unmatched.tiv.sum() / max(long.tiv.sum(), 1e-9)
    print(f"\n{len(unmatched)} name-side pairs, {int(unmatched.rows.sum())} rows, "
          f"{unmatched.tiv.sum():,.1f} TIV ({share:.2%} of all TIV)")
    print(f"\nAdd each to {args.crosswalk} as action=map (with ccode) or action=drop,"
          "\nwith a note saying why. Then re-run. Written to sipri_ingest_dropped.csv.")
    sys.exit(2)

# ----------------------------------------------------------------------------
# 3b. Membership check (informational): mapped rows outside the COW spell
# ----------------------------------------------------------------------------
spans = {}
for c, sy, ey in zip(sl.ccode, sl.styear, sl.endyear):
    spans.setdefault(int(c), []).append((int(sy), int(ey)))
last_cow_year = int(sl.endyear.max())
inside = lambda c, y: any(a <= y <= b for a, b in spans.get(int(c), []))
om = []
for key, nm in (("rec", "Recipient"), ("sup", "Supplier")):
    d = long[long[f"{key}_cc"].notna() & (long.yr <= last_cow_year)]
    bad = d[[not inside(c, y) for c, y in zip(d[f"{key}_cc"], d.yr)]]
    if len(bad):
        om.append(bad.groupby([nm, f"{key}_cc"]).agg(rows=("tiv", "size"), tiv=("tiv", "sum"),
                  yr_min=("yr", "min"), yr_max=("yr", "max")).reset_index()
                  .set_axis(["name", "ccode", "rows", "tiv", "yr_min", "yr_max"], axis=1)
                  .assign(side=key))
om = (pd.concat(om) if om else pd.DataFrame(columns=["name","ccode","rows","tiv","yr_min","yr_max","side"])
      ).sort_values("tiv", ascending=False)
om.to_csv(OUT / "sipri_ingest_outside_membership.csv", index=False)
if len(om):
    print(f"\nMapped rows outside the COW membership spell (≤{last_cow_year}; informational):")
    print(om.head(12).round(1).to_string(index=False))

# ----------------------------------------------------------------------------
# 4. Aggregate to recipient-supplier-year
# ----------------------------------------------------------------------------
ok = long.dropna(subset=["rec_cc", "sup_cc"]).copy()
ok["rec_cc"] = ok.rec_cc.astype(int); ok["sup_cc"] = ok.sup_cc.astype(int)
ok = ok[ok.rec_cc != ok.sup_cc]
if SCHEMA == "NEW" and ok["local"].notna().any():
    ok["tiv_local"] = np.where(ok["local"].astype(bool), ok.tiv, 0.0)
else:
    ok["tiv_local"] = np.nan

full = (ok.groupby(["rec_cc", "sup_cc", "yr"], as_index=False)
          .agg(tiv_all=("tiv", "sum"), tiv_local=("tiv_local", lambda s: s.sum(min_count=1))))
full["tiv_crossborder"] = full.tiv_all - full.tiv_local.fillna(0.0)
full = full[full.tiv_all > 0]
full.to_csv(OUT / "bilateral_tiv_by_year_full.csv", index=False)

mcol = "tiv_all" if args.measure == "all" else "tiv_crossborder"
flow = (full[full[mcol] > 0][["rec_cc", "sup_cc", "yr", mcol]].rename(columns={mcol: "tiv"}))
flow.to_csv(OUT / "bilateral_tiv_by_year.csv", index=False)

ls = full.groupby(["rec_cc", "yr"], as_index=False).agg(
        tiv_all=("tiv_all", "sum"), tiv_local=("tiv_local", lambda s: s.sum(min_count=1)))
ls["licensed_share"] = ls.tiv_local / ls.tiv_all
ls.to_csv(OUT / "licensed_share_by_recipient_year.csv", index=False)

# ----------------------------------------------------------------------------
# 5. Audit
# ----------------------------------------------------------------------------
by_reason = (dropped.groupby("reason").agg(name_side_pairs=("name", "size"),
             rows=("rows", "sum"), tiv=("tiv", "sum")).round(2).to_dict("index"))
audit = dict(
    input=args.input, schema=SCHEMA, measure=args.measure, rows_read=n_in,
    rows_per_delivery_year=int(len(long)),
    local_production_values=lp_counts,
    legacy_replication_factor=round(replication, 3),
    distinct_names=int(len(names)),
    dropped_by_reason=by_reason, unmatched=0,
    outside_membership_tiv=round(float(om.tiv.sum()), 1) if len(om) else 0.0,
    tiv_all=round(float(full.tiv_all.sum()), 1),
    tiv_local=None if full.tiv_local.isna().all() else round(float(full.tiv_local.sum()), 1),
    tiv_crossborder=round(float(full.tiv_crossborder.sum()), 1),
    tiv_in_flow_file=round(float(flow.tiv.sum()), 1),
    years=[int(flow.yr.min()), int(flow.yr.max())],
    recipients=int(flow.rec_cc.nunique()), suppliers=int(flow.sup_cc.nunique()),
    flow_rows=int(len(flow)),
)
if audit["tiv_local"] is not None:
    audit["local_flag_share_of_all_tiv"] = round(audit["tiv_local"] / audit["tiv_all"], 4)
json.dump(audit, open(OUT / "sipri_ingest_audit.json", "w"), indent=2)

banner("SIPRI INGEST — PASSED")
print(json.dumps(audit, indent=2))
print(f"\nOutputs in {OUT}")
