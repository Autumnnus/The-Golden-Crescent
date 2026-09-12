"""Deterministic population and industry plans shared by build and scenario reports.

No GDP or clout simulation: counts are exact; labor, infrastructure and technology
constraints are diagnostics based on the installed game, not invented forecasts.
"""
from collections import defaultdict
from decimal import Decimal, ROUND_FLOOR
import math
import copy
from . import mechanics, pdx
from .world import WorldError


def enabled(world):
    return world.version >= 2 or any(c.population or c.industry or c.technology or c.laws or c.institutions or c.interest_groups or c.companies or c.military or c.history_mode != 'inherit' for c in world.countries.values()) or any(s.population or s.industry for s in world.states.values())


def obj(value, allowed, where):
    if not isinstance(value, dict): raise WorldError(f'{where}: expected an object')
    extra = set(value) - set(allowed)
    if extra: raise WorldError(f'{where}: unknown fields {sorted(extra, key=str)}')
    return value


def number(value, where, low=0, high=None, integer=False):
    if type(value) not in (int, float) or not math.isfinite(value) or value < low or (high is not None and value > high) or (integer and type(value) is not int):
        raise WorldError(f'{where}: expected {"integer" if integer else "number"} in {low}..{high or "infinity"}')
    return value


def known(name, table, data, where):
    if not isinstance(name, str) or name not in data[table]:
        raise WorldError(f'{where}: unknown {table} identifier {name!r}; use tgc.py rules --kind {table}')


def shares(values, where):
    if not isinstance(values, dict) or not values: raise WorldError(f'{where}: nonempty ratio mapping required')
    for key, value in values.items(): number(value, f'{where}.{key}', 0, 1)
    if abs(sum(Decimal(str(v)) for v in values.values()) - Decimal(1)) > Decimal('0.000000001'):
        raise WorldError(f'{where}: ratios must sum to 1 (not percentages out of 100)')


def apportion(total, weights):
    """Largest remainder: exact total and stable ties, with Decimal arithmetic."""
    if not weights: return []
    ws = [Decimal(str(w)) for w in weights]
    if not sum(ws): ws = [Decimal(1)] * len(ws)
    weight_sum = sum(ws)
    amounts = [Decimal(total) * w / weight_sum for w in ws]
    out = [int(a.to_integral_value(rounding=ROUND_FLOOR)) for a in amounts]
    for i in sorted(range(len(ws)), key=lambda i: (-(amounts[i] - out[i]), i))[:total-sum(out)]: out[i] += 1
    return out


POP_KEYS = {'total','scale','cultures','religions','composition','literacy','wealth','by_owner'}

def validate_population(spec, data, where, allow_owners=False):
    obj(spec, POP_KEYS if allow_owners else POP_KEYS-{'by_owner'}, where)
    if 'total' in spec and 'scale' in spec: raise WorldError(f'{where}: choose total or scale')
    if 'total' in spec: number(spec['total'],where+'.total',integer=True)
    if 'scale' in spec: number(spec['scale'],where+'.scale',0,100)
    if 'literacy' in spec: number(spec['literacy'],where+'.literacy',0,1)
    if 'wealth' in spec: number(spec['wealth'],where+'.wealth',1,100)
    for field,table in [('cultures','cultures'),('religions','religions')]:
        if field in spec:
            shares(spec[field],where+'.'+field)
            for name in spec[field]: known(name,table,data,where)
    if 'composition' in spec:
        if 'cultures' in spec or 'religions' in spec: raise WorldError(f'{where}: composition and separate marginals are mutually exclusive')
        rows=spec['composition']
        if not isinstance(rows,list) or not rows: raise WorldError(f'{where}: composition must be a nonempty list')
        for i,row in enumerate(rows):
            obj(row,{'culture','religion','share','pop_type'},where)
            known(row.get('culture'),'cultures',data,where);known(row.get('religion'),'religions',data,where)
            if row.get('pop_type'): known(row['pop_type'],'pop_types',data,where)
        shares({i:r.get('share') for i,r in enumerate(rows)},where+'.composition')
    if not isinstance(spec.get('by_owner',{}),dict): raise WorldError(f'{where}.by_owner: expected mapping')
    for tag,part in spec.get('by_owner',{}).items(): validate_population(part,data,where+'/'+tag)


def population_plan(rows, spec):
    """Retain unedited joint distribution; explicit marginals create a cross product."""
    total = spec.get('total',round(sum(p['size'] for p in rows)*spec.get('scale',1)))
    if 'composition' in spec:
        templates=[{k:v for k,v in r.items() if k!='share'} for r in spec['composition']]
        weights=[r['share'] for r in spec['composition']]
    elif 'cultures' in spec or 'religions' in spec:
        old_c=defaultdict(int);old_r=defaultdict(int)
        for p in rows: old_c[p['culture']]+=p['size'];old_r[p['religion']]+=p['size']
        cs=spec.get('cultures',old_c);rs=spec.get('religions',old_r)
        if not cs or not rs: raise WorldError('New population requires composition or both cultures and religions')
        templates=[];weights=[]
        for cu,cw in sorted(cs.items()):
            for rel,rw in sorted(rs.items()):
                templates.append({'culture':cu,'religion':rel});weights.append(Decimal(str(cw))*Decimal(str(rw)))
    else: templates=rows;weights=[r['size'] for r in rows]
    if total and not templates: raise WorldError('Cannot populate empty land without a composition')
    return [{**r,'size':n} for r,n in zip(templates,apportion(total,weights)) if n]


def building_records(script):
    return [n for n in pdx.parse(script).getall('create_building') if isinstance(n,pdx.Node)]


def level(node):
    def walk(n):
        return sum(int(float(it.value)) if it.key=='levels' and isinstance(it.value,str) else walk(it.value) if isinstance(it.value,pdx.Node) else 0 for it in n.items)
    return sum(walk(n) for n in node.getall('add_ownership') if isinstance(n,pdx.Node)) or node.get_int('level',0)


def set_levels(node, total):
    slots=[]
    def walk(n):
        for it in n.items:
            if it.key=='levels' and isinstance(it.value,str): slots.append(it)
            elif isinstance(it.value,pdx.Node): walk(it.value)
    for ownership in node.getall('add_ownership'):
        if isinstance(ownership,pdx.Node):walk(ownership)
    if slots:
        for it,n in zip(slots,apportion(total,[float(i.value) for i in slots])): it.value=str(n)
    else:
        node.items=[it for it in node.items if it.key!='level'];node.items.append(pdx.Item('level','=',str(total)))


def validate_industry(spec,data,where,allow_owners=False):
    obj(spec,{'mode','scale','buildings','by_owner'} if allow_owners else {'mode','scale','buildings'},where)
    if spec.get('mode','merge') not in ('merge','replace'): raise WorldError(f'{where}: mode must be merge or replace')
    number(spec.get('scale',1),where+'.scale',0,100)
    if not isinstance(spec.get('buildings',{}),dict): raise WorldError(f'{where}: buildings must be a mapping')
    for name,item in spec.get('buildings',{}).items():
        known(name,'buildings',data,where)
        if type(item) is int: item={'level':item}
        obj(item,{'level','production_methods','ownership','reserves'},where+'/'+name)
        number(item.get('level'),where+'/'+name+'.level',0,10000,True)
        if item.get('ownership','self') not in ('self','government'): raise WorldError(f'{where}: ownership must be self or government')
        number(item.get('reserves',1),where+'.reserves',0,1)
        if not isinstance(item.get('production_methods',[]),list): raise WorldError(f'{where}: production_methods must be a list')
        groups=data['buildings'][name]['production_method_groups'];seen=set()
        for pm in item.get('production_methods',[]):
            known(pm,'production_methods',data,where)
            matches=[g for g in groups if pm in data['production_method_groups'][g]['production_methods']]
            if not matches: raise WorldError(f'{where}: {pm} does not belong to {name}')
            if seen.intersection(matches): raise WorldError(f'{where}: two production methods in the same group for {name}')
            seen.update(matches)
    if not isinstance(spec.get('by_owner',{}),dict): raise WorldError(f'{where}.by_owner: expected mapping')
    for tag,part in spec.get('by_owner',{}).items():validate_industry(part,data,where+'/'+tag)


def industry_plan(script, spec, tag, state, data):
    records=building_records(script) if spec.get('mode','merge')=='merge' else []
    for rec in records: set_levels(rec,round(level(rec)*spec.get('scale',1)))
    for name,item in spec.get('buildings',{}).items():
        if type(item) is int:item={'level':item}
        previous=next((r for r in records if r.get_str('building')==name),None)
        records=[r for r in records if r.get_str('building')!=name]
        if not item['level']:continue
        pms=list(item.get('production_methods', previous.get_list('activate_production_methods') if previous else []))
        # Keep inherited methods on level-only edits; fill every omitted group.
        for group in data['buildings'][name]['production_method_groups']:
            methods=data['production_method_groups'][group]['production_methods']
            if methods and not set(methods)&set(pms):pms.append(methods[0])
        n=item['level']
        if previous is not None and 'ownership' not in item:
            record=copy.deepcopy(previous);set_levels(record,n)
            record.set('activate_production_methods',pdx.parse(' '.join(pms)))
            if 'reserves' in item:record.set('reserves',str(item['reserves']))
            records.append(record)
            continue
        ownership=f'country = {{ country = c:{tag} levels = {n} }}' if item.get('ownership','self' if data['buildings'][name].get('ownership_type')=='self' else 'government')=='government' else f'building = {{ type = {name} country = c:{tag} region = {state} levels = {n} }}'
        records.append(pdx.parse(f'building = {name}\nadd_ownership = {{ {ownership} }}\nreserves = {item.get("reserves",1)}\nactivate_production_methods = {{ {" ".join(pms)} }}'))
    return '\n'.join('create_building = {\n'+pdx.dumps(r)+'\n}' for r in records if level(r)>0)


def merged_population(*specs):
    result={}
    for s in specs:
        if 'total' in s:result.pop('scale',None)
        if 'scale' in s:result.pop('total',None)
        if 'composition' in s:
            result.pop('cultures',None);result.pop('religions',None)
        if 'cultures' in s or 'religions' in s:result.pop('composition',None)
        result.update({k:v for k,v in s.items() if k!='by_owner'})
    return result


def apply(res):
    data=mechanics.catalog();res.population_settings={}
    for tag,c in res.world.countries.items():
        validate_population(c.population,data,tag+'.population');validate_industry(c.industry,data,tag+'.industry')
    for name,s in res.world.states.items():
        validate_population(s.population,data,name+'.population',True);validate_industry(s.industry,data,name+'.industry',True)
        owners={t for t,_,_ in res.state_owners.get(name,[])}
        for spec in (s.population,s.industry):
            for tag in spec.get('by_owner',{}):
                if tag not in owners:raise WorldError(f'{name}: {tag} has no state share')
    country_totals={}
    for tag,c in res.world.countries.items():
        if 'total' in c.population:
            names=sorted(n for n,ts in res.state_owners.items() if any(t==tag for t,_,_ in ts))
            counts=[sum(p['size'] for p in res.state_pops.get(n,{}).get(tag,[])) for n in names]
            country_totals.update({(n,tag):v for n,v in zip(names,apportion(c.population['total'],counts))})
    for name,owners in res.state_owners.items():
        ss=res.world.states.get(name); sp=ss.population if ss else {};si=ss.industry if ss else {}
        tags=sorted({t for t,_,_ in owners})
        rows_by_tag=res.state_pops.setdefault(name,{})
        state_total={}
        if 'total' in sp:
            state_total=dict(zip(tags,apportion(sp['total'],[sum(p['size'] for p in rows_by_tag.get(t,[])) for t in tags])))
        for tag in tags:
            c=res.world.countries.get(tag);cp=dict(c.population) if c else {};ci=c.industry if c else {}
            rows=rows_by_tag.get(tag,[])
            # Materialize default religion before redistributing, preserving the vanilla meaning.
            rows=[{**p,'religion':p.get('religion') or data['cultures'][p['culture']].get('religion')} for p in rows]
            if (name,tag) in country_totals:cp['total']=country_totals[name,tag]
            local={**sp,**({'total':state_total[tag]} if tag in state_total else {})}
            ps=merged_population(cp,local,sp.get('by_owner',{}).get(tag,{}))
            if ps:rows=population_plan(rows,ps)
            rows_by_tag[tag]=rows
            settings={k:ps[k] for k in ('literacy','wealth') if k in ps}
            if c and c.literacy is not None:settings.setdefault('literacy',c.literacy_rate)
            if settings:res.population_settings[name,tag]=settings
            script=res.state_buildings.setdefault(name,{}).get(tag,'')
            for plan in (ci,si,si.get('by_owner',{}).get(tag,{})):
                if plan:script=industry_plan(script,plan,tag,name,data)
            if res.country_type(tag)=='decentralized' and building_records(script):raise WorldError(f'{name}: decentralized {tag} cannot have buildings')
            if script.strip():res.state_buildings[name][tag]=script
            else:res.state_buildings[name].pop(tag,None)
