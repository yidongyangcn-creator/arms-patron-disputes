import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _paths import RAW, REFERENCE, DERIVED, FIG, TAB

#!/usr/bin/env python3
"""Import-intensity condition for the patron measure.
A dominant supplier only confers leverage if imports matter for the recipient's
armament. intensity_i,t = SIPRI TIV imported over the 5-yr window / military
expenditure over the same window (NMC milex). States below the p-th percentile of
intensity among importers (large domestic producers such as Japan, or China after
1960) are treated as not import-dependent, and shared dominance is switched off
for them. Adds imp_int_i/j, dep_i/j, sd_w5_int to the panel."""
import pandas as pd, numpy as np, statsmodels.formula.api as smf
from collections import defaultdict
P=pd.read_csv(f"{DERIVED}/clean_polrel_panel_1955_2014.csv")
flow=pd.read_csv(f"{DERIVED}/bilateral_tiv_by_year.csv")
nmc=pd.read_csv(f"{RAW}/NMC_Documentation-6.0/NMC-60-wsupplementary/NMC-60-wsupplementary.csv",
                encoding='latin-1',low_memory=False)
imp=flow.groupby(['rec_cc','yr'])['tiv'].sum().to_dict()
mil={(int(c),int(y)):v for c,y,v in zip(nmc.ccode,nmc.year,nmc.milex) if v not in (-9,) and v==v and v>0}
mmax=max(y for _,y in mil)
def intensity(c,t):     # window ending t: TIV (million) / milex (thousand USD -> million)
    tiv=sum(imp.get((c,y),0.0) for y in range(t-4,t+1))
    mx=sum(mil.get((c,min(y,mmax)),np.nan) for y in range(t-4,t+1))
    if mx!=mx or mx<=0: return np.nan
    return tiv/(mx/1000.0)
P['imp_int_i']=[intensity(int(r.ccode1),int(r.year)-1) for r in P.itertuples()]
P['imp_int_j']=[intensity(int(r.ccode2),int(r.year)-1) for r in P.itertuples()]
bi=P[P.both_imp_w5==1]
vals=pd.concat([bi.imp_int_i,bi.imp_int_j]).dropna()
for q in [0.10,0.25]:
    thr=vals.quantile(q)
    P[f'dep{int(q*100)}']=((P.imp_int_i>=thr)&(P.imp_int_j>=thr)).astype(float)
    P.loc[P.imp_int_i.isna()|P.imp_int_j.isna(),f'dep{int(q*100)}']=np.nan
    P[f'sd_w5_int{int(q*100)}']=P.sd_w5*P[f'dep{int(q*100)}']
print(f"intensity thresholds: p10={vals.quantile(.10):.4f}, p25={vals.quantile(.25):.4f}, median={vals.median():.4f}")
for c,nm in [(740,'Japan'),(732,'ROK'),(713,'Taiwan'),(710,'China'),(651,'Egypt'),(645,'Iraq'),(666,'Israel')]:
    print(f"  {nm:7} intensity 1975={intensity(c,1975) if intensity(c,1975)==intensity(c,1975) else float('nan'):.4f}  2005={intensity(c,2005) if intensity(c,2005)==intensity(c,2005) else float('nan'):.4f}")

CTRL=['ally_defense','cinc_diff','regime_dist','ln_capdist','ln_trade_lag1']
PY=['py','py2','py3']; U=['unga']; CS="+".join(CTRL+PY+U)
def fit(df,dv,var,label):
    d=df.dropna(subset=[dv,var]+CTRL+PY+U).copy()
    if d[var].std()==0 or d[dv].sum()<8: print(f"{label}: n/a"); return
    m=smf.logit(f"{dv} ~ {var}+{CS}",data=d).fit(disp=0,cov_type='cluster',cov_kwds={'groups':d['dyad_id']},maxiter=300)
    print(f"{label:58} N={len(d):6d} ev={int(d[dv].sum()):4d}  OR={np.exp(m.params[var]):.3f} p={m.pvalues[var]:.3f}")
bi=P[P.both_imp_w5==1]; cw=bi[bi.year<=1989]; pc=bi[bi.year>=1990]
ap=bi[(bi.ccode1>=700)&(bi.ccode2>=700)]
for q in [10,25]:
    v=f'sd_w5_int{q}'
    print(f"\n=== shared dominant patron, import-dependent both sides (p{q} cut) ===")
    fit(cw,'onset',v,f"  CW primary")
    fit(cw,'onset_orig',v,f"  CW primary, originator-only")
    fit(pc,'onset',v,f"  post-1990")
    fit(bi,'onset',v,f"  full 1955-2014")
    fit(ap,'onset',v,f"  Asia-Pacific, full period")
print("\n=== comparison: unconditioned sd_w5 ===")
fit(cw,'onset','sd_w5',"  CW primary"); fit(ap,'onset','sd_w5',"  Asia-Pacific, full period")
P.to_csv(f"{DERIVED}/clean_polrel_panel_1955_2014.csv",index=False)
print("panel updated: imp_int_i/j, dep10/25, sd_w5_int10/25")
