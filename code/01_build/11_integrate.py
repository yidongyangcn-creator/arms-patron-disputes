import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _paths import RAW, REFERENCE, DERIVED, FIG, TAB

#!/usr/bin/env python3
"""Integrate global SIPRI register + MID 5.0 + V-Dem + COW controls into a
harmonised dyad-year panel and produce a data overview.
Outputs written to OUT dir.
"""
import pandas as pd, numpy as np, io, json, os, itertools
from collections import defaultdict

OUT=BASE+"/build"
os.makedirs(OUT, exist_ok=True)
YEARS=list(range(1990,2015))   # modelling window (MID 5.0 ends 2014)

# ----------------------------------------------------------------------
# 1) COUNTRY CROSSWALK  (everything -> COW ccode)
# ----------------------------------------------------------------------
sl=pd.read_csv(f"{REFERENCE}/statelist2024.csv")
name2ccode={str(n).strip():int(c) for n,c in zip(sl.statenme,sl.ccode)}
ccode2abb={int(c):a for c,a in zip(sl.ccode,sl.stateabb)}

SIPRI_OVERRIDE={
 'United States':2,'Soviet Union':365,'Turkiye':640,'Viet Nam':816,
 'South Vietnam':817,'DR Congo':490,"Cote d'Ivoire":437,'Czechia':316,
 'North Macedonia':343,'Bosnia-Herzegovina':346,'Cabo Verde':402,
 'Timor-Leste':860,'eSwatini':572,'East Germany (GDR)':265,
 'North Yemen':678,'Yemen Arab Republic (North Yemen)':678,'South Yemen':680,
 'Antigua and Barbuda':58,'Saint Kitts and Nevis':60,'Saint Vincent':57,
}
DROP_NONCOW={'Aruba','Biafra','Katanga','Northern Cyprus','Palestine',
 'Western Sahara','unknown recipient(s)','unknown supplier(s)'}
def sipri2ccode(n):
    if pd.isna(n) or n in DROP_NONCOW or '*' in str(n): return None
    n=str(n).strip()
    if n in SIPRI_OVERRIDE: return SIPRI_OVERRIDE[n]
    return name2ccode.get(n)

# ----------------------------------------------------------------------
# 2) SIPRI REGISTER -> bilateral TIV by delivery year -> overlap
# ----------------------------------------------------------------------
lines=open(f"{RAW}/trade-register.csv",encoding="utf-8",errors="replace").readlines()
hi=[i for i,l in enumerate(lines) if l.startswith("Recipient,Supplier")][0]
reg=pd.read_csv(io.StringIO("".join(lines[hi:])))
reg.columns=[c.strip() for c in reg.columns]
reg=reg.rename(columns={'SIPRI TIV of delivered weapons':'tiv',
                        'Year(s) of delivery':'dyears'})
reg['rec_cc']=reg.Recipient.map(sipri2ccode)
reg['sup_cc']=reg.Supplier.map(sipri2ccode)
reg['tiv']=pd.to_numeric(reg['tiv'],errors='coerce')
# expand multi-year deliveries ("2012; 2013; 2016")
reg2=reg.dropna(subset=['rec_cc','sup_cc']).copy()
reg2['dyears']=reg2['dyears'].astype(str)
reg2=reg2.assign(yr=reg2['dyears'].str.split(';')).explode('yr')
reg2['yr']=pd.to_numeric(reg2['yr'],errors='coerce')
reg2=reg2.dropna(subset=['yr'])
reg2['yr']=reg2['yr'].astype(int)
reg2['rec_cc']=reg2['rec_cc'].astype(int); reg2['sup_cc']=reg2['sup_cc'].astype(int)
reg2=reg2[(reg2.tiv>0)&(reg2.rec_cc!=reg2.sup_cc)]
# annual recipient<-supplier TIV
flow=(reg2.groupby(['rec_cc','sup_cc','yr'],as_index=False)['tiv'].sum())

def overlap_year(yr):
    """return dict {(i,j):overlap} for recipients active in yr (L1 share similarity)."""
    d=flow[flow.yr==yr]
    if d.empty: return {},set()
    tot=d.groupby('rec_cc')['tiv'].transform('sum')
    d=d.assign(w=d.tiv/tot)
    # share vectors
    shares=defaultdict(dict)
    for r,s,w in zip(d.rec_cc,d.sup_cc,d.w): shares[r][s]=w
    recs=sorted(shares)
    out={}
    for a,b in itertools.combinations(recs,2):
        sa,sb=shares[a],shares[b]
        common=set(sa)&set(sb)
        ov=sum(min(sa[k],sb[k]) for k in common)
        if ov>0: out[(a,b)]=ov
    return out,set(recs)

overlap_by_year={}; importers_by_year={}
for y in range(1949,2026):
    ov,recs=overlap_year(y); overlap_by_year[y]=ov; importers_by_year[y]=recs

# ----------------------------------------------------------------------
# 3) MID 5.0 -> dyadic conflict & onset
# ----------------------------------------------------------------------
midb=pd.read_csv(f"{RAW}/MID-5-Data-and-Supporting-Materials/MIDB 5.0.csv",
                 encoding='latin-1')
def mid_dyad_years():
    dy=defaultdict(set)            # (i,j) -> set of years in dispute
    for dn,g in midb.groupby('dispnum'):
        a=g[g.sidea==1]; b=g[g.sidea==0]
        for _,x in a.iterrows():
            for _,y in b.iterrows():
                sy=max(int(x.styear),int(y.styear))
                ey=min(int(x.endyear),int(y.endyear))
                i,j=sorted([int(x.ccode),int(y.ccode)])
                for yr in range(sy,ey+1):
                    dy[(i,j)].add(yr)
    return dy
dy=mid_dyad_years()
def mid_set(yr):  return {k for k,ys in dy.items() if yr in ys}
def onset_set(yr):return {k for k,ys in dy.items() if yr in ys and (yr-1) not in ys}

# ----------------------------------------------------------------------
# 4) V-DEM regime  (COWcode present)
# ----------------------------------------------------------------------
vd=pd.read_csv(f"{RAW}/V-Dem-CY-FullOthers-v16_csv/V-Dem-CY-Full+Others-v16.csv",
               usecols=['COWcode','year','v2x_polyarchy','v2x_libdem','e_polity2'],
               low_memory=False)
vd=vd.dropna(subset=['COWcode'])
vd['COWcode']=vd['COWcode'].astype(int)
poly={(int(c),int(y)):p for c,y,p in zip(vd.COWcode,vd.year,vd.v2x_polyarchy)}

# ----------------------------------------------------------------------
# 5) CINC + ALLIANCE + CONTIGUITY coverage
# ----------------------------------------------------------------------
nmc=pd.read_csv(f"{RAW}/NMC_Documentation-6.0/NMC-60-wsupplementary/NMC-60-wsupplementary.csv",encoding='latin-1',low_memory=False)
cinc={(int(c),int(y)):v for c,y,v in zip(nmc.ccode,nmc.year,nmc.cinc) if v not in (-9,)}
ally=pd.read_csv(f"{RAW}/version4.1_csv/alliance_v4.1_by_dyad_yearly.csv")
ally_def=set()
for c1,c2,yr,d in zip(ally.ccode1,ally.ccode2,ally.year,ally.defense):
    if d==1:
        i,j=sorted([int(c1),int(c2)]); ally_def.add((i,j,int(yr)))

# ----------------------------------------------------------------------
# 6) REGION map (coarse COW buckets)
# ----------------------------------------------------------------------
def region(cc):
    if 2<=cc<=99: return "Americas"
    if 100<=cc<=199: return "S.America"
    if 200<=cc<=399: return "Europe/PostSoviet"
    if 600<=cc<=698: return "MENA"
    if 400<=cc<=599: return "SubSaharanAfrica"
    if 700<=cc<=999: return "Asia-Pacific"
    return "Other"

# ----------------------------------------------------------------------
# 7) OVERVIEW STATISTICS
# ----------------------------------------------------------------------
rows=[]
for y in YEARS:
    mids=mid_set(y); ons=onset_set(y); ov=overlap_by_year[y]
    imp=importers_by_year[y]
    # onset dyads with computable lagged overlap (both imported in y-1)
    imp_lag=importers_by_year[y-1]
    onset_cov=sum(1 for (i,j) in ons if i in imp_lag and j in imp_lag)
    rows.append(dict(year=y,
        mid_dyads=len(mids), onset_dyads=len(ons),
        n_importers=len(imp),
        overlap_pairs=len(ov),
        onset_with_overlap_data=onset_cov))
ov_df=pd.DataFrame(rows)
ov_df.to_csv(f"{OUT}/overview_yearly.csv",index=False)

# region breakdown of onsets 1990-2014
reg_rows=[]
allons=defaultdict(int); allons_cov=defaultdict(int)
for y in YEARS:
    imp_lag=importers_by_year[y-1]
    for (i,j) in onset_set(y):
        ri,rj=region(i),region(j)
        key=ri if ri==rj else "cross-region"
        allons[key]+=1
        if i in imp_lag and j in imp_lag: allons_cov[key]+=1
reg_df=pd.DataFrame([dict(region=k,onsets=v,onsets_with_overlap=allons_cov[k])
                     for k,v in sorted(allons.items(),key=lambda x:-x[1])])
reg_df.to_csv(f"{OUT}/overview_by_region.csv",index=False)

# ----------------------------------------------------------------------
# 8) BUILD INTEGRATED DYAD-YEAR PANEL (politically-relevant-ish: keep dyads
#    where EITHER country imported arms in t-1 OR a MID ever occurred)
# ----------------------------------------------------------------------
# universe of COW states active 1990-2014 from statelist
active=set()
for ab,cc,sy,ey in zip(sl.stateabb,sl.ccode,sl.styear,sl.endyear):
    if int(sy)<=2014 and int(ey)>=1990: active.add(int(cc))
panel=[]
for y in YEARS:
    mids=mid_set(y); ons=onset_set(y); ov=overlap_by_year[y]
    ov_lag=overlap_by_year[y-1]; imp_lag=importers_by_year[y-1]
    states=sorted(c for c in active if c<=999)
    for i,j in itertools.combinations(states,2):
        onset=1 if (i,j) in ons else 0
        in_mid=1 if (i,j) in mids else 0
        ovl=ov_lag.get((i,j),0.0)
        # keep row only if politically relevant: importer-overlap computable OR mid present
        both_imp= i in imp_lag and j in imp_lag
        if not (both_imp or in_mid or onset): continue
        panel.append(dict(year=y,ccode1=i,ccode2=j,
            abb1=ccode2abb.get(i,i),abb2=ccode2abb.get(j,j),
            region1=region(i),region2=region(j),
            mid=in_mid,onset=onset,
            overlap_lag1=ovl,
            both_import_lag1=int(both_imp),
            ally_defense=int((i,j,y) in ally_def),
            cinc_diff=abs(cinc.get((i,y),np.nan)-cinc.get((j,y),np.nan)) if (i,y) in cinc and (j,y) in cinc else np.nan,
            polyarchy1=poly.get((i,y),np.nan),
            polyarchy2=poly.get((j,y),np.nan)))
panel=pd.DataFrame(panel)
panel['regime_dist']=(panel.polyarchy1-panel.polyarchy2).abs()
panel.to_csv(f"{OUT}/dyad_year_panel_1990_2014.csv",index=False)

# overlap full matrix (long) for all years, for the R pipeline
flow.to_csv(f"{OUT}/bilateral_tiv_by_year.csv",index=False)
ovlong=[]
for y,ov in overlap_by_year.items():
    for (i,j),v in ov.items(): ovlong.append((y,i,j,v))
pd.DataFrame(ovlong,columns=['year','ccode1','ccode2','overlap']).to_csv(
    f"{OUT}/overlap_long_allyears.csv",index=False)

# summary json
summary=dict(
  sipri_deal_rows=int(len(reg)), sipri_mapped_flows=int(len(flow)),
  sipri_unmapped_names=int(reg.rec_cc.isna().sum()+reg.sup_cc.isna().sum()),
  mid_dyad_pairs=int(len(dy)),
  mid_onsets_1990_2014=int(ov_df.onset_dyads.sum()),
  onsets_with_overlap_data=int(ov_df.onset_with_overlap_data.sum() if 'onset_with_overlap_data' in ov_df else ov_df.onset_dyads.sum()),
  panel_rows=int(len(panel)),
  panel_onset_rate=float(panel.onset.mean()),
  cinc_coverage=float(panel.cinc_diff.notna().mean()),
  regime_coverage=float(panel.regime_dist.notna().mean()),
)
json.dump(summary,open(f"{OUT}/summary.json","w"),indent=2)
print("=== SUMMARY ==="); print(json.dumps(summary,indent=2))
print("\n=== YEARLY (head/tail) ==="); print(ov_df.to_string(index=False))
print("\n=== BY REGION ==="); print(reg_df.to_string(index=False))
print("\nOutputs in",OUT)
