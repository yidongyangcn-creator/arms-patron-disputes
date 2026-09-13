import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _paths import RAW, REFERENCE, DERIVED, FIG, TAB

#!/usr/bin/env python3
"""Baseline hardening: (1) zero-diagnostic (gradient vs import status),
(2) Carter-Signorino peace-years, (3) standard politically-relevant sample,
(4) Firth penalized logit. Prints a spec ladder for the overlap coefficient."""
import pandas as pd, numpy as np, statsmodels.formula.api as smf
from collections import defaultdict
p=pd.read_csv(f"{DERIVED}/dyad_year_panel_1990_2014.csv")
p['dyad_id']=p.ccode1.astype(str)+"_"+p.ccode2.astype(str)

# ---------- (2) PEACE YEARS from MIDB full history (1946+) ----------
midb=pd.read_csv(f"{RAW}/MID-5-Data-and-Supporting-Materials/MIDB 5.0.csv",encoding='latin-1')
dy=defaultdict(set)
for dn,g in midb.groupby('dispnum'):
    a=g[g.sidea==1]; b=g[g.sidea==0]
    for _,x in a.iterrows():
        for _,y in b.iterrows():
            i,j=sorted([int(x.ccode),int(y.ccode)])
            sy=max(int(x.styear),int(y.styear)); ey=min(int(x.endyear),int(y.endyear))
            for yr in range(max(sy,1946),ey+1): dy[(i,j)].add(yr)
def peace_years(i,j,t):
    ys=[y for y in dy.get((i,j),()) if y<t]
    return (t-max(ys)) if ys else (t-1945)
p['py']=[peace_years(int(r.ccode1),int(r.ccode2),int(r.year)) for r in p.itertuples()]
p['py2']=p.py**2/100; p['py3']=p.py**3/1000

# ---------- (3) POLITICALLY RELEVANT: contiguity OR major power ----------
cont=pd.read_csv(f"{RAW}/DirectContiguity320/contdir.csv")
cont_pairs=defaultdict(list)
for r in cont.itertuples():
    i,j=sorted([int(r.statelno),int(r.statehno)])
    cont_pairs[(i,j)].append((r.begin//100, r.end//100))
def contig(i,j,t):
    return any(b<=t<=e for b,e in cont_pairs.get((tuple(sorted((i,j)))[0],tuple(sorted((i,j)))[1]),[]))
MAJORS_ALL={2,200,220,365,710}; MAJORS_91={255,740}
def polrel(r):
    i,j,t=int(r.ccode1),int(r.ccode2),int(r.year)
    maj=MAJORS_ALL | (MAJORS_91 if t>=1991 else set())
    return int(i in maj or j in maj or contig(i,j,t))
p['polrel']=[polrel(r) for r in p.itertuples()]

CTRL=['ally_defense','cinc_diff','regime_dist','ln_capdist','ln_trade_lag1']
PY=['py','py2','py3']
def run(df,rhs,label):
    d=df.dropna(subset=['onset','overlap_lag1']+[v for v in rhs if v!='both_import_lag1']).copy()
    m=smf.logit("onset ~ overlap_lag1 + "+" + ".join(rhs),data=d).fit(
        disp=0,cov_type='cluster',cov_kwds={'groups':d['dyad_id']},maxiter=200)
    b,pv=m.params['overlap_lag1'],m.pvalues['overlap_lag1']
    bi=f"  both_imp OR={np.exp(m.params['both_import_lag1']):.2f} p={m.pvalues['both_import_lag1']:.3f}" if 'both_import_lag1' in rhs else ""
    print(f"{label:52} N={len(d):6d} on={int(d.onset.sum()):4d}  overlap OR={np.exp(b):.3f} p={pv:.3f}{bi}")
    return d

print("="*100)
print("SPEC LADDER — overlap_lag1 coefficient under each fix")
print("="*100)
run(p, CTRL,                                  "A. reference (current sample, hard-test controls)")
run(p, CTRL+['both_import_lag1'],             "B. + both-import indicator (zero diagnostic)")
sub=p[p.both_import_lag1==1]
run(sub, CTRL,                                "C. both-import SUBSAMPLE (gradient only)")
run(p, CTRL+PY,                               "D. + peace-years cubic (Carter-Signorino)")
pr=p[p.polrel==1]
print(f"\n   politically-relevant sample: {len(pr)} rows ({pr.onset.sum():.0f} onsets) of {len(p)}")
run(pr, CTRL+PY+['both_import_lag1'],         "E. POLREL sample + peace-yrs + import indicator")
final=run(pr[pr.both_import_lag1==1], CTRL+PY,"F. FINAL: polrel + both-import + peace-yrs")

# ---------- (4) FIRTH penalized logit on spec F ----------
print("\n--- Firth penalized logit (spec F) ---")
try:
    from firthlogist import FirthLogisticRegression
    X=final[['overlap_lag1']+CTRL+PY].values; y=final['onset'].values
    fl=FirthLogisticRegression(max_iter=200).fit(X,y)
    print(f"   overlap OR={np.exp(fl.coef_[0]):.3f}  beta={fl.coef_[0]:+.3f}  p={fl.pvals_[0]:.4f}")
except Exception as e:
    print("   firthlogist failed:",e)

p.to_csv(f"{DERIVED}/dyad_year_panel_1990_2014.csv",index=False)
print("\npanel updated with py, py2, py3, polrel")
