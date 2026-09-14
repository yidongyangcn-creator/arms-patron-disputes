import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _paths import RAW, REFERENCE, DERIVED, FIG, TAB

#!/usr/bin/env python3
"""(1) w5 (5-yr trailing window) as PRIMARY measure: re-run all main tables.
(2) Continuous leverage decomposition: same-top dummy vs continuous patron
    share vs dependence asymmetry — what carries the coefficient?
(3) Market-concentration moderator: does the patron effect scale with global
    supplier concentration (HHI)?  NOTE: financing terms (concessional vs cash)
    need aid data we do not yet have — flagged, not run."""
import pandas as pd, numpy as np, statsmodels.formula.api as smf
from statsmodels.discrete.conditional_models import ConditionalLogit
from collections import defaultdict

# ---------------- window-5 shares, tops, overlap, HHI ----------------
flow=pd.read_csv(f"{DERIVED}/bilateral_tiv_by_year.csv").rename(columns={'rec_cc':'i','sup_cc':'k','yr':'t'})
fl=flow.groupby(['i','k','t'])['tiv'].sum()
by_ik=defaultdict(dict)
for (i,k,t),v in fl.items(): by_ik[i].setdefault(k,{})[t]=v
share5={}
for i,ks in by_ik.items():
    for t in range(1954,2015):
        sums={k:sum(v for yy,v in tv.items() if t-4<=yy<=t) for k,tv in ks.items()}
        sums={k:s for k,s in sums.items() if s>0}
        tot=sum(sums.values())
        if tot>0: share5[(i,t)]={k:s/tot for k,s in sums.items()}
def top5(i,t):
    s=share5.get((i,t));
    if not s: return None
    k=max(s,key=s.get); return k,s[k]
def ov5(i,j,t):
    a=share5.get((i,t)); b=share5.get((j,t))
    if not a or not b: return np.nan
    return sum(min(a[k],b[k]) for k in set(a)&set(b))
# global supplier HHI on 5-yr windows
glob=defaultdict(lambda: defaultdict(float))
for (i,k,t),v in fl.items():
    for tt in range(t,t+5):
        if 1954<=tt<=2014: glob[tt][k]+=v
HHI={t:sum((v/sum(d.values()))**2 for v in d.values()) for t,d in glob.items()}

P=pd.read_csv(f"{DERIVED}/clean_polrel_panel_1955_2014.csv")
def build_vars(df):
    st,pm,da,us,ov=[],[],[],[],[]
    for r in df.itertuples():
        i,j,t=int(r.ccode1),int(r.ccode2),int(r.year)-1
        a=top5(i,t); b=top5(j,t)
        if a is None or b is None:
            st.append(np.nan); pm.append(np.nan); da.append(np.nan); us.append(np.nan)
        else:
            same=int(a[0]==b[0])
            st.append(same)
            pm.append(min(a[1],b[1]) if same else 0.0)
            da.append(abs(a[1]-b[1]) if same else np.nan)
            us.append(int(a[0]==2 and b[0]==2 and a[1]>=.5 and b[1]>=.5))
        ov.append(ov5(i,j,t))
    df['same_top5']=st; df['pshare_min']=pm; df['dep_asym']=da
    df['shared_us_w5']=us; df['overlap_w5']=ov
    df['sd_w5']=[(1 if (s==1 and p>=.5) else (0 if s==s else np.nan)) if s==s else np.nan
                 for s,p in zip(st,pm)]
    df['hhi']=[HHI.get(int(y)-1,np.nan) for y in df.year]
    return df
P=build_vars(P)
zh=(P.hhi-P.hhi.mean())/P.hhi.std(); P['hhi_z']=zh

CTRL=['ally_defense','cinc_diff','regime_dist','ln_capdist','ln_trade_lag1']
PY=['py','py2','py3']; U=['unga']
def run(df,formula_rhs,var,label,show=None):
    need=[v.strip() for v in formula_rhs.replace('*','+').replace(':','+').split('+')]
    d=df.dropna(subset=['onset']+[n for n in need if n in df.columns]).copy()
    m=smf.logit(f"onset ~ {formula_rhs}",data=d).fit(disp=0,
        cov_type='cluster',cov_kwds={'groups':d['dyad_id']},maxiter=300)
    out=f"{label:56} N={len(d):6d} on={int(d.onset.sum()):4d} "
    for v in (show or [var]):
        out+=f" | {v}: OR={np.exp(m.params[v]):.3f} p={m.pvalues[v]:.3f}"
    print(out); return m

C="+".join(CTRL+PY+U)
bi=P[P.both_imp_w5==1]; cw=bi[bi.year<=1989]; pc=bi[bi.year>=1990]

print("="*110)
print("(1) MAIN TABLES, w5 PRIMARY MEASURE (both-importers, full controls + peace-yrs + UNGA)")
print("="*110)
run(cw,f"sd_w5+{C}",'sd_w5',              "T1 Cold War: shared dominant patron")
run(pc,f"sd_w5+{C}",'sd_w5',              "T1 Post-90: shared dominant patron")
run(cw,f"shared_us_w5+{C}",'shared_us_w5',"T1 Cold War: shared US patron")
run(pc,f"shared_us_w5+{C}",'shared_us_w5',"T1 Post-90: shared US patron")
run(cw,f"overlap_w5+{C}",'overlap_w5',    "T1 Cold War: overlap gradient (w5)")
run(pc,f"overlap_w5+{C}",'overlap_w5',    "T1 Post-90: overlap gradient (w5)")
d=bi.copy(); d['cwera']=(d.year<=1989).astype(int)
run(d,f"sd_w5*cwera+{C}",'sd_w5',         "T1 Pooled + era interaction",show=['sd_w5','sd_w5:cwera'])

# dyad-FE
for label,df in [("Cold War",cw),("Full 1955-2014",bi)]:
    dd=df.dropna(subset=['onset','sd_w5']+['ally_defense','cinc_diff','regime_dist','ln_trade_lag1']+PY+U).copy()
    g=dd.groupby('dyad_id').onset.transform('sum'); n=dd.groupby('dyad_id').onset.transform('count')
    dfe=dd[(g>0)&(g<n)]
    cl=ConditionalLogit(dfe['onset'],dfe[['sd_w5','ally_defense','cinc_diff','regime_dist','ln_trade_lag1']+PY+U],
                        groups=dfe['dyad_id']).fit(disp=0)
    print(f"T1 dyad-FE {label:14}                                dyads={dfe.dyad_id.nunique():4d} obs={len(dfe):6d}  | sd_w5: OR={np.exp(cl.params['sd_w5']):.3f} p={cl.pvalues['sd_w5']:.3f}")

# MENA complete network with w5
mp=pd.read_csv(f"{DERIVED}/clean_mena_panel_1990_2014.csv")
mp=build_vars(mp)
mc="+".join(CTRL+PY)
run(mp,f"sd_w5+{mc}",'sd_w5',             "T1 MENA net (post-90): shared dominant (w5)")
run(mp,f"shared_us_w5+{mc}",'shared_us_w5',"T1 MENA net (post-90): shared US (w5)")

print("\n"+"="*110)
print("(2) CONTINUOUS LEVERAGE DECOMPOSITION (both-importers; financing terms NOT feasible w/o aid data)")
print("="*110)
for label,df in [("Cold War",cw),("Full 1955-2014",bi)]:
    run(df,f"same_top5+{C}",'same_top5',              f"L1 {label}: same top supplier (any share)")
    run(df,f"same_top5+pshare_min+{C}",'pshare_min',  f"L2 {label}: + continuous min patron share",show=['same_top5','pshare_min'])
    run(df,f"sd_w5+pshare_min+{C}",'pshare_min',      f"L3 {label}: binary >=50% vs continuous",show=['sd_w5','pshare_min'])
    st=df[df.same_top5==1]
    run(st,f"pshare_min+dep_asym+{C}",'dep_asym',     f"L4 {label}: within same-top: share + asym",show=['pshare_min','dep_asym'])
    run(df,f"sd_w5+overlap_w5+{C}",'sd_w5',           f"L5 {label}: horse-race patron vs overlap",show=['sd_w5','overlap_w5'])

print("\n"+"="*110)
print("(3) MARKET-CONCENTRATION MODERATOR (full 1955-2014, both-importers)")
print("="*110)
print(f"   global 5yr HHI: 1960={HHI.get(1960):.3f} 1975={HHI.get(1975):.3f} 1990={HHI.get(1990):.3f} 2005={HHI.get(2005):.3f} 2014={HHI.get(2014):.3f}")
m=run(bi,f"sd_w5*hhi_z+{C}",'sd_w5',      "M1 sd_w5 x HHI(z)",show=['sd_w5','sd_w5:hhi_z'])
b0=m.params['sd_w5']; b1=m.params['sd_w5:hhi_z']
for z,lab in [(-1,'low conc (-1sd)'),(0,'mean'),(1,'high conc (+1sd)')]:
    print(f"      effect at {lab:16}: OR={np.exp(b0+b1*z):.3f}")
run(bi,f"pshare_min*hhi_z+same_top5+{C}",'pshare_min',"M2 continuous share x HHI(z)",show=['pshare_min','pshare_min:hhi_z'])
P.to_csv(f"{DERIVED}/clean_polrel_panel_1955_2014.csv",index=False)
print("\npanel updated: same_top5, pshare_min, dep_asym, shared_us_w5, overlap_w5, hhi")
