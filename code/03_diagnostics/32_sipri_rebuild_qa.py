import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _paths import DERIVED, TAB

#!/usr/bin/env python3
"""32_sipri_rebuild_qa.py — what changed between the old and rebuilt SIPRI flows.

Run after 10_sipri_ingest.py, against a copy of the pre-rebuild derived files:
    cp -r data/derived data/derived_OLD      # BEFORE re-running anything
    python code/01_build/10_sipri_ingest.py
    python code/03_diagnostics/32_sipri_rebuild_qa.py

Reports, old vs new:
  1. global TIV by year            — should fall by roughly the replication factor
  2. dominant supplier per recipient-year — how many change, and for the case countries
  3. shared dominant patron, importing dyad-years — how many flip 0->1 and 1->0
  4. overlap (L1 share similarity) — correlation and mean absolute change
  5. licensed-production share by recipient — who is most affected
Writes output/tables/sipri_rebuild_qa.md and prints the same.
"""
import argparse, itertools
import numpy as np, pandas as pd
from collections import defaultdict

ap = argparse.ArgumentParser()
ap.add_argument("--old", default=str(DERIVED.parent / "derived_OLD" / "bilateral_tiv_by_year.csv"))
ap.add_argument("--new", default=str(DERIVED / "bilateral_tiv_by_year.csv"))
ap.add_argument("--licensed", default=str(DERIVED / "licensed_share_by_recipient_year.csv"))
ap.add_argument("--out", default=str(TAB / "sipri_rebuild_qa.md"))
ap.add_argument("--recipients", default="", help="comma-separated ccodes to restrict to (for partial tests)")
ap.add_argument("--years", default="", help="e.g. 1990-2014")
args = ap.parse_args()

old = pd.read_csv(args.old); new = pd.read_csv(args.new)
if args.recipients:
    keep = {int(x) for x in args.recipients.split(",")}
    old = old[old.rec_cc.isin(keep)]; new = new[new.rec_cc.isin(keep)]
if args.years:
    a, b = map(int, args.years.split("-"))
    old = old[old.yr.between(a, b)]; new = new[new.yr.between(a, b)]

CASES = {651: "EGY", 666: "ISR", 640: "TUR", 350: "GRC", 750: "IND", 770: "PAK",
         670: "SAU", 630: "IRN", 732: "ROK", 140: "BRA", 696: "UAE", 663: "JOR"}
L = []
def say(s=""): print(s); L.append(s)

say("# SIPRI rebuild — what changed\n")
say(f"old: `{args.old}`  \nnew: `{args.new}`\n")

# 1 -------------------------------------------------------------------------
g = pd.DataFrame({"old": old.groupby("yr").tiv.sum(), "new": new.groupby("yr").tiv.sum()}).fillna(0)
g["ratio"] = g.old / g.new.replace(0, np.nan)
say("## 1. Total TIV by year\n")
say(f"Total: old {g.old.sum():,.0f} → new {g.new.sum():,.0f} (old/new = {g.old.sum()/g.new.sum():.2f})\n")
say("| year | old | new | old/new |\n|---|---|---|---|")
for y in [y for y in g.index if y % 5 == 0]:
    r = g.loc[y]; say(f"| {y} | {r.old:,.0f} | {r.new:,.0f} | {r.ratio:.2f} |")

# 2 -------------------------------------------------------------------------
def dominant(f):
    f = f.copy(); f["sh"] = f.tiv / f.groupby(["rec_cc", "yr"]).tiv.transform("sum")
    t = f.sort_values("sh", ascending=False).groupby(["rec_cc", "yr"]).first()
    return t[["sup_cc", "sh"]]
do, dn = dominant(old), dominant(new)
j = do.join(dn, lsuffix="_old", rsuffix="_new", how="inner")
flip = j[j.sup_cc_old != j.sup_cc_new]
say("\n## 2. Dominant supplier per recipient-year\n")
say(f"{len(flip):,} of {len(j):,} recipient-years ({len(flip)/max(len(j),1):.1%}) change dominant supplier.\n")
cf = flip.reset_index(); cf = cf[cf.rec_cc.isin(CASES)]
if len(cf):
    say("Changes for case-study countries:\n\n| recipient | year | old dominant (share) | new dominant (share) |\n|---|---|---|---|")
    for r in cf.itertuples():
        say(f"| {CASES[r.rec_cc]} | {r.yr} | {r.sup_cc_old} ({r.sh_old:.2f}) | {r.sup_cc_new} ({r.sh_new:.2f}) |")

# 3 -------------------------------------------------------------------------
# Paper definition (22_patron_confirmation.py, line 98): same top supplier AND that
# supplier >= 50% of BOTH sides' imports. Year here is the supply year; the panel
# uses it at t-1.
def shared(dom, sup=None):
    d = dom.reset_index(); out = {}
    for y, g2 in d.groupby("yr"):
        m = {r.rec_cc: (r.sup_cc, r.sh) for r in g2.itertuples()}
        for a, b in itertools.combinations(sorted(m), 2):
            (sa, ha), (sb, hb) = m[a], m[b]
            ok = sa == sb and ha >= .5 and hb >= .5 and (sup is None or sa == sup)
            out[(a, b, y)] = int(ok)
    return pd.Series(out)
say("\n## 3. Shared dominant patron (paper definition: same top supplier, ≥50% of both)\n")
for label, sup in [("shared_dominant", None), ("shared_us", 2), ("shared_soviet", 365)]:
    so, sn = shared(do, sup), shared(dn, sup)
    both = pd.concat([so.rename("old"), sn.rename("new")], axis=1, join="inner")
    f01 = int(((both.old == 0) & (both.new == 1)).sum()); f10 = int(((both.old == 1) & (both.new == 0)).sum())
    say(f"**{label}** — {len(both):,} importing dyad-years; =1 in {int(both.old.sum()):,} (old) vs "
        f"{int(both.new.sum()):,} (new); flips 0→1 {f01:,}, 1→0 {f10:,} "
        f"({(f01+f10)/max(len(both),1):.1%} recoded).\n")
    if label == "shared_dominant":
        eg = both.loc[[k for k in both.index if {k[0], k[1]} <= set(CASES)]]
        eg = eg[eg.old != eg.new]
        if len(eg):
            say("Recoded case-study dyads:\n\n| dyad | year | old | new |\n|---|---|---|---|")
            for (a, b, y), r in eg.iterrows():
                say(f"| {CASES[a]}–{CASES[b]} | {y} | {r.old} | {r.new} |")
            say("")
WP = {290: "POL", 315: "CZE", 265: "GDR", 310: "HUN", 360: "ROM", 355: "BUL", 365: "USSR"}
say("**Warsaw Pact check.** SIPRI records Soviet designs built under licence in Poland and "
    "Czechoslovakia (T-55, T-72, MiG-21) as Soviet transfers. Because these members bought almost "
    "everything from the USSR either way, removing licensed production should shrink the Soviet "
    "*volume* far more than the Soviet *share* — so `shared_soviet` may barely move, while "
    "volume-based measures (16 leverage, 29 import intensity) may move a lot. Both are reported:\n")
say("| member | decade | Soviet share old | new | cross-border TIV old | new | new/old |\n|---|---|---|---|---|---|---|")
def wp(f, cc, a, b):
    s = f[(f.rec_cc == cc) & f.yr.between(a, b)]; t = s.tiv.sum()
    return (s[s.sup_cc == 365].tiv.sum() / t if t else float("nan")), t
for cc, ab in WP.items():
    if cc == 365: continue
    for a, b in [(1960, 1969), (1970, 1979), (1980, 1989)]:
        (so_, to), (sn_, tn) = wp(old, cc, a, b), wp(new, cc, a, b)
        if to == 0 and tn == 0: continue
        say(f"| {ab} | {a}s | {so_:.0%} | {sn_:.0%} | {to:,.0f} | {tn:,.0f} | {tn/to if to else float('nan'):.2f} |")

# 4 -------------------------------------------------------------------------
def overlaps(f):
    out = {}
    for y, d in f.groupby("yr"):
        d = d.assign(w=d.tiv / d.groupby("rec_cc").tiv.transform("sum"))
        sh = defaultdict(dict)
        for r, s, w in zip(d.rec_cc, d.sup_cc, d.w): sh[r][s] = w
        for a, b in itertools.combinations(sorted(sh), 2):
            out[(a, b, y)] = sum(min(sh[a][k], sh[b][k]) for k in set(sh[a]) & set(sh[b]))
    return pd.Series(out)
oo, on = overlaps(old), overlaps(new)
ov = pd.concat([oo.rename("old"), on.rename("new")], axis=1, join="inner")
say("\n## 4. Supplier-portfolio overlap\n")
say(f"{len(ov):,} common dyad-years. Correlation old–new {ov.old.corr(ov.new):.3f}; "
    f"mean |Δ| {(ov.old-ov.new).abs().mean():.3f}; share with |Δ| > 0.10: {((ov.old-ov.new).abs()>0.10).mean():.1%}.")

# 5 -------------------------------------------------------------------------
say("\n## 5. Licensed-production share\n")
try:
    ls = pd.read_csv(args.licensed)
    if ls.licensed_share.notna().any():
        top = (ls.groupby("rec_cc").apply(lambda d: d.tiv_local.sum() / d.tiv_all.sum())
                 .sort_values(ascending=False).head(15))
        say(f"Licensed production is {ls.tiv_local.sum()/ls.tiv_all.sum():.1%} of all TIV.\n")
        say("| recipient | licensed share of its imports |\n|---|---|")
        for cc, v in top.items(): say(f"| {CASES.get(cc, cc)} | {v:.1%} |")
    else:
        say("Not available — the input was the OLD per-deal export, which carries no local-production field.")
except FileNotFoundError:
    say("licensed_share_by_recipient_year.csv not found.")

pathlib.Path(args.out).parent.mkdir(parents=True, exist_ok=True)
open(args.out, "w").write("\n".join(L) + "\n")
print(f"\nwritten to {args.out}")
