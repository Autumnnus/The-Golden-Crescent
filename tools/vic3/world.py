"""`world/` altindaki insan tarafindan yazilan kaynak veriyi yukler.

Bu, modun harita verisinin TEK kaynagidir. `common/history/...` altindaki oyun
dosyalari buradan uretilir; onlar cikti, bu girdi.

Dizin duzeni:
    world/_defaults.yml          global ayarlar, kultur/din donusum tablolari
    world/_aliases.yml           Turkce/serbest isim -> STATE_* eslemesi
    world/countries/*.yml        ulke tanimlari
    world/states/*.yml           state atamalari
    world/state_regions/*.yml    (opsiyonel) vanilla state_region yamalari
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from . import paths


class WorldError(Exception):
    """Kaynak veride bicim hatasi."""


@dataclass
class PopSpec:
    culture: str
    size: int
    religion: str | None = None
    pop_type: str | None = None


@dataclass
class BuildingSpec:
    building: str
    levels: int | None = None
    owner: str = "country"          # "country" | "manor_house" | ham bina anahtari
    production_methods: list[str] = field(default_factory=list)


@dataclass
class OwnerSlice:
    """Bir state'in tek bir ulkeye ait parcasi."""

    owner: str
    provinces: list[str] | None = None   # None -> geri kalan her sey
    rest: bool = False


@dataclass
class StateSpec:
    name: str
    slices: list[OwnerSlice] = field(default_factory=list)
    homelands: list[str] = field(default_factory=list)
    pops: Any = "inherit"               # "inherit" | "none" | dict | list[PopSpec]
    buildings: Any = "inherit"          # "inherit" | "none" | list[BuildingSpec]
    source_file: str = ""

    @property
    def owners(self) -> list[str]:
        return [s.owner for s in self.slices]


@dataclass
class CountrySpec:
    tag: str
    color: Any = None
    country_type: str = "unrecognized"
    tier: str = "principality"
    cultures: list[str] = field(default_factory=list)
    religion: str | None = None      # country_definitions'taki `religion =` -> devlet dini
    tech_tier: int | None = None     # 1 = en ileri, 7 = hicbir sey
    literacy: str | None = None      # very_high | high | middling | low | very_low | baseline
    capital: str | None = None
    name: str | None = None
    adjective: str | None = None
    name_tr: str | None = None
    religion_map: dict[str, str] = field(default_factory=dict)
    religion_split: dict[str, dict[str, float]] = field(default_factory=dict)
    # {kultur: {kaynak_din: {hedef_din: oran}}} - kulture ozel bolusturme.
    # religion_split'ten ONCE bakilir; bulunursa o kazanir.
    culture_religion_split: dict[str, dict[str, dict[str, float]]] = field(default_factory=dict)
    culture_map: dict[str, str] = field(default_factory=dict)
    pop_scale: float = 1.0
    # Baslangic tabiiyeti: bu ulke `overlord`'un `subject_type` tipinde tabiisi.
    overlord: str | None = None
    subject_type: str = "vassal"
    liberty_desire: int | None = None
    source_file: str = ""


@dataclass
class World:
    defaults: dict[str, Any] = field(default_factory=dict)
    aliases: dict[str, str] = field(default_factory=dict)
    countries: dict[str, CountrySpec] = field(default_factory=dict)
    states: dict[str, StateSpec] = field(default_factory=dict)
    state_region_patches: dict[str, dict[str, Any]] = field(default_factory=dict)
    diplomacy: dict[str, Any] = field(default_factory=dict)   # world/_diplomacy.yml

    @property
    def religion_map(self) -> dict[str, str]:
        return self.defaults.get("religion_map") or {}

    @property
    def culture_map(self) -> dict[str, str]:
        return self.defaults.get("culture_map") or {}

    @property
    def pop_scale(self) -> float:
        return float(self.defaults.get("pop_scale", 1.0))

    @property
    def religion_split(self) -> dict[str, dict[str, float]]:
        return _normalize_splits(self.defaults.get("religion_split") or {}, "world/_defaults.yml")

    def splits_for(self, tag: str) -> dict[str, dict[str, float]]:
        """Global + ulkeye ozel din bolusturme tablolarini birlestirir."""
        splits = dict(self.religion_split)
        country = self.countries.get(tag)
        if country:
            splits.update(country.religion_split)
        return splits

    def culture_splits_for(self, tag: str) -> dict[str, dict[str, dict[str, float]]]:
        """Kulture ozel din bolusturme tablolari."""
        country = self.countries.get(tag)
        return dict(country.culture_religion_split) if country else {}

    def subjects(self) -> list[tuple[str, str, str]]:
        """(overlord, subject, subject_type) uclulerini kaynak sirasinda dondurur."""
        out = []
        for tag in sorted(self.countries):
            spec = self.countries[tag]
            if spec.overlord:
                out.append((spec.overlord, tag, spec.subject_type))
        return out

    def maps_for(self, tag: str) -> tuple[dict[str, str], dict[str, str], float]:
        """Global + ulkeye ozel donusum tablolarini birlestirir."""
        country = self.countries.get(tag)
        religions = dict(self.religion_map)
        cultures = dict(self.culture_map)
        scale = self.pop_scale
        if country:
            religions.update(country.religion_map)
            cultures.update(country.culture_map)
            scale *= country.pop_scale
        return religions, cultures, scale


# ---------------------------------------------------------------------------
# Yukleme
# ---------------------------------------------------------------------------

def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise WorldError(f"{path.name}: YAML okunamadi -> {exc}") from None
    if not isinstance(data, dict):
        raise WorldError(f"{path.name}: dosyanin kokunde sozluk bekleniyordu")
    return data


def _parse_pops(raw: Any, where: str) -> Any:
    if raw is None or isinstance(raw, str):
        return raw or "inherit"
    if isinstance(raw, dict):
        # {inherit: true, scale: .., religion_map: {..}, religion_split: {..}}
        if raw.get("religion_split"):
            raw = {**raw, "religion_split": _normalize_splits(raw["religion_split"], where)}
        return raw
    if isinstance(raw, list):
        pops = []
        for item in raw:
            if not isinstance(item, dict) or "culture" not in item:
                raise WorldError(f"{where}: pop girdisinde 'culture' zorunlu -> {item!r}")
            if "size" not in item:
                raise WorldError(f"{where}: pop girdisinde 'size' zorunlu -> {item!r}")
            pops.append(
                PopSpec(
                    culture=str(item["culture"]),
                    size=int(item["size"]),
                    religion=item.get("religion"),
                    pop_type=item.get("pop_type"),
                )
            )
        return pops
    raise WorldError(f"{where}: 'pops' beklenmeyen bicimde -> {type(raw).__name__}")


def _parse_buildings(raw: Any, where: str) -> Any:
    if raw is None or isinstance(raw, str):
        return raw or "inherit"
    if isinstance(raw, list):
        buildings = []
        for item in raw:
            if isinstance(item, str):
                buildings.append(BuildingSpec(building=item))
                continue
            if not isinstance(item, dict) or "building" not in item:
                raise WorldError(f"{where}: bina girdisinde 'building' zorunlu -> {item!r}")
            buildings.append(
                BuildingSpec(
                    building=str(item["building"]),
                    levels=item.get("levels"),
                    owner=str(item.get("owner", "country")),
                    production_methods=list(item.get("production_methods") or item.get("pms") or []),
                )
            )
        return buildings
    raise WorldError(f"{where}: 'buildings' beklenmeyen bicimde -> {type(raw).__name__}")


def _parse_state(name: str, raw: Any, source: str) -> StateSpec:
    where = f"{source}:{name}"
    if isinstance(raw, str):
        # kisayol:  STATE_X: RUM
        return StateSpec(name=name, slices=[OwnerSlice(owner=raw)], source_file=source)
    if not isinstance(raw, dict):
        raise WorldError(f"{where}: sozluk ya da tag kisayolu bekleniyordu")

    slices: list[OwnerSlice] = []
    if "split" in raw:
        split = raw["split"]
        if not isinstance(split, list):
            raise WorldError(f"{where}: 'split' liste olmali")
        for item in split:
            if not isinstance(item, dict) or "owner" not in item:
                raise WorldError(f"{where}: split girdisinde 'owner' zorunlu -> {item!r}")
            slices.append(
                OwnerSlice(
                    owner=str(item["owner"]),
                    provinces=[str(p) for p in item["provinces"]] if item.get("provinces") else None,
                    rest=bool(item.get("rest", False)),
                )
            )
        rest_count = sum(1 for s in slices if s.rest or s.provinces is None)
        if rest_count > 1:
            raise WorldError(f"{where}: split icinde en fazla bir 'rest: true' olabilir")
        if rest_count == 0:
            raise WorldError(
                f"{where}: split parcalarinin biri 'rest: true' olmali "
                f"(state'in tum province'lari atanmali)"
            )
    elif "owner" in raw:
        owner = raw["owner"]
        if owner not in (None, "none", "unowned"):
            slices.append(OwnerSlice(owner=str(owner)))
    else:
        raise WorldError(f"{where}: 'owner' ya da 'split' gerekli (sahipsiz icin owner: unowned)")

    return StateSpec(
        name=name,
        slices=slices,
        homelands=[str(h) for h in (raw.get("homelands") or [])],
        pops=_parse_pops(raw.get("pops"), where),
        buildings=_parse_buildings(raw.get("buildings"), where),
        source_file=source,
    )


def _normalize_splits(raw: Any, where: str) -> dict[str, dict[str, float]]:
    """`religion_split` tablosunu {kaynak: {hedef: oran}} olarak normalize eder.

    Oranlar toplami 1 olmak zorunda degil; her kaynak icin kendi icinde
    normalize edilir. Boylece `{mujtahidiyya: 2, orthodox: 1}` de yazilabilir.
    """
    if not raw:
        return {}
    if not isinstance(raw, dict):
        raise WorldError(f"{where}: 'religion_split' sozluk olmali")
    out: dict[str, dict[str, float]] = {}
    for source_religion, targets in raw.items():
        if not isinstance(targets, dict) or not targets:
            raise WorldError(
                f"{where}: religion_split['{source_religion}'] "
                f"{{hedef: oran}} sozlugu olmali"
            )
        weights = {}
        for target, weight in targets.items():
            value = float(weight)
            if value < 0:
                raise WorldError(f"{where}: religion_split oranlari negatif olamaz ({target})")
            if value > 0:
                weights[str(target)] = value
        total = sum(weights.values())
        if total <= 0:
            raise WorldError(f"{where}: religion_split['{source_religion}'] tum oranlari sifir")
        out[str(source_religion)] = {t: w / total for t, w in weights.items()}
    return out


def _parse_country(tag: str, raw: Any, source: str) -> CountrySpec:
    where = f"{source}:{tag}"
    if not isinstance(raw, dict):
        raise WorldError(f"{where}: sozluk bekleniyordu")
    overlord = raw.get("overlord")
    if overlord is not None and not isinstance(overlord, str):
        raise WorldError(f"{where}: 'overlord' ulke tag'i olmali")
    if raw.get("subject_type") and not overlord:
        raise WorldError(f"{where}: 'subject_type' yazildi ama 'overlord' yok")
    return CountrySpec(
        tag=tag,
        color=raw.get("color"),
        country_type=str(raw.get("country_type", "unrecognized")),
        tier=str(raw.get("tier", "principality")),
        cultures=[str(c) for c in (raw.get("cultures") or [])],
        religion=str(raw["religion"]) if raw.get("religion") else None,
        tech_tier=int(raw["tech_tier"]) if raw.get("tech_tier") is not None else None,
        literacy=str(raw["literacy"]) if raw.get("literacy") else None,
        capital=raw.get("capital"),
        name=raw.get("name"),
        adjective=raw.get("adjective"),
        name_tr=raw.get("name_tr"),
        religion_map=dict(raw.get("religion_map") or {}),
        religion_split=_normalize_splits(raw.get("religion_split"), where),
        culture_religion_split={
            str(culture): _normalize_splits(table, f"{where}:{culture}")
            for culture, table in (raw.get("culture_religion_split") or {}).items()
        },
        culture_map=dict(raw.get("culture_map") or {}),
        pop_scale=float(raw.get("pop_scale", 1.0)),
        overlord=str(overlord) if overlord else None,
        subject_type=str(raw.get("subject_type", "vassal")),
        liberty_desire=(
            int(raw["liberty_desire"]) if raw.get("liberty_desire") is not None else None
        ),
        source_file=source,
    )


def load_world() -> World:
    world = World()
    world.defaults = _read_yaml(paths.WORLD_DEFAULTS)
    world.aliases = {
        str(k): str(v) for k, v in (_read_yaml(paths.WORLD_DIR / "_aliases.yml") or {}).items()
    }
    world.diplomacy = _read_yaml(paths.WORLD_DIR / "_diplomacy.yml")

    for file in sorted(paths.WORLD_COUNTRIES_DIR.glob("*.yml")):
        for tag, raw in _read_yaml(file).items():
            if tag in world.countries:
                raise WorldError(
                    f"{file.name}: '{tag}' zaten {world.countries[tag].source_file} icinde tanimli"
                )
            world.countries[tag] = _parse_country(str(tag), raw, file.name)

    for file in sorted(paths.WORLD_STATES_DIR.glob("*.yml")):
        for name, raw in _read_yaml(file).items():
            key = str(name)
            if key in world.states:
                raise WorldError(
                    f"{file.name}: '{key}' zaten {world.states[key].source_file} icinde tanimli"
                )
            world.states[key] = _parse_state(key, raw, file.name)

    patch_dir = paths.WORLD_DIR / "state_regions"
    for file in sorted(patch_dir.glob("*.yml")):
        for name, raw in _read_yaml(file).items():
            if not isinstance(raw, dict):
                raise WorldError(f"{file.name}:{name}: yama sozluk olmali")
            world.state_region_patches.setdefault(str(name), {}).update(raw)

    return world


def resolve_state_name(query: str, world: World | None = None) -> list[str]:
    """Serbest metni STATE_* ismine cevirir; once alias, sonra bulanik arama."""
    from . import index as index_mod

    world = world or load_world()
    normalized = index_mod.normalize(query)
    for alias, target in world.aliases.items():
        if index_mod.normalize(alias) == normalized:
            return [target]
    return index_mod.find_states(query)
