"""Source-backed mechanics catalog from the installed game (never written to)."""
from functools import lru_cache
from . import pdx
from .paths import VANILLA, MOD

TABLES = {
    'country_types': 'country_types', 'country_ranks': 'country_ranks', 'laws': 'laws', 'law_groups': 'law_groups', 'technologies': 'technology/technologies',
    'buildings': 'buildings', 'building_groups': 'building_groups',
    'production_methods': 'production_methods', 'production_method_groups': 'production_method_groups',
    'companies': 'company_types', 'interest_groups': 'interest_groups',
    'combat_units': 'combat_unit_types', 'ships': 'ship_types',
    'strategic_regions': 'strategic_regions', 'subject_types': 'subject_types',
    'diplomatic_actions': 'diplomatic_actions', 'institutions': 'institutions',
    'cultures': 'cultures', 'religions': 'religions', 'pop_types': 'pop_types',
    'technology_tiers': 'scripted_effects',
}

@lru_cache(maxsize=1)
def catalog():
    out = {}
    for table, sub in TABLES.items():
        entries = {}
        files = {}
        for root in (VANILLA, MOD):
            for path in sorted((root / 'common' / sub).rglob('*.txt')):
                if root == MOD and path.name.startswith(('ve_scenario', 'tgc_')):
                    continue
                files[str(path.relative_to(root))] = path
        for path in files.values():
            if table == 'technology_tiers' and 'starting_inventions' not in path.name:
                continue
            for key, node in pdx.parse_file(path).pairs():
                if not isinstance(node, pdx.Node): continue
                if table == 'technology_tiers' and not key.startswith('effect_starting_technology_tier_'): continue
                key = key.removeprefix('REPLACE_OR_CREATE:')
                record = {'source': str(path.relative_to(VANILLA if VANILLA in path.parents else MOD)),
                          'script': pdx.dumps(node)}
                for field in ('group','building_group','era','category','religion','institution','diplomatic_action','naval','ownership_type','max_manpower','port','has_military','has_economy'):
                    if node.get_str(field) is not None: record[field] = node.get_str(field)
                for field in ('unlocking_technologies','disallowing_laws','production_method_groups','production_methods',
                              'building_types','preferred_headquarters','valid_overlord_country_types',
                              'valid_subject_country_types','valid_overlord_ranks','valid_subject_ranks','states'):
                    record[field] = node.get_list(field)
                entries[key] = record
        out[table] = entries
    return out


def technology_set(node, data=None, seen=None):
    """Resolve startup tiers and explicit grants, including prerequisite closure later."""
    data = data or catalog(); seen = set() if seen is None else seen
    result = set()
    for item in node.items:
        if item.key == 'add_technology_researched': result.add(str(item.value))
        elif item.key == 'add_era_researched':
            result.update(k for k,v in data['technologies'].items() if v.get('era') == item.value)
        elif item.key in data['technology_tiers'] and item.key not in seen:
            seen.add(item.key)
            result.update(technology_set(pdx.parse(data['technology_tiers'][item.key]['script']), data, seen))
    return result


def prerequisites(names, data=None):
    data = data or catalog(); result = set(); pending = list(names)
    while pending:
        name = pending.pop()
        if name in result: continue
        if name not in data['technologies']: raise ValueError(f'Unknown technology: {name}')
        result.add(name); pending.extend(data['technologies'][name]['unlocking_technologies'])
    return result


def query(kind=None, search="", limit=30, offset=0, script=False, out=None):
    import json
    data = catalog()
    if limit < 1 or limit > 1000 or offset < 0:
        raise ValueError("rules: limit must be 1..1000 and offset nonnegative")
    if kind is None:
        result = {"kinds": {k: len(v) for k,v in data.items()}, "usage": "rules --kind buildings --query textile --script"}
    else:
        if kind not in data: raise ValueError(f"Unknown kind {kind}; choose {sorted(data)}")
        keys = [k for k in sorted(data[kind]) if search.lower() in k.lower()]
        result = {"kind":kind,"total":len(keys),"offset":offset,"next_offset":offset+limit if offset+limit<len(keys) else None,
                  "entries":{k:{f:v for f,v in data[kind][k].items() if (script or f!='script') and v!=[]} for k in keys[offset:offset+limit]}}
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if out:
        from .atlas import write_output
        write_output(out,text)
    else: print(text)
    return 0


def technology_order(names, data):
    """Grant dependencies before dependents, independent of identifier sorting."""
    selected=set(names);active=set();done=set();ordered=[]
    def visit(name):
        if name in done:return
        if name in active:raise ValueError(f'Technology dependency cycle: {name}')
        active.add(name)
        for parent in sorted(data['technologies'][name]['unlocking_technologies']):
            if parent in selected:visit(parent)
        active.remove(name);done.add(name);ordered.append(name)
    for name in sorted(selected):visit(name)
    return ordered
