import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _paths import RAW, REFERENCE, DERIVED, FIG, TAB

#!/usr/bin/env python3
"""Rebuild the dyad-year panel UNCONDITIONALLY over all politically-relevant
dyad-years (contiguous OR major power), 1990-2014 — no selection on imports or
conflict. Then re-run the extensive (both-import) vs intensive (overlap
gradient) decomposition cleanly, incl. a hand-rolled Firth logit."""
import pandas as pd, numpy as np, itertools, statsmodels.formula.api as smf
from collections import defaultdict
# ---------- state universe ----------
sl=pd.read_csv(f"{REFERENCE}/statelist2024.csv")
active_years={}
for r in sl.itertuples():
    active_years.setdefault(int(r.ccode),[]).append((int(r.styear),int(r.endyear)))
def active(c,t): return any(s<=t<=e for s,e in active_years.get(c,[]))
YEARS=range(1990,2015)

# ---------- contiguity & majors -> polrel dyad list ----------
cont=pd.read_csv(f"{RAW}/DirectContiguity320/contdir.csv")
cont_sp=defaultdict(list)
for r in cont.itertuples():
    i,j=sorted([int(r.statelno),int(r.statehno)])
    cont_sp[(i,j)].append((r.begin//100,r.end//100))
def contig(i,j,t): return any(b<=t<=e for b,e in cont_sp.get((i,j),[]))
MAJ_ALL={2,200,220,365,710}; MAJ_91={255,740}
def is_polrel(i,j,t):
    maj=MAJ_ALL|(MAJ_91 if t>=1991 else set())
    return i in maj or j in maj or contig(i,j,t)

# ---------- conflict (MIDB) ----------
midb=pd.read_csv(f"{RAW}/MID-5-Data-and-Supporting-Materials/MIDB 5.0.csv",encoding='latin-1')
dy=defaultdict(set)
for dn,g in midb.groupby('dispnum'):
    a=g[g.sidea==1]; b=g[g.sidea==0]
    for _,x in a.iterrows():
        for _,y in b.iterrows():
            i,j=sorted([int(x.ccode),int(y.ccode)])
            sy=max(int(x.styear),int(y.styear)); ey=min(int(x.endyear),int(y.endyear))
            for yr in range(max(sy,1946),ey+1): dy[(i,j)].add(yr)

# ---------- overlap & importers ----------
ov=pd.read_csv(f"{DERIVED}/overlap_long_allyears.csv")
ovd={(int(r.ccode1),int(r.ccode2),int(r.year)):r.overlap for r in ov.itertuples()}
tiv=pd.read_csv(f"{DERIVED}/bilateral_tiv_by_year.csv")
imp_by_year=tiv.groupby('yr')['rec_cc'].apply(set).to_dict()

# ---------- covariates ----------
ally=pd.read_csv(f"{RAW}/version4.1_csv/alliance_v4.1_by_dyad_yearly.csv")
ally_set={(min(int(a),int(b)),max(int(a),int(b)),int(y)) for a,b,y,d in
          zip(ally.ccode1,ally.ccode2,ally.year,ally.defense) if d==1}
nmc=pd.read_csv(f"{RAW}/NMC_Documentation-6.0/NMC-60-wsupplementary/NMC-60-wsupplementary.csv",
                encoding='latin-1',low_memory=False)
cinc={(int(c),int(y)):v for c,y,v in zip(nmc.ccode,nmc.year,nmc.cinc) if v!=-9}
vd=pd.read_csv(f"{RAW}/V-Dem-CY-FullOthers-v16_csv/V-Dem-CY-Full+Others-v16.csv",
               usecols=['COWcode','year','v2x_polyarchy'],low_memory=False).dropna(subset=['COWcode'])
poly={(int(c),int(y)):p for c,y,p in zip(vd.COWcode,vd.year,vd.v2x_polyarchy)}
dist=pd.read_csv(f"{RAW}/dyadic_capital_distance.csv")
distd={(min(int(r.ccode1),int(r.ccode2)),max(int(r.ccode1),int(r.ccode2))):r.capdist_km for r in dist.itertuples()}
tr=pd.read_csv(f"{RAW}/COW_Trade_4.0/Dyadic_COW_4.0.csv",
               usecols=['ccode1','ccode2','year','smoothtotrade'],low_memory=False)
tr=tr[(tr.year>=1989)&(tr.year<=2013)]
trd={}
for r in tr.itertuples():
    v=r.smoothtotrade
    if v is not None and v>=0:
        trd[(min(int(r.ccode1),int(r.ccode2)),max(int(r.ccode1),int(r.ccode2)),int(r.year))]=v
ip=pd.read_csv(f"{RAW}/ideal_points_voeten.csv",encoding='latin-1')
ip['year']=ip.session+1945
ipd={(int(c),int(y)):v for c,y,v in zip(ip.ccode,ip.year,ip.IdealPoint)}

def peace_years(i,j,t):
    ys=[y for y in dy.get((i,j),()) if y<t]
    return (t-max(ys)) if ys else (t-1945)

# ---------- build ----------
rows=[]
states=sorted({c for c in sl.ccode.unique() if c<=999})
for t in YEARS:
    act=[c for c in states if active(c,t)]
    impl=imp_by_year.get(t-1,set())
    for i,j in itertools.combinations(act,2):
        if not is_polrel(i,j,t): continue
        mid=1 if t in dy.get((i,j),()) else 0
        onset=1 if (mid and (t-1) not in dy.get((i,j),())) else 0
        both=int(i in impl and j in impl)
        a=ipd.get((i,t)); b=ipd.get((j,t))
        pyv=peace_years(i,j,t)
        rows.append((t,i,j,mid,onset,
            ovd.get((i,j,t-1),0.0),both,
            int((i,j,t) in ally_set),
            abs(cinc.get((i,t),np.nan)-cinc.get((j,t),np.nan)),
            abs(poly.get((i,t),np.nan)-poly.get((j,t),np.nan)),
            np.log(distd.get((i,j),np.nan)+1),
            np.log(trd.get((i,j,t-1),np.nan)+1),
            abs(a-b) if a is not None and b is not None else np.nan,
            pyv,pyv**2/100,pyv**3/1000))
cp=pd.DataFrame(rows,columns=['year','ccode1','ccode2','mid','onset','overlap_lag1',
    'both_import_lag1','ally_defense','cinc_diff','regime_dist','ln_capdist',
    'ln_trade_lag1','unga_ideal_dist','py','py2','py3'])
cp['dyad_id']=cp.ccode1.astype(str)+"_"+cp.ccode2.astype(str)
cp.to_csv(f"{DERIVED}/clean_polrel_panel_1990_2014.csv",index=False)
print(f"CLEAN PANEL: {len(cp)} dyad-years, {cp.onset.sum()} onsets, onset rate {cp.onset.mean():.3%}")
print(f"  both-import share: {cp.both_import_lag1.mean():.1%}; onsets in both-import rows: {cp[cp.both_import_lag1==1].onset.sum()}")

# ---------- clean ladder ----------
CTRL=['ally_defense','cinc_diff','regime_dist','ln_capdist','ln_trade_lag1']
PY=['py','py2','py3']
def run(df,rhs,label,var='overlap_lag1'):
    d=df.dropna(subset=['onset',var]+[v for v in rhs if v not in ('both_import_lag1',)]).copy()
    m=smf.logit(f"onset ~ {var} + "+" + ".join(rhs),data=d).fit(
        disp=0,cov_type='cluster',cov_kwds={'groups':d['dyad_id']},maxiter=200)
    b,pv=m.params[var],m.pvalues[var]
    extra=""
    if 'both_import_lag1' in rhs:
        extra=f"  both_imp OR={np.exp(m.params['both_import_lag1']):.2f} p={m.pvalues['both_import_lag1']:.3f}"
    print(f"{label:56} N={len(d):6d} on={int(d.onset.sum()):4d}  {var} OR={np.exp(b):.3f} p={pv:.3f}{extra}")

print("\n"+"="*104)
print("CLEAN LADDER (unconditional politically-relevant panel)")
print("="*104)
run(cp,CTRL+PY,                       "1. onset ~ overlap + controls + peace-yrs")
run(cp,CTRL+PY+['both_import_lag1'],  "2. + both-import indicator (clean extensive margin)")
run(cp[cp.both_import_lag1==1],CTRL+PY,"3. both-import SUBSAMPLE (clean gradient test)")
run(cp,CTRL+PY,                       "4. extensive margin alone: onset ~ both_import",var='both_import_lag1')

# ---------- hand-rolled Firth logit on spec 2 ----------
def firth(y,X):
    Xc=np.column_stack([np.ones(len(X)),X]); beta=np.zeros(Xc.shape[1])
    for _ in range(60):
        eta=Xc@beta; pr=1/(1+np.exp(-eta)); W=pr*(1-pr)
        XW=Xc*W[:,None]; I=Xc.T@XW
        Ii=np.linalg.inv(I)
        h=np.einsum('ij,jk,ik->i',XW,Ii,Xc)
        U=Xc.T@(y-pr+h*(0.5-pr))
        step=Ii@U; beta+=step
        if np.max(np.abs(step))<1e-8: break
    se=np.sqrt(np.diag(Ii))
    return beta,se
d=cp.dropna(subset=['onset','overlap_lag1']+CTRL+PY).copy()
cols=['overlap_lag1','both_import_lag1']+CTRL+PY
bet,se=firth(d.onset.values.astype(float),d[cols].values)
from scipy import stats
print("\n--- Firth penalized logit (spec 2, hand-rolled) ---")
for k,name in [(1,'overlap_lag1'),(2,'both_import_lag1')]:
    z=bet[k]/se[k]; pv=2*stats.norm.sf(abs(z))
    print(f"   {name:18} OR={np.exp(bet[k]):.3f}  p={pv:.4f}")
