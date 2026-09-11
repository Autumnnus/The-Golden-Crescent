# The Golden Crescent — toolchain

## Senaryo Atlası — oyunu açmadan harita geliştir

Yeni etkileşimli atlas ve LLM iş akışı: [LLM_MAP_WORKFLOW.md](LLM_MAP_WORKFLOW.md).
Python **3.10+** gerekir; bağımlılıklar `tools/requirements.txt` içindedir.

```bash
.venv/bin/python tools/tgc.py atlas
.venv/bin/python tools/tgc.py atlas --scenario tools/examples/ve_atlas_scenario.yml
.venv/bin/python tools/tgc.py catalog --region 08_middle_east --out build/context.json
.venv/bin/python tools/tgc.py map --scenario tools/examples/ve_atlas_scenario.yml --mode changes --data
```

Atlas tek HTML + JSON olarak `build/maps/` içine yazılır. Tarayıcıda eyalet/il seç,
ülkeye ata, önce/sonra karşılaştır, geri al ve senaryoyu indir. JSON/YAML
senaryoları bellekte uygulanır; `world/` veya oyun dosyalarına yazılmaz.
Siyasi harita bölünmüş eyaletleri il bazında gösterir. `religion` sahibin devlet
dinidir; `changes` il sahipliği farkıdır. `--baseline vanilla` mod–vanilla
karşılaştırması, `--width 8192` ayrıntılı çıktı, `--borders province` il sınırları içindir.


`world/*.yml` is the source of truth. Every generated game file is produced by
`build` and **must never be edited by hand**: `build` deletes its own previous
output on every run, so a hand-edit is silently lost.

```
world/*.yml  --( python tools/tgc.py build )-->  common/history/{states,pops,buildings}
                                                 common/country_definitions/
                                                 localization/
```

The Victoria 3 install is **read-only**. It is read for state regions, country
definitions, cultures, religions and every other vanilla identifier; nothing in
this toolchain opens it for writing (`paths.assert_read_only` guards every write).

---

## Commands

| command | what it does |
|---|---|
| `python tools/tgc.py build` | `world/` → game files, and rewrites `replace_paths` |
| `python tools/tgc.py check` | validate; **must be 0 errors before a phase is done** |
| `python tools/tgc.py find <name>` | resolve a state region by any name, alias or province hex |
| `python tools/tgc.py show <state>` | inspect one state: provinces, pops, buildings, vanilla owner |
| `python tools/tgc.py map --mode <m>` | render `political`, `reference`, `religion`, `phase` or `changes` |
| `python tools/tgc.py atlas` | offline interactive atlas + JSON context |
| `python tools/tgc.py catalog --region <r>` | compact verified JSON context for LLMs |
| `python tools/tgc.py index` | rebuild `build/index.json` — **after a Victoria 3 patch** |
| `python tools/tgc.py geo` | rasterise `provinces.png` — **after a Victoria 3 patch** |
| `python tools/tgc.py selftest` | regression-test the toolchain — run after touching `tools/` |
| `python tools/crashinfo.py` | read the newest minidump and name the fault |

After any change to `world/`:

```bash
python tools/tgc.py build && python tools/tgc.py check
```

Before writing YAML, resolve names with `find` and inspect the target with
`show`. Never guess a `STATE_*` id or a province hex — vanilla has several
near-identical names and a typo silently produces unowned land.

When the user describes a region in prose or a screenshot, render a shared
reference map first, confirm the names against it, then edit `world/`:

```bash
python tools/tgc.py map --mode reference --region 08_middle_east
```

---

## world/ schema

```
world/_aliases.yml          free-form name -> STATE_* (used by `find`)
world/countries/*.yml       TAG -> country spec
world/states/*.yml          STATE_* -> ownership spec
world/diplomacy/*.yml       pacts and relations
world/state_regions/*.yml   patches to map_data/state_regions (use sparingly)
```

### countries

```yaml
TUR:
  color: [40, 84, 160]          # or omit to keep the vanilla colour
  country_type: recognized      # recognized | unrecognized | colonial | decentralized
  tier: empire                  # empire | kingdom | grand_principality | principality | city_state | hegemony
  cultures: [turkish]
  religion: mujtahidiyya
  tech_tier: 1
  literacy: high                # very_high high middling low very_low baseline
  capital: EASTERN_THRACE       # the STATE_ prefix is optional
  name: Empire of Rum
  adjective: Rumi
  name_tr: "Rûm İmparatorluğu"
  religion_map: {sunni: mujtahidiyya}                    # rename a religion
  religion_split: {orthodox: {mujtahidiyya: 0.35, orthodox: 0.65}}
  culture_religion_split: {spanish: {catholic: 0.2, hikmatiyya: 0.8}}
  culture_map: {ottoman: turkish}
  overlord: TUR                 # when this country is a subject
  subject_type: puppet
  liberty_desire: 15
  phase: "3"                    # for `map --mode phase`
```

Conversion precedence for one pop: `culture_religion_split` (most specific),
then `religion_split`, then `religion_map`. Only the first that matches applies.

### states

```yaml
STATE_ZULULAND: ZUL                      # shorthand: whole state to one owner

STATE_ERZURUM:
  owner: ERZ
  pops: inherit                          # inherit | drop
  buildings: inherit                     # inherit | drop
  homelands: [turkish, armenian]
  claims: [TUR]

STATE_MERZ:                              # a split state
  split:
    - {owner: KHO, provinces: [x6598F7, x6CF557]}
    - {owner: BUK, rest: true}
```

A state **not listed** here keeps its vanilla owner, vanilla pops and vanilla
buildings verbatim — including skipping religion conversion. If a country's
conversion should reach a state, that state must be listed.

---

## Engine rules the generator encodes

These were all learned from real crashes. See `YENIDEN_KURULUM.md` §2.

**`replace_paths` is generated, never hand-written.** A directory declared there
has its vanilla content deleted. Declaring one the mod then leaves empty wipes
that content from the game — this is how a world lost every army and every
ruler. `build` rewrites the list from the directories it actually filled.

**Override semantics differ per directory. Do not generalise one to another.**

| directory | mechanism |
|---|---|
| `common/history/{states,pops,buildings}` | Executed script. Differently-named files do **not** override — they all run. Only `replace_paths` silences vanilla. |
| `common/history/{diplomacy,military_formations,countries,population}` | Executed script, but a **same-named** file replaces vanilla's. No `replace_paths` needed. |
| `common/country_definitions` | Keyed database. A duplicate key in another file is **silently discarded**. Needs `REPLACE_OR_CREATE:TAG`. |
| `common/coat_of_arms` | Keyed database with **no** `REPLACE_OR_CREATE`. Last loaded wins → prefix the file `zzz_`. |
| `common/on_actions` | Keyed database that does **not** merge. Redefining `on_game_started_after_lobby` in your own file is silently discarded; add journal entries via `common/history/countries`. |
| `map_data/state_regions` | Neither. Changing one state means regenerating that whole vanilla-named file. |

**`decentralized` countries cannot own buildings.** Vanilla has exactly zero
buildings for them. The engine never allocates building storage for that country
type, so writing one is a write into unallocated memory: `0xC0000005` on load,
with nothing in any log. `buildings: inherit` on a state handed to a
decentralized owner would copy vanilla's buildings across — the generator drops
them and `check` fails if any survive. They *can* have pops and technology, but
not journal entries (`has_events = no`).

**`subject_type` must match both countries' `country_type`.** `check` validates
this against vanilla's own `common/subject_types` rather than a written-down
table, because the real matrix is not what you would guess:

| subject_type | overlord must be | subject must be |
|---|---|---|
| `vassal`, `tributary` | **unrecognized** | unrecognized, recognized, colonial |
| `puppet`, `protectorate` | recognized, colonial, company | recognized, unrecognized |
| `dominion`, `colony`, `chartered_company` | recognized, colonial, company | colonial (+company) |
| `personal_union` | recognized, colonial, unrecognized | recognized, colonial, unrecognized |
| `crown_land` | recognized | recognized, unrecognized |

A *recognized* overlord therefore cannot hold `vassal` or `tributary` subjects.

**Every country with land needs a capital it owns**, or the engine reports
`Event target link 'capital' returned an invalid object`. This applies to
vanilla countries whose land the mod redistributed, and to `set_capital` /
`set_market_capital` calls hidden in `common/history/countries`, which a
`country_definitions` audit never sees.

**Both sides of a diplomacy record must own land**, or:
`Assertion failed: Attempted to create relations for invalid countries!`
Redistribution routinely leaves vanilla tags landless.

**Vanilla's own data is inconsistent** — the same province in two states,
capitals a country does not own. `check` resolves untouched vanilla in parallel
and demotes any finding vanilla already has to a `[vanilla]` warning. Something
true of vanilla is not a bug we introduced; chasing one costs hours.

---

## build/ is a cache

`build/` is git-ignored and fully regenerable:

| file | from | rebuild with |
|---|---|---|
| `index.json` | the whole vanilla install | `tgc.py index` |
| `state_ids.npy`, `province_codes.npy`, `geo.json`, `state_adjacency.json` | `provinces.png` | `tgc.py geo` |
| `maps/*.png` | the two above | `tgc.py map` |

Re-run `index` and `geo` after a Victoria 3 update.

---

## Module layout

| module | responsibility |
|---|---|
| `vic3/pdx.py` | Clausewitz tokenizer, parser, serializer |
| `vic3/paths.py` | roots; `assert_read_only` guards every write |
| `vic3/index.py` | vanilla → `build/index.json` |
| `vic3/geo.py` | `provinces.png` → per-pixel state raster |
| `vic3/world.py` | load and validate `world/*.yml` |
| `vic3/build.py` | resolved world → game files |
| `vic3/check.py` | validation rules, with a vanilla baseline |
| `vic3/mapdraw.py` | province-accurate PNG rendering |
| `vic3/atlas.py` | shared map snapshot, offline HTML and LLM context |
| `vic3/scenario.py` | validated in-memory scenario overlays |
| `vic3/atlas_web/` | dependency-free interactive atlas UI |
| `vic3/report.py` | `find` and `show` |
| `crashinfo.py` | minidump → cause of a load crash |
