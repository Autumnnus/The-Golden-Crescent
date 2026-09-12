"""Read installed definitions, assets and optional scenario context. No Atlas import."""
import hashlib
import json
from pathlib import Path
from vic3 import pdx
from vic3.paths import MOD, VANILLA


class FlavorError(ValueError):
    pass


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def writable(path):
    path = Path(path).resolve()
    if VANILLA == path or VANILLA in path.parents or not (path == MOD or MOD in path.parents):
        raise FlavorError(f'Çıktı yalnız mod çalışma klasörüne yazılabilir: {path}')
    return path


TABLES = {
    'countries': 'common/country_definitions', 'cultures': 'common/cultures',
    'religions': 'common/religions', 'laws': 'common/laws',
    'technologies': 'common/technology/technologies', 'buildings': 'common/buildings',
    'modifiers': 'common/static_modifiers', 'journal_groups': 'common/journal_entry_groups',
    'media': 'gfx/media_aliases', 'events': 'events',
    'journals': 'common/journal_entries', 'states': 'map_data/state_regions',
    'on_actions': 'common/on_actions', 'scripted_effects': 'common/scripted_effects',
}


class Sources:
    def __init__(self, context=None):
        self.tables = {}; self.used = {}; self.context = None; self.context_path = None; self.countries_used=set()
        for kind, directory in TABLES.items():
            files = {}
            for root in (VANILLA, MOD):
                for path in sorted((root / directory).rglob('*.txt')):
                    files[path.relative_to(root).as_posix()] = path
            entries = {}
            for path in files.values():
                for key, node in pdx.parse_file(path).pairs():
                    if isinstance(node, pdx.Node):
                        entries[key.removeprefix('REPLACE_OR_CREATE:')] = (path, node)
            self.tables[kind] = entries
        if context:
            self.context_path = Path(context).resolve()
            self.context = json.loads(self.context_path.read_text(encoding='utf-8-sig'))
            if not isinstance(self.context, dict) or self.context.get('version') != 2 or self.context.get('validation') != 'passed':
                raise FlavorError('Bağlam tam ve doğrulanmış bir v2 scenario-report.json olmalı.')
            if not isinstance(self.context.get('countries'), dict) or not isinstance(self.context.get('states'), dict):
                raise FlavorError('Bağlam ülke ve eyalet raporlarını içermeli; ülke filtresi kullanmayın.')
            self.touch(self.context_path)
        for relative in ('common/on_actions/_on_actions.md', 'common/on_actions/00_code_on_actions.txt',
                         'events/canal_events.txt', 'common/journal_entries/00_canals.txt',
                         'common/journal_entries/00_acw_entries.txt', 'events/indochina.txt',
                         'events/bic_breakup.txt', 'events/1848.txt', 'gfx/media_aliases/media_aliases.txt'):
            path = VANILLA / relative
            if not path.is_file():
                raise FlavorError(f'Desteklenen kaynak sözleşmesi bulunamadı: {relative}')
            self.touch(path)

    def touch(self, path):
        path = Path(path).resolve(); self.used[str(path)] = file_hash(path)
        return path

    def require(self, kind, key):
        if not isinstance(key, str) or key not in self.tables[kind]:
            if kind == 'countries' and isinstance(key, str) and self.context and key in self.context['countries']:
                return None
            raise FlavorError(f'Bilinmeyen {kind} kimliği: {key!r}; catalog ile sorgulayın.')
        path, node = self.tables[kind][key]; self.touch(path)
        return node

    def country(self, key):
        self.require('countries', key)
        self.countries_used.add(key)
        if self.context and key not in self.context['countries']:
            raise FlavorError(f'{key}: seçilen senaryo bağlamında toprağı olan bir ülke değil.')

    def asset(self, relative):
        if not isinstance(relative, str) or not relative.startswith('gfx/') or '..' in Path(relative).parts or '\\' in relative:
            raise FlavorError(f'GFX yolu gfx/ altında olmalı: {relative!r}')
        for root in (MOD, VANILLA):
            p = root / relative
            if p.is_file(): return self.touch(p)
        raise FlavorError(f'GFX dosyası bulunamadı: {relative}')

    def media(self, key, seen=None):
        seen = set() if seen is None else seen
        if key in seen: raise FlavorError(f'Medya fallback döngüsü: {key}')
        seen.add(key); node = self.require('media', key)
        for field in ('video', 'texture'):
            if node.get_str(field): self.asset(node.get_str(field))
        if node.get_str('fallback'): self.media(node.get_str('fallback'), seen)
        return node

    def query(self, kind, query='', limit=20, offset=0):
        if kind == 'icons':
            names = sorted({p.relative_to(root).as_posix() for root in (VANILLA, MOD)
                            for p in (root/'gfx/interface/icons').rglob('*.dds') if query.lower() in str(p).lower()})
            rows = [{'id': k} for k in names[offset:offset+limit]]
        else:
            names = sorted(k for k in self.tables[kind] if query.lower() in k.lower())
            rows = [{'id': k, 'source': str(self.tables[kind][k][0]),
                     'script': pdx.dumps(self.tables[kind][k][1])} for k in names[offset:offset+limit]]
        return {'kind': kind, 'total': len(names), 'items': rows,
                'next_offset': offset+limit if offset+limit < len(names) else None}
