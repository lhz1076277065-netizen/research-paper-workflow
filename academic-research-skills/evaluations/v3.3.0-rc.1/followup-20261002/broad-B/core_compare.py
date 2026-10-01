"""Counterexample to hourly coverage as a proxy for continuous-stay opportunities.
All weights/schedules in the counterexample are synthetic. No health effect is estimated.
Run: python core_compare.py (stdlib only).
"""
from pathlib import Path
import json

def opportunity_hours(intervals, stay, travel=0, horizon=(12,18)):
    assert stay >= 0 and travel >= 0 and horizon[0] <= horizon[1]
    # Intervals belong to one site: touching intervals permit a continuous stay.
    merged=[]
    for start,end in sorted(intervals):
        assert start <= end
        if merged and start <= merged[-1][1]:
            merged[-1][1]=max(merged[-1][1],end)
        else: merged.append([start,end])
    return sum(max(0,min(end-travel-stay,horizon[1])-max(start-travel,horizon[0])) for start,end in merged)

def demo():
    weights={'A':1000,'B':600}
    baseline={'A':[(8,12)],'B':[(13,15)]}
    choices={'extend_A':{'A':[(8,13)],'B':[(13,15)]},'extend_B':{'A':[(8,12)],'B':[(12,15)]}}
    results=[]
    for travel in [0,10/60,15/60]:
        for name,schedule in choices.items():
            gain=lambda stay:sum(weights[k]*(opportunity_hours(schedule[k],stay,travel)-opportunity_hours(baseline[k],stay,travel)) for k in weights)
            results.append({'choice':name,'travel_minutes':travel*60,'incremental_person_start_hours_L0':gain(0),'incremental_person_start_hours_L2':gain(2)})
    assert results[0]['incremental_person_start_hours_L0']==1000
    assert results[1]['incremental_person_start_hours_L0']==600
    assert results[0]['incremental_person_start_hours_L2']==0
    assert results[1]['incremental_person_start_hours_L2']==600
    for row in results:
        if row['choice']=='extend_A': assert row['incremental_person_start_hours_L2']==0
        else: assert row['incremental_person_start_hours_L2']>0
    assert opportunity_hours([(12,13),(13,15)],2)==1
    assert opportunity_hours([(12,13),(14,15)],2)==0
    assert opportunity_hours([(12,14)],2)==0 # One exactly timed start has zero measure.
    announced={'open_hours_per_center_day':12,'travel_minutes_assumed':10,'stay_hours_scenario':2,'departure_horizon':[12,24],'latest_departure_hour':24-2-10/60,'feasible_departure_hours':opportunity_hours([(12,24)],2,10/60,(12,24)),'interpretation':'announced schedule opportunity; no observed attendance or physiology'}
    output={'counterexample':'synthetic; one added center-hour in either choice; uniformly weighted departure times, not observed demand','results':results,'representative_schedule_calculation':announced,'checks':'passed'}
    Path(__file__).with_name('core-results.json').write_text(json.dumps(output,indent=2))
    print(json.dumps(output,indent=2))
if __name__=='__main__': demo()
