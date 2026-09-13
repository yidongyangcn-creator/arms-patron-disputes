import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _paths import RAW, REFERENCE, DERIVED, FIG, TAB

#!/usr/bin/env python3
"""UCDP extension: (a) alternative DV consistency check 1955-2014,
(b) NEW post-2014 test (2015-2024) in the most multipolarized market era,
(c) extended market-concentration moderation on pooled 1955-2024."""
import pandas as pd, numpy as np, itertools, statsmodels.formula.api as smf
from collections import defaultdict
# ---------- UCDP interstate dyad conflict years (GW -> COW) ----------
U=pd.read_csv(f"{RAW}/Dyadic_v26_1.csv",low_memory=False)
U=U[U.type_of_conflict==2].copy()
GW2COW={260:255,678:679,816:816,340:345}   # Germany, Yemen, Vietnam(same), Serbia
def g2c(x):
    try: x=int(x)
    except: return None
    return GW2COW.get(x,x)
udy=defaultdict(set)
for r in U.itertuples():
    for a in str(r.gwno_a).split(','):
        for b in str(r.gwno_b).split(','):
            ca,cb=g2c(a),g2c(b)
            if ca is None or cb is None or ca==cb: continue
            i,j=sorted([ca,cb]); udy[(i,j)].add(int(r.year))
def u_onset(i,j,t):
    ys=udy.get((tuple(sorted((i,j)))[0],tuple(sorted((i,j)))[1]),set())
    return 1 if (t in ys and (t-1) not in ys) else 0
print(f"UCDP interstate pairs: {len(udy)}; onsets 2015-2024: "
      f"{sum(1 for (i,j),ys in udy.items() for t in ys if t>=2015 and t-1 not in ys)}")

# ---------- (a) alternative-DV check on existing panel ----------
P=pd.read_csv(f"{DERIVED}/clean_polrel_panel_1955_2014.csv")
P['onset_ucdp']=[u_onset(int(r.ccode1),int(r.ccode2),int(r.year)) for r in P.itertuples()]
CTRL=['ally_defense','cinc_diff','regime_dist','ln_capdist','ln_trade_lag1']
PY=['py','py2','py3']
bi=P[P.both_imp_w5==1]
def run(df,dv,var,rhs,label):
    d=df.dropna(subset=[dv,var]+rhs).copy()
    if d[dv].sum()<8: print(f"{label}: too few events ({int(d[dv].sum())})"); return None
    m=smf.logit(f"{dv} ~ {var} + "+" + ".join(rhs),data=d).fit(disp=0,
        cov_type='cluster',cov_kwds={'groups':d['dyad_id']},maxiter=300)
    print(f"{label:58} N={len(d):6d} ev={int(d[dv].sum()):4d}  OR={np.exp(m.params[var]):.3f} p={m.pvalues[var]:.3f}")
    return m
print("\n(a) UCDP as ALTERNATIVE DV, 1955-2014 (much rarer than MID: >=25 deaths)")
run(bi[bi.year<=1989],'onset_ucdp','sd_w5',CTRL+PY+['unga'],"  CW: sd_w5 -> UCDP onset")
run(bi,'onset_ucdp','sd_w5',CTRL+PY+['unga'],              "  full 1955-2014: sd_w5 -> UCDP onset")

# ---------- (b) build 2015-2024 extension panel ----------
flow=pd.read_csv(f"{DERIVED}/bilateral_tiv_by_year.csv").rename(columns={'rec_cc':'i','sup_cc':'k','yr':'t'})
fl=flow.groupby(['i','k','t'])['tiv'].sum()
by_ik=defaultdict(dict)
for (i,k,t),v in fl.items(): by_ik[i].setdefault(k,{})[t]=v
share5={}
for i,ks in by_ik.items():
    for t in range(2010,2025):
        sums={k:sum(v for yy,v in tv.items() if t-4<=yy<=t) for k,tv in ks.items()}
        sums={k:s for k,s in sums.items() if s>0}; tot=sum(sums.values())
        if tot>0: share5[(i,t)]={k:s/tot for k,s in sums.items()}
def top5(i,t):
    s=share5.get((i,t))
    if not s: return None
    k=max(s,key=s.get); return k,s[k]
# polrel: contiguity spell covering 2016 treated as current; majors incl. Germany/Japan
cont=pd.read_csv(f"{RAW}/DirectContiguity320/contdir.csv")
cont_now={(min(int(r.statelno),int(r.statehno)),max(int(r.statelno),int(r.statehno)))
          for r in cont.itertuples() if r.end//100>=2016}
MAJ={2,200,220,365,710,255,740}
sl=pd.read_csv(f"{REFERENCE}/statelist2024.csv")
active=sorted({int(c) for c,sy,ey in zip(sl.ccode,sl.styear,sl.endyear) if sy<=2024 and ey>=2015 and int(c)<=999})
vd=pd.read_csv(f"{RAW}/V-Dem-CY-FullOthers-v16_csv/V-Dem-CY-Full+Others-v16.csv",
               usecols=['COWcode','year','v2x_polyarchy'],low_memory=False).dropna(subset=['COWcode'])
poly={(int(c),int(y)):p for c,y,p in zip(vd.COWcode,vd.year,vd.v2x_polyarchy)}
dist=pd.read_csv(f"{RAW}/dyadic_capital_distance.csv")
distd={(min(int(r.ccode1),int(r.ccode2)),max(int(r.ccode1),int(r.ccode2))):r.capdist_km for r in dist.itertuples()}
ally=pd.read_csv(f"{RAW}/version4.1_csv/alliance_v4.1_by_dyad_yearly.csv")
ally12={(min(int(a),int(b)),max(int(a),int(b))) for a,b,y,d_ in
        zip(ally.ccode1,ally.ccode2,ally.year,ally.defense) if d_==1 and y==2012}
# combined conflict history for peace-years: MID(<=2014) + UCDP
import pickle
midb=pd.read_csv(f"{RAW}/MID-5-Data-and-Supporting-Materials/MIDB 5.0.csv",encoding='latin-1')
mdy=defaultdict(set)
for dn,g in midb.groupby('dispnum'):
    a=g[g.sidea==1]; b=g[g.sidea==0]
    for _,x in a.iterrows():
        for _,y in b.iterrows():
            i,j=sorted([int(x.ccode),int(y.ccode)])
            for yr in range(max(int(max(x.styear,y.styear)),1946),int(min(x.endyear,y.endyear))+1):
                mdy[(i,j)].add(yr)
def peace(i,j,t):
    hist={y for y in mdy.get((i,j),set()) if y<t} | {y for y in udy.get((i,j),set()) if y<t}
    return (t-max(hist)) if hist else (t-1945)
rows=[]
for t in range(2015,2025):
    for i,j in itertools.combinations(active,2):
        m=MAJ
        if not (i in m or j in m or (i,j) in cont_now): continue
        a=top5(i,t-1); b=top5(j,t-1)
        if a is None or b is None: continue          # both-importer design
        sd=int(a[0]==b[0] and a[1]>=.5 and b[1]>=.5)
        st=int(a[0]==b[0])
        pyv=peace(i,j,t)
        rows.append((t,i,j,u_onset(i,j,t),sd,st,
            int((i,j) in ally12),
            abs(poly.get((i,t),np.nan)-poly.get((j,t),np.nan)),
            np.log(distd.get((i,j),np.nan)+1),pyv,pyv**2/100,pyv**3/1000))
X=pd.DataFrame(rows,columns=['year','ccode1','ccode2','onset','sd_w5','same_top5',
    'ally_ff','regime_dist','ln_capdist','py','py2','py3'])
X['dyad_id']=X.ccode1.astype(str)+"_"+X.ccode2.astype(str)
X.to_csv(f"{DERIVED}/extension_panel_2015_2024.csv",index=False)
print(f"\n(b) 2015-2024 extension panel: {len(X)} dyad-years, {X.onset.sum()} onsets, sd_w5 share={X.sd_w5.mean():.1%}")
run(X,'onset','sd_w5',['ally_ff','regime_dist','ln_capdist']+PY,"  2015-24: sd_w5 -> UCDP onset (lean controls)")
run(X,'onset','same_top5',['ally_ff','regime_dist','ln_capdist']+PY,"  2015-24: same top supplier")

# ---------- (c) extended concentration moderation, pooled 1955-2024, UCDP DV ----------
glob=defaultdict(lambda: defaultdict(float))
for (i,k,t),v in fl.items():
    for tt in range(t,t+5):
        if 1954<=tt<=2024: glob[tt][k]+=v
HHI={t:sum((v/sum(dd.values()))**2 for v in dd.values()) for t,dd in glob.items()}
print(f"\n(c) HHI: 1975={HHI[1975]:.3f} 1990={HHI[1990]:.3f} 2005={HHI[2005]:.3f} 2015={HHI[2015]:.3f} 2023={HHI[2023]:.3f}")
old=bi[['year','ccode1','ccode2','onset_ucdp','sd_w5','regime_dist','ln_capdist','py','py2','py3','dyad_id']].rename(columns={'onset_ucdp':'onset'}).copy()
old['ally_ff']=bi['ally_defense'].values
pool=pd.concat([old,X[['year','ccode1','ccode2','onset','sd_w5','ally_ff','regime_dist','ln_capdist','py','py2','py3','dyad_id']]],ignore_index=True)
pool['hhi']=pool.year.map(lambda y:HHI.get(int(y)-1,np.nan))
pool['hhi_z']=(pool.hhi-pool.hhi.mean())/pool.hhi.std()
d=pool.dropna(subset=['onset','sd_w5','hhi_z','ally_ff','regime_dist','ln_capdist']+PY).copy()
m=smf.logit("onset ~ sd_w5*hhi_z + ally_ff + regime_dist + ln_capdist + py+py2+py3",data=d).fit(
    disp=0,cov_type='cluster',cov_kwds={'groups':d['dyad_id']},maxiter=300)
b0,b1=m.params['sd_w5'],m.params['sd_w5:hhi_z']
print(f"POOLED 1955-2024, UCDP DV: sd_w5 OR={np.exp(b0):.3f} p={m.pvalues['sd_w5']:.3f} | "
      f"x HHI(z) OR={np.exp(b1):.3f} p={m.pvalues['sd_w5:hhi_z']:.3f}  (N={len(d)}, ev={int(d.onset.sum())})")
for z,lab in [(-1.3,'2015-24 level'),(0,'mean'),(1,'CW level')]:
    print(f"   effect at {lab:12}: OR={np.exp(b0+b1*z):.3f}")
