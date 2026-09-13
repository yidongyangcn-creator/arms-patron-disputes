import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _paths import RAW, REFERENCE, DERIVED, FIG, TAB

#!/usr/bin/env python3
"""Identification suite for the shared-patron effect on the clean 1955-2014 panel.
(1) Dyad-FE conditional logit (within-dyad: gaining/losing a shared patron).
(2) Bartik shift-share IV: predicted shared-dominance from predetermined base
    shares x leave-one-out global supplier shifts.
Era bases: 1950-54 base for 1957-89; 1980-89 base for 1990-2014."""
import pandas as pd, numpy as np, statsmodels.formula.api as smf
from statsmodels.discrete.conditional_models import ConditionalLogit
from linearmodels.iv import IV2SLS
from collections import defaultdict
P=pd.read_csv(f"{DERIVED}/clean_polrel_panel_1955_2014.csv")
CTRL_TV=['ally_defense','cinc_diff','regime_dist','ln_trade_lag1']  # time-varying
PY=['py','py2','py3']

# =================== (1) DYAD FIXED EFFECTS ===================
print("="*80)
print("(1) DYAD-FE conditional logit — within-dyad shared-patron changes")
print("="*80)
for label,df in [("Cold War 1955-89",P[(P.year<=1989)&(P.both_import_lag1==1)]),
                 ("Full 1955-2014",P[P.both_import_lag1==1])]:
    d=df.dropna(subset=['onset','shared_dominant']+CTRL_TV+PY).copy()
    g=d.groupby('dyad_id').onset.transform('sum')
    n=d.groupby('dyad_id').onset.transform('count')
    dfe=d[(g>0)&(g<n)]
    try:
        cl=ConditionalLogit(dfe['onset'],dfe[['shared_dominant']+CTRL_TV+PY],
                            groups=dfe['dyad_id']).fit(disp=0)
        b,pv=cl.params['shared_dominant'],cl.pvalues['shared_dominant']
        print(f"[{label:18}] dyads={dfe.dyad_id.nunique():4d} obs={len(dfe):6d}  "
              f"shared_dominant OR={np.exp(b):.3f} p={pv:.3f}")
    except Exception as e:
        print(f"[{label}] failed: {e}")

# =================== (2) BARTIK IV ===================
print("\n"+"="*80)
print("(2) SHIFT-SHARE IV for shared dominant patron")
print("="*80)
flow=pd.read_csv(f"{DERIVED}/bilateral_tiv_by_year.csv").rename(columns={'rec_cc':'i','sup_cc':'k','yr':'t'})
G=flow.groupby(['k','t'])['tiv'].sum().to_dict()          # global supplier exports
own={(r.i,r.k,r.t):r.tiv for r in flow.itertuples()}

def base_shares(lo,hi):
    b=flow[(flow.t>=lo)&(flow.t<=hi)].groupby(['i','k'])['tiv'].sum().reset_index()
    tot=b.groupby('i')['tiv'].transform('sum'); b['w0']=b.tiv/tot
    out=defaultdict(dict)
    for r in b.itertuples(): out[r.i][r.k]=r.w0
    return out
BASES={'cw':base_shares(1950,1954),'post':base_shares(1980,1989)}
def pred_top(i,t):
    w0=BASES['cw'] if t<=1989 else BASES['post']
    if i not in w0: return None
    num={k:w*max(G.get((k,t),0.0)-own.get((i,k,t),0.0),0.0) for k,w in w0[i].items()}
    s=sum(num.values())
    if s<=0: return None
    k_top=max(num,key=num.get)
    return k_top,num[k_top]/s
cache={}
def z_shared(i,j,t):
    a=cache.get((i,t)) or pred_top(i,t); cache[(i,t)]=a
    b=cache.get((j,t)) or pred_top(j,t); cache[(j,t)]=b
    if a is None or b is None: return np.nan
    return int(a[0]==b[0] and a[1]>=.5 and b[1]>=.5)
sub=P[(P.both_import_lag1==1)&((P.year>=1957))].copy()
sub['z']=[z_shared(int(r.ccode1),int(r.ccode2),int(r.year)-1) for r in sub.itertuples()]
CTRL=['ally_defense','cinc_diff','regime_dist','ln_capdist','ln_trade_lag1']
for label,df in [("Cold War 1957-89",sub[sub.year<=1989]),("Full 1957-2014",sub)]:
    d=df.dropna(subset=['onset','shared_dominant','z']+CTRL+PY).copy(); d['const']=1
    if d.z.std()==0: print(f"[{label}] no instrument variation"); continue
    print(f"\n[{label}] N={len(d)}, onsets={int(d.onset.sum())}, instrument coverage share={df.z.notna().mean():.0%}")
    fs=smf.ols("shared_dominant ~ z + "+" + ".join(CTRL+PY),data=d).fit(
        cov_type='cluster',cov_kwds={'groups':d['dyad_id']})
    t=fs.params['z']/fs.bse['z']
    print(f"  First stage: coef={fs.params['z']:+.3f}  t={t:.1f}  F≈{t**2:.0f}")
    rf=smf.logit("onset ~ z + "+" + ".join(CTRL+PY),data=d).fit(disp=0,
        cov_type='cluster',cov_kwds={'groups':d['dyad_id']},maxiter=300)
    print(f"  Reduced form (logit): OR={np.exp(rf.params['z']):.3f}  p={rf.pvalues['z']:.3f}")
    iv=IV2SLS(d['onset'],d[['const']+CTRL+PY],d[['shared_dominant']],d[['z']]).fit(
        cov_type='clustered',clusters=d['dyad_id'])
    ols=IV2SLS(d['onset'],d[['const','shared_dominant']+CTRL+PY],None,None).fit(
        cov_type='clustered',clusters=d['dyad_id'])
    print(f"  2SLS-LPM shared_dominant: coef={iv.params['shared_dominant']:+.4f} p={iv.pvalues['shared_dominant']:.3f}"
          f"   [OLS-LPM {ols.params['shared_dominant']:+.4f} p={ols.pvalues['shared_dominant']:.3f}]")
