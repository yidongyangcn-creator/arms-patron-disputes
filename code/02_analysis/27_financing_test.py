import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _paths import RAW, REFERENCE, DERIVED, FIG, TAB

#!/usr/bin/env python3
"""Financing test (USAID Greenbook): is the shared-US-patron effect concentrated
among aid-financed clients?  Adds aid_i, aid_j, both_us_aid, ln_min_aid to the panel.
(Previously run inline; saved here so the repository pipeline can reproduce it.)"""
import pandas as pd, numpy as np, statsmodels.formula.api as smf
P=pd.read_csv(f"{DERIVED}/clean_polrel_panel_1955_2014.csv")
aid=pd.read_csv(f"{RAW}/us_military_aid_greenbook.csv")
sl=pd.read_csv(f"{REFERENCE}/statelist2024.csv")
name2cc={str(n).strip():int(c) for n,c in zip(sl.statenme,sl.ccode)}
OV={'United States':2,'Russia':365,'Turkey':640,'Vietnam':816,'Congo (Kinshasa)':490,
 'Congo (Brazzaville)':484,"Cote d'Ivoire":437,'Czechia':316,'North Macedonia':343,
 'Bosnia and Herzegovina':346,'Cabo Verde':402,'Timor-Leste':860,'Eswatini':572,
 'Germany':255,'Yemen':679,'Korea, South':732,'Korea, Republic of':732,'South Korea':732,
 'Burma':775,'Burma (Myanmar)':775,'Egypt':651,'Israel':666,'Iran':630,'Iraq':645,'Syria':652}
aid['ccode']=aid.country.map(lambda n: OV.get(str(n).strip(),name2cc.get(str(n).strip())))
aid=aid.dropna(subset=['ccode']); aid['ccode']=aid.ccode.astype(int)
A={(int(c),int(y)):v for c,y,v in zip(aid.ccode,aid.year,aid.oblig_const)}
def aid5(c,t): return sum(A.get((c,y),0.0) for y in range(t-5,t))
P['aid_i']=[aid5(int(r.ccode1),int(r.year)) for r in P.itertuples()]
P['aid_j']=[aid5(int(r.ccode2),int(r.year)) for r in P.itertuples()]
P['both_us_aid']=((P.aid_i>50e6)&(P.aid_j>50e6)).astype(int)
P['ln_min_aid']=np.log(np.minimum(P.aid_i,P.aid_j)+1)
CTRL=['ally_defense','cinc_diff','regime_dist','ln_capdist','ln_trade_lag1']
PY=['py','py2','py3']; U=['unga']; C="+".join(CTRL+PY+U)
d=P[P.both_imp_w5==1].dropna(subset=['onset','shared_us_w5','both_us_aid']+CTRL+PY+U).copy()
def run(f,show,label):
    m=smf.logit(f"onset ~ {f}",data=d).fit(disp=0,cov_type='cluster',cov_kwds={'groups':d['dyad_id']},maxiter=300)
    print(f"{label:48}"+"".join(f" | {v}: OR={np.exp(m.params[v]):.3f} p={m.pvalues[v]:.3f}" for v in show)); return m
run(f"shared_us_w5+{C}",['shared_us_w5'],"F0 shared US patron (baseline)")
run(f"both_us_aid+{C}",['both_us_aid'],"F1 both US-aid-financed")
m=run(f"shared_us_w5*both_us_aid+{C}",['shared_us_w5','both_us_aid','shared_us_w5:both_us_aid'],"F2 interaction")
b=m.params
print(f"   effect when both aid-financed OR={np.exp(b['shared_us_w5']+b['shared_us_w5:both_us_aid']):.3f}; not aid-financed OR={np.exp(b['shared_us_w5']):.3f}")
run(f"shared_us_w5+ln_min_aid+shared_us_w5:ln_min_aid+{C}",['shared_us_w5','shared_us_w5:ln_min_aid'],"F3 continuous aid interaction")
P.to_csv(f"{DERIVED}/clean_polrel_panel_1955_2014.csv",index=False)
