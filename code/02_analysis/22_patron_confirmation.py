import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _paths import RAW, REFERENCE, DERIVED, FIG, TAB

#!/usr/bin/env python3
"""Confirmatory test of the shared-patron hypothesis in the Cold War era.
PRIMARY (declared ex ante): shared dominant patron (any supplier >=50% of both
sides' imports) -> lower MID onset, global politically-relevant dyads 1955-1989.
SECONDARY: US vs Soviet patron split; post-1990 comparison; era pooling."""
import pandas as pd, numpy as np, itertools, statsmodels.formula.api as smf
from collections import defaultdict
# ---------- states ----------
sl=pd.read_csv(f"{REFERENCE}/statelist2024.csv")
spans=defaultdict(list)
for r in sl.itertuples(): spans[int(r.ccode)].append((int(r.styear),int(r.endyear)))
def active(c,t): return any(s<=t<=e for s,e in spans.get(c,[]))
YEARS=range(1955,2015)

# ---------- polrel ----------
cont=pd.read_csv(f"{RAW}/DirectContiguity320/contdir.csv")
cont_sp=defaultdict(list)
for r in cont.itertuples():
    i,j=sorted([int(r.statelno),int(r.statehno)])
    cont_sp[(i,j)].append((r.begin//100,r.end//100))
def contig(i,j,t): return any(b<=t<=e for b,e in cont_sp.get((i,j),[]))
def majors(t):
    m={2,200,220,365,710}
    if t>=1991: m|={255,740}
    return m
def polrel(i,j,t):
    m=majors(t); return i in m or j in m or contig(i,j,t)

# ---------- conflict ----------
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

# ---------- arms: importers, dominant patron ----------
tiv=pd.read_csv(f"{DERIVED}/bilateral_tiv_by_year.csv")
imp_by_year=tiv.groupby('yr')['rec_cc'].apply(set).to_dict()
tot=tiv.groupby(['rec_cc','yr'])['tiv'].transform('sum'); tiv['sh']=tiv.tiv/tot
top=tiv.sort_values('sh',ascending=False).groupby(['rec_cc','yr']).first().reset_index()
dom={(int(r.rec_cc),int(r.yr)):(int(r.sup_cc),r.sh) for r in top.itertuples()}
ov=pd.read_csv(f"{DERIVED}/overlap_long_allyears.csv")
ovd={(int(r.ccode1),int(r.ccode2),int(r.year)):r.overlap for r in ov.itertuples()}

# ---------- controls ----------
ally=pd.read_csv(f"{RAW}/version4.1_csv/alliance_v4.1_by_dyad_yearly.csv")
ally_set={(min(int(a),int(b)),max(int(a),int(b)),int(y)) for a,b,y,d in
          zip(ally.ccode1,ally.ccode2,ally.year,ally.defense) if d==1}
amax=max(y for _,_,y in ally_set)
nmc=pd.read_csv(f"{RAW}/NMC_Documentation-6.0/NMC-60-wsupplementary/NMC-60-wsupplementary.csv",
                encoding='latin-1',low_memory=False)
cinc={(int(c),int(y)):v for c,y,v in zip(nmc.ccode,nmc.year,nmc.cinc) if v!=-9}
cmax=max(y for _,y in cinc)
vd=pd.read_csv(f"{RAW}/V-Dem-CY-FullOthers-v16_csv/V-Dem-CY-Full+Others-v16.csv",
               usecols=['COWcode','year','v2x_polyarchy'],low_memory=False).dropna(subset=['COWcode'])
poly={(int(c),int(y)):p for c,y,p in zip(vd.COWcode,vd.year,vd.v2x_polyarchy)}
dist=pd.read_csv(f"{RAW}/dyadic_capital_distance.csv")
distd={(min(int(r.ccode1),int(r.ccode2)),max(int(r.ccode1),int(r.ccode2))):r.capdist_km for r in dist.itertuples()}
tr=pd.read_csv(f"{RAW}/COW_Trade_4.0/Dyadic_COW_4.0.csv",
               usecols=['ccode1','ccode2','year','smoothtotrade'],low_memory=False)
tr=tr[(tr.year>=1954)&(tr.year<=2013)]
trd={(min(int(r.ccode1),int(r.ccode2)),max(int(r.ccode1),int(r.ccode2)),int(r.year)):r.smoothtotrade
     for r in tr.itertuples() if r.smoothtotrade>=0}

def cinc_at(c,t): return cinc.get((c,min(t,cmax)),np.nan)
def ally_at(i,j,t): return int((i,j,min(t,amax)) in ally_set)

# ---------- build ----------
rows=[]
states=sorted(c for c in spans if c<=999)
for t in YEARS:
    act=[c for c in states if active(c,t)]
    impl=imp_by_year.get(t-1,set())
    for i,j in itertools.combinations(act,2):
        if not polrel(i,j,t): continue
        onset=1 if (t in dy.get((i,j),()) and (t-1) not in dy.get((i,j),())) else 0
        di=dom.get((i,t-1)); dj=dom.get((j,t-1))
        both=int(i in impl and j in impl)
        sd=su=ss=np.nan
        if di and dj:
            sd=int(di[0]==dj[0] and di[1]>=.5 and dj[1]>=.5)
            su=int(di[0]==2   and dj[0]==2   and di[1]>=.5 and dj[1]>=.5)
            ss=int(di[0]==365 and dj[0]==365 and di[1]>=.5 and dj[1]>=.5)
        pyv=peace_years(i,j,t)
        rows.append((t,i,j,onset,ovd.get((i,j,t-1),0.0),both,sd,su,ss,
            ally_at(i,j,t),abs(cinc_at(i,t)-cinc_at(j,t)),
            abs(poly.get((i,t),np.nan)-poly.get((j,t),np.nan)),
            np.log(distd.get((i,j),np.nan)+1),
            np.log(trd.get((i,j,t-1),np.nan)+1),
            pyv,pyv**2/100,pyv**3/1000))
P=pd.DataFrame(rows,columns=['year','ccode1','ccode2','onset','overlap_lag1','both_import_lag1',
    'shared_dominant','shared_us','shared_soviet','ally_defense','cinc_diff','regime_dist',
    'ln_capdist','ln_trade_lag1','py','py2','py3'])
P['dyad_id']=P.ccode1.astype(str)+"_"+P.ccode2.astype(str)
P.to_csv(f"{DERIVED}/clean_polrel_panel_1955_2014.csv",index=False)
cw=P[P.year<=1989]; pc=P[P.year>=1990]
print(f"PANEL 1955-2014: {len(P)} rows, {P.onset.sum()} onsets | ColdWar {len(cw)}/{cw.onset.sum()} | Post {len(pc)}/{pc.onset.sum()}")

CTRL=['ally_defense','cinc_diff','regime_dist','ln_capdist','ln_trade_lag1']
PY=['py','py2','py3']
def run(df,var,label,rhs=None):
    rhs=rhs or CTRL+PY
    d=df.dropna(subset=['onset',var]+rhs).copy()
    m=smf.logit(f"onset ~ {var} + "+" + ".join(rhs),data=d).fit(
        disp=0,cov_type='cluster',cov_kwds={'groups':d['dyad_id']},maxiter=300)
    b,pv=m.params[var],m.pvalues[var]
    print(f"{label:58} N={len(d):6d} on={int(d.onset.sum()):4d}  OR={np.exp(b):.3f} p={pv:.3f}")

print("\n=== PRIMARY (declared): shared dominant patron, Cold War 1955-89, both-importers ===")
run(cw[cw.both_import_lag1==1],'shared_dominant',"PRIMARY: shared dominant patron (CW)")

print("\n=== SECONDARY ===")
run(cw[cw.both_import_lag1==1],'shared_us',    "  Cold War: shared US patron")
run(cw[cw.both_import_lag1==1],'shared_soviet',"  Cold War: shared SOVIET patron")
run(cw[cw.both_import_lag1==1],'overlap_lag1', "  Cold War: generic overlap gradient")
run(pc[pc.both_import_lag1==1],'shared_dominant',"  Post-90: shared dominant patron")
run(pc[pc.both_import_lag1==1],'shared_us',    "  Post-90: shared US patron")
d=P[P.both_import_lag1==1].dropna(subset=['onset','shared_dominant']+CTRL+PY).copy()
d['cwera']=(d.year<=1989).astype(int)
m=smf.logit("onset ~ shared_dominant*cwera + "+" + ".join(CTRL+PY),data=d).fit(
    disp=0,cov_type='cluster',cov_kwds={'groups':d['dyad_id']},maxiter=300)
print(f"\nPooled interaction shared_dominant x ColdWar: OR={np.exp(m.params['shared_dominant:cwera']):.3f} p={m.pvalues['shared_dominant:cwera']:.3f}")
print(f"  (main effect post-90: OR={np.exp(m.params['shared_dominant']):.3f} p={m.pvalues['shared_dominant']:.3f})")
