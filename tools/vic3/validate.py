"""Kaynak veriyi ve uretilmis oyun dosyalarini dogrular.

Amac: oyunu acmadan once yakalanabilecek her hatayi burada yakalamak.
Kontroller iki grupta:
  - kaynak (world/): tanimsiz tag, olmayan kultur/din, eksik province, ...
  - cikti (common/, map_data/): ayni state'in iki kez tanimlanmasi, brace hatasi
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any

from . import index as index_mod
from . import paths, pdx
from .build import resolve_ownership
from .world import PopSpec, World, WorldError, load_world


@dataclass
class Issue:
    level: str  # "error" | "warn"
    where: str
    message: str

    def __str__(self) -> str:
        badge = "HATA" if self.level == "error" else "uyari"
        return f"[{badge}] {self.where}: {self.message}"


@dataclass
class Result:
    issues: list[Issue] = field(default_factory=list)

    def error(self, where: str, message: str) -> None:
        self.issues.append(Issue("error", where, message))

    def warn(self, where: str, message: str) -> None:
        self.issues.append(Issue("warn", where, message))

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.level == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.level == "warn"]


def validate(check_output: bool = True) -> Result:
    result = Result()
    ix = index_mod.load_index()

    try:
        world = load_world()
    except WorldError as exc:
        result.error("world/", str(exc))
        return result

    _check_states(world, ix, result)
    _check_countries(world, ix, result)
    _check_capitals(world, ix, result)
    _check_dead_diplomacy(world, ix, result)
    _check_decentralized_buildings(world, ix, result)
    _check_subjects(world, ix, result)
    _check_diplomacy(world, ix, result)
    _check_coverage(world, ix, result)
    _check_legacy_conflicts(result)
    _check_localization(result)
    if check_output:
        _check_generated_files(result)
    return result


_LOC_KEY = re.compile(r'^\s*([A-Za-z0-9_]+)\s*:\s*\d*\s*"')


def _check_localization(result: Result) -> None:
    """Mod icindeki localization dosyalari arasinda ayni anahtar iki kez var mi?

    Oyun bunu `Duplicate localization key` uyarisiyla loglar ve hangisinin
    kazanacagi yukleme sirasina kalir.
    """
    loc_root = paths.mod("localization")
    if not loc_root.is_dir():
        return
    seen: dict[tuple[str, str], str] = {}
    for file in sorted(loc_root.rglob("*.yml")):
        relative = str(file.relative_to(paths.MOD_ROOT))
        language = file.parent.name if file.parent.name != "replace" else file.parent.parent.name
        for line in file.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            match = _LOC_KEY.match(line)
            if not match:
                continue
            key = (language, match.group(1))
            if key in seen and seen[key] != relative:
                result.error(
                    relative,
                    f"'{match.group(1)}' anahtari {seen[key]} icinde de tanimli "
                    f"(oyun 'Duplicate localization key' uyarisi verir)",
                )
            seen.setdefault(key, relative)


# ---------------------------------------------------------------------------

def _known_tags(world: World, ix: dict[str, Any]) -> set[str]:
    inherit = str(world.defaults.get("unlisted", "inherit")) == "inherit"
    tags = set(world.countries)
    if inherit:
        tags |= set(ix["countries"])
    return tags


def _check_states(world: World, ix: dict[str, Any], result: Result) -> None:
    states_index = ix["states"]
    valid = ix["valid"]
    tags = _known_tags(world, ix)
    cultures = set(valid["cultures"])
    religions = set(valid["religions"])
    pop_types = set(valid["pop_types"])
    buildings = set(valid["buildings"])
    production_methods = set(valid["production_methods"])

    for name, spec in world.states.items():
        where = f"{spec.source_file}:{name}"
        entry = states_index.get(name)
        if entry is None:
            matches = index_mod.find_states(name.removeprefix("STATE_"), ix, limit=3)
            hint = f" (bunu mu demek istedin: {', '.join(matches)})" if matches else ""
            result.error(where, f"boyle bir state yok{hint}")
            continue
        if entry["is_sea"]:
            result.error(where, "deniz state'ine sahiplik atanamaz")
            continue

        for piece in spec.slices:
            if piece.owner not in tags:
                result.error(where, f"tanimsiz ulke tag'i '{piece.owner}'")

        try:
            ownership = resolve_ownership(spec, entry)
        except ValueError as exc:
            result.error(where, str(exc))
            continue

        covered = {p for provinces in ownership.values() for p in provinces}
        missing = [p for p in entry["provinces"] if p not in covered]
        if missing and len(spec.slices) > 1:
            result.warn(
                where,
                f"{len(missing)} province hicbir sahibe atanmadi (ornek: {' '.join(missing[:3])})",
            )

        cross, within = _duplicate_provinces(spec, entry)
        if cross:
            result.error(where, f"ayni province birden fazla sahipte: {' '.join(cross[:5])}")
        if within:
            result.warn(
                where,
                f"province listesinde tekrar eden {len(within)} kayit "
                f"(build sirasinda tekillestiriliyor): {' '.join(within[:5])}",
            )

        for homeland in spec.homelands:
            if homeland not in cultures:
                result.error(where, f"olmayan kultur (homeland) '{homeland}'")

        if isinstance(spec.pops, list):
            for pop in spec.pops:
                _check_pop(pop, where, cultures, religions, pop_types, result)
        elif isinstance(spec.pops, dict):
            for old, new in (spec.pops.get("religion_map") or {}).items():
                if new not in religions:
                    result.error(where, f"religion_map hedefi '{new}' tanimsiz")
                if old not in religions:
                    result.warn(where, f"religion_map kaynagi '{old}' vanilla'da yok")
            for old, new in (spec.pops.get("culture_map") or {}).items():
                if new not in cultures:
                    result.error(where, f"culture_map hedefi '{new}' tanimsiz")

        if isinstance(spec.buildings, list):
            for building in spec.buildings:
                if building.building not in buildings:
                    result.error(where, f"olmayan bina '{building.building}'")
                for pm in building.production_methods:
                    if pm not in production_methods:
                        result.error(where, f"olmayan production method '{pm}'")


def _check_pop(
    pop: PopSpec,
    where: str,
    cultures: set[str],
    religions: set[str],
    pop_types: set[str],
    result: Result,
) -> None:
    if pop.culture not in cultures:
        result.error(where, f"olmayan kultur '{pop.culture}'")
    if pop.religion and pop.religion not in religions:
        result.error(where, f"olmayan din '{pop.religion}'")
    if pop.pop_type and pop.pop_type not in pop_types:
        result.error(where, f"olmayan pop_type '{pop.pop_type}'")
    if pop.size <= 0:
        result.error(where, f"pop boyutu pozitif olmali ({pop.size})")


def _duplicate_provinces(spec: Any, entry: dict[str, Any]) -> tuple[list[str], list[str]]:
    """(farkli sahipler arasinda tekrar edenler, ayni liste icinde tekrar edenler)."""
    within: list[str] = []
    owner_sets: list[set[str]] = []

    for piece in spec.slices:
        provinces = piece.provinces
        if provinces is None:
            continue
        seen: set[str] = set()
        for province in provinces:
            if province in seen:
                within.append(province)
            seen.add(province)
        owner_sets.append(seen)

    cross: list[str] = []
    for i, first in enumerate(owner_sets):
        for second in owner_sets[i + 1:]:
            cross.extend(sorted(first & second))
    return cross, within


_LITERACY_LEVELS = ("very_high", "high", "middling", "low", "very_low", "baseline")


def _effective_ownership(world: World, ix: dict[str, Any]) -> dict[str, set[str]]:
    """Oyunda gercekten kimin neye sahip olacagi: world/ + miras alinanlar.

    `unlisted: inherit` ayarliyken world/states'te YAZMAYAN her state vanilla
    sahibinde kalir; baskent kontrolu bunu da saymali.
    """
    owned: dict[str, set[str]] = defaultdict(set)
    for name, spec in world.states.items():
        for piece in spec.slices:
            owned[piece.owner].add(name)
    if str(world.defaults.get("unlisted", "inherit")) == "inherit":
        for name, entry in ix["states"].items():
            if entry["is_sea"] or name in world.states:
                continue
            for tag in entry.get("vanilla_owners", {}):
                owned[tag].add(name)
    return owned


def _check_dead_diplomacy(world: World, ix: dict[str, Any], result: Result) -> None:
    """Uretilen diplomasi dosyalari artik var olmayan bir ulkeye deginiyor mu?

    Yeniden dagitim vanilla'nin bircok ulkesini topraksiz birakiyor (ABD,
    Meksika, Brezilya, Ispanya, Prusya, Dogu Hindistan Sirketi...). Vanilla'nin
    o ulkelere ait iliski/rekabet/pakt kayitlari tasinirsa oyun var olmayan
    ulkeler arasinda iliski kurmaya calisir ve ACILISTA COKER:

        [pdx_assert.cpp:637]: Assertion failed:
        Attempted to create relations for invalid countries!

    Uretici bunlari eliyor (build._filter_vanilla_diplomacy); burasi elemenin
    gercekten tuttugunun kaniti.
    """
    folder = paths.mod("common", "history", "diplomacy")
    if not folder.is_dir():
        return
    alive = {tag for tag, states in _effective_ownership(world, ix).items() if states}
    for path in sorted(folder.glob("*.txt")):
        dead: Counter[str] = Counter()
        for tag in re.findall(r"c:([A-Za-z_][A-Za-z0-9_]*)\b", path.read_text(encoding="utf-8-sig")):
            if tag not in alive:
                dead[tag] += 1
        if dead:
            listed = ", ".join(f"{tag} x{n}" for tag, n in dead.most_common(6))
            result.error(
                f"common/history/diplomacy/{path.name}",
                f"topraksiz ulkeye {sum(dead.values())} referans ({listed}) "
                f"-> 'invalid countries' assert'i, acilista crash",
            )


def _check_decentralized_buildings(world: World, ix: dict[str, Any], result: Result) -> None:
    """`decentralized` bir ulkeye bina yazilmis mi?

    Vic3'te decentralized ulkeler soyutlanmis nesnelerdir: ekonomileri, bina
    sistemleri ve insaat kuyruklari yoktur ve motor bu yapilari onlar icin HIC
    TAHSIS ETMEZ. Vanilla'nin butun kurulumunda decentralized bir ulkeye ait
    tek bir bina yoktur - dogrulandi, sayi tam olarak sifir.

    Bir state decentralized bir ulkeye gecince `buildings: inherit` vanilla'nin
    binalarini oldugu gibi kopyaliyordu. Sonuc tahsis edilmemis bir diziye yazma
    ve acilista sessiz crash idi:

        Unhandled Exception C0000005 (EXCEPTION_ACCESS_VIOLATION)
        victoria3.exe+0xC03167, YAZMA

    Hicbir log satiri sebebi sylemiyordu; yalnizca minidump'taki yazma ihlali
    ve vanilla ile karsilastirma gosterdi.
    """
    folder = paths.mod("common", "history", "buildings")
    if not folder.is_dir():
        return
    decentralized = {
        tag for tag, entry in ix["countries"].items()
        if entry.get("country_type") == "decentralized"
    }
    for tag, spec in world.countries.items():
        (decentralized.add if spec.country_type == "decentralized" else decentralized.discard)(tag)

    offenders: Counter[str] = Counter()
    for path in sorted(folder.glob("*.txt")):
        for _key, _op, top in pdx.parse_file(path).pairs:
            if not isinstance(top, pdx.Node):
                continue
            for state_key, _o2, state in top.pairs:
                if not isinstance(state, pdx.Node) or not state_key.startswith("s:"):
                    continue
                for region_key, _o3, region in state.pairs:
                    if not isinstance(region, pdx.Node):
                        continue
                    tag = region_key.removeprefix("region_state:")
                    if tag in decentralized:
                        offenders[tag] += sum(
                            1 for k, _o4, _v in region.pairs if k == "create_building"
                        )
    if offenders:
        listed = ", ".join(f"{tag} x{n}" for tag, n in offenders.most_common(8))
        result.error(
            "common/history/buildings",
            f"decentralized ulkelere {sum(offenders.values())} bina yazilmis "
            f"({listed}) -> motor bu ulkeler icin bina yapisi tahsis etmez, "
            f"acilista access violation",
        )


def _check_capitals(world: World, ix: dict[str, Any], result: Result) -> None:
    """Topraga sahip HER ulkenin baskenti kendi topragi icinde mi?

    Bu kontrol yalnizca world/countries icin degil, oyunda dogacak butun
    ulkeler icin yapilir - cunku yeniden dagitim vanilla bir ulkenin
    baskentini baskasina tasidiginda o ulkenin `capital` nesnesi GECERSIZ
    kalir ve `capital`'a dokunan her script COKER:

        Error: Event target link 'capital' returned an invalid object
        Script location: common/dynamic_country_names/00_dynamic_country_names.txt

    Oyun bunu yalnizca crash aninda soyluyor; burada onceden yakaliyoruz.
    """
    owned = _effective_ownership(world, ix)
    for tag, states in sorted(owned.items()):
        if not states:
            continue
        spec = world.countries.get(tag)
        capital = (spec.capital if spec and spec.capital
                   else (ix["countries"].get(tag) or {}).get("capital"))
        where = f"{spec.source_file}:{tag}" if spec else f"vanilla:{tag}"
        if not capital:
            result.error(where, "topraga sahip ama baskenti tanimsiz")
        elif capital not in states:
            sample = " ".join(sorted(s.removeprefix("STATE_") for s in states)[:4])
            result.error(
                where,
                f"baskenti '{capital.removeprefix('STATE_')}' kendi topragi degil "
                f"(sahip oldugu: {sample}) -> oyunda gecersiz capital, crash riski",
            )


def _check_countries(world: World, ix: dict[str, Any], result: Result) -> None:
    cultures = set(ix["valid"]["cultures"])
    country_types = set(ix["valid"]["country_types"]) or {
        "recognized", "unrecognized", "colonial", "decentralized"
    }
    owned_by = _effective_ownership(world, ix)

    for tag, spec in world.countries.items():
        where = f"{spec.source_file}:{tag}"
        if len(tag) != 3 or not tag.isupper() or not tag.isalnum():
            result.error(where, "tag 3 karakterli buyuk harf/rakam olmali")
        if spec.country_type not in country_types:
            result.error(where, f"gecersiz country_type '{spec.country_type}'")
        for culture in spec.cultures:
            if culture not in cultures:
                result.error(where, f"olmayan primary culture '{culture}'")
        if not spec.capital:
            result.warn(where, "baskent tanimli degil")
        elif spec.capital not in ix["states"]:
            result.error(where, f"baskent '{spec.capital}' diye bir state yok")
        # Baskentin ulkeye ait olup olmadigini _check_capitals dogruluyor
        if not spec.name:
            result.warn(where, "localization ismi yok (world/countries icinde 'name:')")
        if spec.tech_tier is not None and not 1 <= spec.tech_tier <= 7:
            result.error(where, f"tech_tier 1-7 arasi olmali (1 = en ileri), verilen {spec.tech_tier}")
        if spec.literacy and spec.literacy not in _LITERACY_LEVELS:
            result.error(
                where,
                f"gecersiz literacy '{spec.literacy}' (gecerliler: {', '.join(_LITERACY_LEVELS)})",
            )
        religions = set(ix["valid"]["religions"])
        if spec.religion and spec.religion not in religions:
            result.error(where, f"devlet dini '{spec.religion}' tanimsiz")
        if not spec.religion and (spec.religion_map or spec.religion_split):
            result.warn(
                where,
                "pop dinleri donusturuluyor ama 'religion:' yok -> devlet dini "
                "birincil kulturun vanilla dininde kalir",
            )
        for old, new in spec.religion_map.items():
            if new not in religions:
                result.error(where, f"religion_map hedefi '{new}' tanimsiz")
            if old not in religions:
                result.warn(where, f"religion_map kaynagi '{old}' hicbir yerde tanimli degil")
        for culture, table in spec.culture_religion_split.items():
            if culture not in cultures:
                result.error(where, f"culture_religion_split kulturu '{culture}' tanimsiz")
            for source_religion, targets in table.items():
                if source_religion not in religions:
                    result.warn(where, f"culture_religion_split kaynagi '{source_religion}' tanimli degil")
                for target in targets:
                    if target not in religions:
                        result.error(where, f"culture_religion_split hedefi '{target}' tanimsiz")
        for source_religion, targets in spec.religion_split.items():
            if source_religion not in religions:
                result.warn(
                    where, f"religion_split kaynagi '{source_religion}' tanimli degil"
                )
            for target in targets:
                if target not in religions:
                    result.error(where, f"religion_split hedefi '{target}' tanimsiz")
        for old, new in spec.culture_map.items():
            if new not in cultures:
                result.error(where, f"culture_map hedefi '{new}' tanimsiz")


def _subject_types() -> set[str]:
    """Vanilla `common/subject_types` anahtarlari -> {puppet, vassal, ...}."""
    directory = paths.vanilla("common", "subject_types")
    types: set[str] = set()
    if not directory.is_dir():
        return types
    for file in sorted(directory.glob("*.txt")):
        try:
            node = pdx.parse_file(file)
        except ValueError:
            continue
        for key, _op, value in node.pairs:
            if isinstance(value, pdx.Node) and key.startswith("subject_type_"):
                types.add(key.removeprefix("subject_type_"))
    return types


def _check_subjects(world: World, ix: dict[str, Any], result: Result) -> None:
    """Baslangic tabiiyetleri: gecerli tip, var olan metbu, dongusuz zincir."""
    tags = _known_tags(world, ix)
    valid_types = _subject_types()
    owned_by: dict[str, set[str]] = defaultdict(set)
    for name, spec in world.states.items():
        for piece in spec.slices:
            owned_by[piece.owner].add(name)

    parent: dict[str, str] = {}
    for tag, spec in world.countries.items():
        if not spec.overlord:
            continue
        where = f"{spec.source_file}:{tag}"
        parent[tag] = spec.overlord
        if spec.overlord == tag:
            result.error(where, "ulke kendi metbusu olamaz")
        if spec.overlord not in tags:
            result.error(where, f"tanimsiz metbu tag'i '{spec.overlord}'")
        if valid_types and spec.subject_type not in valid_types:
            hint = ", ".join(sorted(valid_types))
            result.error(
                where, f"gecersiz subject_type '{spec.subject_type}' (gecerliler: {hint})"
            )
        if not owned_by.get(tag) and tag not in ix["countries"]:
            result.error(where, "tabii ulkenin hic state'i yok; oyunda hic dogmaz")
        if spec.liberty_desire is not None and not 0 <= spec.liberty_desire <= 100:
            result.error(where, f"liberty_desire 0-100 arasi olmali ({spec.liberty_desire})")

    for tag in parent:
        seen = [tag]
        cursor = parent.get(tag)
        while cursor is not None and cursor not in seen:
            seen.append(cursor)
            cursor = parent.get(cursor)
        if cursor is not None:
            spec = world.countries[tag]
            result.error(
                f"{spec.source_file}:{tag}",
                f"tabiiyet zincirinde dongu: {' -> '.join(seen)} -> {cursor}",
            )


def _check_diplomacy(world: World, ix: dict[str, Any], result: Result) -> None:
    """world/_diplomacy.yml: tanimsiz tag, kendi kendiyle cift, tekrar, aralik."""
    if not world.diplomacy:
        return
    tags = _known_tags(world, ix)
    where = "world/_diplomacy.yml"

    for section in ("rivalries", "relations"):
        seen: set[frozenset[str]] = set()
        for item in world.diplomacy.get(section) or []:
            if isinstance(item, dict):
                pair, value = item.get("between"), item.get("value")
            elif isinstance(item, (list, tuple)):
                pair, value = item, None
            else:
                result.error(f"{where}:{section}", f"cift bekleniyordu -> {item!r}")
                continue
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                result.error(f"{where}:{section}", f"iki tag gerekli -> {item!r}")
                continue
            first, second = str(pair[0]), str(pair[1])
            for tag in (first, second):
                if tag not in tags:
                    result.error(f"{where}:{section}", f"tanimsiz ulke tag'i '{tag}'")
            if first == second:
                result.error(f"{where}:{section}", f"'{first}' kendisiyle eslestirilmis")
            key = frozenset((first, second))
            if key in seen:
                result.error(
                    f"{where}:{section}", f"'{first}-{second}' cifti iki kez tanimli"
                )
            seen.add(key)
            if section == "relations":
                if value is None:
                    result.error(f"{where}:relations", f"'{first}-{second}' icin 'value' yok")
                elif not -100 <= int(value) <= 100:
                    result.error(
                        f"{where}:relations", f"'{first}-{second}' degeri -100..100 disinda"
                    )

    for key in world.diplomacy:
        if key not in ("rivalries", "relations"):
            result.warn(where, f"'{key}' bolumu taninmiyor, yok sayilacak")


def _check_coverage(world: World, ix: dict[str, Any], result: Result) -> None:
    land = [n for n, e in ix["states"].items() if not e["is_sea"]]
    defined = set(world.states)
    inherit = str(world.defaults.get("unlisted", "inherit")) == "inherit"
    if not inherit:
        missing = [n for n in land if n not in defined]
        if missing:
            result.warn(
                "kapsam",
                f"{len(missing)} kara state'i hicbir yerde tanimli degil ve "
                f"unlisted:drop ayarli -> sahipsiz kalacaklar",
            )


REPLACED_PATHS = (
    "common/history/states",
    "common/history/pops",
    "common/history/buildings",
    # DIKKAT: buraya bir dizin eklemek vanilla'yi SILER. Modun o dizine kendi
    # icerigini yazmiyorsa dunyada o icerikten HIC KALMAZ.
    #
    # Bir kez `common/history/military_formations` ve `common/history/characters`
    # buraya "kendi icerigimiz yazilana kadar" diye eklendi ve icerik hic
    # yazilmadi: sonuc, hicbir ulkenin ordusu ve hicbir ulkenin hukumdari
    # olmadigi bir dunya ve acilista access violation oldu.
    #
    # Ikisi de artik burada degil:
    #   - military_formations: vanilla dosyalari AYNI ISIMLE suzulup yeniden
    #     yaziliyor (build._write_military_formations), replace_paths gerekmiyor.
    #   - characters: hicbir state referansi tasimadigi icin tamamen vanilla.
    # Asagidaki _check_replace_paths bu hatanin tekrarini engelliyor.
)


def _check_legacy_conflicts(result: Result) -> None:
    """replace_paths beyani ve o dizinlerde kalmis elle yazilmis dosyalar.

    `common/history/*` dosyalari keyed database degil, calisan history
    script'leridir: farkli isimli dosyalar birbirini ezmez, hepsi calisir. Bu
    yuzden vanilla kurulumunu devre disi birakmanin tek yolu metadata.json
    icindeki replace_paths.
    """
    metadata_file = paths.mod(".metadata", "metadata.json")
    declared: list[str] = []
    if not metadata_file.exists():
        result.error(".metadata/metadata.json", "dosya yok")
    else:
        try:
            metadata = json.loads(metadata_file.read_text(encoding="utf-8-sig"))
            declared = list(metadata.get("game_custom_data", {}).get("replace_paths", []))
        except (json.JSONDecodeError, AttributeError) as exc:
            result.error(".metadata/metadata.json", f"okunamadi: {exc}")

    for required in REPLACED_PATHS:
        if required not in declared:
            result.error(
                ".metadata/metadata.json",
                f"game_custom_data.replace_paths icinde '{required}' yok. Bu olmadan "
                f"vanilla'nin ayni dizindeki kurulumu da calisir ve sahiplik/pop "
                f"cakisir.",
            )

    # Beyan edilmis ama BOS birakilmis bir replace_path, o icerigi dunyadan
    # tamamen silmek demektir - vanilla devre disi, yerine hicbir sey yok.
    # Bir kez military_formations ve characters boyle birakildi: sifir ordu,
    # sifir hukumdar ve acilista access violation.
    for relative in declared:
        directory = paths.mod(*relative.split("/"))
        if not directory.is_dir() or not any(directory.glob("*.txt")):
            result.error(
                ".metadata/metadata.json",
                f"'{relative}' replace_paths icinde ama modda o dizinde hic dosya yok. "
                f"Bu vanilla icerigini siler ve yerine hicbir sey koymaz "
                f"(ornegin ordusuz/hukumdarsiz dunya -> acilista crash). "
                f"Ya icerigi uret ya da bu satiri kaldir.",
            )

    marker = "OTOMATIK URETILDI"
    for relative in REPLACED_PATHS:
        directory = paths.mod(*relative.split("/"))
        if not directory.is_dir():
            continue
        for file in sorted(directory.glob("*.txt")):
            head = file.read_text(encoding="utf-8-sig", errors="replace")[:400]
            if marker not in head:
                result.error(
                    f"{relative}/{file.name}",
                    "bu dizin replace_paths ile vanilla'dan ayrildi; icindeki elle "
                    "yazilmis dosyalar uretilenlerle birlikte calisir. Icerigini "
                    "world/ altina tasiyip dosyayi silmelisin.",
                )


def _check_generated_files(result: Result) -> None:
    """Uretilmis dosyalarin sozdizimi ve tekrarli state tanimi kontrolu."""
    targets = [
        *paths.mod("common", "history", "states").glob("*.txt"),
        *paths.mod("common", "history", "pops").glob("*.txt"),
        *paths.mod("common", "history", "buildings").glob("*.txt"),
        *paths.mod("common", "history", "diplomacy").glob("*.txt"),
        *paths.mod("common", "history", "countries").glob("*.txt"),
        *paths.mod("common", "country_definitions").glob("*.txt"),
        *paths.mod("common", "religions").glob("*.txt"),
        *paths.mod("common", "journal_entries").glob("*.txt"),
        *paths.mod("common", "journal_entry_groups").glob("*.txt"),
        *paths.mod("common", "scripted_triggers").glob("*.txt"),
        *paths.mod("common", "scripted_effects").glob("*.txt"),
        *paths.mod("common", "script_values").glob("*.txt"),
        *paths.mod("common", "static_modifiers").glob("*.txt"),
        *paths.mod("common", "game_concepts").glob("*.txt"),
        *paths.mod("common", "coat_of_arms", "coat_of_arms").glob("*.txt"),
        *paths.mod("events").rglob("*.txt"),
        *paths.mod("map_data", "state_regions").glob("*.txt"),
    ]
    seen_states: dict[str, str] = {}
    seen_tags: dict[str, str] = {}

    for file in targets:
        rel = str(file.relative_to(paths.MOD_ROOT))
        text = file.read_text(encoding="utf-8-sig", errors="replace")
        balanced, message = pdx.check_braces(text)
        if not balanced:
            result.error(rel, f"brace dengesi bozuk: {message}")
            continue
        try:
            root = pdx.parse_file(file)
        except ValueError as exc:
            result.error(rel, f"parse edilemedi: {exc}")
            continue

        if file.parent.name == "states":
            for _key, _op, top in root.pairs:
                if not isinstance(top, pdx.Node):
                    continue
                for scoped, _o, _block in top.pairs:
                    if not scoped.startswith("s:"):
                        continue
                    name = scoped.split(":", 1)[1]
                    if name in seen_states:
                        result.error(rel, f"'{name}' zaten {seen_states[name]} icinde tanimli")
                    seen_states[name] = rel
        elif file.parent.name == "country_definitions":
            for raw_tag, _op, value in root.pairs:
                if not isinstance(value, pdx.Node):
                    continue
                # `REPLACE_OR_CREATE:TUR` -> `TUR`
                tag = raw_tag.split(":", 1)[-1]
                if tag in seen_tags:
                    result.error(rel, f"'{tag}' zaten {seen_tags[tag]} icinde tanimli")
                seen_tags[tag] = rel
                if ":" not in raw_tag and tag in _vanilla_tags():
                    result.error(
                        rel,
                        f"'{tag}' vanilla'da da tanimli ama 'REPLACE_OR_CREATE:' oneki yok "
                        f"-> oyun bu tanimi sessizce atar, vanilla kazanir",
                    )


def _vanilla_tags() -> set[str]:
    return set(index_mod.load_index()["countries"])
