"""LLM-first compile/validate/report pipeline for complete version 2 scenarios."""
from collections import defaultdict
import copy
import json
from pathlib import Path

from . import development as dev, history, mechanics, pdx, scenario
from .build import Resolved
from .world import World, WorldError, load_world
from . import index as idx
from .paths import BUILD, MOD, assert_read_only


def group_value(group,key,data,seen=None):
    seen=set() if seen is None else seen
    if not group or group in seen or group not in data['building_groups']:return None
    seen.add(group);node=pdx.parse(data['building_groups'][group]['script'])
    return node.get_str(key) or group_value(node.get_str('parent_group'),key,data,seen)


def report_economy(res,data,techs,lawsets,warnings):
    countries=defaultdict(lambda:{'population':0,'building_levels':0,'cultures':defaultdict(int),'religions':defaultdict(int)})
    states={}
    for name,by_tag in res.state_pops.items():
        state={'population':0,'owners':{}}
        world_state=res.world.states.get(name);raw=res.index['states'][name]
        totals=defaultdict(int);rural_total=0
        for tag,rows in by_tag.items():
            record={'population':sum(p['size'] for p in rows),'cultures':defaultdict(int),'religions':defaultdict(int),'buildings':[],
                    'settings':getattr(res,'population_settings',{}).get((name,tag),{})}
            state['population']+=record['population'];countries[tag]['population']+=record['population'];jobs=0;infra=0
            for row in rows:
                religion=row.get('religion') or data['cultures'].get(row['culture'],{}).get('religion') or 'unknown'
                record['cultures'][row['culture']]+=row['size'];record['religions'][religion]+=row['size']
                countries[tag]['cultures'][row['culture']]+=row['size'];countries[tag]['religions'][religion]+=row['size']
            c=res.world.countries.get(tag)
            touched=bool((world_state and (world_state.industry or (not world_state.ownership_inherit and tag not in {o['country'] for o in res.index['state_history'].get(name,{}).get('owners',[])}))) or (c and (c.industry or c.technology or c.laws or c.history_mode=='replace')))
            for node in dev.building_records(res.state_buildings.get(name,{}).get(tag,'')):
                building=node.get_str('building');level=dev.level(node);pms=node.get_list('activate_production_methods')
                totals[building]+=level;countries[tag]['building_levels']+=level
                definition=data['buildings'].get(building)
                record['buildings'].append({'type':building,'level':level,'production_methods':pms})
                if not definition:continue
                if group_value(definition.get('building_group'),'land_usage',data)=='rural':rural_total+=level
                infra+=float(group_value(definition.get('building_group'),'infrastructure_usage_per_level',data) or 0)*level
                if touched:
                    missing=set(definition['unlocking_technologies'])-techs[tag]
                    if missing:raise WorldError(f'{name}/{tag}: {building} needs {sorted(missing)}')
                    if (definition.get('naval')=='yes' or definition.get('port')=='yes') and raw.get('naval_exit_id') is None:raise WorldError(f'{name}: {building} requires coastal access')
                for pm in pms:
                    definition_pm=data['production_methods'].get(pm)
                    if not definition_pm:continue
                    if touched:
                        missing=set(definition_pm['unlocking_technologies'])-techs[tag]
                        if missing:raise WorldError(f'{name}/{tag}: {pm} needs {sorted(missing)}')
                        conflict=set(definition_pm['disallowing_laws'])&set(lawsets[tag].values())
                        if conflict:raise WorldError(f'{name}/{tag}: {pm} conflicts with {sorted(conflict)}')
                    bm=pdx.parse(definition_pm['script']).get_node('building_modifiers')
                    scaled=bm.get_node('level_scaled') if bm else None
                    if scaled:
                        jobs+=level*sum(float(it.value) for it in scaled.items if (it.key or '').startswith('building_employment_') and (it.key or '').endswith('_add') and isinstance(it.value,str))
            record['estimated_jobs']=max(0,round(jobs));record['infrastructure_demand_base']=round(infra,2)
            if touched and jobs>record['population']*.3:warnings.append(f'{name}/{tag}: {round(jobs)} estimated jobs exceed a 30% workforce screening threshold; inspect labor and qualifications')
            state['owners'][tag]=record
        # Resource and arable limits are shared by every country in a split state.
        touched=bool((world_state and world_state.industry) or any(res.world.countries.get(t) and res.world.countries[t].industry for t in by_tag))
        if touched:
            for building,level in totals.items():
                definition=data['buildings'].get(building,{})
                group=definition.get('building_group')
                if group_value(group,'land_usage',data)=='rural' and building not in raw.get('arable_resources',[]):raise WorldError(f'{name}: {building} is not an allowed arable resource')
                if group_value(group,'capped_by_resources',data)=='yes' and building not in raw.get('capped_resources',{}) and not any(r.get('type')==building for r in raw.get('resources',[])):raise WorldError(f'{name}: no resource deposit for {building}')
                discovered=[r.get('discovered_amount') or 0 for r in raw.get('resources',[]) if r.get('type')==building]
                if discovered and level>sum(discovered):raise WorldError(f'{name}: {building} level {level} exceeds discovered resource capacity {sum(discovered)}')
                if building in raw.get('capped_resources',{}) and level>raw['capped_resources'][building]:raise WorldError(f'{name}: {building} level {level} exceeds shared resource cap {raw["capped_resources"][building]}')
            if rural_total>(raw.get('arable_land') or 0):raise WorldError(f'{name}: {rural_total} agricultural levels exceed {raw.get("arable_land")} arable land')
        state['arable_land']=raw.get('arable_land');state['resource_caps']=raw.get('capped_resources',{})
        states[name]=state
    return dict(countries),states


def compile_world(world,index=None):
    """Return validated source text and report without a filesystem mutation."""
    index=index or idx.load();scenario.validate_world(world,index)
    if world.region_patches:raise WorldError('Version 2 compilation does not emit state_regions patches; remove unapplied patches from the scenario source')
    if world.diplomacy:raise WorldError('Move legacy world/diplomacy entries into the version 2 diplomacy object before compiling')
    res=Resolved(world,index);data=mechanics.catalog();warnings=[]
    for tag in res.landed_tags:
        if not res.countries[tag].get('cultures'):raise WorldError(f'{tag}: a landed country requires at least one primary culture')
    definitions,actions,custom_types,custom_actions,localization=history.custom_subjects(world,data)
    country_text,modifiers,techs,laws,country_start=history.compile_countries(res,data)
    military_text,military=history.compile_military(res,data,techs,warnings)
    diplomacy_text,diplomacy=history.compile_diplomacy(res,data,definitions,actions,warnings)
    # Reuse crash-prevention checks; compare with vanilla to avoid false failures.
    from . import check
    rep=check.Report();base=check.Report()
    checked_index=copy.copy(index);checked_index['country_history']={}
    check._world_rules(rep,res,checked_index)
    vanilla=Resolved(World(),index);check._world_rules(base,vanilla,checked_index);rep.subtract(base)
    if rep.errors:raise WorldError('\n'.join(f'{rule}: {message}' for rule,message in rep.errors))
    warnings.extend(message for _,message in rep.warnings)
    # Check actual emitted capital setters, not superseded vanilla history files.
    for tag,node in history_nodes(country_text).items():
        for field in ('set_capital','set_market_capital'):
            value=node.get_str(field)
            if value and value.startswith('s:') and not history.owns(res,tag,value[2:]):raise WorldError(f'{tag}: emitted {field} {value} is not owned')
    countries,states=report_economy(res,data,techs,laws,warnings)
    baseline_pops=defaultdict(int);baseline_levels=defaultdict(int)
    for owners in vanilla.state_pops.values():
        for tag,rows in owners.items():baseline_pops[tag]+=sum(p['size'] for p in rows)
    for owners in vanilla.state_buildings.values():
        for tag,script in owners.items():baseline_levels[tag]+=sum(dev.level(n) for n in dev.building_records(script))
    for tag,record in countries.items():
        record.update(country_start.get(tag,{}));record['military']=military.get(tag,{})
        record['overlord']=diplomacy['overlords'].get(tag)
        record['baseline_population']=baseline_pops[tag]
        record['baseline_building_levels']=baseline_levels[tag]
    files={
        'common/history/countries/ve_scenario_countries.txt':country_text,
        'common/history/population/ve_scenario_population.txt':history.compile_population(res),
        'common/history/military_formations/ve_scenario_military.txt':military_text,
        'common/history/diplomacy/ve_scenario_diplomacy.txt':diplomacy_text,
    }
    if modifiers:files['common/static_modifiers/ve_scenario_igs.txt']=modifiers
    if custom_types:files['common/subject_types/ve_scenario_subjects.txt']=custom_types
    if custom_actions:files['common/diplomatic_actions/ve_scenario_subjects.txt']=custom_actions
    for lang,col in [('english',1),('turkish',2)]:
        if localization:files[f'localization/{lang}/tgc_generated_subjects_l_{lang}.yml']='l_'+lang+':\n'+'\n'.join(f' {r[0]}:0 {history.q(r[col])}' for r in localization)+'\n'
    for name,text in files.items():
        if name.endswith('.txt'):pdx.parse(text)
    report={'version':2,'validation':'passed','validation_scope':'static_source','runtime_tested':False,
            'countries':countries,'states':states,'diplomacy':diplomacy,
            'warnings':list(dict.fromkeys(warnings)),
            'limits':['Literacy and wealth are setup inputs, not guaranteed January 1 values: the installed starting_pop scripted effects explicitly warn that setup recalculates them.',
                      'Population counts and configured ratios are deterministic; GDP, migration, employment, exact IG clout and equilibrium prices require game simulation.',
                      'Infrastructure demand excludes throughput, terrain and technology modifiers; job counts are a screening estimate, not hiring predictions.',
                      'Company possible/attainable and diplomatic action triggers can depend on runtime/DLC conditions; their full source is available through rules.',
                      'Character history, journal entries, on_actions and events are not regenerated or fully validated; scenario changes can invalidate their saved scopes and country assumptions, including during setup.']}
    return res,files,report


def history_nodes(text):
    return {k[2:]:v for k,v in pdx.parse(text).get_node('COUNTRIES').pairs() if k.startswith('c:')}


def run(path, action='validate', out=None, country=None):
    document=scenario.load(path);world=scenario.overlay(load_world(),document)
    res,files,report=compile_world(world)
    report['title']=document.get('title','Scenario')
    if country:
        if country not in report['countries']:raise WorldError(f'{country}: no landed country in report')
        report['countries']={country:report['countries'][country]}
        report['states']={s:v for s,v in report['states'].items() if country in v['owners']}
    if action=='build':
        if not out:out=BUILD/'scenarios'/'preview'
        output=Path(out).resolve();assert_read_only(output)
        if output==MOD or MOD in output.parents and BUILD not in output.parents:
            raise WorldError('scenario build writes a preview bundle under build/ or an external directory; use world/scenario.yml + build for the active mod')
        from . import build
        result=build.build(world_override=world,output_root=output,compiled=(res,files,report),verbose=False)
        report['output']=str(output);report['files']=result['written']
        output_report=output/'scenario-report.json'
    else:output_report=Path(out) if out else None
    payload=json.dumps(report,ensure_ascii=False,indent=2)
    if output_report:
        from .atlas import write_output
        write_output(output_report,payload)
        print(f'{action}: passed; wrote {output_report}')
    elif action=='report':print(payload)
    else:print(f'validation: passed · {len(report["states"])} states · {len(report["countries"])} countries · {len(report["warnings"])} notes')
    return 0
