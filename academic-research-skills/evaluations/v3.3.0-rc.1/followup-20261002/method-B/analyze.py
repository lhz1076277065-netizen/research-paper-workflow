"""Official regional screening plus explicitly hypothetical household couplings.
Run with the stipulated Python interpreter; no household microdata are created.
"""
from pathlib import Path
import hashlib, json, platform, sys, time
import numpy as np
import pandas as pd
import scipy
from scipy.optimize import linprog

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / 'method-input'
OUT = Path(__file__).resolve().parent
START = time.perf_counter()
KEY = ['MeasureID', 'GeoType', 'GeoID', 'TimePeriodID']

def table(name):
    obj = json.loads((RAW / name).read_text())
    assert len(set(map(len, obj.values()))) == 1, name
    return pd.DataFrame(obj)


def bounds(p, q):
    """Sharp risk-difference bounds for two known household marginals."""
    assert 0 < p < 1 and 0 <= q <= 1
    lo, hi = max(0., p + q - 1), min(p, q)
    return ((lo-p*q)/(p*(1-p)), (hi-p*q)/(p*(1-p)))


def solve(p, q):
    # Cell order: A1Y1, A1Y0, A0Y1, A0Y0. Household margins only.
    matrix = [[1, 1, 1, 1], [1, 1, 0, 0], [1, 0, 1, 0]]
    c = np.array([1/p, 0, -1/(1-p), 0])
    lo = linprog(c, A_eq=matrix, b_eq=[1, p, q], bounds=(0, None), method='highs')
    hi = linprog(-c, A_eq=matrix, b_eq=[1, p, q], bounds=(0, None), method='highs')
    assert lo.success and hi.success
    np.testing.assert_allclose([lo.fun, -hi.fun], bounds(p, q), atol=1e-8)
    return lo, hi


manifest = json.loads((RAW / 'manifest.json').read_text())
for name, expected in manifest.items():
    assert hashlib.sha256((RAW / name).read_bytes()).hexdigest() == expected, name
geo, ac, veg, temp, canopy = [table(x) for x in ['GeoLookup.json', '2185.json', '2143.json', '2141.json', '2157.json']]
quality = {}
for name, df in [('ac', ac), ('vegetation', veg), ('temperature', temp), ('canopy', canopy)]:
    quality[name] = {'rows': len(df), 'duplicate_keys': int(df.duplicated(KEY).sum()),
                     'missing_value': int(df.Value.isna().sum()),
                     'flagged_rows': int(df.Note.fillna('').ne('').sum())}
    if name != "ac": assert not df.duplicated(KEY).any(), name
    elif df.duplicated(KEY).any(): df.loc[df.duplicated(KEY, keep=False)].to_csv(OUT/"excluded-duplicate-records.csv", index=False)
assert not geo.duplicated(['GeoType', 'GeoID']).any()
for df in [ac, veg, canopy]:
    percentages = df.loc[df.MeasureID.ne(782), 'Value']
    assert percentages.dropna().between(0, 100).all()

z = ac.query('GeoType=="UHF42" and MeasureID==781 and TimePeriodID==46')[['GeoType','GeoID','Value','CI','Note']].rename(columns={'Value':'with_ac_pct', 'CI':'ac_ci','Note':'ac_note'})
z = z.merge(veg.query('GeoType=="UHF42" and TimePeriodID==46')[['GeoType','GeoID','Value']].rename(columns={'Value':'vegetation_land_pct'}),on=['GeoType','GeoID'],validate='one_to_one')
z = z.merge(temp.query('GeoType=="UHF42"')[['GeoType','GeoID','Value']].rename(columns={'Value':'surface_temperature_F'}),on=['GeoType','GeoID'],validate='one_to_one')
z = z.merge(geo[['GeoType','GeoID','Name']],on=['GeoType','GeoID'],validate='one_to_one')
assert len(z) == 42 and not z.duplicated(['GeoType','GeoID']).any()
assert z.with_ac_pct.notna().all() and z.with_ac_pct.between(0,100).all()
z['no_ac_pct'] = 100-z.with_ac_pct
criteria = {}
for percentile in [.5, .6, 2/3]:
    thresholds = {'no_ac_pct_min': float(z.no_ac_pct.quantile(percentile)),
                  'vegetation_land_pct_max': float(z.vegetation_land_pct.quantile(1-percentile)),
                  'surface_temperature_F_min': float(z.surface_temperature_F.quantile(percentile))}
    mask = (z.no_ac_pct.ge(thresholds['no_ac_pct_min']) & z.vegetation_land_pct.le(thresholds['vegetation_land_pct_max']) & z.surface_temperature_F.ge(thresholds['surface_temperature_F_min']))
    label = f'screen_{percentile:.3f}'
    z[label] = mask
    criteria[label] = {'thresholds':thresholds,'GeoIDs': z.loc[mask,'GeoID'].tolist()}
z['retained_all_screens'] = z[[x for x in z if x.startswith('screen_')]].all(axis=1)
z['screening_households_for_100_noAC_expected'] = 100/(z.no_ac_pct/100)
z.to_csv(OUT/'regional-screen.csv', index=False)

worlds, bound_rows = [], []
for row in z.itertuples():
    p = row.no_ac_pct/100
    N, M = 1000, 500  # Explicit construction, not real household counts/marginals.
    D = round(N*p)
    assert abs(D/N-p) < 1e-10
    for world, J in [('noAC_all_adequate', 0), ('noAC_all_inadequate', D)]:
        cells = [J, D-J, M-J, N-D-M+J]
        assert min(cells)>=0 and sum(cells)==N and sum(cells[:2])==D and cells[0]+cells[2]==M
        r_noac, r_ac = cells[0]/D, cells[2]/(N-D)
        worlds.append({'GeoID':row.GeoID,'Name':row.Name,'world':world,'constructed_N':N,'constructed_q':M/N,
                       'observed_noAC_share':p,'A1Y1':cells[0],'A1Y0':cells[1],'A0Y1':cells[2],'A0Y0':cells[3],
                       'r_noAC':r_noac,'r_AC':r_ac,'risk_difference':r_noac-r_ac,'status':'hypothetical_not_measured'})
    for q in [.1,.3,.5,.7,.9]:
        lo, hi = solve(p, q)
        bound_rows.append({'GeoID':row.GeoID,'Name':row.Name,'observed_p':p,'hypothetical_q':q,
                           'delta_lower':lo.fun,'delta_upper':-hi.fun,'status':'conditional_on_unmeasured_household_q'})
pd.DataFrame(worlds).to_csv(OUT/'hypothetical-couplings.csv',index=False)
pd.DataFrame(bound_rows).to_csv(OUT/'conditional-bounds.csv',index=False)
# Independent small check against LP includes extreme p and q, not only the study case.
for p in [.001,.167,.5,.999]:
    for q in [0,.001,.2,.5,.999,1]: solve(p,q)

comparison = ac.query('MeasureID==781 and TimePeriodID in [41,46]').merge(ac.query('MeasureID==1045 and TimePeriodID in [41,46]'),on=['GeoType','GeoID','TimePeriodID'],suffixes=('_with','_without'),validate='one_to_one')
quality['complement_check'] = {'matched_rows':len(comparison),'max_abs_sum_minus_100_pct':float((comparison.Value_with+comparison.Value_without-100).abs().max())}
quality['duplicate_handling'] = 'Conflicting Subboro 31, measure 781, year 2023 values retained in audit file; 2017 UHF analysis and historical complement check unaffected; no averaging or silent deduplication.'
quality['join'] = {'UHF42_rows_per_source':42,'joined_rows':42,'unmatched':0,'household_weights_available':False,'UHF2017_empty_ci':int(z.ac_ci.eq('').sum()),'UHF2017_flagged':int(z.ac_note.ne('').sum()),'2014_2017_are_distinct':True,'area_household_marginals_interchangeable':False}
correlations = {'noAC_vs_vegetation_spearman':float(z.no_ac_pct.corr(z.vegetation_land_pct,method='spearman')),'noAC_vs_surface_temp_spearman':float(z.no_ac_pct.corr(z.surface_temperature_F,method='spearman'))}
results = {'design':'exploratory regional screening and conditional identification construction; no causal or new-method claim',
           'official_AC_and_vegetation_year':2017,'temperature_date':'2018-07-17','tree_canopy_year_available':2014,
           'regional_unit':'UHF42; 42 regions, not 42 independent household samples', 'correlations':correlations,
           'criteria':criteria,'robust_material_acquisition_candidates':z.loc[z.retained_all_screens,['GeoID','Name','no_ac_pct','vegetation_land_pct','surface_temperature_F']].to_dict('records'),
           'representative_worlds': [x for x in worlds if x['GeoID']==107],
           'conditional_bound_cases':len(bound_rows),'LP_solves':2*(len(bound_rows)+24),'checks':'hashes, schema lengths, unique keys, percent ranges, one-to-one join, 84 exact synthetic tables, sharp formula vs independent LP; PASS',
           'runtime_seconds':time.perf_counter()-START,'environment':{'python':sys.version,'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'platform':platform.platform()},
           'no_confidence_interval':'No UHF AC SE/CI or household weights in the starting materials; no population inference p-values computed.'}
(OUT/'quality.json').write_text(json.dumps(quality,ensure_ascii=False,indent=2))
(OUT/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False,indent=2))
print('QUALITY',json.dumps(quality,ensure_ascii=False))
