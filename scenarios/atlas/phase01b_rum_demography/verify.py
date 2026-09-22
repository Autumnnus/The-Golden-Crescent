"""Read-only acceptance of the bounded demographic/institution preview; not engine validation."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def read(path):
    return json.loads(path.read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify():
    src = read(HERE/'scenario.json')
    parent = read(HERE.parent/'phase01_rum/geography.json')
    plan = read(HERE/'population-plan.json')
    old = read(ROOT/'build/phase01/report.json')
    now = read(ROOT/'build/phase01b/report.json')
    compiled = read(ROOT/'build/phase01b/generated/scenario-report.json')
    assert now == {k:v for k,v in compiled.items() if k not in {'files','output'}}
    assert now['validation']=='passed' and now['runtime_tested'] is False
    assert now['target_mod']==str(ROOT)
    assert now['warnings']==old['warnings']
    assert now['diplomacy']==old['diplomacy']
    assert {k:v for k,v in src.items() if k not in {'title','description','countries','states'}} == {k:v for k,v in parent.items() if k not in {'title','description','countries','states'}}
    assert {k:v for k,v in src['countries'].items() if k!='RUM'} == {k:v for k,v in parent['countries'].items() if k!='RUM'}
    regions = {r['state']:r for r in plan['regions']}
    assert len(regions)==25 and sum(r['population'] for r in regions.values())==27000000
    assert set(now['countries'])==set(old['countries'])
    for tag, data in old['countries'].items():
        if tag!='RUM':
            assert now['countries'][tag]==data, tag
    assert set(src['states'])==set(parent['states'])
    for sid, st in src['states'].items():
        assert {k:v for k,v in st.items() if k!='population'}==parent['states'][sid], sid
        if sid in regions:
            p=regions[sid]
            assert st['population']=={'by_owner':{'RUM':{'total':p['population'],'literacy':p['literacy']}}}
    for sid, st in old['states'].items():
        current=now['states'][sid]
        assert set(st['owners'])==set(current['owners'])
        for tag, owner in st['owners'].items():
            new=current['owners'][tag]
            if tag!='RUM':
                assert new==owner, (sid,tag)
                continue
            p=regions[sid]
            assert new['population']==p['population']
            assert new['settings']['literacy']==p['literacy']
            assert new['buildings']==owner['buildings']
            for field in ('cultures','religions'):
                assert set(new[field])==set(owner[field])
                assert sum(new[field].values())==p['population']
                # Marginals may aggregate several rounded joint cohorts. Check bounded drift.
                for key, count in owner[field].items():
                    expected=count*p['population']/owner['population']
                    assert abs(new[field][key]-expected)<20, (sid,field,key)
    rum=now['countries']['RUM']; spec=src['countries']['RUM']
    assert rum['population']==27000000
    assert rum['military']==old['countries']['RUM']['military']
    assert rum['building_levels']==old['countries']['RUM']['building_levels']
    assert set(rum['laws'])==set(spec['laws']['values']) and len(rum['laws'])==24
    assert rum['settings']['institutions']==spec['institutions']
    literacy=sum(r['population']*r['literacy'] for r in regions.values())/27000000
    assert .38<=literacy<=.44
    assert not (ROOT/'world/scenario.yml').exists()
    return {'status':'passed','scope':'RUM population/literacy inputs and 24 law/3 institution mapping',
            'scenario_sha256':sha(HERE/'scenario.json'),'parent_sha256':sha(HERE.parent/'phase01_rum/geography.json'),
            'report_sha256':sha(ROOT/'build/phase01b/report.json'), 'population':27000000,
            'regions':25,'weighted_literacy_input':literacy,'unchanged_other_countries':len(now['countries'])-1,
            'additional_warnings':[],'runtime_tested':False,'playable_release':False,
            'composition_check':'marginal proportional drift only; joint cohort generation not independently audited in this subphase',
            'pending':['1811 emancipation and slave-status cleanup','regional final culture/religion design','industry and bureaucracy funding','final technology and military','IG government','other regional countries','hubs and legacy events']}

if __name__=='__main__':
    print(json.dumps(verify(),ensure_ascii=False,indent=2))
