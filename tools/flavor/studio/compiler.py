"""Approved plan → additive game files; manifest-owned transactional installation."""
import json
import os
from pathlib import Path
import tempfile
from vic3 import pdx
from .model import q
from .source import FlavorError, MOD, digest, file_hash, writable


def initialize(plan):
    values='\n'.join(f'set_variable = {{ name = {plan.var(k)} value = {v} }}'
                     for k,v in plan.variables.items() if v is not None)
    return f'{plan.namespace}_initialize = {{\nif = {{ limit = {{ NOT = {{ has_variable = {plan.namespace}_initialized }} }}\n{values}\nset_variable = {plan.namespace}_initialized\n}}\n}}'


def gate(plan,key):
    node=plan.nodes[key]
    return f'c:{node["country"]} ?= this\nis_country_alive = yes\nNOT = {{ has_variable = {plan.generated(key,"seen")} }}\n'+plan.condition(node.get('trigger',{'always':True}))


def enqueue(plan,key,delay):
    pending=plan.generated(key,'pending');seen=plan.generated(key,'seen')
    return f'''c:{plan.nodes[key]['country']} ?= {{
{plan.namespace}_initialize = yes
if = {{ limit = {{ is_country_alive = yes NOT = {{ has_variable = {seen} }} NOT = {{ has_variable = {pending} }} }}
set_variable = {pending}
trigger_event = {{ on_action = {plan.generated(key,'dispatch')} days = {delay} }}
}}
}}'''


def links(plan,values):
    return '\n'.join(enqueue(plan,link['to'],link.get('delay_days',1)) for link in values)


def render(plan):
    """Called only after approval by CLI; pure enough for compiler regression tests."""
    events=[f'namespace = {plan.namespace}'];journals=[];on_actions=[];media=[]
    localization={'english':{},'turkish':{}}
    def loc(key,value):
        for language,short in (('english','en'),('turkish','tr')):localization[language][key]=value[short]
        return key
    for key,node in plan.nodes.items():
        seen=plan.generated(key,'seen');dispatch=plan.generated(key,'dispatch')
        action=f'trigger_event = {{ id = {plan.event_id(key)} }}' if node['kind']=='event' else f'add_journal_entry = {{ type = {plan.je(key)} }}'
        if node.get('progress'):
            # goal_add_value is relative to the value at creation; reset before add.
            action=f'set_variable = {{ name = {plan.var(node["progress"]["variable"])} value = 0 }}\n'+action
        on_actions.append(f'''{dispatch} = {{ effect = {{
{plan.namespace}_initialize = yes
remove_variable = {plan.generated(key,'pending')}
if = {{ limit = {{ {gate(plan,key)} }} set_variable = {seen}\n{action} }}
}} }}''')
        if node['kind']=='event':
            eid=plan.event_id(key)
            title=loc(eid+'.t',node['title']);desc=loc(eid+'.d',node['description'])
            flavor='flavor = '+loc(eid+'.f',node['flavor']) if 'flavor' in node else ''
            options=[]
            for op in node['options']:
                name=loc(eid+'.'+op['id'],op['text'])
                condition='trigger = { '+plan.condition(op['when'])+' }' if 'when' in op else ''
                options.append(f'''option = {{ name = {name}
default_option = {'yes' if op.get('default') else 'no'}
ai_chance = {{ base = {op.get('ai_weight',1)} }}
{condition}
{plan.actions(op.get('effects',[]))}
{links(plan,op.get('next',[]))}
}}''')
            events.append(f'''{eid} = {{
type = country_event
title = {title}
desc = {desc}
{flavor}
event_image = {{ video = {q(plan.media(node['media']))} }}
icon = {q(plan.icon(node.get('icon','gfx/interface/icons/event_icons/event_newspaper.dds')))}
on_created_soundeffect = "event:/SFX/UI/Alerts/event_appear"
duration = 3
trigger = {{ c:{node['country']} ?= this is_country_alive = yes {plan.condition(node.get('trigger',{'always':True}))} }}
immediate = {{ set_variable = {seen}\n{plan.actions(node.get('immediate',[]))} }}
{chr(10).join(options)}
}}''')
            if 'video' in node['media']:
                alias=plan.media(node['media']);path=next(k for k,v in plan.assets.items() if str(v)==str(plan.local_asset(node['media']['video'],{'.bk2'})))
                media.append(f'{alias} = {{ video = {q(path)} fallback = {node["media"]["fallback"]} }}')
        else:
            jid=plan.je(key);loc(jid,node['title']);loc(jid+'_reason',node['description'])
            progress=node.get('progress');initial='';goal=''
            if progress:
                variable=plan.var(progress['variable'])
                initial=f'set_variable = {{ name = {variable} value = 0 }}'
                goal='scope:journal_entry = { is_goal_complete = yes }'
            parts=[f'{jid} = {{',f'icon = {q(plan.icon(node.get("icon","gfx/interface/icons/event_icons/event_newspaper.dds")))}',
                   f'group = {node.get("group","je_group_technology")}',
                   'should_be_pinned_by_default_uninvolved_or_context = yes',
                   'immediate = { '+initial+'\n'+plan.actions(node.get('immediate',[]))+' }',
                   'complete = { '+plan.condition(node['complete'])+'\n'+goal+' }']
            if progress:
                parts.extend(['progressbar = yes',f'current_value = {{ value = root.var:{variable} }}',
                              f'goal_add_value = {{ value = {progress["goal"]} }}',
                              f'on_monthly_pulse = {{ effect = {{ change_variable = {{ name = {variable} add = {progress.get("monthly_increment",1)} }} }} }}'])
            if 'fail' in node:parts.append('fail = { '+plan.condition(node['fail'])+' }')
            if 'timeout_days' in node:parts.append('timeout = '+str(node['timeout_days']))
            for outcome in ('on_complete','on_fail','on_timeout'):
                if outcome in node:
                    spec=node[outcome]
                    parts.append(outcome+' = {\n'+plan.actions(spec.get('effects',[]))+'\n'+links(plan,spec.get('next',[]))+'\n}')
            parts.append('}');journals.append('\n'.join(parts))
    for pulse in ('monthly','yearly'):
        roots=[k for k,n in plan.nodes.items() if n.get('entry',{}).get('pulse')==pulse]
        if roots:
            name=f'{plan.namespace}_{pulse}'
            # Installed _on_actions.md explicitly prescribes additive on_actions lists.
            on_actions.append(f'on_{pulse}_pulse_country = {{ on_actions = {{ {name} }} }}')
            calls='\n'.join('if = { limit = { '+gate(plan,k)+' }\n'+enqueue(plan,k,1)+'\n}' for k in roots)
            countries=' '.join(f'c:{t} ?= this' for t in sorted({plan.nodes[k]['country'] for k in roots}))
            on_actions.append(name+' = { trigger = { OR = { '+countries+' } } effect = {\n'+f'{plan.namespace}_initialize = yes\n'+calls+'\n} }')
    modifiers=[]
    for key,spec in plan.modifiers.items():
        name=plan.generated(key,'modifier');loc(name,spec['title'])
        modifiers.append(name+' = {\n'+'\n'.join(f'{k} = {v}' for k,v in spec['values'].items())+'\n}')
    filename=f've_flavor_{plan.namespace}.txt';raw={}
    if len(events)>1:raw['events/'+filename]='\n\n'.join(events)
    if journals:raw['common/journal_entries/'+filename]='\n\n'.join(journals)
    raw['common/on_actions/'+filename]='\n\n'.join(on_actions)
    raw['common/scripted_effects/'+filename]=initialize(plan)
    if modifiers:raw['common/static_modifiers/'+filename]='\n\n'.join(modifiers)
    if media:raw['gfx/media_aliases/'+filename]='\n\n'.join(dict.fromkeys(media))
    header='# GENERATED BY FLAVOR STUDIO — edit the approved plan, not this file.\n'
    files={}
    for name,value in raw.items():
        pdx.parse(value)
        files[name]=b'\xef\xbb\xbf'+(header+value+'\n').encode('utf-8')
    for language,values in localization.items():
        value=f'l_{language}:\n'+'\n'.join(f' {k}:0 {q(v)}' for k,v in values.items())+'\n'
        files[f'localization/{language}/ve_flavor_{plan.namespace}_l_{language}.yml']=b'\xef\xbb\xbf'+value.encode('utf-8')
    for name,path in plan.assets.items():files[name]=path.read_bytes()
    return files


def approval(plan,path):
    try:value=json.loads(Path(path).read_text(encoding='utf-8-sig'))
    except (OSError,ValueError) as exc:raise FlavorError(f'Onay belgesi okunamadı: {exc}') from None
    if not isinstance(value,dict) or value.get('kind')!='flavor-approval-v1' or value.get('approved') is not True or value.get('fingerprint')!=plan.fingerprint() or value.get('namespace')!=plan.namespace:
        raise FlavorError('Onay eksik veya eski. Güncel önizlemeyi kullanıcı inceleyip onaylamalı.')
    return value


def record_approval(plan,review_path,note,out):
    """For explicit conversational approval. Never call merely to unblock build."""
    review=json.loads(Path(review_path).read_text(encoding='utf-8-sig'))
    if review.get('fingerprint')!=plan.fingerprint() or review.get('namespace')!=plan.namespace:
        raise FlavorError('Onaylanan önizleme bu plan/kaynak sürümüyle eşleşmiyor.')
    if not isinstance(note,str) or len(note.strip())<8:raise FlavorError('Kullanıcının bu taslağa verdiği açık onayı not olarak kaydedin.')
    from datetime import datetime,timezone
    value={'kind':'flavor-approval-v1','approved':True,'namespace':plan.namespace,'fingerprint':plan.fingerprint(),
           'reviewed_at':datetime.now(timezone.utc).isoformat(),'origin':'explicit-conversation-approval','note':note}
    path=destination(MOD,str(Path(out).resolve().relative_to(MOD)))
    if MOD/'build/flavor' not in path.parents:raise FlavorError('Onay kaydı build/flavor/ altında olmalı.')
    atomic(path,json.dumps(value,ensure_ascii=False,indent=2).encode());return path


def destination(root,relative):
    path=Path(root)/relative;writable(path)
    if Path(relative).is_absolute() or '..' in Path(relative).parts:raise FlavorError('Geçersiz çıktı yolu.')
    for part in (path,*path.parents):
        if part==MOD:break
        if part.is_symlink():raise FlavorError(f'Symlink çıktısı reddedildi: {part}')
    return path


def atomic(path,data):
    path=writable(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.flavor-',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as out:out.write(data)
        os.replace(name,path)
    finally:
        if os.path.exists(name):os.unlink(name)


def transaction(changes):
    previous={p:p.read_bytes() if p.exists() else None for p in changes}
    try:
        for path,data in changes.items():
            if data is None:path.unlink(missing_ok=True)
            else:atomic(path,data)
    except BaseException:
        for path,data in previous.items():
            if data is None:path.unlink(missing_ok=True)
            else:atomic(path,data)
        raise


def manifest(plan,files):
    import hashlib
    return {'namespace':plan.namespace,'fingerprint':plan.fingerprint(),
            'files':{k:hashlib.sha256(v).hexdigest() for k,v in files.items()}}


def read_manifest(path,namespace):
    if not path.exists():return {'namespace':namespace,'files':{}}
    value=json.loads(path.read_text())
    if not isinstance(value,dict) or value.get('namespace')!=namespace or not isinstance(value.get('files'),dict):
        raise FlavorError('Manifest biçimi veya namespace uyuşmuyor.')
    filename=f've_flavor_{namespace}.txt'
    allowed={f'{d}/{filename}' for d in ('events','common/journal_entries','common/on_actions','common/scripted_effects','common/static_modifiers','gfx/media_aliases')}
    allowed|={f'localization/{lang}/ve_flavor_{namespace}_l_{lang}.yml' for lang in ('english','turkish')}
    for name,h in value['files'].items():
        if not isinstance(name,str) or '..' in Path(name).parts or not isinstance(h,str) or len(h)!=64:
            raise FlavorError('Bozuk manifest dosya kaydı.')
        if name not in allowed and not (name.startswith(f'gfx/event_pictures/ve_flavor/{namespace}/') or name.startswith(f'gfx/interface/icons/ve_flavor/{namespace}/')):
            raise FlavorError(f'Manifest başka içeriğe sahiplik iddia ediyor: {name}')
    return value


def write_bundle(plan,approved,root):
    approval(plan,approved);root=writable(root)
    allowed=MOD/'build/flavor'
    if allowed not in root.parents:raise FlavorError('Derleme klasörü build/flavor/ altında olmalı.')
    files=render(plan);oldpath=root/'flavor-manifest.json'
    old=read_manifest(oldpath,plan.namespace)
    changes={destination(root,k):v for k,v in files.items()}
    for k in set(old['files'])-set(files):changes[destination(root,k)]=None
    changes[destination(root,'flavor-manifest.json')]=json.dumps(manifest(plan,files),indent=2).encode()
    changes[destination(root,'validation.json')]=json.dumps(plan.report(),ensure_ascii=False,indent=2).encode()
    transaction(changes);return root


def install(plan,approved):
    approval(plan,approved)
    missing=plan.sources.countries_used-set(plan.sources.tables['countries'])
    if missing:raise FlavorError(f'Ülke tanımları etkin modda yok: {sorted(missing)}. Önce Atlas kaynağını derleyin; sonra flavor önizlemesini yenileyin.')
    files=render(plan)
    meta=MOD/'.metadata/metadata.json'
    if meta.exists():
        paths=json.loads(meta.read_text(encoding='utf-8-sig')).get('game_custom_data',{}).get('replace_paths',[])
        for prefix in paths:
            if any(name.startswith(prefix.rstrip('/')+'/') for name in files):
                raise FlavorError(f'{prefix}: replace_paths ile flavor çıktısı çakışıyor; mevcut override sözleşmesini ayrıca çözün.')
    state=destination(MOD,f'.flavor/installed/{plan.namespace}.json')
    old=read_manifest(state,plan.namespace)
    if old.get('namespace',plan.namespace)!=plan.namespace:raise FlavorError('Manifest namespace uyuşmazlığı.')
    changes={destination(MOD,k):v for k,v in files.items()}
    for k in set(old['files'])|set(files):
        path=destination(MOD,k)
        if path.exists() and (k not in old['files'] or file_hash(path)!=old['files'][k]):
            raise FlavorError(f'Elle yazılmış/değiştirilmiş dosya korunuyor: {path}')
        if k in old['files'] and not path.exists():raise FlavorError(f'Kurulu paket dosyası eksik: {path}; önce kayıp dosyayı geri yükleyin.')
        if k not in files:changes[path]=None
    changes[state]=json.dumps(manifest(plan,files),indent=2).encode()
    transaction(changes);return list(files)


def check_installed(namespace):
    path=destination(MOD,f'.flavor/installed/{namespace}.json')
    if not path.exists():raise FlavorError(f'Kurulu flavor paketi yok: {namespace}')
    manifest=read_manifest(path,namespace);errors=[]
    for rel,expected in manifest['files'].items():
        p=destination(MOD,rel)
        if not p.exists() or file_hash(p)!=expected:errors.append(rel)
    if errors:raise FlavorError('Eksik/değişmiş kurulu dosyalar: '+', '.join(errors))
    return manifest
