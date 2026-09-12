"""Compile editable startup mechanics by filtering real vanilla ASTs.

References: common/history/{countries,population,military_formations,diplomacy},
scripted_effects/00_starting_*.txt, diplomatic_actions/23_subject_vassal.txt.
Every emitted history layer is COMPLETE and requires replace_paths for that layer.
"""
from collections import defaultdict
from functools import lru_cache
import copy
import re
from . import pdx, mechanics, development as dev
from .paths import VANILLA, MOD
from .world import WorldError


def parse(text): return pdx.parse(text)
def add(node, text): node.items.extend(parse(text).items)
def set_value(node,key,value):
    node.items=[i for i in node.items if i.key!=key];add(node,f'{key} = {value}')
def q(text):
    return '"'+str(text).replace('\\','\\\\').replace('"','\\"').replace('\n',' ')+'"'


def filter_tree(node, drop):
    kept=[]
    for item in node.items:
        if drop(item):continue
        if isinstance(item.value,pdx.Node):filter_tree(item.value,drop)
        kept.append(item)
    node.items=kept


@lru_cache(maxsize=None)
def source_layer(sub):
    result=pdx.Node()
    files={}
    for root in (VANILLA,MOD):
        for file in sorted((root/'common/history'/sub).glob('*.txt')):
            if root==MOD and file.name.startswith(('ve_scenario','tgc_')):continue
            files[file.name]=file
    for file in files.values():
        tree=pdx.parse_file(file)
        expected={'countries':'COUNTRIES','population':'POPULATION','military_formations':'MILITARY_FORMATIONS','diplomacy':'DIPLOMACY'}[sub]
        for root,block in tree.pairs():
            if root != expected or not isinstance(block,pdx.Node):raise WorldError(f'{file}: unsupported history root {root}; refusing to discard it')
            for item in block.items:
                if not (item.key or '').startswith('c:') or not isinstance(item.value,pdx.Node):raise WorldError(f'{file}: unsupported global history entry {item.key}; refusing to discard it')
            result.items.extend(block.items)
    return result


def country_nodes(sub):
    result={}
    for it in copy.deepcopy(source_layer(sub)).items:
        if it.key and it.key.startswith('c:') and isinstance(it.value,pdx.Node):
            result.setdefault(it.key[2:],pdx.Node()).items.extend(it.value.items)
    return result


def wrap(root, countries):
    node=pdx.Node([pdx.Item('c:'+tag,'?=',body) for tag,body in sorted(countries.items())])
    return root+' = {\n'+pdx.dumps(node)+'\n}'


def effective_tech(c, base, data):
    plan=c.technology if c else {}
    dev.obj(plan,{'mode','tier','add','remove','prerequisites'},'technology')
    mode=plan.get('mode','replace' if c and c.tech_tier is not None else 'merge')
    if mode not in ('merge','replace'):raise WorldError('technology.mode: merge or replace required')
    current=mechanics.technology_set(base,data) if mode=='merge' else set()
    tier=plan.get('tier',c.tech_tier if c else None)
    if tier is not None:
        dev.number(tier,'technology.tier',1,7,True)
        key=f'effect_starting_technology_tier_{tier}_tech'
        dev.known(key,'technology_tiers',data,'technology.tier')
        current.update(mechanics.technology_set(parse(data['technology_tiers'][key]['script']),data))
    for key in ('add','remove'):
        if not isinstance(plan.get(key,[]),list):raise WorldError('technology.'+key+': expected list')
        for name in plan.get(key,[]):dev.known(name,'technologies',data,'technology')
    current.update(plan.get('add',[]));current.difference_update(plan.get('remove',[]))
    if plan.get('prerequisites','add') not in ('add','error'):raise WorldError('technology.prerequisites: add or error required')
    closure=mechanics.prerequisites(current,data)
    if closure.intersection(plan.get('remove',[])):raise WorldError('Removed technology is still required by a selected technology')
    if plan.get('prerequisites')=='error' and closure-current:raise WorldError(f'Missing technology prerequisites: {sorted(closure-current)}')
    return closure


def effective_laws(c,base,data):
    plan=c.laws if c else {};dev.obj(plan,{'mode','values'},'laws')
    mode=plan.get('mode','merge')
    if mode not in ('merge','replace'):raise WorldError('laws.mode: merge or replace required')
    laws={}
    if mode=='merge':
        for val in base.getall('activate_law'):
            name=str(val).removeprefix('law_type:')
            if name in data['laws']:laws[data['laws'][name].get('group')]=name
    seen=set()
    if not isinstance(plan.get('values',[]),list):raise WorldError('laws.values: expected list')
    for law in plan.get('values',[]):
        dev.known(law,'laws',data,'laws');group=data['laws'][law].get('group')
        if group in seen:raise WorldError(f'Two selected laws in {group}')
        seen.add(group);laws[group]=law
    return laws


def validate_country(tag,c,res,data,tech,laws):
    if c.history_mode not in ('inherit','replace'):raise WorldError(f'{tag}: history_mode must be inherit or replace')
    for law in (laws.values() if c.technology or c.tech_tier is not None else c.laws.get('values',[])):
        missing=set(data['laws'][law]['unlocking_technologies'])-tech
        if missing:raise WorldError(f'{tag}: {law} needs technologies {sorted(missing)}')
        conflicts=set(data['laws'][law]['disallowing_laws']) & set(laws.values())
        # Check both directions: some older laws disallow the new one instead.
        conflicts |= {other for other in laws.values() if law in data['laws'][other]['disallowing_laws']}
        if conflicts:raise WorldError(f'{tag}: {law} conflicts with {sorted(conflicts)}')
    if not isinstance(c.institutions,dict):raise WorldError(f'{tag}.institutions: expected mapping')
    for name,value in c.institutions.items():
        dev.known(name,'institutions',data,tag);dev.number(value,tag+'.'+name,0,5,True)
        if value and not any(data['laws'][law].get('institution')==name for law in laws.values()):
            raise WorldError(f'{tag}: {name} has no enabling selected/starting law')
    dev.obj(c.interest_groups,{'mode','ruling','strength'},tag+'.interest_groups')
    if c.interest_groups.get('mode','merge') not in ('replace','merge'):raise WorldError('interest_groups.mode: merge or replace required')
    if not isinstance(c.interest_groups.get('ruling',[]),list) or not isinstance(c.interest_groups.get('strength',{}),dict):raise WorldError(f'{tag}: ruling must be a list and strength a mapping')
    for ig in c.interest_groups.get('ruling',[]):dev.known(ig,'interest_groups',data,tag)
    for ig,value in c.interest_groups.get('strength',{}).items():
        dev.known(ig,'interest_groups',data,tag);dev.number(value,tag+'.strength',-1,10)
    dev.obj(c.companies,{'mode','add','remove'},tag+'.companies')
    if c.companies.get('mode','merge') not in ('replace','merge'):raise WorldError('companies.mode: merge or replace required')
    if any(not isinstance(c.companies.get(k,[]),list) for k in ('add','remove')):raise WorldError(f'{tag}: companies.add/remove must be lists')
    for company in c.companies.get('remove',[]):dev.known(company,'companies',data,tag)
    seen=set()
    for company in c.companies.get('add',[]):
        dev.obj(company,{'type','headquarters'},tag+'.companies.add')
        name=company.get('type');dev.known(name,'companies',data,tag)
        if name in seen:raise WorldError(f'{tag}: duplicate company {name}')
        seen.add(name);state=state_id(company.get('headquarters'))
        if not owns(res,tag,state):raise WorldError(f'{tag}: company headquarters {state} is not owned')
        eligible=set(data['companies'][name]['building_types'])
        present={n.get_str('building') for n in dev.building_records(res.state_buildings.get(state,{}).get(tag,'')) if dev.level(n)>0}
        if eligible and not eligible & present:raise WorldError(f'{tag}: {name} headquarters {state} has no eligible company building; expected {sorted(eligible)}')


def state_id(name):
    if not isinstance(name,str):raise WorldError('State id must be a string')
    return name if name.startswith('STATE_') else 'STATE_'+name.upper()

def owns(res,tag,state):return any(t==tag for t,_,_ in res.state_owners.get(state,[]))


def compile_countries(res,data):
    source=country_nodes('countries');out={};techs={};lawsets={};modifiers=[];summary={}
    for tag in sorted(res.landed_tags):
        c=res.world.countries.get(tag);original=source.get(tag,pdx.Node())
        base=pdx.Node() if c and c.history_mode=='replace' else copy.deepcopy(original)
        tech=effective_tech(c,base,data);laws=effective_laws(c,base,data)
        techs[tag]=tech;lawsets[tag]=laws
        if c:
            validate_country(tag,c,res,data,tech,laws)
            if c.technology or c.tech_tier is not None:
                filter_tree(base,lambda i:i.key in ('add_technology_researched','add_era_researched') or (i.key or '').startswith('effect_starting_technology_tier_'))
                grants=parse('\n'.join(f'add_technology_researched = {name}' for name in mechanics.technology_order(tech,data)))
                base.items=grants.items+base.items
            if c.laws:
                filter_tree(base,lambda i:i.key=='activate_law' or (i.key or '').startswith('active_law:'))
                # Institutions and other inherited effects must see the new laws.
                is_tech=lambda i:i.key in ('add_technology_researched','add_era_researched') or (i.key or '').startswith('effect_starting_technology_tier_')
                law_items=parse('\n'.join(f'activate_law = law_type:{name}' for name in laws.values())).items
                base.items=[i for i in base.items if is_tech(i)]+law_items+[i for i in base.items if not is_tech(i)]
            if c.institutions:
                filter_tree(base,lambda i:i.key=='set_institution_investment_level' and isinstance(i.value,pdx.Node) and i.value.get_str('institution') in c.institutions)
                for name,value in c.institutions.items():add(base,f'set_institution_investment_level = {{ institution = {name} level = {value} }}')
            if c.interest_groups:
                if c.interest_groups.get('mode')=='replace':
                    filter_tree(base,lambda i:i.key=='add_ruling_interest_group')
                    add(base,'every_interest_group = { remove_ruling_interest_group = yes }')
                for ig in c.interest_groups.get('ruling',[]):add(base,f'ig:{ig} ?= {{ add_ruling_interest_group = yes }}')
                strength=c.interest_groups.get('strength',{})
                if strength:
                    key=f've_scenario_ig_{tag.lower()}'
                    modifiers.append(key+' = {\n'+'\n'.join(f'interest_group_{ig}_pol_str_mult = {v}' for ig,v in strength.items())+'\n}')
                    add(base,f'add_modifier = {{ name = {key} }}')
            if c.companies:
                remove=set(c.companies.get('remove',[]))|{v['type'] for v in c.companies.get('add',[])}
                replace=c.companies.get('mode')=='replace'
                filter_tree(base,lambda i:(i.key=='add_company' and (replace or str(i.value).removeprefix('company_type:') in remove)) or ((i.key or '').startswith('company:') and (replace or i.key[8:] in remove)))
                for item in c.companies.get('add',[]):
                    name=item['type'];add(base,f'add_company = company_type:{name}\ncompany:{name} = {{ set_company_state_region = s:{state_id(item["headquarters"])} }}')
            if c.capital:
                filter_tree(base,lambda i:i.key=='set_capital');add(base,f'set_capital = s:{c.capital}')
            if c.market_capital:
                if not owns(res,tag,c.market_capital):raise WorldError(f'{tag}: market capital is not owned')
                filter_tree(base,lambda i:i.key=='set_market_capital');add(base,f'set_market_capital = s:{c.market_capital}')
        validate_emitted_country(tag, c, base, res, data, laws)
        # No fabricated absolute clout: report the chosen multiplier, not a prediction.
        summary[tag]={'technologies':sorted(tech),'laws':list(laws.values()),'settings':{
            'institutions':c.institutions,'interest_groups':c.interest_groups,'companies':c.companies,'history_mode':c.history_mode} if c else {}}
        out[tag]=base
    return wrap('COUNTRIES',out), '\n'.join(modifiers),techs,lawsets,summary



def validate_emitted_country(tag, c, node, res, data, laws):
    """Audit inherited setters too; changing a map can invalidate their scopes."""
    for item in node.items:
        if (item.key or '').startswith('company:') and isinstance(item.value,pdx.Node):
            hq=item.value.get_str('set_company_state_region')
            if hq and hq.startswith('s:') and not owns(res,tag,hq[2:]):
                raise WorldError(f'{tag}: inherited company {item.key} headquarters {hq} is no longer owned; remove or relocate the company')
        if c and c.laws and item.key=='set_institution_investment_level' and isinstance(item.value,pdx.Node):
            name=item.value.get_str('institution');value=item.value.get_int('level',0)
            if value and not any(data['laws'][law].get('institution')==name for law in laws.values()):
                raise WorldError(f'{tag}: inherited {name} level {value} has no enabling law; set institution level 0 or choose an enabling law')


def compile_population(res):
    countries=country_nodes('population')
    countries={t:n for t,n in countries.items() if t in res.landed_tags}
    # Country baseline initializers run first; exact state/share settings run afterwards.
    node=pdx.Node([pdx.Item('c:'+t,'?=',n) for t,n in sorted(countries.items())])
    for (state,tag),settings in sorted(getattr(res,'population_settings',{}).items()):
        effects=[]
        if 'literacy' in settings:effects.append(f'set_pop_literacy = {{ literacy_rate = {settings["literacy"]} }}')
        if 'wealth' in settings:effects.append(f'set_pop_wealth = {{ wealth_distribution = {settings["wealth"]} update_loyalties = no }}')
        add(node,f's:{state} = {{ region_state:{tag} = {{ every_scope_pop = {{ {" ".join(effects)} }} }} }}')
    return 'POPULATION = {\n'+pdx.dumps(node)+'\n}'


def compile_military(res,data,techs,warnings):
    nodes=country_nodes('military_formations');out={};summary={}
    for tag in sorted(res.landed_tags):
        c=res.world.countries.get(tag);plan=c.military if c else {}
        dev.obj(plan,{'mode','formations'},tag+'.military')
        if plan.get('mode','merge') not in ('replace','merge'):raise WorldError('military.mode: merge or replace required')
        node=copy.deepcopy(nodes.get(tag,pdx.Node())) if plan.get('mode','merge')=='merge' else pdx.Node()
        def orphan(it):
            if it.key in ('combat_unit','ship') and isinstance(it.value,pdx.Node):
                s=it.value.get_str('state_region','').removeprefix('s:')
                if s and not owns(res,tag,s):warnings.append(f'{tag}: removed inherited army unit in lost state {s}');return True
            return False
        filter_tree(node,orphan)
        if not isinstance(plan.get('formations',[]),list):raise WorldError(f'{tag}: formations must be a list')
        for i,form in enumerate(plan.get('formations',[])):
            dev.obj(form,{'name','type','hq_region','units','ships'},tag+'.formation')
            kind=form.get('type');hq=form.get('hq_region')
            if kind not in ('army','fleet'):raise WorldError(f'{tag}: formation type must be army or fleet')
            dev.known(hq,'strategic_regions',data,tag)
            if not any(owns(res,tag,s) for s in data['strategic_regions'][hq]['states']):raise WorldError(f'{tag}: headquarters {hq} has no owned state')
            if data['country_types'][res.country_type(tag)].get('has_military')=='no':raise WorldError(f'{tag}: country type has no military')
            if kind=='army' and form.get('ships') or kind=='fleet' and form.get('units'):raise WorldError(f'{tag}: army uses units; fleet uses ships')
            body=parse(f'type = {kind}\nhq_region = sr:{hq}\nname = {q(form.get("name",f"ve_{tag}_{i}"))}')
            rows=form.get('units' if kind=='army' else 'ships',[])
            if not isinstance(rows,list) or not rows:raise WorldError(f'{tag}: empty formation')
            for unit in rows:
                dev.obj(unit,{'type','state','count'},tag+'.unit')
                table='combat_units' if kind=='army' else 'ships';name=unit.get('type')
                dev.known(name,table,data,tag);dev.number(unit.get('count'),tag+'.count',1,10000,True)
                missing=set(data[table][name]['unlocking_technologies'])-techs[tag]
                if missing:raise WorldError(f'{tag}: {name} needs technologies {sorted(missing)}')
                state=state_id(unit['state']) if 'state' in unit else None
                if kind=='army' and not state:raise WorldError(f'{tag}: army unit requires a state')
                if state and not owns(res,tag,state):raise WorldError(f'{tag}: unit state {state} is not owned')
                if kind=='fleet':
                    coastal=[s for s,owners in res.state_owners.items() if any(t==tag for t,_,_ in owners) and res.index['states'][s].get('naval_exit_id') is not None]
                    if not coastal or (state and state not in coastal):raise WorldError(f'{tag}: fleet requires owned coastal land')
                effect,prefix=('combat_unit','unit_type') if kind=='army' else ('ship','ship_type')
                add(body,f'{effect} = {{ type = {prefix}:{name} count = {unit["count"]} '+(f'state_region = s:{state}' if state else '')+' }')
            node.items.append(pdx.Item('create_military_formation','=',body))
        out[tag]=node
        if c and (c.technology or c.tech_tier is not None):
            for form in node.getall('create_military_formation'):
                if not isinstance(form,pdx.Node):continue
                for effect,table,prefix in [('combat_unit','combat_units','unit_type:'),('ship','ships','ship_type:')]:
                    for unit in form.getall(effect):
                        if not isinstance(unit,pdx.Node):continue
                        unit_type=unit.get_str('type','').removeprefix(prefix)
                        if unit_type in data[table]:
                            missing=set(data[table][unit_type]['unlocking_technologies'])-techs[tag]
                            if missing:raise WorldError(f'{tag}: inherited {unit_type} needs {sorted(missing)}; replace military or retain technology')
        totals={'battalions':0,'ships':0}
        for form in node.getall('create_military_formation'):
            if isinstance(form,pdx.Node):
                for effect,key in [('combat_unit','battalions'),('ship','ships')]:totals[key]+=sum(u.get_int('count',0) for u in form.getall(effect) if isinstance(u,pdx.Node))
        summary[tag]=totals
    return wrap('MILITARY_FORMATIONS',out),summary


def custom_subjects(world,data):
    defs=copy.deepcopy(data['subject_types']);actions=copy.deepcopy(data['diplomatic_actions'])
    types=[];pacts=[];loc=[]
    for key,spec in world.subject_types.items():
        if not isinstance(key,str) or not re.fullmatch(r've_[a-z0-9_]+',key):raise WorldError('Custom subject names must start with ve_ and use lowercase identifiers')
        if 'subject_type_'+key in defs or key in actions:raise WorldError(f'{key}: custom subject identifier already exists')
        dev.obj(spec,{'base','name','name_tr','overlord_types','subject_types','can_have_subjects','income_transfer','join_overlord_wars'},key)
        base=spec.get('base','vassal');base_key='subject_type_'+base
        dev.known(base_key,'subject_types',data,key)
        node=parse(defs[base_key]['script']);action_name=defs[base_key]['diplomatic_action'];action=parse(actions[action_name]['script'])
        set_value(node,'diplomatic_action',key)
        for field in ('overlord','subject'):
            values=spec.get(field+'_types',defs[base_key]['valid_'+field+'_country_types'])
            if not isinstance(values,list) or not values:raise WorldError(f'{key}: {field}_types requires a list')
            for v in values:
                if v not in data['country_types']:raise WorldError(f'{key}: unknown country type {v}')
            set_value(node,'valid_'+field+'_country_types','{ '+' '.join(values)+' }')
        for field in ('valid_overlord_ranks','valid_subject_ranks'):set_value(node,field,'{ '+' '.join(sorted(data['country_ranks']))+' }')
        set_value(node,'overlord_must_be_higher_rank','no')
        for field in ('can_have_subjects','join_overlord_wars'):
            if field in spec:
                if type(spec[field]) is not bool:raise WorldError(f'{key}.{field}: boolean required')
                set_value(node,field,'yes' if spec[field] else 'no')
        pact=action.get_node('pact');set_value(pact,'subject_type','subject_type_'+key)
        if 'income_transfer' in spec:
            dev.number(spec['income_transfer'],key+'.income_transfer',0,1);set_value(pact,'income_transfer',spec['income_transfer'])
        types.append('subject_type_'+key+' = {\n'+pdx.dumps(node)+'\n}')
        pacts.append(key+' = {\n'+pdx.dumps(action)+'\n}')
        defs['subject_type_'+key]={**defs[base_key], 'diplomatic_action':key,'valid_overlord_country_types':node.get_list('valid_overlord_country_types'),'valid_subject_country_types':node.get_list('valid_subject_country_types'),'script':pdx.dumps(node)}
        actions[key]={'script':pdx.dumps(action)}
        for suffix in (key,'subject_type_'+key,key+'_action_name',key+'_desc'):loc.append((suffix,spec.get('name',key),spec.get('name_tr',spec.get('name',key))))
    return defs,actions,'\n'.join(types),'\n'.join(pacts),loc


def compile_diplomacy(res,data,defs,actions,warnings):
    plan=res.world.diplomacy_policy
    dev.obj(plan,{'mode','reset_countries','subjects','relations','pacts','remove'},'diplomacy')
    if plan.get('mode','inherit') not in ('inherit','replace'):raise WorldError('diplomacy.mode: inherit or replace required')
    for field in ('reset_countries','subjects','relations','pacts','remove'):
        if not isinstance(plan.get(field,[]),list):raise WorldError(f'diplomacy.{field}: expected list')
    for field in ('subjects','relations','pacts','remove'):
        if any(not isinstance(p,dict) for p in plan.get(field,[])):raise WorldError(f'diplomacy.{field}: expected objects')
    if any(not isinstance(t,str) for t in plan.get('reset_countries',[])):raise WorldError('reset_countries requires country tags')
    reset=set(plan.get('reset_countries',[]))
    for t in reset:
        if t not in res.countries:raise WorldError(f'diplomacy.reset_countries: unknown country {t}')
    subjects=list(plan.get('subjects',[]))
    for tag,c in res.world.countries.items():
        if c.overlord:subjects.append({'overlord':c.overlord,'subject':tag,'type':c.subject_type,**({'liberty_desire':c.liberty_desire} if c.liberty_desire is not None else {})})
    for field in ('reset_countries','subjects','relations','pacts','remove'):
        if not isinstance(plan.get(field,[]),list):raise WorldError(f'diplomacy.{field}: expected list')
    for field in ('subjects','relations','pacts','remove'):
        if any(not isinstance(p,dict) for p in plan.get(field,[])):raise WorldError(f'diplomacy.{field}: expected objects')
    for field,keys,rows in [('subjects',('overlord','subject','type'),subjects),('relations',('actor','target'),plan.get('relations',[])),('pacts',('actor','target','type'),plan.get('pacts',[])),('remove',('actor','target'),plan.get('remove',[]))]:
        for row in rows:
            if any(not isinstance(row.get(k),str) for k in keys):raise WorldError(f'diplomacy.{field}: requires text identifiers {keys}')
    changed_subjects={p.get('subject') for p in subjects}
    subject_actions={d.get('diplomatic_action') for d in defs.values()}
    overrides={tuple(sorted((p.get('actor',''),p.get('target','')))) for p in plan.get('relations',[])}
    remove=plan.get('remove',[])
    for r in remove:
        dev.obj(r,{'actor','target','type'},'diplomacy.remove')
        if r.get('actor') not in res.countries or r.get('target') not in res.countries:raise WorldError('diplomacy.remove requires known actor and target')
        if 'type' in r:dev.known(r['type'],'diplomatic_actions',{'diplomatic_actions':actions},'diplomacy.remove')
    source=country_nodes('diplomacy') if plan.get('mode','inherit')=='inherit' else {}
    output={};graph={};edge_types={};relations=[];pacts=[]
    def refs(node):
        found=set()
        for it in node.items:
            if isinstance(it.value,str) and it.value.startswith('c:'):found.add(it.value[2:])
            elif isinstance(it.value,pdx.Node):found.update(refs(it.value))
        return found
    for actor,node in source.items():
        if actor not in res.landed_tags or actor in reset:continue
        def drop(it):
            targets=refs(it.value) if isinstance(it.value,pdx.Node) else {it.value[2:]} if isinstance(it.value,str) and it.value.startswith('c:') else set()
            if it.key=='add_liberty_desire' and actor in changed_subjects:return True
            if targets & reset or targets-res.landed_tags:return True
            target=it.value.get_str('country','').removeprefix('c:') if isinstance(it.value,pdx.Node) else ''
            typ=it.value.get_str('type') if isinstance(it.value,pdx.Node) else None
            if it.key=='create_diplomatic_pact' and typ in subject_actions and target in changed_subjects:return True
            if it.key=='set_relations' and tuple(sorted((actor,target))) in overrides:return True
            if it.key=='create_diplomatic_pact' and any(p.get('type')==typ and {p.get('actor'),p.get('target')}=={actor,target} for p in plan.get('pacts',[])):return True
            return any(r.get('actor')==actor and r.get('target') in targets and (not r.get('type') or r['type']==typ) for r in remove)
        filter_tree(node,drop);output[actor]=node
    # Baseline subject graph is part of cycle validation, not only the new edges.
    def read_edges(actor,node):
        for it in node.items:
            if it.key=='create_diplomatic_pact' and isinstance(it.value,pdx.Node):
                t=it.value.get_str('country','').removeprefix('c:');typ=it.value.get_str('type')
                if typ in subject_actions:
                    if t in graph and graph[t]!=actor:raise WorldError(f'{t}: multiple overlords')
                    graph[t]=actor;edge_types[t]=typ
                pacts.append({'actor':actor,'target':t,'type':typ,'source':'inherited'})
    for actor,node in output.items():read_edges(actor,node)
    selected=set()
    for spec in subjects:
        dev.obj(spec,{'overlord','subject','type','liberty_desire'},'diplomacy.subjects')
        actor,target,typ=spec.get('overlord'),spec.get('subject'),spec.get('type')
        if target in selected:raise WorldError(f'{target}: multiple selected overlords')
        selected.add(target)
        for tag in (actor,target):
            if tag not in res.landed_tags:raise WorldError(f'diplomacy: {tag} owns no land')
        key='subject_type_'+str(typ);dev.known(key,'subject_types',{'subject_types':defs},'diplomacy')
        definition=defs[key]
        for tag,side in ((actor,'overlord'),(target,'subject')):
            if res.country_type(tag) not in definition['valid_'+side+'_country_types']:raise WorldError(f'{tag}: {typ} does not allow country_type {res.country_type(tag)} as {side}; use a compatible custom subject type')
        graph[target]=actor;edge_types[target]=typ
        add(output.setdefault(actor,pdx.Node()),f'create_diplomatic_pact = {{ country = c:{target} type = {definition["diplomatic_action"]} }}')
        pacts.append({'actor':actor,'target':target,'type':typ,'source':'scenario'})
    for target in graph:
        seen=set();current=target
        while current in graph:
            if current in seen:raise WorldError(f'Diplomatic dependency cycle involving {current}')
            seen.add(current);current=graph[current]
    for target,actor in graph.items():
        if actor in graph and (target in selected or actor in selected):
            parent_type='subject_type_'+edge_types[actor]
            if parse(defs[parent_type]['script']).get_str('can_have_subjects')=='no':raise WorldError(f'{actor}: its subject type cannot have subjects; use a type with can_have_subjects: true')
    final_desire=[]
    for spec in subjects:
        if 'liberty_desire' in spec:
            value=dev.number(spec['liberty_desire'],'liberty_desire',0,100)
            # Country value liberty_desire is used by vanilla political_lobbies;
            # add_liberty_desire accepts a script value in diplomatic_actions/46_doctrine_of_lapse.
            # Append a final country block after all pact creation blocks.
            # Alphabetic tag order must not set desire before a subject exists.
            final_desire.append(f'c:{spec["subject"]} ?= {{ add_liberty_desire = {{ value = {value} subtract = liberty_desire }} }}')
    seen_pacts=set()
    for spec in plan.get('pacts',[]):
        key=(spec['actor'],spec['target'],spec['type'])
        if key in seen_pacts:raise WorldError('Duplicate diplomatic pact')
        seen_pacts.add(key)
        dev.obj(spec,{'actor','target','type'},'diplomacy.pacts')
        actor,target,typ=spec.get('actor'),spec.get('target'),spec.get('type')
        if actor not in res.landed_tags or target not in res.landed_tags or actor==target:raise WorldError('Pact parties must be distinct landed countries')
        if typ in subject_actions:raise WorldError('Use diplomacy.subjects for dependencies')
        dev.known(typ,'diplomatic_actions',{'diplomatic_actions':actions},'diplomacy')
        if not parse(actions[typ]['script']).get_node('pact'):raise WorldError(f'{typ} is an action, not a persistent pact')
        add(output.setdefault(actor,pdx.Node()),f'create_diplomatic_pact = {{ country = c:{target} type = {typ} }}')
        pacts.append({**spec,'source':'scenario'})
    seen_relations=set()
    for spec in plan.get('relations',[]):
        pair=tuple(sorted((str(spec.get('actor')),str(spec.get('target')))))
        if pair in seen_relations:raise WorldError('Duplicate relation pair')
        seen_relations.add(pair)
        dev.obj(spec,{'actor','target','value'},'diplomacy.relations')
        actor,target=spec.get('actor'),spec.get('target')
        if actor not in res.landed_tags or target not in res.landed_tags or actor==target:raise WorldError('Relation parties must be distinct landed countries')
        value=dev.number(spec.get('value'),'relations.value',-100,100)
        add(output.setdefault(actor,pdx.Node()),f'set_relations = {{ country = c:{target} value = {value} }}');relations.append(spec)
    text=wrap('DIPLOMACY',output)
    if final_desire:text=text[:-1]+'\n'+'\n'.join(final_desire)+'\n}'
    return text,{'overlords':graph,'pacts':pacts,'relations':relations}
