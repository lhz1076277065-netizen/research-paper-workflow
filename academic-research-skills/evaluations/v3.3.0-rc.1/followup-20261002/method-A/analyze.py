"""Recompute published regional screens and explicitly hypothetical household bounds.
Run with the Python executable specified in the task. No network or new dependency.
"""
from pathlib import Path
import hashlib
import json
import platform
import sys
import numpy as np
import pandas as pd
import scipy
from scipy.optimize import linprog
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent
INPUT = ROOT.parent / 'method-input'

def load(name):
    return pd.DataFrame(json.loads((INPUT / name).read_text()))

def select(df, measure, geo, period, label):
    x = df.loc[(df.MeasureID == measure) & (df.GeoType == geo) & (df.TimePeriodID == period)].copy()
    assert not x.duplicated(['GeoType', 'GeoID']).any()
    return x[['GeoType', 'GeoID', 'Value', 'CI', 'Note']].rename(columns={'Value': label, 'CI': label+'_CI', 'Note': label+'_Note'})

def frontier(x, a, cover):
    # ponytail: O(n²) scan for 42 districts; vectorize if the geography count grows.
    return [not any((x[a].iloc[k] >= x[a].iloc[i] and x[cover].iloc[k] <= x[cover].iloc[i]) and
                    (x[a].iloc[k] > x[a].iloc[i] or x[cover].iloc[k] < x[cover].iloc[i])
                    for k in range(len(x))) for i in range(len(x))]

def table(a, b, j):
    return np.array([j, a-j, b-j, 1-a-b+j])

def bounds(a, b):
    assert 0 < a < 1 and 0 <= b <= 1
    lo, hi = max(0, a+b-1), min(a, b)
    return lo, hi, (lo-a*b)/(a*(1-a)), (hi-a*b)/(a*(1-a))

def run():
    manifest = json.loads((INPUT/'manifest.json').read_text())
    assert all(hashlib.sha256((INPUT/n).read_bytes()).hexdigest() == h for n,h in manifest.items())
    ac, canopy, vegetation, heat, geo = map(load, ['2185.json','2157.json','2143.json','2141.json','GeoLookup.json'])
    names = geo[['GeoType','GeoID','Name','Borough']]
    rows = []
    for filename, df in [('2185',ac),('2157',canopy),('2143',vegetation),('2141',heat)]:
        for keys, d in df.groupby(['MeasureID','GeoType','TimePeriodID']):
            rows.append(dict(file=filename, MeasureID=int(keys[0]), GeoType=keys[1], TimePeriodID=int(keys[2]), n=len(d), missing=int(d.Value.isna().sum())))
    pd.DataFrame(rows).to_csv(ROOT/'coverage.csv',index=False)
    z = select(ac,781,'UHF42',41,'ac2014').merge(select(canopy,708,'UHF42',41,'canopy2014'),on=['GeoType','GeoID'],validate='one_to_one')
    z = z.merge(select(ac,781,'UHF42',46,'ac2017'),on=['GeoType','GeoID'],validate='one_to_one')
    z = z.merge(select(vegetation,690,'UHF42',46,'vegetation2017'),on=['GeoType','GeoID'],validate='one_to_one')
    z = z.merge(select(heat,688,'UHF42',47,'surface2018_F'),on=['GeoType','GeoID'],validate='one_to_one').merge(names,on=['GeoType','GeoID'],validate='one_to_one')
    assert len(z)==42 and not z[['ac2014','canopy2014','ac2017','vegetation2017']].isna().any().any()
    z['no_ac2014'], z['no_ac2017'] = 100-z.ac2014,100-z.ac2017
    z['frontier2014']=frontier(z,'no_ac2014','canopy2014')
    z['frontier2017']=frontier(z,'no_ac2017','vegetation2017')
    z.to_csv(ROOT/'district_comparison.csv',index=False)
    stats = {'source_commit':'d3558441d122b4db4b9fd4d2011be500df6b584a','n_UHF':42,'definitions':{'no_ac':'100 minus measure 781; functioning AC, not affordability or usage','canopy':'land share, not household access','screen':'Pareto high no_AC and low published land cover; not intervention benefit or population count'},'comparison':{}}
    for y,c in [('2014','canopy2014'),('2017','vegetation2017')]:
        a='no_ac'+y
        stats['comparison'][y]={'pearson':float(z[a].corr(z[c])),'spearman':float(spearmanr(z[a],z[c]).statistic),'frontier':z.loc[z['frontier'+y],['GeoID','Name',a,c]].to_dict('records'),'AC_CI_available':int(z['ac'+y+'_CI'].str.len().gt(0).sum()),'AC_notes':int(z['ac'+y+'_Note'].str.len().gt(0).sum())}
    # Deliberately favorable but UNVALIDATED bridge: let household outdoor deficit b=1-canopy.
    # This is a counterfactual information audit, never a household measurement.
    constructions=[]
    eq=np.array([[1,1,0,0],[1,0,1,0],[1,1,1,1]],float)
    for r in z.itertuples():
        a,b=r.no_ac2014/100,1-r.canopy2014/100
        lo,hi,dl,du=bounds(a,b)
        for label,j,delta in [('lower',lo,dl),('upper',hi,du)]:
            cells=table(a,b,j)
            assert cells.min() >= -1e-12 and np.allclose(eq@cells,[a,b,1])
            opt=linprog([1 if label=='lower' else -1,0,0,0],A_eq=eq,b_eq=[a,b,1],bounds=(0,None),method='highs')
            assert opt.success and abs(opt.x[0]-j)<1e-9
            assert dl<=1e-12 and du>=-1e-12  # independence is feasible
            constructions.append(dict(GeoID=r.GeoID,Name=r.Name,scenario='hypothetical_household_marginal_bridge',endpoint=label,a=a,b=b,j=j,A1Y1=float(cells[0]),A1Y0=float(cells[1]),A0Y1=float(cells[2]),A0Y0=float(cells[3]),P_Y_given_A=j/a,delta=delta))
    pd.DataFrame(constructions).to_csv(ROOT/'hypothetical_joint_tables.csv',index=False)
    # Bounds for acquiring only a correct household marginal: every nondegenerate pair still allows independence.
    for a in [.01,.257,.5,.99]:
        for b in [0,.1,.92916,1]:
            lo,hi,dl,du=bounds(a,b); assert lo-1e-12<=a*b<=hi+1e-12
    boroughs=[]
    for y,period,df,measure in [('2014',41,canopy,708),('2017',46,vegetation,690)]:
        v=select(ac,781,'Borough',period,'ac_pct').merge(select(ac,782,'Borough',period,'ac_count'),on=['GeoType','GeoID'],validate='one_to_one').merge(select(df,measure,'Borough',period,'regional_cover'),on=['GeoType','GeoID'],validate='one_to_one').merge(names,on=['GeoType','GeoID'],validate='one_to_one')
        v['total_count_approx']=v.ac_count/(v.ac_pct/100)
        v['no_ac_count_approx']=v.total_count_approx-v.ac_count
        v['year']=y; boroughs.append(v)
        means={k:float(np.average(v.regional_cover,weights=v[w])) for k,w in [('all_household_context','total_count_approx'),('no_AC_context','no_ac_count_approx'),('AC_context','ac_count')]}
        means['noAC_minus_AC_context_pp']=means['no_AC_context']-means['AC_context']
        means['warning']='assigned borough land context, not personal outdoor access; denominators recovered from rounded estimates'
        stats.setdefault('borough_context',{})[y]=means
    pd.concat(boroughs).to_csv(ROOT/'borough_context.csv',index=False)
    stats['hypothetical_Hunts_Point']= [r for r in constructions if r['GeoID']==107]
    stats['verification']={'input_manifest':'passed','LP_extrema_checks':84,'independence_feasible':'42/42 hypothetical district margins','dependencies':{'python':sys.version,'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__},'platform':platform.platform(),'seed':'none; deterministic','solver':'scipy.optimize.linprog/HiGHS default settings','tolerance':1e-9}
    (ROOT/'results.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2))
    print(json.dumps(stats,ensure_ascii=False,indent=2))

if __name__=='__main__':
    run()
