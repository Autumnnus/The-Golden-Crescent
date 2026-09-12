"""A deliberately typed country-scope DSL: no unchecked PDX escape hatch."""
import datetime
import math
import re
from pathlib import Path
import yaml
from vic3 import pdx
from .source import FlavorError, Sources, digest, file_hash

IDENT = re.compile(r'^[a-z][a-z0-9_]{0,55}$')
TAG = re.compile(r'^[A-Z0-9]{2,8}$')
ICON = 'gfx/interface/icons/event_icons/event_newspaper.dds'
MODIFIER_KEYS = {'country_prestige_add', 'country_authority_add', 'country_bureaucracy_add'}
VERSION = 1


def obj(value, allowed, where):
    if not isinstance(value, dict) or any(not isinstance(k, str) for k in value):
        raise FlavorError(f'{where}: nesne/metin anahtarları gerekiyor.')
    extra = set(value)-set(allowed)
    if extra: raise FlavorError(f'{where}: desteklenmeyen alanlar {sorted(extra)}')


def seq(value, where, minimum=0):
    if not isinstance(value, list) or len(value) < minimum:
        raise FlavorError(f'{where}: en az {minimum} öğeli liste gerekiyor.')
    return value


def ident(value):
    if not isinstance(value, str) or not IDENT.fullmatch(value):
        raise FlavorError(f'Geçersiz kimlik: {value!r}; küçük harf/rakam/alt çizgi kullanın.')
    return value


def number(value, where, low=-1000000, high=1000000, integer=False):
    if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high or (integer and type(value) is not int):
        raise FlavorError(f'{where}: {low}..{high} aralığında {"tam " if integer else ""}sayı gerekiyor.')
    return value


def text(value, where):
    if not isinstance(value, str) or not value.strip() or len(value) > 20000 or any(ord(c)<32 and c not in '\n\t' for c in value):
        raise FlavorError(f'{where}: boş olmayan, kontrol karakteri içermeyen metin gerekiyor.')
    # Dynamic localization needs scope contracts; do not silently accept scope typos.
    if any(c in value for c in '[]$'):
        raise FlavorError(f'{where}: dinamik localization desteklenmiyor; ülke/bağlam adlarını açık metinle yazın.')
    return value


def q(value):
    return '"'+str(value).replace('\\','\\\\').replace('"','\\"').replace('\n',r'\n').replace('\t',' ')+'"'


class UniqueLoader(yaml.SafeLoader):
    pass


def mapping(loader, node, deep=False):
    result = {}
    for key_node, val_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str) or key in result:
            raise FlavorError(f'Yinelenen veya metin olmayan YAML/JSON anahtarı: {key!r}')
        result[key] = loader.construct_object(val_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)


def load(path):
    path = Path(path).resolve()
    try:
        raw=path.read_text(encoding='utf-8-sig')
        if any(isinstance(token,yaml.AliasToken) for token in yaml.scan(raw)):
            raise FlavorError('YAML alias/anchor yeniden kullanımı desteklenmiyor; açık değerler yazın.')
        doc = yaml.load(raw, Loader=UniqueLoader)
    except (OSError, yaml.YAMLError) as exc:
        raise FlavorError(str(exc)) from None
    return doc


class Plan:
    def __init__(self, document, path, sources=None):
        self.doc = document; self.path = Path(path).resolve(); self.sources = sources or Sources()
        self.edges = []; self.warnings = []; self.assets = {}; self.read_vars = set(); self.written_vars = set()
        obj(document, {'version','namespace','title','summary','assumptions','variables','modifiers','nodes'}, 'plan')
        if type(document.get('version')) is not int or document['version'] != VERSION: raise FlavorError('version: 1 gerekiyor.')
        self.namespace = ident(document.get('namespace'))
        if not self.namespace.startswith('ve_') or len(self.namespace)>32: raise FlavorError('namespace ve_ ile başlamalı ve en fazla 32 karakter olmalı.')
        text(document.get('title'),'title'); text(document.get('summary'),'summary')
        for item in seq(document.get('assumptions',[]),'assumptions'): text(item,'assumption')
        self.variables = document.get('variables',{})
        obj(self.variables, self.variables if isinstance(self.variables,dict) else (), 'variables')
        for name, default in self.variables.items():
            ident(name)
            if default is not None: number(default, name)
        self.modifiers = document.get('modifiers',{})
        obj(self.modifiers, self.modifiers if isinstance(self.modifiers,dict) else (), 'modifiers')
        for name, spec in self.modifiers.items():
            ident(name); obj(spec, {'title','values'},name); self.localized(spec.get('title'),name)
            obj(spec.get('values'),MODIFIER_KEYS,name+'.values')
            if not spec['values']: raise FlavorError(f'{name}: boş modifier.')
            for value in spec['values'].values(): number(value,name)
        self.nodes = document.get('nodes')
        obj(self.nodes, self.nodes if isinstance(self.nodes,dict) else (), 'nodes')
        if not 1 <= len(self.nodes) <= 150: raise FlavorError('Bir paket 1–150 düğüm içermeli; büyük hikâyeleri paketlere ayırın.')
        numbers=set();progress_variables=set()
        for key,node in self.nodes.items():
            ident(key)
            obj(node, {'kind','number','country','title','description','flavor','context','trigger','entry',
                       'icon','media','options','immediate','complete','fail','timeout_days',
                       'on_complete','on_fail','on_timeout','group','progress'},key)
            kind=node.get('kind')
            if kind not in ('event','journal'): raise FlavorError(f'{key}: kind event veya journal olmalı.')
            tag=node.get('country')
            if not isinstance(tag,str) or not TAG.fullmatch(tag): raise FlavorError(f'{key}: sabit ülke etiketi gerekiyor.')
            self.sources.country(tag)
            self.localized(node.get('title'),key+'.title'); self.localized(node.get('description'),key+'.description')
            text(node.get('context'),key+'.context')
            if 'flavor' in node:self.localized(node['flavor'],key+'.flavor')
            if 'trigger' in node:self.condition(node['trigger'])
            if 'entry' in node:
                obj(node['entry'],{'pulse'},key+'.entry')
                if node['entry'].get('pulse') not in ('monthly','yearly'): raise FlavorError('entry.pulse monthly veya yearly olmalı.')
            self.icon(node.get('icon',ICON))
            if kind=='event':
                forbidden=set(node)&{'complete','fail','timeout_days','on_complete','on_fail','on_timeout','group','progress'}
                n=number(node.get('number'),key+'.number',1,999999,True)
                if n in numbers: raise FlavorError('Event number benzersiz olmalı.')
                numbers.add(n); self.media(node.get('media'))
                options=seq(node.get('options'),key+'.options',1)
                if len(options)>6:raise FlavorError('Event başına en fazla 6 seçenek desteklenir.')
                ids=set();defaults=[]
                for option in options:
                    obj(option,{'id','text','default','ai_weight','when','effects','next'},key+'.option')
                    oid=ident(option.get('id'))
                    if oid in ids: raise FlavorError(f'{key}: yinelenen seçenek {oid}')
                    ids.add(oid); self.localized(option.get('text'),key+'.'+oid)
                    if type(option.get('default',False)) is not bool:raise FlavorError('default boolean olmalı.')
                    if option.get('default'):defaults.append(option)
                    number(option.get('ai_weight',1),'ai_weight',0,10000)
                    if 'when' in option:self.condition(option['when'])
                    self.actions(option.get('effects',[]));self.links(key,option.get('next',[]),f'seçim: {oid}')
                if len(defaults)!=1 or 'when' in defaults[0] or defaults[0].get('ai_weight',1)<=0:
                    raise FlavorError(f'{key}: koşulsuz, pozitif AI ağırlıklı tam bir varsayılan seçenek gerekiyor.')
            else:
                forbidden=set(node)&{'number','options','media','flavor'}
                self.condition(node.get('complete'))
                self.sources.require('journal_groups',node.get('group','je_group_technology'))
                if 'fail' in node:self.condition(node['fail'])
                if 'timeout_days' in node:number(node['timeout_days'],'timeout_days',1,36500,True)
                if 'on_timeout' in node and 'timeout_days' not in node:raise FlavorError(f'{key}: on_timeout için timeout_days gerekiyor.')
                if 'on_fail' in node and 'fail' not in node:raise FlavorError(f'{key}: on_fail için fail gerekiyor.')
                if node.get('complete') == node.get('fail'):raise FlavorError(f'{key}: complete ve fail aynı koşul olamaz.')
                for outcome in ('on_complete','on_fail','on_timeout'):
                    action=node.get(outcome,{})
                    obj(action,{'effects','next'},outcome);self.actions(action.get('effects',[]));self.links(key,action.get('next',[]),outcome)
                if 'timeout_days' not in node:self.warnings.append(f'{key}: zaman aşımı yok; tamamlama koşulu gerçekleşmezse günlük açık kalır.')
                if 'progress' in node:
                    progress=node['progress'];obj(progress,{'variable','goal','monthly_increment'},key+'.progress')
                    name=progress.get('variable');self.var(name)
                    if name in progress_variables:raise FlavorError('İki günlük aynı ilerleme değişkenini kullanamaz.')
                    progress_variables.add(name);self.written_vars.add(name)
                    number(progress.get('goal'),'progress.goal',1,100000)
                    number(progress.get('monthly_increment',1),'progress.monthly_increment',0.001,100000)
                    if node.get('timeout_days',36500)/28*progress.get('monthly_increment',1)<progress['goal']:
                        self.warnings.append(f'{key}: ilerleme hedefi zaman aşımından önce ulaşılamayacak kadar yüksek görünüyor.')
            if forbidden:raise FlavorError(f'{key}/{kind}: geçersiz alanlar {sorted(forbidden)}')
            self.actions(node.get('immediate',[]))
        self.graph()
        for name in self.read_vars-self.written_vars:
            if self.variables[name] is None:self.warnings.append(f'{name}: koşullarda okunuyor fakat bu paket tarafından hiç ayarlanmıyor.')
        self.collision_check()
        self.warnings.append('Statik kaynak kontrolü; oyun motoru ve tam ekonomi simülasyonu çalıştırılmadı.')
        self.warnings.append('Gecikmeli bağlantı, teslim anında koşul sağlanmazsa atlanır; otomatik tekrar denenmez. Giriş düğümleri kendi pulse aralıklarında tekrar değerlendirilir.')
        if not self.sources.context:self.warnings.append('Atlas bağlamı seçilmedi: yeni ülkeler etkin mod tanımlarından alınır; alternatif dünya sahipliği ayrıca bağlanmadı.')

    def localized(self, value, where):
        obj(value,{'tr','en'},where)
        for language in ('tr','en'):text(value.get(language),where+'.'+language)

    def var(self, name):
        if not isinstance(name,str) or name not in self.variables:raise FlavorError(f'Tanımsız paket değişkeni: {name!r}')
        return self.namespace+'_var_'+name

    def generated(self,key,suffix): return f'{self.namespace}_{suffix}_{key}'
    def event_id(self,key):return f'{self.namespace}.{self.nodes[key]["number"]}'
    def je(self,key):return self.generated(key,'je')

    def condition(self, expr, depth=0):
        if depth>16:raise FlavorError('Koşullar en fazla 16 seviye iç içe olabilir.')
        obj(expr,{'all','any','not','always','after','before','is_player','has_law','technology',
                  'primary_culture','state_religion','has_culture_pop','has_religion_pop',
                  'owns_state','has_building','has_variable','variable'},'condition')
        if not expr:raise FlavorError('Boş koşul yerine always: true kullanın.')
        lines=[]
        for op,value in expr.items():
            if op in ('all','any'):
                lines.append(('AND' if op=='all' else 'OR')+' = { '+ ' '.join(self.condition(v,depth+1) for v in seq(value,op,1))+' }')
            elif op=='not':lines.append('NOT = { '+self.condition(value,depth+1)+' }')
            elif op in ('always','is_player'):
                if type(value) is not bool:raise FlavorError(f'{op}: boolean gerekiyor.')
                lines.append(f'{op} = {"yes" if value else "no"}')
            elif op in ('after','before'):
                if not isinstance(value,str) or not re.fullmatch(r'\d{4}\.\d{1,2}\.\d{1,2}',value):raise FlavorError('Tarih metni YYYY.M.D olmalı.')
                try:datetime.date(*map(int,value.split('.')))
                except ValueError:raise FlavorError(f'Geçersiz tarih: {value}') from None
                lines.append(f'game_date {">=" if op=="after" else "<"} {value}')
            elif op=='has_variable':
                name=self.var(value);self.read_vars.add(value);lines.append('has_variable = '+name)
            elif op=='variable':
                obj(value,{'name','op','value'},'variable')
                name=self.var(value.get('name'));self.read_vars.add(value['name'])
                if value.get('op') not in ('=','!=','>','<','>=','<='):raise FlavorError('Geçersiz değişken karşılaştırması.')
                n=number(value.get('value'),'variable.value')
                lines.append(f'has_variable = {name} var:{name} {value["op"]} {n}')
            else:
                table,engine,prefix={
                    'has_law':('laws','has_law','law_type:'), 'technology':('technologies','has_technology_researched',''),
                    'primary_culture':('cultures','country_has_primary_culture','cu:'),
                    'state_religion':('religions','country_has_state_religion','rel:'),
                    'has_culture_pop':('cultures','culture','cu:'), 'has_religion_pop':('religions','religion','rel:'),
                    'owns_state':('states','state_region','s:'),'has_building':('buildings','has_building','')}[op]
                self.sources.require(table,value)
                clause=f'{engine} = {prefix}{value}'
                if op in ('has_culture_pop','has_religion_pop'):clause='any_scope_pop = { '+clause+' }'
                if op=='owns_state':clause='any_scope_state = { '+clause+' }'
                lines.append(clause)
        if 'after' in expr and 'before' in expr and tuple(map(int,expr['after'].split('.'))) >= tuple(map(int,expr['before'].split('.'))):
            raise FlavorError('Tarih aralığı boş veya ters.')
        return '\n'.join(lines)

    def actions(self, actions, depth=0):
        if depth>12:raise FlavorError('Effects aşırı iç içe.')
        lines=[]
        for effect in seq(actions,'effects'):
            obj(effect,{'set_variable','remove_variable','add_modifier','remove_modifier','relations',
                        'add_primary_culture','state_religion','activate_law','add_technology','if'},'effect')
            if len(effect)!=1:raise FlavorError('Her effect tam bir işlem içermeli.')
            op,value=next(iter(effect.items()))
            if op=='if':
                obj(value,{'when','then','else'},'if')
                lines.append('if = { limit = { '+self.condition(value.get('when'))+' } '+self.actions(value.get('then',[]),depth+1)+' }')
                if 'else' in value:lines.append('else = { '+self.actions(value['else'],depth+1)+' }')
            elif op=='set_variable':
                obj(value,{'name','value'},op);name=self.var(value.get('name'));self.written_vars.add(value['name'])
                lines.append(f'set_variable = {{ name = {name} value = {number(value.get("value",1),op)} }}')
            elif op=='remove_variable':lines.append('remove_variable = '+self.var(value))
            elif op in ('add_modifier','remove_modifier'):
                if op=='add_modifier':obj(value,{'name','days'},op);name=value.get('name');days=number(value.get('days'),op+'.days',1,36500,True)
                else:name=value
                if not isinstance(name,str):raise FlavorError('Modifier adı metin olmalı.')
                if name in self.modifiers:name=self.generated(name,'modifier')
                else:
                    definition=self.sources.require('modifiers',name)
                    if any(k not in ('icon',) and not k.startswith('country_') for k in definition.keys()):
                        raise FlavorError(f'{name}: yalnız ülke modifier alanları desteklenir; kapsamı belirsiz modifier reddedildi.')
                lines.append(f'add_modifier = {{ name = {name} days = {days} }}' if op=='add_modifier' else f'remove_modifier = {name}')
            elif op=='relations':
                obj(value,{'country','value'},op);self.sources.country(value.get('country'))
                amount=number(value.get('value'),op,-100,100)
                lines.append(f'if = {{ limit = {{ exists = c:{value["country"]} }} change_relations = {{ country = c:{value["country"]} value = {amount} }} }}')
            else:
                table,engine,prefix={
                    'add_primary_culture':('cultures','add_primary_culture','cu:'),
                    'state_religion':('religions','set_state_religion','rel:'),
                    'activate_law':('laws','activate_law','law_type:'),
                    'add_technology':('technologies','add_technology_researched','')}[op]
                self.sources.require(table,value);lines.append(f'{engine} = {prefix}{value}')
                if op in ('activate_law','add_technology'):
                    warning=f'{op}/{value}: ID doğrulandı; gelecek tarihteki kanun/teknoloji önkoşullarını hikâyenin koşullarıyla ayrıca sağlayın.'
                    if warning not in self.warnings:self.warnings.append(warning)
        return '\n'.join(lines)

    def local_asset(self, relative, extensions):
        if not isinstance(relative,str) or '\\' in relative:raise FlavorError('Asset yolu metin ve / ayırıcılı olmalı.')
        p=(self.path.parent/relative).resolve()
        if self.path.parent not in p.parents or not p.is_file() or p.suffix.lower() not in extensions:
            raise FlavorError(f'Asset plan klasörünün içinde olmalı; uzantılar {extensions}: {relative}')
        self.sources.touch(p);return p

    def icon(self, value):
        if isinstance(value,str):
            p=self.sources.asset(value)
            if p.suffix.lower()!='.dds':raise FlavorError('Oyun simgesi DDS olmalı.')
            return value
        obj(value,{'file'},'icon');p=self.local_asset(value.get('file'),{'.dds'})
        from PIL import Image
        try:
            with Image.open(p) as im:
                if im.format!='DDS':raise FlavorError('Simge gerçek DDS olmalı.')
                im.load()
        except OSError as exc:raise FlavorError(f'DDS okunamıyor: {exc}') from None
        target=f'gfx/interface/icons/ve_flavor/{self.namespace}/{file_hash(p)[:16]}.dds'
        self.assets[target]=p;return target

    def media(self, value):
        obj(value,{'alias','video','fallback','poster'},'media')
        if ('alias' in value)==('video' in value):raise FlavorError('media: alias veya video seçeneklerinden tam biri gerekiyor.')
        if 'alias' in value:
            if 'fallback' in value:raise FlavorError('Mevcut alias fallback kaynağını kendisi belirler.')
            self.sources.media(value['alias']);key=value['alias']
        else:
            p=self.local_asset(value['video'],{'.bk2'})
            with p.open('rb') as f:header=f.read(4)
            if not header.startswith(b'KB2'):raise FlavorError('Özel video gerçek Bink 2 (.bk2) olmalı.')
            warning='Özel Bink videonun başlığı ve dosya yolu kontrol edildi; codec/DLC davranışı motor içinde sınanmalı. Poster yalnız önizleme içindir.'
            if warning not in self.warnings:self.warnings.append(warning)
            self.sources.media(value.get('fallback'))
            target=f'gfx/event_pictures/ve_flavor/{self.namespace}/{file_hash(p)[:16]}.bk2'
            self.assets[target]=p;key=self.generated(file_hash(p)[:16],'media')
        if 'poster' in value:
            p=self.local_asset(value['poster'],{'.png','.jpg','.jpeg','.webp'})
            from PIL import Image
            try:
                with Image.open(p) as im:im.verify()
            except OSError as exc:raise FlavorError(f'Poster okunamıyor: {exc}') from None
        return key

    def links(self, source, links, label):
        for link in seq(links,'next'):
            obj(link,{'to','delay_days'},'next')
            target=link.get('to')
            if not isinstance(target,str) or target not in self.nodes:raise FlavorError(f'{source}: hedef bulunamadı: {target!r}')
            delay=number(link.get('delay_days',1),'delay_days',1,36500,True)
            edge={'from':source,'to':target,'label':label,'delay_days':delay}
            if edge in self.edges:raise FlavorError(f'Yinelenen bağlantı: {source} → {target}')
            self.edges.append(edge)

    def graph(self):
        roots=[k for k,n in self.nodes.items() if 'entry' in n]
        if not roots:raise FlavorError('En az bir entry düğümü gerekiyor; zincir kendiliğinden başlamaz.')
        reached=set();pending=list(roots)
        while pending:
            key=pending.pop()
            if key in reached:continue
            reached.add(key);pending.extend(e['to'] for e in self.edges if e['from']==key)
        if set(self.nodes)-reached:raise FlavorError(f'Girişten ulaşılamayan düğümler: {sorted(set(self.nodes)-reached)}')
        visiting=set();done=set()
        def visit(key):
            if key in visiting:raise FlavorError(f'Zincir döngüsü: {key}. Düğümler ülke başına tek kullanımlıdır.')
            if key in done:return
            visiting.add(key)
            for e in self.edges:
                if e['from']==key:visit(e['to'])
            visiting.remove(key);done.add(key)
        for key in self.nodes:visit(key)
        for key in self.nodes:
            parents=[e for e in self.edges if e['to']==key]
            if len(parents)>1:self.warnings.append(f'{key}: birden fazla giriş var. İlk geçerli teslim kazanır; bu bir AND birleştirmesi değildir.')

    def collision_check(self):
        filename=f've_flavor_{self.namespace}.txt'
        names=[('scripted_effects',self.namespace+'_initialize')]
        for key,n in self.nodes.items():
            kind='events' if n['kind']=='event' else 'journals'
            name=self.event_id(key) if kind=='events' else self.je(key)
            names.append((kind,name));names.append(('on_actions',self.generated(key,'dispatch')))
            if 'entry' in n:names.append(('on_actions',self.namespace+'_'+n['entry']['pulse']))
        names.extend(('modifiers',self.generated(k,'modifier')) for k in self.modifiers)
        for n in self.nodes.values():
            if 'video' in n.get('media',{}):names.append(('media',self.media(n['media'])))
        from .source import MOD
        state=MOD/f'.flavor/installed/{self.namespace}.json'
        import json
        owned=json.loads(state.read_text()).get('files',{}) if state.exists() else {}
        for kind,name in names:
            entry=self.sources.tables[kind].get(name)
            if entry:
                path=entry[0]
                ours=path.name==filename and MOD in path.parents and owned.get(path.relative_to(MOD).as_posix())==file_hash(path)
                if not ours:raise FlavorError(f'Oyun kimliği çakışması veya değiştirilmiş kurulu dosya: {name} ({path})')

    def fingerprint(self):
        for name,expected in self.sources.used.items():
            path=Path(name)
            if not path.is_file() or file_hash(path)!=expected:
                raise FlavorError(f'Kaynak doğrulama sırasında değişti; yeniden önizleyin: {name}')
        implementation={p.relative_to(Path(__file__).parent.parent).as_posix():file_hash(p)
                        for p in Path(__file__).parent.parent.rglob('*') if p.suffix in ('.py','.html','.css','.js') and 'tests' not in p.parts}
        return digest({'contract':VERSION,'plan':self.doc,'dependencies':self.sources.used,'implementation':implementation})

    def report(self):
        return {'validation':'passed','validation_scope':'static_source','runtime_tested':False,
                'namespace':self.namespace,'fingerprint':self.fingerprint(),'plan':self.doc,'edges':self.edges,
                'warnings':self.warnings,'source_dependencies':self.sources.used,
                'context':str(self.sources.context_path) if self.sources.context_path else None}
