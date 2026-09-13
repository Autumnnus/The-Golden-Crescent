"""Read-only phase acceptance against fresh Atlas artifacts. Run from mod root."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent

def read(p):
    return json.loads(p.read_text())

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def verify():
    src = read(HERE / 'geography.json')
    evidence = read(HERE / 'source-evidence.json')
    report = read(ROOT / 'build/phase01/report.json')
    baseline = read(ROOT / 'build/phase01/baseline-report.json')
    atlas = read(ROOT / 'build/phase01/full-map.json')
    assert evidence['scenario_sha256'] == sha(HERE / 'geography.json'), 'Stale evidence'
    assert report['target_mod'] == str(ROOT)
    assert report['validation'] == 'passed' and not report['runtime_tested']
    compiled = read(ROOT / 'build/phase01/generated/scenario-report.json')
    assert report == {k:v for k,v in compiled.items() if k not in {'files','output'}}
    states = {s['id']: s for s in atlas['states']}
    actual_changed = {s['id'] for s in atlas['states'] if s['changed']}
    assert actual_changed == set(src['states']), 'Unexpected changed state scope'
    owner_map = {}
    for sid, st in states.items():
        for o in st['owners']:
            for p in o['provinces']:
                if sid in src['states']:
                    assert (sid,p) not in owner_map, ('Duplicate',sid,p)
                owner_map[sid,p] = o['tag']
    def totals(st, field):
        counts = Counter()
        for o in st['owners'].values():
            counts.update(o[field])
        return counts
    for sid in src['states']:
        original = evidence['states'][sid]
        expected = set(original['provinces']) - set(original['impassable'])
        assert {p for s,p in owner_map if s==sid} == expected, ('Coverage',sid)
        now, old = report['states'][sid], baseline['states'][sid]
        assert now['population'] == old['population'], ('Population loss',sid)
        for field in ['cultures','religions']:
            assert totals(now,field) == totals(old,field), (field,sid)
        levels = lambda st: sum(b['level'] for o in st['owners'].values() for b in o['buildings'])
        assert levels(now) == levels(old), ('Building loss',sid)
    for sid, hubs in evidence['hub_owner_expectations'].items():
        for hub, owner in hubs.items():
            province = evidence['states'][sid]['hubs'][hub]
            assert owner_map[sid,province] == owner, (sid,hub)
    landed = set(owner_map.values())
    assert not landed.intersection(evidence['must_be_landless'])
    overlords = report['diplomacy']['overlords']
    assert {t for t,o in overlords.items() if o=='RUM'} == set(evidence['required_subjects'])
    assert not set(evidence['must_be_independent']).intersection(overlords)
    for t, c in src['countries'].items():
        assert any(s==c['capital'] and o==t for (s,p),o in owner_map.items()), ('Capital',t)
    assert report['countries']['BAS'] == baseline['countries']['BAS'], 'Bastar modified'
    added = set(report['warnings']) - set(baseline['warnings'])
    expected = {'EGY: removed inherited army unit in lost state '+s for s in ['STATE_SYRIA','STATE_ALEPPO','STATE_LEBANON','STATE_PALESTINE']}
    assert added == expected, ('New warnings',added)
    assert not (ROOT/'world/scenario.yml').exists()
    return {'status':'passed','scope':'geography_and_transfer_only','runtime_tested':False,
            'scenario_sha256':sha(HERE/'geography.json'),'report_sha256':sha(ROOT/'build/phase01/report.json'),
            'changed_states':len(actual_changed),'country_definitions':len(src['countries']),
            'rum_dependencies':len(evidence['required_subjects']),
            'population_culture_religion_and_building_totals_preserved':True,
            'hub_ownership_checks':sum(map(len,evidence['hub_owner_expectations'].values())),
            'baseline_warnings':len(baseline['warnings']),'additional_warnings':sorted(added),
            'playable_release':False,'active_world_modified':False,
            'next_phase':'1B: demography/economy/laws/military/hubs/legacy content audit'}

if __name__ == '__main__':
    print(json.dumps(verify(),indent=2,ensure_ascii=False))
