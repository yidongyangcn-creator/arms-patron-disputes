import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _paths import RAW, REFERENCE, DERIVED, FIG, TAB

#!/usr/bin/env python3
"""Outside-options / substitutability: is the patron effect concentrated among
LOCKED dyads (no meaningful alternative supplier)?
outside_i = number of suppliers besides the patron delivering >5% of i's imports
            in the w5 window.  locked dyad = both sides have outside==0.
Validation: Iraq should flip to 'has outside option' when French deliveries start (mid-1970s)."""
import pandas as pd, numpy as np, statsmodels.formula.api as smf
from collections import defaultdict
flow=pd.read_csv(f"{DERIVED}/bilateral_tiv_by_year.csv").rename(columns={'rec_cc':'i','sup_cc':'k','yr':'t'})
fl=flow.groupby(['i','k','t'])['tiv'].sum()
by_ik=defaultdict(dict)
for (i,k,t),v in fl.items(): by_ik[i].setdefault(k,{})[t]=v
share5={}
for i,ks in by_ik.items():
    for t in range(1954,2015):
        sums={k:sum(v for yy,v in tv.items() if t-4<=yy<=t) for k,tv in ks.items()}
        sums={k:s for k,s in sums.items() if s>0}; tot=sum(sums.values())
        if tot>0: share5[(i,t)]={k:s/tot for k,s in sums.items()}
def outside(i,t):
    s=share5.get((i,t))
    if not s: return None
    top=max(s,key=s.get)
    return sum(1 for k,v in s.items() if k!=top and v>0.05)

# validation: Iraq (645) outside options over time
print("VALIDATION — Iraq's outside options (suppliers >5% besides top):")
for t in [1965,1970,1974,1978,1982,1986,1990]:
    s=share5.get((645,t),{})
    tops=sorted(s.items(),key=lambda x:-x[1])[:3]
    print(f"  {t}: outside={outside(645,t)}  top3={[(k,round(v,2)) for k,v in tops]}")

P=pd.read_csv(f"{DERIVED}/clean_polrel_panel_1955_2014.csv")
P['out_i']=[outside(int(r.ccode1),int(r.year)-1) for r in P.itertuples()]
P['out_j']=[outside(int(r.ccode2),int(r.year)-1) for r in P.itertuples()]
P['locked']=((P.out_i==0)&(P.out_j==0)).astype(float)
P.loc[P.out_i.isna()|P.out_j.isna(),'locked']=np.nan
P['out_min']=np.minimum(P.out_i,P.out_j)

CTRL=['ally_defense','cinc_diff','regime_dist','ln_capdist','ln_trade_lag1']
PY=['py','py2','py3']; U=['unga']
bi=P[P.both_imp_w5==1]
def run(df,f,show,label):
    need=[v.strip() for v in f.replace('*','+').replace(':','+').split('+')]
    d=df.dropna(subset=['onset']+[n for n in need if n in df.columns]).copy()
    m=smf.logit(f"onset ~ {f}",data=d).fit(disp=0,cov_type='cluster',
        cov_kwds={'groups':d['dyad_id']},maxiter=300)
    out=f"{label:56} N={len(d):6d} ev={int(d.onset.sum()):4d}"
    for v in show: out+=f" | {v}: OR={np.exp(m.params[v]):.3f} p={m.pvalues[v]:.3f}"
    print(out); return m
C="+".join(CTRL+PY+U)
cw=bi[bi.year<=1989]
print(f"\nlocked share (both no alternative >5%): CW={cw.locked.mean():.1%}, full={bi.locked.mean():.1%}")

print("\n=== LOCKED-DYAD TEST (the substitutability hypothesis) ===")
for lab,df in [("Cold War",cw),("Full 1955-2014",bi)]:
    m=run(df,f"sd_w5*locked+{C}",['sd_w5','locked','sd_w5:locked'],f"S1 {lab}: sd_w5 x locked")
    b=m.params
    print(f"     -> patron effect when LOCKED:   OR={np.exp(b['sd_w5']+b['sd_w5:locked']):.3f}")
    print(f"     -> patron effect with options:  OR={np.exp(b['sd_w5']):.3f}")
    run(df[df.locked==1],f"sd_w5+{C}",['sd_w5'],f"S2 {lab}: among locked dyads only")
    run(df[df.locked==0],f"sd_w5+{C}",['sd_w5'],f"S3 {lab}: among dyads with options")
    run(df,f"sd_w5+out_min+{C}",['sd_w5','out_min'],f"S4 {lab}: + continuous outside options")
P.to_csv(f"{DERIVED}/clean_polrel_panel_1955_2014.csv",index=False)
print("\npanel updated with out_i, out_j, locked, out_min")
