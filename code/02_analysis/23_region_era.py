import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _paths import RAW, REFERENCE, DERIVED, FIG, TAB

#!/usr/bin/env python3
"""Region x era analysis of the shared-patron effect on the CLEAN 1955-2014
panel. Replaces the voided old forest plot."""
import pandas as pd, numpy as np, statsmodels.formula.api as smf
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
P=pd.read_csv(f"{DERIVED}/clean_polrel_panel_1955_2014.csv")
def region(cc):
    if cc<100: return "N.Am/Carib"
    if cc<200: return "S.America"
    if cc<400: return "Europe"
    if cc<600: return "SubSah.Africa"
    if cc<699: return "MENA"
    return "Asia-Pacific"
P['r1']=P.ccode1.map(region); P['r2']=P.ccode2.map(region)
P['regcell']=np.where(P.r1==P.r2,P.r1,"cross-region")
P=P[P.both_import_lag1==1]

CTRL=['ally_defense','cinc_diff','regime_dist','ln_capdist','ln_trade_lag1']
PY=['py','py2','py3']
def fit(df,var):
    for rhs in (CTRL+PY, ['ln_capdist']+PY):   # fall back to lean if separation
        d=df.dropna(subset=['onset',var]+rhs).copy()
        if d.onset.sum()<8 or d[var].std()==0: return None
        try:
            m=smf.logit(f"onset ~ {var} + "+" + ".join(rhs),data=d).fit(
                disp=0,cov_type='cluster',cov_kwds={'groups':d['dyad_id']},maxiter=300)
            b,se=m.params[var],m.bse[var]
            if se>10: continue
            return dict(N=len(d),on=int(d.onset.sum()),OR=np.exp(b),
                        lo=np.exp(b-1.96*se),hi=np.exp(b+1.96*se),p=m.pvalues[var],
                        lean=(rhs!=CTRL+PY))
        except Exception: continue
    return None

eras=[("Cold War 1955-89",P[P.year<=1989]),("Post-1990",P[P.year>=1990])]
regions=["MENA","Asia-Pacific","Europe","SubSah.Africa","S.America","N.Am/Carib","cross-region"]
rows=[]
print(f"{'region':14} {'era':18} {'N':>6} {'on':>4} {'sharedDom OR':>13} {'p':>6}   {'overlap OR':>10} {'p':>6}")
for reg in regions:
    for elab,edf in eras:
        d=edf[edf.regcell==reg]
        a=fit(d,'shared_dominant'); o=fit(d,'overlap_lag1')
        if a is None and o is None: continue
        f=lambda x,k: f"{x[k]:.3f}" if x else "  --"
        print(f"{reg:14} {elab:18} {a['N'] if a else (o['N'] if o else 0):6d} "
              f"{a['on'] if a else (o['on'] if o else 0):4d} "
              f"{f(a,'OR'):>13} {f(a,'p'):>6}   {f(o,'OR'):>10} {f(o,'p'):>6}"
              f"{'  (lean)' if a and a['lean'] else ''}")
        if a: rows.append(dict(region=reg,era=elab,**a))
R=pd.DataFrame(rows); R.to_csv(f"{TAB}/region_era_patron_results.csv",index=False)

# ---- forest plot: shared_dominant by region, two era panels ----
fig,axes=plt.subplots(1,2,figsize=(13,4.8),sharey=True)
for ax,(elab,_) in zip(axes,eras):
    sub=R[R.era==elab].set_index('region').reindex(regions).dropna(subset=['OR']).iloc[::-1]
    y=range(len(sub))
    ax.errorbar(sub.OR,y,xerr=[sub.OR-sub.lo,sub.hi-sub.OR],fmt='o',color='#b2182b',
                ecolor='#999',capsize=4,ms=7)
    ax.axvline(1,ls='--',c='k',lw=1); ax.set_xscale('log')
    ax.set_yticks(list(y)); ax.set_yticklabels(sub.index)
    ax.set_title(elab); ax.set_xlabel("shared dominant patron OR (log, 95% CI)")
    for yi,(_,r) in zip(y,sub.iterrows()):
        ax.annotate(f"n={int(r.on)}",(r.hi,yi),fontsize=8,va='center',
                    xytext=(5,0),textcoords='offset points')
fig.suptitle("Shared dominant arms patron and MID onset — clean panel, by region and era",y=1.02)
plt.tight_layout(); plt.savefig(f"{FIG}/FIG_patron_by_region_era.png",dpi=150,bbox_inches='tight')
print("\nSaved FIG_patron_by_region_era.png, region_era_patron_results.csv")
