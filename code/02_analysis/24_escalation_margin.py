import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _paths import RAW, REFERENCE, DERIVED, FIG, TAB

#!/usr/bin/env python3
"""Formalize the two-margin design:
 Margin 1 (onset): does shared patronage prevent NEW disputes?  [headline re-run]
 Margin 2 (escalation): conditional on a dispute, does it cap WAR / fatalities?
Dispute-level models with controls + Firth; combined main table saved."""
import pandas as pd, numpy as np, statsmodels.formula.api as smf
from collections import defaultdict
from scipy import stats
P=pd.read_csv(f"{DERIVED}/clean_polrel_panel_1955_2014.csv")
CTRL=['ally_defense','cinc_diff','regime_dist','ln_capdist','ln_trade_lag1']
PY=['py','py2','py3']; U=['unga']

# ---------- Margin 2: dispute-level dataset ----------
midb=pd.read_csv(f"{RAW}/MID-5-Data-and-Supporting-Materials/MIDB 5.0.csv",encoding='latin-1')
rows=[]
for dn,g in midb.groupby('dispnum'):
    a=g[g.sidea==1]; b=g[g.sidea==0]
    for _,x in a.iterrows():
        for _,y in b.iterrows():
            i,j=sorted([int(x.ccode),int(y.ccode)])
            sy=max(int(x.styear),int(y.styear))
            if sy<1955 or sy>2014: continue
            h=max(int(x.hostlev),int(y.hostlev))
            f1,f2=int(x.fatality),int(y.fatality)
            fat=np.nan if (f1<0 and f2<0) else int(max(f1,0)>0 or max(f2,0)>0)
            rows.append((dn,i,j,sy,int(h==5),fat))
E=pd.DataFrame(rows,columns=['dispnum','ccode1','ccode2','styear','war','fatal']).drop_duplicates()
E['dyad_id']=E.ccode1.astype(str)+"_"+E.ccode2.astype(str)
E['year']=E.styear
# merge measures & covariates from panel (same dyad-year)
mvars=['sd_w5','shared_us_w5','same_top5','both_imp_w5']+CTRL+PY+U
E=E.merge(P[['ccode1','ccode2','year']+mvars],on=['ccode1','ccode2','year'],how='left')
E['cwera']=(E.year<=1989).astype(int)
print(f"dispute-level dataset: {len(E)} dyadic disputes 1955-2014; wars={int(E.war.sum())}, "
      f"fatal={int(E.fatal.sum() if E.fatal.notna().any() else 0)}; covariate coverage={E.sd_w5.notna().mean():.0%}")

def esc(dv,var,rhs,label):
    d=E.dropna(subset=[dv,var]+rhs).copy()
    if d[var].std()==0: print(f"{label}: no variation"); return
    m=smf.logit(f"{dv} ~ {var} + "+" + ".join(rhs) if rhs else f"{dv} ~ {var}",data=d).fit(
        disp=0,cov_type='cluster',cov_kwds={'groups':d['dyad_id']},maxiter=300)
    print(f"{label:58} N={len(d):5d} ev={int(d[dv].sum()):4d}  OR={np.exp(m.params[var]):.3f} p={m.pvalues[var]:.3f}")
    return m

print("\n=== MARGIN 2: ESCALATION | dispute occurred ===")
esc('war','sd_w5',[],                          "war ~ sd_w5 (bivariate)")
esc('war','sd_w5',['cwera'],                   "war ~ sd_w5 + era")
esc('war','sd_w5',CTRL+['cwera'],              "war ~ sd_w5 + full controls + era")
esc('war','shared_us_w5',CTRL+['cwera'],       "war ~ shared US + controls + era")
esc('war','same_top5',CTRL+['cwera'],          "war ~ same top supplier + controls + era")
esc('fatal','sd_w5',[],                        "fatality ~ sd_w5 (bivariate)")
esc('fatal','sd_w5',CTRL+['cwera'],            "fatality ~ sd_w5 + controls + era")

# Firth for war with controls
def firth(y,X):
    Xc=np.column_stack([np.ones(len(X)),X]); beta=np.zeros(Xc.shape[1])
    for _ in range(80):
        eta=Xc@beta; pr=1/(1+np.exp(-eta)); W=pr*(1-pr)
        XW=Xc*W[:,None]; I=Xc.T@XW; Ii=np.linalg.inv(I)
        h=np.einsum('ij,jk,ik->i',XW,Ii,Xc)
        U_=Xc.T@(y-pr+h*(0.5-pr)); step=Ii@U_; beta+=step
        if np.max(np.abs(step))<1e-8: break
    return beta,np.sqrt(np.diag(Ii))
d=E.dropna(subset=['war','sd_w5']+CTRL+['cwera'])
cols=['sd_w5']+CTRL+['cwera']
bet,se=firth(d.war.values.astype(float),d[cols].values)
z=bet[1]/se[1]
print(f"Firth: war ~ sd_w5 + controls + era:                       OR={np.exp(bet[1]):.3f} p={2*stats.norm.sf(abs(z)):.4f}")

# ---------- Margin 1 headline (for the combined table) ----------
print("\n=== MARGIN 1: ONSET (headline, w5, both-importers, +UNGA) ===")
bi=P[P.both_imp_w5==1]; cw=bi[bi.year<=1989]; pc=bi[bi.year>=1990]
res=[]
def on(df,var,label):
    d=df.dropna(subset=['onset',var]+CTRL+PY+U).copy()
    m=smf.logit(f"onset ~ {var} + "+" + ".join(CTRL+PY+U),data=d).fit(
        disp=0,cov_type='cluster',cov_kwds={'groups':d['dyad_id']},maxiter=300)
    print(f"{label:58} N={len(d):5d} ev={int(d.onset.sum()):4d}  OR={np.exp(m.params[var]):.3f} p={m.pvalues[var]:.3f}")
    res.append(dict(margin='onset',sample=label,measure=var,
                    OR=round(np.exp(m.params[var]),3),p=round(m.pvalues[var],3),
                    N=len(d),events=int(d.onset.sum())))
on(cw,'sd_w5',"onset CW: shared dominant patron")
on(pc,'sd_w5',"onset post-90: shared dominant patron")
on(cw,'same_top5',"onset CW: same top supplier")
on(pc,'shared_us_w5',"onset post-90: shared US patron")
# append escalation rows to combined table
for dv,var,rhs,lab in [('war','sd_w5',CTRL+['cwera'],"escalation: war | dispute"),
                        ('fatal','sd_w5',CTRL+['cwera'],"escalation: fatality | dispute")]:
    d=E.dropna(subset=[dv,var]+rhs).copy()
    m=smf.logit(f"{dv} ~ {var} + "+" + ".join(rhs),data=d).fit(disp=0,
        cov_type='cluster',cov_kwds={'groups':d['dyad_id']},maxiter=300)
    res.append(dict(margin='escalation',sample=lab,measure=var,
                    OR=round(np.exp(m.params[var]),3),p=round(m.pvalues[var],3),
                    N=len(d),events=int(d[dv].sum())))
pd.DataFrame(res).to_csv(f"{TAB}/two_margin_main_table.csv",index=False)
E.to_csv(f"{DERIVED}/dispute_level_1955_2014.csv",index=False)
print("\nsaved two_margin_main_table.csv, dispute_level_1955_2014.csv")
