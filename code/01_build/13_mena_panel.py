import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _paths import RAW, REFERENCE, DERIVED, FIG, TAB

#!/usr/bin/env python3
"""Clean re-test of the MENA effect: unconditional COMPLETE-network panel
(the original writing-sample design: all 105 dyads of MENA15, 1990-2014,
 no selection on imports or conflict), with peace-years and Firth."""
import pandas as pd, numpy as np, itertools, statsmodels.formula.api as smf
from collections import defaultdict
from scipy import stats
MENA={692:'BHR',690:'KUW',698:'OMA',694:'QAT',670:'SAU',696:'UAE',630:'IRN',
      645:'IRQ',666:'ISR',663:'JOR',660:'LEB',652:'SYR',679:'YEM',640:'TUR',651:'EGY'}
YEARS=range(1990,2015)

# conflict
midb=pd.read_csv(f"{RAW}/MID-5-Data-and-Supporting-Materials/MIDB 5.0.csv",encoding='latin-1')
dy=defaultdict(set)
for dn,g in midb.groupby('dispnum'):
    a=g[g.sidea==1]; b=g[g.sidea==0]
    for _,x in a.iterrows():
        for _,y in b.iterrows():
            i,j=sorted([int(x.ccode),int(y.ccode)])
            sy=max(int(x.styear),int(y.styear)); ey=min(int(x.endyear),int(y.endyear))
            for yr in range(max(sy,1946),ey+1): dy[(i,j)].add(yr)

# overlap, importers, dominant suppliers
ov=pd.read_csv(f"{DERIVED}/overlap_long_allyears.csv")
ovd={(int(r.ccode1),int(r.ccode2),int(r.year)):r.overlap for r in ov.itertuples()}
tiv=pd.read_csv(f"{DERIVED}/bilateral_tiv_by_year.csv")
imp_by_year=tiv.groupby('yr')['rec_cc'].apply(set).to_dict()
tot=tiv.groupby(['rec_cc','yr'])['tiv'].transform('sum'); tiv['sh']=tiv.tiv/tot
top=tiv.sort_values('sh',ascending=False).groupby(['rec_cc','yr']).first().reset_index()
dom={(int(r.rec_cc),int(r.yr)):(int(r.sup_cc),r.sh) for r in top.itertuples()}

# covariates
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
trd={(min(int(r.ccode1),int(r.ccode2)),max(int(r.ccode1),int(r.ccode2)),int(r.year)):r.smoothtotrade
     for r in tr.itertuples() if r.smoothtotrade>=0}

def peace_years(i,j,t):
    ys=[y for y in dy.get((i,j),()) if y<t]
    return (t-max(ys)) if ys else (t-1945)

rows=[]
cc=sorted(MENA)
for t in YEARS:
    impl=imp_by_year.get(t-1,set())
    for i,j in itertools.combinations(cc,2):
        mid=1 if t in dy.get((i,j),()) else 0
        onset=1 if (mid and (t-1) not in dy.get((i,j),())) else 0
        di=dom.get((i,t-1)); dj=dom.get((j,t-1))
        sd=np.nan; su=np.nan
        if di and dj:
            sd=int(di[0]==dj[0] and di[1]>=.5 and dj[1]>=.5)
            su=int(di[0]==2 and dj[0]==2 and di[1]>=.5 and dj[1]>=.5)
        pyv=peace_years(i,j,t)
        rows.append((t,i,j,MENA[i],MENA[j],onset,
            ovd.get((i,j,t-1),0.0), int(i in impl and j in impl), sd, su,
            int((i,j,t) in ally_set),
            abs(cinc.get((i,t),np.nan)-cinc.get((j,t),np.nan)),
            abs(poly.get((i,t),np.nan)-poly.get((j,t),np.nan)),
            np.log(distd.get((i,j),np.nan)+1),
            np.log(trd.get((i,j,t-1),0)+1),
            pyv,pyv**2/100,pyv**3/1000))
mp=pd.DataFrame(rows,columns=['year','ccode1','ccode2','abb1','abb2','onset',
    'overlap_lag1','both_import_lag1','shared_dominant','shared_us','ally_defense',
    'cinc_diff','regime_dist','ln_capdist','ln_trade_lag1','py','py2','py3'])
mp['dyad_id']=mp.abb1+"_"+mp.abb2
mp.to_csv(f"{DERIVED}/clean_mena_panel_1990_2014.csv",index=False)
print(f"MENA complete-network panel: {len(mp)} dyad-years, {mp.onset.sum()} onsets "
      f"({mp.onset.mean():.2%}), both-import share {mp.both_import_lag1.mean():.0%}")

CTRL=['ally_defense','cinc_diff','regime_dist','ln_capdist','ln_trade_lag1']
PY=['py','py2','py3']
def run(df,rhs,label,var='overlap_lag1'):
    d=df.dropna(subset=['onset',var]+[v for v in rhs if v!='both_import_lag1']).copy()
    try:
        m=smf.logit(f"onset ~ {var} + "+" + ".join(rhs),data=d).fit(
            disp=0,cov_type='cluster',cov_kwds={'groups':d['dyad_id']},maxiter=300)
        b,pv=m.params[var],m.pvalues[var]
        extra=f"  both_imp OR={np.exp(m.params['both_import_lag1']):.2f} p={m.pvalues['both_import_lag1']:.2f}" if 'both_import_lag1' in rhs else ""
        print(f"{label:52} N={len(d):5d} on={int(d.onset.sum()):3d}  {var} OR={np.exp(b):.3f} p={pv:.3f}{extra}")
    except Exception as e:
        print(f"{label:52} FAILED: {e}")

print("\n"+"="*100)
print("CLEAN MENA LADDER (complete network, no selection)")
print("="*100)
run(mp,['ln_capdist']+PY,               "1. lean: overlap + distance + peace-yrs")
run(mp,CTRL+PY,                          "2. full controls + peace-yrs")
run(mp,CTRL+PY+['both_import_lag1'],     "3. + both-import indicator")
run(mp[mp.both_import_lag1==1],CTRL+PY,  "4. both-import SUBSAMPLE (gradient)")
run(mp,CTRL+PY,                          "5. shared dominant supplier",var='shared_dominant')
run(mp,CTRL+PY,                          "6. shared US patron",var='shared_us')

# Firth on spec 2
def firth(y,X):
    Xc=np.column_stack([np.ones(len(X)),X]); beta=np.zeros(Xc.shape[1])
    for _ in range(80):
        eta=Xc@beta; pr=1/(1+np.exp(-eta)); W=pr*(1-pr)
        XW=Xc*W[:,None]; I=Xc.T@XW; Ii=np.linalg.inv(I)
        h=np.einsum('ij,jk,ik->i',XW,Ii,Xc)
        U=Xc.T@(y-pr+h*(0.5-pr)); step=Ii@U; beta+=step
        if np.max(np.abs(step))<1e-8: break
    return beta,np.sqrt(np.diag(Ii))
d=mp.dropna(subset=['onset','overlap_lag1']+CTRL+PY)
cols=['overlap_lag1']+CTRL+PY
bet,se=firth(d.onset.values.astype(float),d[cols].values)
z=bet[1]/se[1]
print(f"\nFirth (spec 2): overlap OR={np.exp(bet[1]):.3f}  p={2*stats.norm.sf(abs(z)):.4f}")
