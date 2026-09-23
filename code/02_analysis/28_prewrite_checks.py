import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _paths import RAW, REFERENCE, DERIVED, FIG, TAB

#!/usr/bin/env python3
"""Pre-writing checks.
1. Patron-selection alternative: (a) does an onset predict LOSS of shared-patron
   status afterwards? (b) effect among long-peace dyads (py>=20), where the patron
   cannot be reacting to recent conflict; (c) effect when patron-sharing was
   established >=5 years earlier.
2. Originator-only onsets (drop coalition joiner dyads).
3. No-trade-control main table (keeps Eastern-bloc dyads).
4. Full politically-relevant sample with both-importer dummy (no conditioning).
5. Year fixed effects.  6. Asia-Pacific decomposition."""
import pandas as pd, numpy as np, statsmodels.formula.api as smf
from collections import defaultdict
P=pd.read_csv(f"{DERIVED}/clean_polrel_panel_1955_2014.csv").sort_values(['ccode1','ccode2','year'])
CTRL=['ally_defense','cinc_diff','regime_dist','ln_capdist','ln_trade_lag1']
PY=['py','py2','py3']; U=['unga']
def fit(df,f,var,label,extra=None):
    need=[v.strip() for v in f.replace('*','+').replace(':','+').split('+') if not v.strip().startswith('C(')]
    dv0=f.split('~')[0].strip(); d=df.dropna(subset=[dv0,var]+[n for n in need if n in df.columns]).copy()
    m=smf.logit(f,data=d).fit(disp=0,cov_type='cluster',cov_kwds={'groups':d['dyad_id']},maxiter=300)
    dv=f.split('~')[0].strip()
    s=f"{label:60} N={len(d):6d} ev={int(d[dv].sum()):4d}  {var}: OR={np.exp(m.params[var]):.3f} p={m.pvalues[var]:.3f}"
    if extra:
        for v in extra: s+=f" | {v}: OR={np.exp(m.params[v]):.3f} p={m.pvalues[v]:.3f}"
    print(s); return m
CS="+".join(CTRL+PY+U); Cnt="+".join([c for c in CTRL if c!='ln_trade_lag1']+PY+U)
bi=P[P.both_imp_w5==1]; cw=bi[bi.year<=1989]

print("="*100); print("1. PATRON-SELECTION ALTERNATIVE"); print("="*100)
# (a) reverse timing: among dyad-years with sd_w5==1, does onset at t predict sd_w5==0 at t+3?
g=P.groupby(['ccode1','ccode2'])
P['sd_lead3']=g['sd_w5'].shift(-3); P['sd_lead1']=g['sd_w5'].shift(-1)
S=P[(P.sd_w5==1)].dropna(subset=['sd_lead3']).copy(); S['lose3']=(S.sd_lead3==0).astype(int)
S1=P[(P.sd_w5==1)].dropna(subset=['sd_lead1']).copy(); S1['lose1']=(S1.sd_lead1==0).astype(int)
print(f"  baseline: P(lose shared patron within 3 yrs | no onset)={S[S.onset==0].lose3.mean():.1%}, | onset={S[S.onset==1].lose3.mean():.1%}  (n onsets={int(S.onset.sum())})")
fit(S,"lose3 ~ onset + ln_capdist + ally_defense + py+py2+py3",'onset',"1a  lose shared patron within 3y ~ onset")
fit(S1,"lose1 ~ onset + ln_capdist + ally_defense + py+py2+py3",'onset',"1a  lose shared patron next year ~ onset")
# (b) long-peace subsample
for lab,df in [("CW",cw),("full",bi)]:
    fit(df[df.py>=20],f"onset ~ sd_w5+{CS}",'sd_w5',f"1b  {lab}: dyads at peace >=20 yrs")
    fit(df[df.py>=10],f"onset ~ sd_w5+{CS}",'sd_w5',f"1b  {lab}: dyads at peace >=10 yrs")
# (c) patron-sharing established >=5 years before t
P['sd_lag5']=g['sd_w5'].shift(5)
P['sd_est5']=((P.sd_w5==1)&(P.sd_lag5==1)).astype(float); P.loc[P.sd_lag5.isna(),'sd_est5']=np.nan
bi=P[P.both_imp_w5==1]; cw=bi[bi.year<=1989]
fit(cw,f"onset ~ sd_est5+{CS}",'sd_est5',"1c  CW: sharing established >=5y before t")
fit(bi,f"onset ~ sd_est5+{CS}",'sd_est5',"1c  full: sharing established >=5y before t")

print("\n"+"="*100); print("2. ORIGINATOR-ONLY ONSETS (coalition joiners dropped)"); print("="*100)
midb=pd.read_csv(f"{RAW}/MID-5-Data-and-Supporting-Materials/MIDB 5.0.csv",encoding='latin-1')
dy=defaultdict(set); n_all=0; n_orig=0
for dn,gd in midb.groupby('dispnum'):
    a=gd[(gd.sidea==1)&(gd.orig==1)]; b=gd[(gd.sidea==0)&(gd.orig==1)]
    for _,x in a.iterrows():
        for _,y in b.iterrows():
            i,j=sorted([int(x.ccode),int(y.ccode)])
            for yr in range(max(int(max(x.styear,y.styear)),1946),int(min(x.endyear,y.endyear))+1): dy[(i,j)].add(yr)
def onset_o(i,j,t):
    ys=dy.get((i,j),set()); return int(t in ys and (t-1) not in ys)
P['onset_orig']=[onset_o(int(r.ccode1),int(r.ccode2),int(r.year)) for r in P.itertuples()]
bi=P[P.both_imp_w5==1]; cw=bi[bi.year<=1989]
print(f"  onsets all-dyads={int(bi.onset.sum())} vs originator-only={int(bi.onset_orig.sum())}")
fit(cw,f"onset_orig ~ sd_w5+{CS}",'sd_w5',"2   CW primary, originator dyads only")
fit(bi,f"onset_orig ~ shared_us_w5+{CS}",'shared_us_w5',"2   full, shared US, originator only")
fit(cw,f"onset_orig ~ same_top5+{CS}",'same_top5',"2   CW same-top, originator only")

print("\n"+"="*100); print("3. NO TRADE CONTROL (keeps Eastern-bloc dyads)"); print("="*100)
# w5 soviet patron
flow=pd.read_csv(f"{DERIVED}/bilateral_tiv_by_year.csv").rename(columns={'rec_cc':'i','sup_cc':'k','yr':'t'})
fl=flow.groupby(['i','k','t'])['tiv'].sum(); by_ik=defaultdict(dict)
for (i,k,t),v in fl.items(): by_ik[i].setdefault(k,{})[t]=v
top5={}
for i,ks in by_ik.items():
    for t in range(1954,2015):
        sums={k:sum(v for yy,v in tv.items() if t-4<=yy<=t) for k,tv in ks.items()}
        sums={k:s for k,s in sums.items() if s>0}; tot=sum(sums.values())
        if tot>0: k=max(sums,key=sums.get); top5[(i,t)]=(k,sums[k]/tot)
def sov(i,j,t):
    a=top5.get((i,t)); b=top5.get((j,t))
    if a is None or b is None: return np.nan
    return int(a[0]==365 and b[0]==365 and a[1]>=.5 and b[1]>=.5)
P['shared_sov_w5']=[sov(int(r.ccode1),int(r.ccode2),int(r.year)-1) for r in P.itertuples()]
bi=P[P.both_imp_w5==1]; cw=bi[bi.year<=1989]
for v in ['sd_w5','shared_us_w5','shared_sov_w5']:
    fit(cw,f"onset ~ {v}+{CS}",v,f"3   CW {v:14} WITH trade control")
    fit(cw,f"onset ~ {v}+{Cnt}",v,f"3   CW {v:14} NO trade control")

print("\n"+"="*100); print("4. FULL POLREL SAMPLE (no both-importer conditioning)"); print("="*100)
P['sd_w5_0']=P.sd_w5.fillna(0)
for lab,df in [("CW",P[P.year<=1989]),("full",P)]:
    fit(df,f"onset ~ sd_w5_0 + both_imp_w5 + {CS}",'sd_w5_0',f"4   {lab}: sd (0 if not both-import) + both-import dummy",extra=['both_imp_w5'])

print("\n"+"="*100); print("5. YEAR FIXED EFFECTS"); print("="*100)
fit(cw,f"onset ~ sd_w5 + C(year) + {CS}",'sd_w5',"5   CW primary + year FE")
fit(bi,f"onset ~ shared_us_w5 + C(year) + {CS}",'shared_us_w5',"5   full shared US + year FE")

print("\n"+"="*100); print("6. ASIA-PACIFIC: which shared-patron dyads have onsets?"); print("="*100)
sl=pd.read_csv(f"{REFERENCE}/statelist2024.csv"); abb={int(c):a for c,a in zip(sl.ccode,sl.stateabb)}
ap=bi[(bi.ccode1>=700)&(bi.ccode2>=700)&(bi.sd_w5==1)&(bi.onset==1)]
print(ap.assign(d=ap.ccode1.map(abb)+"-"+ap.ccode2.map(abb)).groupby('d').year.apply(list).to_string())
P.drop(columns=['sd_lead3','sd_lead1','sd_lag5']).to_csv(f"{DERIVED}/clean_polrel_panel_1955_2014.csv",index=False)
