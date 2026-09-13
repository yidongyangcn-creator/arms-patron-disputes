import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _paths import RAW, REFERENCE, DERIVED, FIG, TAB

#!/usr/bin/env python3
"""Quantitative backbones for the case studies: patron delivery series vs
crisis chronology, one figure per case + finalized case-selection table."""
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from collections import defaultdict
flow=pd.read_csv(f"{DERIVED}/bilateral_tiv_by_year.csv")
P=pd.read_csv(f"{DERIVED}/clean_polrel_panel_1955_2014.csv")

def series(sup,rec,y0,y1):
    d=flow[(flow.sup_cc==sup)&(flow.rec_cc==rec)&(flow.yr>=y0)&(flow.yr<=y1)]
    s=d.set_index('yr').tiv
    return [s.get(y,0.0) for y in range(y0,y1+1)]
def sd_years(c1,c2):
    lo,hi=min(c1,c2),max(c1,c2)
    d=P[(P.ccode1==lo)&(P.ccode2==hi)&(P.sd_w5==1)]
    return sorted(d.year)

def case_fig(fname,title,sup,supname,a,b,an,bn,y0,y1,onsets,notes,extra_shade=None):
    yrs=list(range(y0,y1+1))
    sa=series(sup,a,y0,y1); sb=series(sup,b,y0,y1)
    fig,ax=plt.subplots(figsize=(10,4.2))
    # shared-patron shading (w5 measure, panel years only)
    for y in sd_years(a,b):
        if y0<=y<=y1: ax.axvspan(y-.5,y+.5,color='#fdd9c4',lw=0,zorder=0)
    if extra_shade:
        ax.axvspan(extra_shade[0],extra_shade[1],color='#c6dbef',alpha=.6,lw=0,zorder=0)
    ax.plot(yrs,sa,color='#b2182b',lw=2,label=f"{supname} → {an}")
    ax.plot(yrs,sb,color='#2166ac',lw=2,label=f"{supname} → {bn}")
    for y in onsets:
        if y0<=y<=y1:
            ax.axvline(y,ls='--',c='k',lw=1)
            ax.annotate(str(y),(y,ax.get_ylim()[1]*0.97),rotation=90,fontsize=8,
                        va='top',ha='right')
    for (x,ytext,txt) in notes:
        ax.annotate(txt,(x,ytext),fontsize=8,style='italic')
    ax.set_title(title,fontsize=11)
    ax.set_ylabel("SIPRI TIV delivered (m)"); ax.set_xlim(y0,y1)
    ax.legend(fontsize=9,loc='upper left')
    plt.tight_layout(); plt.savefig(f"{FIG}/{fname}",dpi=150); plt.close()
    print("saved",fname)

# ---- Case A: Iraq-Syria (Soviet patron) ----
case_fig("CASE_iraq_syria.png",
    "Iraq & Syria: Soviet deliveries and bilateral MID onsets (orange = shared dominant patron, w5)",
    365,"USSR",645,652,"Iraq","Syria",1955,1995,[1957,1976,1982,1987,1990],
    [(1980.3,50,"")],extra_shade=None)

# suspension check (numbers for the text)
print("\nUSSR->Iraq TIV 1978-84:",[round(v) for v in series(365,645,1978,1984)])
print("USSR->Syria TIV 1978-84:",[round(v) for v in series(365,652,1978,1984)])

# ---- Case B: Hungary-Romania (Soviet patron, on-the-line) ----
case_fig("CASE_hungary_romania.png",
    "Hungary & Romania: Soviet deliveries; single display-level incident 1971 (orange = shared patron)",
    365,"USSR",310,360,"Hungary","Romania",1955,1990,[1971],[])

# ---- Shadow case: Greece-Turkey (US patron; 1974 Cyprus; embargo 75-78 shaded blue) ----
case_fig("CASE_greece_turkey.png",
    "Greece & Turkey: US deliveries; Cyprus 1974 and US embargo on Turkey 1975-78 (blue band)",
    2,"USA",350,640,"Greece","Turkey",1960,1990,[1963,1967,1974,1978,1981,1989],
    [],extra_shade=(1974.8,1978.8))
print("\nUSA->Turkey TIV 1972-80:",[round(v) for v in series(2,640,1972,1980)])

# ---- Boundary case: Egypt-Israel (US patron after 1979) ----
case_fig("CASE_egypt_israel.png",
    "Egypt & Israel: US deliveries; wars end 1979, lower-level onsets continue (orange = shared US patron)",
    2,"USA",651,666,"Egypt","Israel",1965,2014,[1967,1973,1983,1989,2004,2006,2009,2011,2014],[])
# Egypt's Soviet-to-US switch for the text
print("\nUSSR->Egypt TIV 1970-80:",[round(v) for v in series(365,651,1970,1980)])
print("USA ->Egypt TIV 1975-85:",[round(v) for v in series(2,651,1975,1985)])

# ---- finalized case-selection table ----
midb=pd.read_csv(f"{RAW}/MID-5-Data-and-Supporting-Materials/MIDB 5.0.csv",encoding='latin-1')
import statsmodels.formula.api as smf
CTRL=['ally_defense','cinc_diff','regime_dist','ln_capdist','ln_trade_lag1']
PY=['py','py2','py3']
d=P[P.both_imp_w5==1].dropna(subset=['onset','sd_w5']+CTRL+PY+['unga']).copy()
m=smf.logit("onset ~ sd_w5 + "+" + ".join(CTRL+PY+['unga']),data=d).fit(disp=0,maxiter=300)
d['phat']=m.predict(d)
sl=pd.read_csv(f"{REFERENCE}/statelist2024.csv"); abb={int(c):a for c,a in zip(sl.ccode,sl.stateabb)}
agg=d.groupby(['ccode1','ccode2']).agg(years=('onset','size'),onsets=('onset','sum'),
    predicted=('phat','sum'),patron_share_yrs=('sd_w5','mean')).reset_index()
agg=agg[agg.patron_share_yrs>=0.5]
agg['residual']=agg.onsets-agg.predicted
agg['dyad']=agg.ccode1.map(abb)+"-"+agg.ccode2.map(abb)
off=agg.nlargest(10,'residual')
onl=agg[(agg.patron_share_yrs>=0.9)&(agg.years>=20)].copy()
onl['absres']=onl.residual.abs(); onl=onl.nsmallest(10,'absres')
sel=pd.concat([off.assign(role='off-the-line'),onl.assign(role='on-the-line')])
sel['selected']=sel.dyad.map({'IRQ-SYR':'CASE A','HUN-RUM':'CASE B','GRC-TUR':'shadow'}).fillna('')
sel.round(2).to_csv(f"{TAB}/case_selection_table.csv",index=False)
print("\nOFF-the-line top10:");print(off[['dyad','years','onsets','predicted','patron_share_yrs','residual']].round(2).to_string(index=False))
print("\nON-the-line (conc>=0.9, years>=20):");print(onl[['dyad','years','onsets','predicted','patron_share_yrs','residual']].round(2).to_string(index=False))
