"""`world/` kaynagindan Victoria 3 oyun dosyalarini uretir.

Vanilla'yi ezme mekanizmasi dizine gore degisir; her biri oyunda dogrulandi:

  common/history/{states,pops,buildings}
      `.metadata/metadata.json` -> game_custom_data.replace_paths ile vanilla
      dizini tamamen yok sayilir. Bu yuzden kendi `tgc_` dosya isimlerimizi
      kullaniyoruz. Bunlar keyed database degil, calisan history script'leri;
      replace_paths olmadan vanilla'nin sahiplik/pop/bina kurulumu da calisir ve
      vanilla'nin geri kalan history'si (military_formations vb.) tutarsiz kalir.

  common/country_definitions
      Keyed database. Farkli isimli dosyada duz duplicate anahtar SESSIZCE ATILIR
      ("Duplicated key TUR will not be created"), vanilla kazanir. Dogru yol
      `REPLACE_OR_CREATE:TAG` oneki - kendi dosya adimizla override edebiliyoruz,
      vanilla'nin dokunmadigimiz 800 ulkesi yerinde kaliyor.

  map_data/state_regions
      Harita verisi; REPLACE_OR_CREATE yok. Tek bir state'i degistirmek icin o
      vanilla dosyasinin TAMAMINI ayni isimle yeniden uretmek gerekiyor.

Ciktilar:
    common/history/states/tgc_states.txt
    common/history/pops/tgc_pops_<bolge>.txt
    common/history/buildings/tgc_buildings_<bolge>.txt
    common/country_definitions/tgc_countries.txt
    localization/english/replace/tgc_generated_countries_l_english.yml
    map_data/state_regions/<vanilla dosya adi>.txt      (sadece yama varsa)
"""

from __future__ import annotations

import re
from collections import defaultdict
from functools import lru_cache
from dataclasses import dataclass
from typing import Any

from . import index as index_mod
from . import paths, pdx
from .world import BuildingSpec, CountrySpec, PopSpec, StateSpec, World, load_world

TAB = "\t"


@dataclass
class BuildReport:
    files: list[str]
    states_from_world: int
    states_inherited: int
    states_unowned: int
    countries_written: int
    warnings: list[str]


# ---------------------------------------------------------------------------
# Cozumleme: her state icin (owner -> province listesi)
# ---------------------------------------------------------------------------

def resolve_ownership(spec: StateSpec, entry: dict[str, Any]) -> dict[str, list[str]]:
    """StateSpec'i somut `{tag: [province...]}` haritasina cevirir."""
    all_provinces = list(entry["provinces"])
    if not spec.slices:
        return {}
    if len(spec.slices) == 1 and spec.slices[0].provinces is None:
        return {spec.slices[0].owner: all_provinces}

    assigned: dict[str, list[str]] = {}
    taken: set[str] = set()
    rest_owner: str | None = None

    for piece in spec.slices:
        if piece.provinces is None or piece.rest:
            rest_owner = piece.owner
            continue
        unknown = [p for p in piece.provinces if p not in all_provinces]
        if unknown:
            raise ValueError(
                f"{spec.name}: bu province'lar state'e ait degil -> {' '.join(unknown[:5])}"
            )
        assigned.setdefault(piece.owner, []).extend(piece.provinces)
        taken.update(piece.provinces)

    if rest_owner is not None:
        remainder = [p for p in all_provinces if p not in taken]
        if remainder:
            assigned.setdefault(rest_owner, []).extend(remainder)

    # Ayni province listede iki kez gecebiliyor (elle yazilmis kaynaklarda sik);
    # sirayi bozmadan tekilleştir.
    return {tag: list(dict.fromkeys(provinces)) for tag, provinces in assigned.items()}


def _split_pops_proportionally(
    pops: list[dict[str, Any]], ownership: dict[str, list[str]]
) -> dict[str, list[dict[str, Any]]]:
    """Miras alinan pop'lari sahiplerin province payina gore boler."""
    if len(ownership) <= 1:
        only = next(iter(ownership), None)
        return {only: pops} if only else {}

    total = sum(len(v) for v in ownership.values()) or 1
    out: dict[str, list[dict[str, Any]]] = {}
    for tag, provinces in ownership.items():
        share = len(provinces) / total
        scaled = []
        for pop in pops:
            size = int(round(pop.get("size", 0) * share))
            if size > 0:
                scaled.append({**pop, "size": size})
        out[tag] = scaled
    return out


# ---------------------------------------------------------------------------
# Pop uretimi
# ---------------------------------------------------------------------------

def _apply_pop_maps(
    pop: dict[str, Any],
    religion_map: dict[str, str],
    culture_map: dict[str, str],
    scale: float,
    culture_religion: dict[str, str],
) -> dict[str, Any] | None:
    culture = pop.get("culture")
    religion = pop.get("religion")

    # Din yazilmamissa oyun kulturun varsayilanini kullanir; donusumun onu da
    # yakalamasi icin acikca cozuyoruz.
    if religion is None and religion_map:
        religion = culture_religion.get(culture)

    culture = culture_map.get(culture, culture)
    if religion is not None:
        religion = religion_map.get(religion, religion)
        # Donusum sonrasi din, yeni kulturun varsayilaniyla ayniysa yazmaya gerek yok
        if religion == culture_religion.get(culture):
            religion = None

    size = int(round(pop.get("size", 0) * scale))
    if size <= 0:
        return None
    return {"culture": culture, "religion": religion, "pop_type": pop.get("pop_type"), "size": size}


def _split_pop_by_religion(
    pop: dict[str, Any],
    splits: dict[str, dict[str, float]],
    culture_religion: dict[str, str],
    culture_splits: dict[str, dict[str, dict[str, float]]] | None = None,
) -> list[dict[str, Any]]:
    """Bir pop'u kaynak dinine gore birden fazla dine boler.

    Karma nufuslu eyaletler icin: `{orthodox: {mujtahidiyya: .6, orthodox: .4}}`
    Bolusturme religion_map'ten ONCE calisir; ciktisi sonra map'ten gecer.
    En buyuk paya yuvarlama artigi verilir, boylece toplam nufus korunur.

    `culture_splits` verilirse pop'un KULTURUNE ozel tablo once denenir. Buna
    ihtiyac var cunku ayni dini paylasan iki grup ayni tarihi yasamamis
    olabilir: Yeni Dunya'da vanilla hem yerli Nahua'yi hem Iberyali
    yerlesimciyi "katolik" sayiyor, oysa bu evrende yerliyi donduren kimse
    olmadi - Katoliklik yalnizca Endulus'un kendi Hristiyan tebaasi kadar.
    """
    religion = pop.get("religion")
    if religion is None:
        religion = culture_religion.get(pop.get("culture"))
    table = None
    if culture_splits:
        table = (culture_splits.get(pop.get("culture")) or {}).get(religion)
    if table is None:
        table = splits.get(religion)
    if not table:
        return [pop]

    size = int(pop.get("size", 0))
    ordered = sorted(table.items(), key=lambda kv: (-kv[1], kv[0]))
    out: list[dict[str, Any]] = []
    handed_out = 0
    for target, ratio in ordered[1:]:
        piece = int(size * ratio)
        if piece > 0:
            out.append({**pop, "religion": target, "size": piece})
            handed_out += piece
    remainder = size - handed_out
    if remainder > 0:
        out.insert(0, {**pop, "religion": ordered[0][0], "size": remainder})
    return out or [pop]


def _pops_for_state(
    spec: StateSpec,
    entry: dict[str, Any],
    ownership: dict[str, list[str]],
    world: World,
    culture_religion: dict[str, str],
) -> dict[str, list[dict[str, Any]]]:
    directive = spec.pops

    if directive == "none" or not ownership:
        return {}

    # 1) Acik pop listesi
    if isinstance(directive, list):
        explicit = [
            {"culture": p.culture, "religion": p.religion, "pop_type": p.pop_type, "size": p.size}
            for p in directive
        ]
        primary = next(iter(ownership))
        return {primary: explicit}

    # 2) inherit (opsiyonel ayarlarla)
    options: dict[str, Any] = directive if isinstance(directive, dict) else {}
    local_religion_map = dict(options.get("religion_map") or {})
    local_culture_map = dict(options.get("culture_map") or {})
    local_splits = dict(options.get("religion_split") or {})
    local_scale = float(options.get("scale", 1.0))

    vanilla_pops: list[dict[str, Any]] = []
    for pops in entry["vanilla_pops"].values():
        vanilla_pops.extend(pops)
    if not vanilla_pops:
        return {}

    per_owner = _split_pops_proportionally(vanilla_pops, ownership)

    result: dict[str, list[dict[str, Any]]] = {}
    for tag, pops in per_owner.items():
        religion_map, culture_map, scale = world.maps_for(tag)
        religion_map.update(local_religion_map)
        culture_map.update(local_culture_map)
        splits = world.splits_for(tag)
        splits.update(local_splits)
        culture_splits = world.culture_splits_for(tag)
        scale *= local_scale
        converted = []
        for pop in pops:
            for piece in _split_pop_by_religion(pop, splits, culture_religion, culture_splits):
                mapped = _apply_pop_maps(
                    piece, religion_map, culture_map, scale, culture_religion
                )
                if mapped:
                    converted.append(mapped)
        if converted:
            result[tag] = converted
    return result


# ---------------------------------------------------------------------------
# Bina uretimi
# ---------------------------------------------------------------------------

_TAG_REF = re.compile(r'c:([A-Z0-9]{2,4})')
_TAG_SCOPE = re.compile(r'c:([A-Z0-9]{3})\s*\?=')


_OWNERSHIP_REGION = re.compile(r'region\s*=\s*"(STATE_[A-Z_]+)"')
_PM_BLOCK = re.compile(r'\n?[ \t]*activate_production_methods\s*=\s*\{[^}]*\}')
_PM_NAME = re.compile(r'"([a-z_0-9]+)"')


@lru_cache(maxsize=1)
def _vanilla_tech_tiers() -> dict[str, int]:
    """Vanilla `common/history/countries` icindeki tier'lar - yedek kaynak.

    world/ icinde `tech_tier` yazmayan ulkeler icin kullanilir; boylece
    dokunmadigimiz ulkeler vanilla uretim metotlarini aynen korur.
    """
    out: dict[str, int] = {}
    directory = paths.vanilla("common", "history", "countries")
    for file in sorted(directory.glob("*.txt")) if directory.is_dir() else []:
        text = file.read_text(encoding="utf-8-sig", errors="replace")
        tier = re.search(r"effect_starting_technology_tier_(\d)_tech", text)
        if not tier:
            continue
        for tag in set(_TAG_SCOPE.findall(text)):
            out.setdefault(tag, int(tier.group(1)))
    return out


def _available_technologies(tag: str, world: World) -> set[str]:
    """Bir ulkenin baslangicta arastirdigi teknolojiler.

    Once world/ icindeki `tech_tier`, yoksa vanilla'nin verdigi tier. Ikisi de
    yoksa bos kume - o ulke hicbir teknoloji gerektiren uretim metodunu
    calistiramaz, ki dogrusu da bu.
    """
    tier = world.countries[tag].tech_tier if tag in world.countries else None
    if tier is None:
        tier = _vanilla_tech_tiers().get(tag)
    if tier is None:
        return set()
    return _tier_technologies().get(tier, set())


@lru_cache(maxsize=1)
def _tech_eras() -> dict[str, str]:
    out: dict[str, str] = {}
    directory = paths.vanilla("common", "technology", "technologies")
    for file in sorted(directory.glob("*.txt")) if directory.is_dir() else []:
        root = pdx.parse_file(file)
        for name, _op, node in root.pairs:
            if isinstance(node, pdx.Node):
                era = node.get_str("era")
                if era:
                    out[name] = era
    return out


@lru_cache(maxsize=1)
def _tier_technologies() -> dict[int, set[str]]:
    """`effect_starting_technology_tier_N_tech` her tier icin ne veriyor?

    `add_era_researched = era_N` o donemin TUM teknolojilerini aciyor;
    `add_technology_researched = X` tek tek ekliyor.
    """
    eras: dict[str, set[str]] = defaultdict(set)
    for tech, era in _tech_eras().items():
        eras[era].add(tech)

    out: dict[int, set[str]] = {}
    source = paths.vanilla("common", "scripted_effects", "00_starting_inventions.txt")
    if not source.exists():
        return out
    root = pdx.parse_file(source)
    for name, _op, node in root.pairs:
        match = re.fullmatch(r"effect_starting_technology_tier_(\d)_tech", name)
        if not match or not isinstance(node, pdx.Node):
            continue
        techs: set[str] = set()
        for key, _o, value in node.pairs:
            if key == "add_era_researched" and isinstance(value, str):
                era = value
                # era_2 acildiysa era_1 de acilmis sayilir
                for candidate, members in eras.items():
                    if candidate <= era:
                        techs |= members
            elif key == "add_technology_researched" and isinstance(value, str):
                techs.add(value)
        out[int(match.group(1))] = techs
    return out


@lru_cache(maxsize=1)
def _pm_requirements() -> dict[str, list[str]]:
    """Uretim metodu -> onu acan teknolojiler."""
    out: dict[str, list[str]] = {}
    directory = paths.vanilla("common", "production_methods")
    for file in sorted(directory.glob("*.txt")) if directory.is_dir() else []:
        try:
            root = pdx.parse_file(file)
        except ValueError:
            continue
        for name, _op, node in root.pairs:
            if isinstance(node, pdx.Node):
                techs = node.get_list("unlocking_technologies")
                if techs:
                    out[name] = techs
    return out


def _sanitize_inherited_building(raw: str, tag: str, state_name: str, world: World) -> str:
    """Vanilla bina blogunu yeni sahibe gore guvenli hale getirir.

    Iki hata sinifini kapatir (ikisi de oyun log'unda `create_building effect`):

    1. CAPRAZ-EYALET SAHIPLIK. Vanilla'da bir bina baska bir eyaletteki
       bankaya/malikaneye ait olabiliyor (`region = "STATE_ILE_DE_FRANCE"`).
       Sahiplik yeniden dagitilinca o ulke artik orada toprak sahibi olmayabilir
       -> "Invalid state in STATE_X for TAG". Kendi eyaleti disina isaret eden
       sahiplik girdileri atiliyor. Blok tamamen bosalirsa BINA KOMPLE
       DUSURULUYOR (bos string dondurulur).

       Ilk denemede `add_ownership` kaldirilip yerine `levels` yaziliyordu,
       ama `building_trade_center` gibi bazi binalar `levels` kabul etmiyor
       ve oyun "Both levels and ownerships are undefined" demeye devam etti.
       Sahibi kalmayan bina zaten anlamsiz: dusurmek dogrusu.

    2. ARASTIRILMAMIS TEKNOLOJI. Vanilla'nin sectigi uretim metodu, bizim
       verdigimiz tech_tier'da olmayan bir teknoloji isteyebiliyor
       -> "must have invented Enclosure". Sahibin acamadigi metotlar atiliyor.

    NOT: Bu islem PARSER ile yapiliyor, satir kesip bicerek degil. Ilk surum
    satir bazliydi ve `building = "building_railway"` satirini de siliyordu
    (aradigi `building = {` desenine benzedigi icin) - sonuc bina adi olmayan
    bozuk bloklar oldu.
    """
    try:
        node = pdx.parse("x = " + raw).get_block("x")
    except ValueError:
        return raw
    if node is None:
        return raw

    ownership = node.get_block("add_ownership")
    if ownership is not None:
        surviving, dropped_levels = [], 0
        for key, op, value in ownership.pairs:
            if key == "building" and isinstance(value, pdx.Node):
                region = value.get_str("region")
                if region and region != state_name:
                    dropped_levels += value.get_int("levels") or 0
                    continue
            surviving.append((key, op, value))
        if surviving:
            ownership.pairs = surviving
        else:
            return ""   # sahibi kalmadi -> bina dusuruluyor

    available = _available_technologies(tag, world)
    requirements = _pm_requirements()
    methods = node.get_block("activate_production_methods")
    if methods is not None:
        keep = [
            name for name in methods.scalars
            if all(t in available for t in requirements.get(pdx.unquote(name), []))
        ]
        if keep:
            methods.scalars = keep
        else:
            node.remove("activate_production_methods")

    return node.dumps(0)


def _buildings_for_state(
    spec: StateSpec,
    entry: dict[str, Any],
    ownership: dict[str, list[str]],
    world: World,
) -> dict[str, list[str]]:
    """Sahip basina, dosyaya basilmaya hazir `create_building` govdeleri."""
    directive = spec.buildings
    if directive == "none" or not ownership:
        return {}

    if isinstance(directive, list):
        primary = next(iter(ownership))
        return {primary: [_render_building(b, primary, spec.name) for b in directive]}

    # inherit: vanilla binalarini al, ulke referanslarini yeni sahibe cevir
    result: dict[str, list[str]] = {}
    owners = list(ownership)
    vanilla_buildings = entry["vanilla_buildings"]
    if not vanilla_buildings:
        return {}

    # Vanilla'da state bolunmusse her parcayi sirayla yeni sahiplere dagit,
    # tek sahip varsa hepsini ona ver.
    flattened: list[dict[str, Any]] = []
    for old_tag, buildings in vanilla_buildings.items():
        for building in buildings:
            flattened.append({**building, "old_tag": old_tag})

    for i, building in enumerate(flattened):
        new_tag = owners[0] if len(owners) == 1 else owners[i % len(owners)]
        raw = building["raw"]
        raw = _TAG_REF.sub(lambda m: f"c:{new_tag}", raw)
        raw = _sanitize_inherited_building(raw, new_tag, spec.name, world)
        if raw:
            result.setdefault(new_tag, []).append(raw)
    return result


def _render_building(spec: BuildingSpec, tag: str, state_name: str) -> str:
    lines = ["{", f'{TAB}building="{spec.building}"']
    if spec.owner == "country":
        lines.append(f"{TAB}add_ownership={{")
        lines.append(f"{TAB}{TAB}country={{")
        lines.append(f'{TAB}{TAB}{TAB}country="c:{tag}"')
        lines.append(f"{TAB}{TAB}{TAB}levels={spec.levels or 1}")
        lines.append(f"{TAB}{TAB}}}")
        lines.append(f"{TAB}}}")
    else:
        owner_building = "building_manor_house" if spec.owner == "manor_house" else spec.owner
        lines.append(f"{TAB}add_ownership={{")
        lines.append(f"{TAB}{TAB}building={{")
        lines.append(f'{TAB}{TAB}{TAB}type="{owner_building}"')
        lines.append(f'{TAB}{TAB}{TAB}country="c:{tag}"')
        lines.append(f"{TAB}{TAB}{TAB}levels={spec.levels or 1}")
        lines.append(f'{TAB}{TAB}{TAB}region="{state_name}"')
        lines.append(f"{TAB}{TAB}}}")
        lines.append(f"{TAB}}}")
    lines.append(f"{TAB}reserves=1")
    if spec.production_methods:
        pms = " ".join(f'"{pm}"' for pm in spec.production_methods)
        lines.append(f"{TAB}activate_production_methods={{ {pms} }}")
    lines.append("}")
    return "\n".join(lines)


def _indent_block(text: str, levels: int) -> str:
    pad = TAB * levels
    return "\n".join(pad + line if line.strip() else line for line in text.splitlines())


# ---------------------------------------------------------------------------
# Ana build
# ---------------------------------------------------------------------------

def build(verbose: bool = True) -> BuildReport:
    ix = index_mod.load_index()
    world = load_world()
    states_index = ix["states"]
    culture_religion = ix.get("culture_religion", {})
    inherit_unlisted = str(world.defaults.get("unlisted", "inherit")) == "inherit"

    warnings: list[str] = []
    written: list[str] = []

    state_lines: list[str] = []
    pops_by_file: dict[str, list[str]] = defaultdict(list)
    buildings_by_file: dict[str, list[str]] = defaultdict(list)

    from_world = inherited = unowned = 0
    living_tags: set[str] = set()      # oyunda gercekten dogacak ulkeler
    decentralized = _decentralized_tags(world, ix)
    dropped_dec: list[str] = []
    owned_states: dict[str, set[str]] = defaultdict(set)   # tag -> sahip oldugu state'ler

    for name in sorted(states_index):
        entry = states_index[name]
        if entry["is_sea"]:
            continue

        spec = world.states.get(name)
        region_file = entry["file"]

        if spec is not None:
            from_world += 1
            try:
                ownership = resolve_ownership(spec, entry)
            except ValueError as exc:
                warnings.append(str(exc))
                continue
            homelands = spec.homelands or entry["vanilla_homelands"]
            pops = _pops_for_state(spec, entry, ownership, world, culture_religion)
            buildings = _buildings_for_state(spec, entry, ownership, world)
        elif inherit_unlisted:
            inherited += 1
            ownership = {
                tag: (provinces or entry["provinces"])
                for tag, provinces in entry["vanilla_owners"].items()
            }
            homelands = entry["vanilla_homelands"]
            pops = {tag: list(p) for tag, p in entry["vanilla_pops"].items() if p}
            # Miras alinan eyaletlerde de ayni iki hata sinifi olusabiliyor:
            # komsu eyalet el degistirdiyse buradaki caprazi sahiplik kirilir.
            buildings = {}
            for tag, blds in entry["vanilla_buildings"].items():
                cleaned = [
                    s for s in (
                        _sanitize_inherited_building(b["raw"], tag, name, world)
                        for b in blds
                    ) if s
                ]
                if cleaned:
                    buildings[tag] = cleaned
        else:
            unowned += 1
            continue

        if not ownership:
            unowned += 1
            continue

        living_tags.update(ownership)
        for tag in ownership:
            owned_states[tag].add(name)
        state_lines.append(_render_state_history(name, ownership, homelands))

        if pops:
            pops_by_file[region_file].append(_render_state_pops(name, pops))
        if buildings:
            rendered = _render_state_buildings(name, buildings, decentralized, dropped_dec)
            if rendered:
                buildings_by_file[region_file].append(rendered)

    # Onceki build'den kalan uretilmis dosyalari temizle (yalnizca kendi
    # basligimizi tasiyanlari); yoksa yeniden adlandirmalar birikip cakisir.
    for directory in (
        paths.mod("common", "history", "states"),
        paths.mod("common", "history", "pops"),
        paths.mod("common", "history", "buildings"),
        paths.mod("common", "history", "diplomacy"),
        paths.mod("common", "history", "population"),
        # NOT: history/countries icinde elle yazilmis tgc_minbar.txt de var;
        # _clean_generated yalnizca "OTOMATIK URETILDI" basligi tasiyanlari siler.
        paths.mod("common", "history", "countries"),
        paths.mod("common", "country_definitions"),
    ):
        _clean_generated(directory)

    # --- history/states (replace_paths ile vanilla dizini yok sayiliyor) -----
    body = "STATES = {\n" + "\n".join(state_lines) + "\n}\n"
    target = paths.mod("common", "history", "states", "tgc_states.txt")
    pdx.write_game_file(target, body)
    written.append(str(target.relative_to(paths.MOD_ROOT)))

    # --- history/pops -------------------------------------------------------
    for region_file, blocks in sorted(pops_by_file.items()):
        body = "POPS = {\n" + "\n".join(blocks) + "\n}\n"
        target = paths.mod("common", "history", "pops", f"tgc_pops_{region_file}")
        pdx.write_game_file(target, body)
        written.append(str(target.relative_to(paths.MOD_ROOT)))

    # --- history/buildings --------------------------------------------------
    for region_file, blocks in sorted(buildings_by_file.items()):
        body = "BUILDINGS = {\n" + "\n".join(blocks) + "\n}\n"
        target = paths.mod("common", "history", "buildings", f"tgc_buildings_{region_file}")
        pdx.write_game_file(target, body)
        written.append(str(target.relative_to(paths.MOD_ROOT)))

    # --- country_definitions ------------------------------------------------
    written.extend(_write_country_definitions(world, ix, warnings))

    # --- history/diplomacy (tabiiyet, rekabet, iliski) -----------------------
    written.extend(_write_diplomacy(world, warnings, living_tags))
    written.extend(_write_rivalries(world, warnings, living_tags))
    written.extend(_write_relations(world, warnings, living_tags))
    written.extend(_write_military_formations(world, warnings, living_tags, owned_states))

    # --- teknoloji ve okuryazarlik -------------------------------------------
    written.extend(_write_technology(world))
    written.extend(_write_population(world, warnings))

    # --- localization -------------------------------------------------------
    written.extend(_write_localization(world))

    # --- state_regions yamalari ---------------------------------------------
    written.extend(_write_state_region_patches(world, ix, warnings))

    report = BuildReport(
        files=written,
        states_from_world=from_world,
        states_inherited=inherited,
        states_unowned=unowned,
        countries_written=len(world.countries),
        warnings=warnings,
    )
    if verbose:
        print(f"{len(written)} dosya yazildi.")
        print(
            f"  world'den: {from_world} state | vanilla'dan miras: {inherited} | "
            f"sahipsiz/atlanan: {unowned}"
        )
        for warning in warnings:
            print(f"  UYARI: {warning}")
    return report


def _render_state_history(name: str, ownership: dict[str, list[str]], homelands: list[str]) -> str:
    lines = [f"{TAB}s:{name} = {{"]
    for tag, provinces in ownership.items():
        lines.append(f"{TAB*2}create_state = {{")
        lines.append(f"{TAB*3}country = c:{tag}")
        lines.append(f"{TAB*3}owned_provinces = {{ {' '.join(provinces)} }}")
        lines.append(f"{TAB*2}}}")
    for homeland in homelands:
        lines.append(f"{TAB*2}add_homeland = cu:{homeland}")
    lines.append(f"{TAB}}}")
    return "\n".join(lines)


def _render_state_pops(name: str, pops: dict[str, list[dict[str, Any]]]) -> str:
    lines = [f"{TAB}s:{name} = {{"]
    for tag, entries in pops.items():
        lines.append(f"{TAB*2}region_state:{tag} = {{")
        for pop in entries:
            lines.append(f"{TAB*3}create_pop = {{")
            if pop.get("pop_type"):
                lines.append(f"{TAB*4}pop_type = {pop['pop_type']}")
            lines.append(f"{TAB*4}culture = {pop['culture']}")
            if pop.get("religion"):
                lines.append(f"{TAB*4}religion = {pop['religion']}")
            lines.append(f"{TAB*4}size = {pop['size']}")
            lines.append(f"{TAB*3}}}")
        lines.append(f"{TAB*2}}}")
    lines.append(f"{TAB}}}")
    return "\n".join(lines)


def _decentralized_tags(world: World, ix: dict[str, Any]) -> set[str]:
    """country_type = decentralized olan her tag (mod tanimi vanilla'yi ezer)."""
    tags = {
        tag for tag, entry in ix["countries"].items()
        if entry.get("country_type") == "decentralized"
    }
    for tag, spec in world.countries.items():
        (tags.add if spec.country_type == "decentralized" else tags.discard)(tag)
    return tags


def _render_state_buildings(
    name: str, buildings: dict[str, list[str]], decentralized: set[str], dropped: list[str]
) -> str:
    """`decentralized` ulkelere BINA YAZILMAZ.

    Vic3'te decentralized ulkeler soyutlanmis nesnelerdir: ekonomileri,
    bina sistemleri ve insaat kuyruklari yoktur, motor onlar icin bu
    yapilari HIC TAHSIS ETMEZ. Vanilla'nin kendi kurulumunda decentralized
    bir ulkeye ait TEK BIR bina bile yoktur (dogrulandi: 0).

    Bir state decentralized bir ulkeye gecince `buildings: inherit` vanilla'nin
    binalarini oldugu gibi kopyaliyordu; sonuc, tahsis edilmemis bir diziye
    yazma ve ACILISTA CRASH (0xC0000005, yazma ihlali) idi.
    """
    lines = [f"{TAB}s:{name} = {{"]
    for tag, blocks in buildings.items():
        if tag in decentralized:
            dropped.append(f"{name}/{tag} ({len(blocks)})")
            continue
        lines.append(f"{TAB*2}region_state:{tag} = {{")
        for block in blocks:
            lines.append(f"{TAB*3}create_building=" + _indent_block(block, 3).lstrip("\t"))
        lines.append(f"{TAB*2}}}")
    lines.append(f"{TAB}}}")
    return "\n".join(lines)


def _clean_generated(directory) -> None:
    """Bu aracin daha once urettigi dosyalari siler; elle yazilanlara dokunmaz."""
    if not directory.is_dir():
        return
    marker = "OTOMATIK URETILDI"
    for file in directory.glob("*.txt"):
        try:
            head = file.read_text(encoding="utf-8-sig", errors="replace")[:400]
        except OSError:
            continue
        if marker in head:
            paths.assert_safe_write(file)
            file.unlink()


def _render_country(spec: CountrySpec) -> str:
    color = spec.color
    if isinstance(color, (list, tuple)):
        color_repr = "{ " + " ".join(str(c) for c in color) + " }"
    elif isinstance(color, str):
        color_repr = color if color.strip().startswith(("{", "rgb", "hsv")) else f"{{ {color} }}"
    else:
        color_repr = "{ 128 128 128 }"

    # REPLACE_OR_CREATE: vanilla'da varsa uzerine yazar, yoksa olusturur.
    # Bu onek olmadan farkli isimli dosyadaki duplicate anahtar sessizce atilir.
    lines = [f"REPLACE_OR_CREATE:{spec.tag} = {{", f"{TAB}color = {color_repr}", ""]
    lines.append(f"{TAB}country_type = {spec.country_type}")
    lines.append(f"{TAB}tier = {spec.tier}")
    lines.append("")
    if spec.cultures:
        lines.append(f"{TAB}cultures = {{ {' '.join(spec.cultures)} }}")
    # `religion` yazilmazsa oyun devlet dinini birincil kulturun varsayilanindan
    # turetir; Ictihat mezhepleri hicbir kulturun varsayilani olmadigi icin
    # bunu acikca yazmak zorundayiz.
    if spec.religion:
        lines.append(f"{TAB}religion = {spec.religion}")
    if spec.capital:
        lines.append(f"{TAB}capital = {spec.capital}")
    lines.append("}")
    return "\n".join(lines)


def _write_country_definitions(world: World, ix: dict[str, Any], warnings: list[str]) -> list[str]:
    """Ulke tanimlarini tek dosyada, `REPLACE_OR_CREATE:` onekiyle yazar.

    Vanilla'nin dokunmadigimiz ulkeleri kendi dosyalarinda kalir; sadece
    `world/countries` altinda tanimladiklarimiz override edilir ya da eklenir.
    Bu, vanilla dosyalarini kopyalamaktan cok daha guncelleme-dostu.
    """
    if not world.countries:
        return []

    blocks = [_render_country(world.countries[tag]) for tag in sorted(world.countries)]
    target = paths.mod("common", "country_definitions", "tgc_countries.txt")
    pdx.write_game_file(target, "\n\n".join(blocks) + "\n")
    written = [str(target.relative_to(paths.MOD_ROOT))]

    if str(world.defaults.get("unlisted", "inherit")) == "drop":
        warnings.append(
            "unlisted: drop ayarli ama vanilla ulkeleri hala yukleniyor. Tamamen "
            "kaldirmak icin metadata.json -> replace_paths listesine "
            "'common/country_definitions' eklemen ve tum ulkeleri world/ altinda "
            "tanimlaman gerekir."
        )

    for tag, spec in world.countries.items():
        if len(tag) != 3 or not tag.isalnum() or not tag.isupper():
            warnings.append(f"{tag}: ulke tag'i 3 karakter buyuk harf/rakam olmali")
        if spec.capital and spec.capital not in ix["states"]:
            warnings.append(f"{tag}: baskent '{spec.capital}' diye bir state yok")

    return written


DIPLOMACY_FILE = "00_subject_relationships.txt"


def _filter_vanilla_diplomacy(
    file_name: str,
    ours: set[str],
    warnings: list[str],
    living: set[str] | None = None,
) -> tuple[list[str], int]:
    """Vanilla diplomasi dosyasindan tasinabilir kismi dondurur.

    Kural 1: `c:TAG ?= { ... }` blogunun sahibi bizdense blok tamamen dusuruluyor
    (kendi kurulumumuzu yazacagiz); degilse yalnizca `country = c:BIZIMKI`
    hedefleyen ic ifadeler dusuruluyor. Boylece Ispanya-Kuba gibi ilgisiz
    vanilla kurulumlari yerinde kalir.

    Kural 2 (`living` verilirse): TARAFLARDAN BIRI ARTIK YOKSA kayit dusuruluyor.
    Yeniden dagitim vanilla'nin bircok ulkesini topraksiz birakiyor (ABD, Meksika,
    Brezilya, Ispanya, Prusya, Dogu Hindistan Sirketi...) ve oyun var olmayan
    ulkeler arasinda iliski kurmaya calisinca CRASH ediyor:

        [pdx_assert.cpp:637]: Assertion failed:
        Attempted to create relations for invalid countries!

    Doner: (korunan bloklarin metni, dusurulen ogelerin sayisi)
    """
    source = paths.vanilla("common", "history", "diplomacy", file_name)
    if not source.exists():
        warnings.append(f"vanilla {file_name} bulunamadi; yalnizca kendi kaydimiz yazildi")
        return [], 0

    kept: list[str] = []
    dropped = 0
    root = pdx.parse_file(source)
    # 00_truces.txt gibi dosyalar birden fazla DIPLOMACY blogu tasiyabiliyor.
    for _key, _op, top in root.pairs:
        if not isinstance(top, pdx.Node):
            continue
        for scoped, _o, block in top.pairs:
            if not isinstance(block, pdx.Node) or not scoped.startswith("c:"):
                continue
            actor = scoped.split(":", 1)[1]
            if actor in ours or (living is not None and actor not in living):
                dropped += 1
                continue
            surviving = []
            for key, _o2, value in block.pairs:
                if isinstance(value, pdx.Node):
                    target = (value.get_str("country") or "").removeprefix("c:")
                    if target and (target in ours
                                   or (living is not None and target not in living)):
                        dropped += 1
                        continue
                surviving.append((key, "=", value))
            if surviving:
                kept.append(f"{TAB}{scoped} ?= " + pdx.Node(pairs=surviving).dumps(1))
    return kept, dropped


def _write_diplomacy_file(
    file_name: str, kept: list[str], mine: list[str], dropped: int, warnings: list[str]
) -> list[str]:
    body = "DIPLOMACY = {\n"
    if kept:
        body += f"{TAB}# --- vanilla'dan devralinan kayitlar ---\n" + "\n".join(kept) + "\n\n"
    body += f"{TAB}# --- world/ ---\n" + "\n".join(mine) + "\n}\n"
    target = paths.mod("common", "history", "diplomacy", file_name)
    pdx.write_game_file(target, body)
    if dropped:
        warnings.append(
            f"{file_name}: world/ icinde tanimli tag'lere dokunan {dropped} vanilla "
            f"kayit atildi (senaryo bunlari gecersiz kiliyor)"
        )
    return [str(target.relative_to(paths.MOD_ROOT))]



# ---------------------------------------------------------------------------
# Ordular
#
# `common/history/military_formations` calistirilan bir script dizini: AYNI
# ISIMLI dosya vanilla'yi degistirir, farkli isimli dosya ona EKLENIR. Bu
# yuzden burada vanilla'nin 10 dosyasi ayni isimlerle, suzulmus halde yeniden
# yaziliyor.
#
# Neden gerekli: vanilla her birligi `state_region = s:STATE_X` ile belirli bir
# state'e koyuyor. Yeniden dagitim sonrasi o state artik o ulkenin degilse oyun
# "create_military_formation" hatasi veriyor (log'da ~185 satir).
#
# NEDEN replace_paths DEGIL: bu dizini replace_paths'e koyup bos birakmak
# vanilla'yi sildigi icin DUNYADA HIC ORDU KALMIYOR. Ayni hatayi
# `common/history/characters` icin de yapmistik; orada zaten hicbir state
# referansi yok, o yuzden o dizin tamamen vanilla'ya birakildi.
# ---------------------------------------------------------------------------

MILITARY_FORMATION_DIR = ("common", "history", "military_formations")


def _write_military_formations(
    world: World, warnings: list[str], living: set[str], owned: dict[str, set[str]]
) -> list[str]:
    source_dir = paths.vanilla(*MILITARY_FORMATION_DIR)
    if not source_dir.is_dir():
        warnings.append("vanilla military_formations dizini bulunamadi; ordular dokunulmadi")
        return []

    written: list[str] = []
    dropped_formations = dropped_units = 0
    for source in sorted(source_dir.glob("*.txt")):
        root = pdx.parse_file(source)
        countries: list[tuple[str, pdx.Node]] = []
        for _key, _op, top in root.pairs:
            if not isinstance(top, pdx.Node):
                continue
            for scoped, _o2, block in top.pairs:
                if not isinstance(block, pdx.Node) or not scoped.startswith("c:"):
                    continue
                tag = scoped.split(":", 1)[1]
                if tag not in living:
                    dropped_formations += sum(
                        1 for k, _o, v in block.pairs if isinstance(v, pdx.Node)
                    )
                    continue
                mine = owned.get(tag, set())
                surviving: list[tuple[str, str, Any]] = []
                for key, _o3, value in block.pairs:
                    if key != "create_military_formation" or not isinstance(value, pdx.Node):
                        surviving.append((key, "=", value))
                        continue
                    units: list[tuple[str, str, Any]] = []
                    for ukey, _o4, unit in value.pairs:
                        if ukey in ("combat_unit", "ship") and isinstance(unit, pdx.Node):
                            region = (unit.get_str("state_region") or "").removeprefix("s:")
                            if region and region not in mine:
                                dropped_units += 1
                                continue
                        units.append((ukey, "=", unit))
                    # Birligi kalmayan tesekkul kurulamaz.
                    if not any(k in ("combat_unit", "ship") for k, _o, _v in units):
                        dropped_formations += 1
                        continue
                    value.pairs = units
                    surviving.append((key, "=", value))
                if any(k == "create_military_formation" for k, _o, _v in surviving):
                    countries.append((scoped, pdx.Node(pairs=surviving)))

        body = "MILITARY_FORMATIONS = {\n"
        body += "\n".join(
            f"{TAB}{scoped} ?= " + node.dumps(1) for scoped, node in countries
        )
        body += "\n}\n"
        target = paths.mod(*MILITARY_FORMATION_DIR, source.name)
        pdx.write_game_file(target, body)
        written.append(str(target.relative_to(paths.MOD_ROOT)))

    if dropped_formations or dropped_units:
        warnings.append(
            f"military_formations: sahiplik degistigi icin {dropped_units} birlik ve "
            f"{dropped_formations} tesekkul atildi (vanilla dosyalari ayni isimle "
            f"yeniden yazildi)"
        )
    return written

def _pair_list(raw: Any, where: str, warnings: list[str]) -> list[tuple[str, str, Any]]:
    """`[[A, B], {between: [A, B], value: N}]` bicimlerini (A, B, ekstra) yapar."""
    out: list[tuple[str, str, Any]] = []
    for item in raw or []:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            out.append((str(item[0]), str(item[1]), None))
        elif isinstance(item, dict) and isinstance(item.get("between"), (list, tuple)):
            pair = item["between"]
            if len(pair) != 2:
                warnings.append(f"{where}: 'between' iki tag icermeli -> {item!r}")
                continue
            out.append((str(pair[0]), str(pair[1]), item))
        else:
            warnings.append(f"{where}: cift bekleniyordu -> {item!r}")
    return out


def _write_rivalries(world: World, warnings: list[str], living: set[str] | None = None) -> list[str]:
    """Baslangic rekabetlerini uretir (vanilla: 00_rivalries.txt).

    Vanilla her rekabeti iki yonlu yaziyor (NET->BEL ve BEL->NET); ayni sekilde
    yaziyoruz.
    """
    pairs = _pair_list(world.diplomacy.get("rivalries"), "_diplomacy.yml:rivalries", warnings)
    if not pairs:
        return []
    ours = set(world.countries)
    kept, dropped = _filter_vanilla_diplomacy("00_rivalries.txt", ours, warnings, living)

    by_actor: dict[str, list[str]] = defaultdict(list)
    for first, second, _extra in pairs:
        if living is not None and (first not in living or second not in living):
            warnings.append(
                f"_diplomacy.yml:rivalries: '{first}-{second}' atlandi - taraflardan "
                f"biri hicbir topraga sahip degil, oyunda dogmayacak"
            )
            continue
        by_actor[first].append(second)
        by_actor[second].append(first)

    mine: list[str] = []
    for actor in sorted(by_actor):
        lines = [f"{TAB}c:{actor} ?= {{"]
        for target in by_actor[actor]:
            lines.append(f"{TAB*2}create_diplomatic_pact = {{")
            lines.append(f"{TAB*3}country = c:{target}")
            lines.append(f"{TAB*3}type = rivalry")
            lines.append(f"{TAB*2}}}")
        lines.append(f"{TAB}}}")
        mine.append("\n".join(lines))
    return _write_diplomacy_file("00_rivalries.txt", kept, mine, dropped, warnings)


def _write_relations(world: World, warnings: list[str], living: set[str] | None = None) -> list[str]:
    """Baslangic iliski degerlerini uretir (vanilla: 00_relations.txt).

    `set_relations` iki yonlu calisir; vanilla da her cifti bir kez yaziyor.
    """
    pairs = _pair_list(world.diplomacy.get("relations"), "_diplomacy.yml:relations", warnings)
    if not pairs:
        return []
    ours = set(world.countries)
    kept, dropped = _filter_vanilla_diplomacy("00_relations.txt", ours, warnings, living)

    by_actor: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for first, second, extra in pairs:
        if living is not None and (first not in living or second not in living):
            warnings.append(
                f"_diplomacy.yml:relations: '{first}-{second}' atlandi - taraflardan "
                f"biri hicbir topraga sahip degil, oyunda dogmayacak"
            )
            continue
        by_actor[first].append((second, int((extra or {}).get("value", 0))))

    mine: list[str] = []
    for actor in sorted(by_actor):
        lines = [f"{TAB}c:{actor} ?= {{"]
        for target, value in by_actor[actor]:
            lines.append(f"{TAB*2}set_relations = {{ country = c:{target} value = {value} }}")
        lines.append(f"{TAB}}}")
        mine.append("\n".join(lines))
    return _write_diplomacy_file("00_relations.txt", kept, mine, dropped, warnings)


def _write_diplomacy(world: World, warnings: list[str], living: set[str] | None = None) -> list[str]:
    """Baslangic tabiiyetlerini `common/history/diplomacy` altina yazar.

    Bu dizin de calisan bir history script'i; farkli isimli dosyalar birbirini
    EZMEZ, hepsi calisir. Vanilla `c:TUR ?= { ... c:EGY protectorate }` gibi
    senaryomuzla celisen paktlar kuruyor ve history'de bir pakti geri alma
    efekti yok. Bu yuzden vanilla dosyasini AYNI ISIMLE yeniden uretiyoruz:
    vanilla icerigi okunur, `world/countries` altinda tanimladigimiz her tag'e
    dokunan paktlar atilir, kendi paktlarimiz eklenir. Boylece Ispanya-Kuba
    gibi ilgisiz vanilla kurulumlari yerinde kalir ve oyun guncellemesinde
    bayat kopya tasimayiz.
    """
    subjects = world.subjects()
    liberty = {
        tag: spec.liberty_desire
        for tag, spec in world.countries.items()
        if spec.liberty_desire is not None
    }
    if not subjects and not liberty:
        return []

    ours = set(world.countries)
    kept, dropped = _filter_vanilla_diplomacy(DIPLOMACY_FILE, ours, warnings, living)

    by_overlord: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for overlord, subject, subject_type in subjects:
        if living is not None and (overlord not in living or subject not in living):
            warnings.append(
                f"{subject}: tabiiyet atlandi - {overlord} ya da {subject} hicbir "
                f"topraga sahip degil"
            )
            continue
        by_overlord[overlord].append((subject, subject_type))

    mine: list[str] = []
    for overlord in sorted(by_overlord):
        lines = [f"{TAB}c:{overlord} ?= {{"]
        for subject, subject_type in by_overlord[overlord]:
            lines.append(f"{TAB*2}create_diplomatic_pact = {{")
            lines.append(f"{TAB*3}country = c:{subject}")
            lines.append(f"{TAB*3}type = {subject_type}")
            lines.append(f"{TAB*2}}}")
        lines.append(f"{TAB}}}")
        mine.append("\n".join(lines))

    for tag in sorted(liberty):
        mine.append(
            f"{TAB}c:{tag} ?= {{\n{TAB*2}add_liberty_desire = {liberty[tag]}\n{TAB}}}"
        )

    return _write_diplomacy_file(DIPLOMACY_FILE, kept, mine, dropped, warnings)


LITERACY_LEVELS = ("very_high", "high", "middling", "low", "very_low", "baseline")
_LITERACY_KEY = "effect_starting_pop_literacy_"


def _write_technology(world: World) -> list[str]:
    """Baslangic teknoloji seviyelerini `common/history/countries` altina yazar.

    EKLEMELI calisir, dosya adi cakismasina gerek yok: `effect_starting_technology_tier_N`
    yalnizca `add_technology_researched` / `add_era_researched` cagirir, yani iki
    dosya da calistiginda sonuc iki kumenin BIRLESIMI olur. Tier 1 daha dusuk
    tier'larin ustkumesi oldugu icin vanilla'nin tier 4'unun uzerine tier 1
    yazmak ulkeyi kesin olarak yukseltir; asagi cekmez.

    Bu yuzden bir ulkeyi GERILETMEK bu yolla mumkun degil - onun icin vanilla
    dosyasini ayni isimle ezmek gerekir. Senaryo Islam dunyasini yukseltip
    Avrupa'yi yerinde biraktigi icin buna ihtiyac yok.
    """
    tiers = {t: s.tech_tier for t, s in world.countries.items() if s.tech_tier is not None}
    if not tiers:
        return []
    lines = ["COUNTRIES = {"]
    for tag in sorted(tiers):
        lines.append(f"{TAB}c:{tag} ?= {{")
        lines.append(f"{TAB*2}effect_starting_technology_tier_{tiers[tag]}_tech = yes")
        lines.append(f"{TAB}}}")
    lines.append("}")
    target = paths.mod("common", "history", "countries", "tgc_technology.txt")
    pdx.write_game_file(target, "\n".join(lines) + "\n")
    return [str(target.relative_to(paths.MOD_ROOT))]


def _vanilla_population_files() -> dict[str, str]:
    """{TAG: vanilla dosya adi} - hangi ulkenin nufus kaydi hangi dosyada."""
    out: dict[str, str] = {}
    directory = paths.vanilla("common", "history", "population")
    if not directory.is_dir():
        return out
    for file in sorted(directory.glob("*.txt")):
        for tag in set(_TAG_SCOPE.findall(file.read_text(encoding="utf-8-sig", errors="replace"))):
            out.setdefault(tag, file.name)
    return out


def _write_population(world: World, warnings: list[str]) -> list[str]:
    """Baslangic okuryazarligini yazar.

    Teknolojinin aksine `set_pop_literacy` bir ATAMA. Vanilla'nin
    `tur - ottoman empire.txt` dosyasi da calisiyor ve hangisinin kazanacagi
    yukleme sirasina kalir - bu yuzden vanilla kaydi olan ulkeler icin o
    dosyayi AYNI ISIMLE yeniden uretiyoruz (dosyalar 3-5 satir, guncelleme
    riski yok). Vanilla kaydi olmayan ulkeler tek bir tgc_ dosyasina gider.
    """
    wanted = {t: s.literacy for t, s in world.countries.items() if s.literacy}
    if not wanted:
        return []

    written: list[str] = []
    vanilla_files = _vanilla_population_files()
    by_file: dict[str, list[str]] = defaultdict(list)
    standalone: list[str] = []
    for tag in sorted(wanted):
        if tag in vanilla_files:
            by_file[vanilla_files[tag]].append(tag)
        else:
            standalone.append(tag)

    # 1) Vanilla kaydi olanlar: o dosyanin tamamini yeniden uret.
    for file_name, tags in sorted(by_file.items()):
        root = pdx.parse_file(paths.vanilla("common", "history", "population", file_name))
        touched = False
        for _key, _op, top in root.pairs:
            if not isinstance(top, pdx.Node):
                continue
            for scoped, _o, block in top.pairs:
                tag = scoped.split(":", 1)[1] if scoped.startswith("c:") else None
                if tag not in tags or not isinstance(block, pdx.Node):
                    continue
                block.pairs = [p for p in block.pairs if not p[0].startswith(_LITERACY_KEY)]
                block.pairs.append((f"{_LITERACY_KEY}{wanted[tag]}", "=", "yes"))
                touched = True
        if not touched:
            warnings.append(f"{file_name}: okuryazarlik yazilacak ulke blogu bulunamadi")
            continue
        blocks = [
            f"{key} = " + value.dumps(0)
            for key, _op, value in root.pairs
            if isinstance(value, pdx.Node)
        ]
        target = paths.mod("common", "history", "population", file_name)
        pdx.write_game_file(target, "\n\n".join(blocks) + "\n")
        written.append(str(target.relative_to(paths.MOD_ROOT)))

    # 2) Vanilla kaydi olmayanlar: tek dosya yeter, cakisma yok.
    if standalone:
        lines = ["POPULATION = {"]
        for tag in standalone:
            lines.append(f"{TAB}c:{tag} ?= {{")
            lines.append(f"{TAB*2}{_LITERACY_KEY}{wanted[tag]} = yes")
            lines.append(f"{TAB}}}")
        lines.append("}")
        target = paths.mod("common", "history", "population", "tgc_population.txt")
        pdx.write_game_file(target, "\n".join(lines) + "\n")
        written.append(str(target.relative_to(paths.MOD_ROOT)))

    return written


def _write_localization(world: World) -> list[str]:
    english: list[str] = []
    turkish: list[str] = []
    for tag in sorted(world.countries):
        spec = world.countries[tag]
        if spec.name:
            english.append(f' {tag}: "{spec.name}"')
        if spec.adjective:
            english.append(f' {tag}_ADJ: "{spec.adjective}"')
        if spec.name_tr:
            turkish.append(f' {tag}: "{spec.name_tr}"')

    written: list[str] = []
    for language, entries in (("english", english), ("turkish", turkish)):
        if not entries:
            continue
        body = f"l_{language}:\n" + "\n".join(entries) + "\n"
        target = paths.mod(
            "localization", language, "replace",
            f"tgc_generated_countries_l_{language}.yml",
        )
        paths.assert_safe_write(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# OTOMATIK URETILDI - kaynak: world/countries/*.yml\n" + body,
            encoding="utf-8-sig",
            newline="\n",
        )
        written.append(str(target.relative_to(paths.MOD_ROOT)))
    return written


def _write_state_region_patches(
    world: World, ix: dict[str, Any], warnings: list[str]
) -> list[str]:
    """Vanilla state_region dosyalarini yamalayip mod'a tam kopyasini yazar.

    Vic3'te map_data/state_regions dosyalari dosya adiyla degistirilir; tek bir
    state'i degistirmek icin o dosyanin tamamini yeniden uretmek gerekir.
    """
    if not world.state_region_patches:
        return []

    scalar_keys = {
        "id", "subsistence_building", "city", "port", "farm", "mine", "wood",
        "arable_land", "naval_exit_id", "graphical_culture", "center_province",
    }
    list_keys = {"provinces", "impassable", "prime_land", "traits", "arable_resources"}

    files_to_patch: dict[str, list[str]] = defaultdict(list)
    for state_name in world.state_region_patches:
        entry = ix["states"].get(state_name)
        if entry is None:
            warnings.append(f"state_region yamasi: '{state_name}' diye bir state yok")
            continue
        files_to_patch[entry["file"]].append(state_name)

    written: list[str] = []
    for file_name, state_names in sorted(files_to_patch.items()):
        source = paths.vanilla("map_data", "state_regions", file_name)
        root = pdx.parse_file(source)
        for state_name in state_names:
            node = root.get_block(state_name)
            if node is None:
                warnings.append(f"{file_name}: '{state_name}' bulunamadi")
                continue
            for key, value in world.state_region_patches[state_name].items():
                if key in list_keys:
                    block = pdx.Node(scalars=[f'"{v}"' if not str(v).startswith('"') else str(v)
                                              for v in value])
                    node.set(key, block)
                elif key in scalar_keys:
                    text = str(value)
                    quoted = text if text.lstrip("-").isdigit() else f'"{text}"'
                    node.set(key, quoted)
                else:
                    warnings.append(f"{state_name}: '{key}' yamasi desteklenmiyor")

        blocks = []
        for name, _op, value in root.pairs:
            if isinstance(value, pdx.Node):
                blocks.append(f"{name} = " + value.dumps(indent=0, inline_scalars=True))
        target = paths.mod("map_data", "state_regions", file_name)
        pdx.write_game_file(target, "\n\n".join(blocks) + "\n")
        written.append(str(target.relative_to(paths.MOD_ROOT)))

    return written
