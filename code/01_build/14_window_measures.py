import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _paths import RAW, REFERENCE, DERIVED, FIG, TAB

#!/usr/bin/env python3
"""Reproduce (or refute) the numbers in Yidong's case-design memo, in OUR pipeline:
 (a) 5-year trailing-window dominant-patron measure + single-year flip rate
 (b) Cold-War estimate with UNGA control; no-defense-pact subsample;
     drop-top-ten-exporter-dyads robustness
 (c) escalation-conditional-on-dispute test (war / any fatality)
 (d) residual ranking of shared-patron dyads (Lieberman case selection)
"""
import pandas as pd, numpy as np, itertools, statsmodels.formula.api as smf
from collections import defaultdict
P=pd.read_csv(f"{DERIVED}/clean_polrel_panel_1955_2014.csv")

# ---------- (a) 5-year trailing window shares ----------
flow=pd.read_csv(f"{DERIVED}/bilateral_tiv_by_year.csv").rename(columns={'rec_cc':'i','sup_cc':'k','yr':'t'})
# cumulative by recipient-supplier for fast window sums
dom5={}   # (i, t) -> (top supplier, share) using window [t-4, t]
imp5=defaultdict(set)  # t -> set of recipients with any imports in window
recs=flow.i.unique()
fl=flow.groupby(['i','k','t'])['tiv'].sum()
by_ik=defaultdict(dict)
for (i,k,t),v in fl.items(): by_ik[i].setdefault(k,{})[t]=v
for i,ks in by_ik.items():
    yrs=sorted({t for kk in ks.values() for t in kk})
    for t in range(1954,2015):
        tot=0; best=None; bestv=0
        sums={}
        for k,tv in ks.items():
            s=sum(v for yy,v in tv.items() if t-4<=yy<=t)
            if s>0: sums[k]=s; tot+=s
        if tot<=0: continue
        imp5[t].add(i)
        k_top=max(sums,key=sums.get)
        dom5[(i,t)]=(k_top,sums[k_top]/tot)

def sd5(i,j,t):   # shared dominant, window ending t
    a=dom5.get((i,t)); b=dom5.get((j,t))
    if a is None or b is None: return np.nan
    return int(a[0]==b[0] and a[1]>=.5 and b[1]>=.5)
P['sd_w5']=[sd5(int(r.ccode1),int(r.ccode2),int(r.year)-1) for r in P.itertuples()]
P['both_imp_w5']=[int(int(r.ccode1) in imp5.get(int(r.year)-1,set()) and int(r.ccode2) in imp5.get(int(r.year)-1,set())) for r in P.itertuples()]

# single-year flip rate among consecutive dyad-years (both measures defined)
P=P.sort_values(['ccode1','ccode2','year'])
g=P.groupby(['ccode1','ccode2'])
sy=P['shared_dominant']; sy_prev=g['shared_dominant'].shift()
w5=P['sd_w5']; w5_prev=g['sd_w5'].shift()
m1=sy.notna()&sy_prev.notna(); m5=w5.notna()&w5_prev.notna()
print(f"(a) FLIP RATES consecutive dyad-years: single-year {(sy[m1]!=sy_prev[m1]).mean():.1%}  |  5-yr window {(w5[m5]!=w5_prev[m5]).mean():.1%}")
print(f"    [memo claim: single-year 11.6%]")

# ---------- UNGA control ----------
ip=pd.read_csv(f"{RAW}/ideal_points_voeten.csv",encoding='latin-1')
ip['year']=ip.session+1945
ipd={(int(c),int(y)):v for c,y,v in zip(ip.ccode,ip.year,ip.IdealPoint)}
P['unga']=[abs(ipd.get((int(r.ccode1),int(r.year)),np.nan)-ipd.get((int(r.ccode2),int(r.year)),np.nan)) for r in P.itertuples()]

CTRL=['ally_defense','cinc_diff','regime_dist','ln_capdist','ln_trade_lag1']
PY=['py','py2','py3']
def run(df,var,rhs,label):
    d=df.dropna(subset=['onset',var]+rhs).copy()
    m=smf.logit(f"onset ~ {var} + "+" + ".join(rhs),data=d).fit(
        disp=0,cov_type='cluster',cov_kwds={'groups':d['dyad_id']},maxiter=300)
    print(f"{label:58} N={len(d):6d} on={int(d.onset.sum()):4d}  OR={np.exp(m.params[var]):.3f} p={m.pvalues[var]:.3f}")

print("\n(b) COLD WAR 1955-89, both-importers (5-yr window measure)")
cw=P[(P.year<=1989)&(P.both_imp_w5==1)]
run(cw,'sd_w5',CTRL+PY,          "  w5 shared dominant patron (no UNGA)")
run(cw,'sd_w5',CTRL+PY+['unga'], "  w5 + UNGA ideal-dist   [memo: OR=0.66 p=0.005]")
run(cw[cw.ally_defense==0],'sd_w5',[c for c in CTRL if c!='ally_defense']+PY+['unga'],
                                  "  no-defense-pact subsample [memo: OR=0.65 p=0.032]")
# top-ten exporters by total TIV
top10=list(flow.groupby('k')['tiv'].sum().sort_values(ascending=False).head(10).index)
print(f"  top-10 exporters (ccode): {top10}")
noX=cw[~cw.ccode1.isin(top10)&~cw.ccode2.isin(top10)]
run(noX,'sd_w5',CTRL+PY+['unga'],"  drop dyads containing top-10 exporter")

# ---------- (c) escalation conditional on dispute ----------
midb=pd.read_csv(f"{RAW}/MID-5-Data-and-Supporting-Materials/MIDB 5.0.csv",encoding='latin-1')
rows=[]
for dn,gd in midb.groupby('dispnum'):
    a=gd[gd.sidea==1]; b=gd[gd.sidea==0]
    for _,x in a.iterrows():
        for _,y in b.iterrows():
            i,j=sorted([int(x.ccode),int(y.ccode)])
            sy_=max(int(x.styear),int(y.styear))
            if sy_<1955 or sy_>2014: continue
            h=max(int(x.hostlev),int(y.hostlev))
            f1,f2=int(x.fatality),int(y.fatality)
            fat=np.nan if (f1<0 and f2<0) else int(max(f1,0)>0 or max(f2,0)>0)
            rows.append((i,j,sy_,int(h==5),fat,sd5(i,j,sy_-1)))
E=pd.DataFrame(rows,columns=['ccode1','ccode2','styear','war','fatal','sd_w5']).drop_duplicates()
E['dyad_id']=E.ccode1.astype(str)+"_"+E.ccode2.astype(str)
print(f"\n(c) ESCALATION | dispute occurred: {len(E)} dyadic disputes 1955-2014  [memo: 3,396]")
for out,lab in [('war','war (hostlev=5)'),('fatal','any fatality')]:
    d=E.dropna(subset=[out,'sd_w5'])
    m=smf.logit(f"{out} ~ sd_w5",data=d).fit(disp=0,cov_type='cluster',cov_kwds={'groups':d['dyad_id']},maxiter=300)
    print(f"   {lab:20} N={len(d)}  shared-patron OR={np.exp(m.params['sd_w5']):.3f} p={m.pvalues['sd_w5']:.3f}"
          f"   [memo: war OR=1.56 p=0.49; fatality OR=0.90 p=0.75]")

# ---------- (d) residual ranking (Lieberman) ----------
d=P[P.both_imp_w5==1].dropna(subset=['onset','sd_w5']+CTRL+PY+['unga']).copy()
m=smf.logit("onset ~ sd_w5 + "+" + ".join(CTRL+PY+['unga']),data=d).fit(disp=0,maxiter=300)
d['phat']=m.predict(d)
sl=pd.read_csv(f"{REFERENCE}/statelist2024.csv"); abb={int(c):a for c,a in zip(sl.ccode,sl.stateabb)}
agg=d.groupby(['ccode1','ccode2']).agg(years=('onset','size'),onsets=('onset','sum'),
    predicted=('phat','sum'),patron_share=('sd_w5','mean')).reset_index()
agg=agg[agg.patron_share>=0.5]        # shared patron in most years
agg['residual']=agg.onsets-agg.predicted
agg['dyad']=agg.ccode1.map(abb)+"-"+agg.ccode2.map(abb)
print(f"\n(d) RESIDUAL RANKING among dyads sharing patron >=50% of years (n={len(agg)})")
print("   OFF-the-line (worst over-performers):")
print(agg.nlargest(6,'residual')[['dyad','years','onsets','predicted','patron_share','residual']].round(2).to_string(index=False))
print("   ON-the-line (best-fitting, full concentration):")
onl=agg[agg.patron_share>=0.99].copy(); onl['absres']=onl.residual.abs()
print(onl.nsmallest(6,'absres')[['dyad','years','onsets','predicted','patron_share','residual']].round(2).to_string(index=False))
P.to_csv(f"{DERIVED}/clean_polrel_panel_1955_2014.csv",index=False)
print("\npanel updated with sd_w5, both_imp_w5, unga")
