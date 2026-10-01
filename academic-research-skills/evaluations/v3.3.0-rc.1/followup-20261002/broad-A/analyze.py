"""Offline pilot. NOAA samples are observations, never imputed person-hours."""
from pathlib import Path
import csv,json
from datetime import datetime,timedelta
ROOT=Path(__file__).resolve().parent

def eligible(arrival, intervals, stay_minutes):
    assert stay_minutes >= 0
    arrival_minute = round(arrival * 60)
    return any(start * 60 <= arrival_minute < end * 60 and arrival_minute + stay_minutes <= end * 60
               for start,end in intervals)

def check():
    # Two co-accessible sites require an outdoor transfer; no cross-site rest concatenation.
    one=[[(12,22)]]; split=[[(12,17)],[(17,22)]]
    times=[12+x/60 for x in range(600)]
    assert all(any(eligible(t,s,0) for s in one)==any(eligible(t,s,0) for s in split) for t in times)
    assert sum(any(eligible(t,s,70) for s in one) for t in times)==531
    assert sum(any(eligible(t,s,70) for s in split) for t in times)==462
    assert eligible(21,[(12,22)],60)
    assert not eligible(22,[(12,22)],0)
    assert not eligible(21,[(12,22)],70)

check()
records=[]
allrows=list(csv.DictReader((ROOT/'phx-2025.csv').open()))
for x in allrows:
    local=datetime.fromisoformat(x['DATE'])-timedelta(hours=7)
    if local.month != 7 or local.weekday()!=6 or x['REPORT_TYPE'].strip()!='FM-15':continue
    value,qc=x['TMP'].split(',')
    if qc not in {'0','1','4','5'} or value=='+9999':continue
    records.append(dict(utc=x['DATE'],local=local.isoformat(),temp_c=int(value)/10,qc=qc,
                        report_type=x['REPORT_TYPE'].strip()))
assert len({x['utc'] for x in records})==len(records)
with (ROOT/'july-sunday-observations.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=records[0]);w.writeheader();w.writerows(records)
summary=[]
for threshold in [32,35,38]:
 for name,intervals in [('actual_library_12_22',[(12,22)]),('equal_hours_shift_14_24',[(14,24)])]:
  for stay in [0,70,120]:
   selected=[x for x in records if x['temp_c']>=threshold]
   count=sum(eligible(datetime.fromisoformat(x['local']).hour+datetime.fromisoformat(x['local']).minute/60,intervals,stay) for x in selected)
   summary.append(dict(threshold_c=threshold,scenario=name,stay_minutes=stay,hot_observations=len(selected),eligible_arrivals=count))
missing=[]
for day in sorted({x['local'][:10] for x in records}):
 hours={datetime.fromisoformat(x['local']).hour for x in records if x['local'][:10]==day}
 missing.extend(f'{day}T{h:02}:00(local hour)' for h in range(24) if h not in hours)
night=[x for x in records if datetime.fromisoformat(x['local']).hour>=22]
result=dict(raw_rows=len(allrows),raw_first=min(x['DATE'] for x in allrows),raw_last=max(x['DATE'] for x in allrows),
             local_timezone='UTC-7; Arizona no DST',sample='All FM-15 quality-passed July 2025 Sundays; no interpolation',
             observations=len(records),expected_hour_bins=96,missing_hour_bins=missing,
             closed_22_to_24_observations=night,
             comparison=summary,
             counterexample=dict(hourly_point_coverage_equal=True,one_site_70min_start_minutes=531,
                                 two_sites_70min_start_minutes=462,minute_grid='12:00 through 21:59 inclusive',
                                 note='Constructed schedule, not observed city network; rest interrupted by any outdoor transfer'),
             interpretation='Arrival opportunity conditional on site reachability and admission. Thresholds are descriptive, not clinical. No occupancy, paths, visits or health effects estimated.')
(ROOT/'pilot-results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False))
print(json.dumps(result,indent=2,ensure_ascii=False))
