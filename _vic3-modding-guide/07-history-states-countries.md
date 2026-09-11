# 07 — History, States, and Country Setup

**Read this file when:** creating/editing the 1836 start (states, pops, buildings, laws, diplomacy), adding or changing countries (definitions, releasables, formables), editing map state data (`state_regions`), or adding state traits/cultures/religions. For general script syntax (`c:`/`s:`/`cu:` scopes, `?=`) see `02-script-language.md`; for file/folder loading rules see `01-mod-structure.md`; for all loc-key details see `08-localization.md`.

Verified against: vanilla game files (paths below) and mod **Victorian Century** (`mod/3219394272`).

---

## 1. The big picture

A playable start-date country is assembled from several databases that must agree with each other:

| Piece | Folder | What it declares |
|---|---|---|
| Tag definition | `common/country_definitions/` | color, tier, type, primary cultures, capital state |
| Territory | `common/history/states/` | which provinces of each state region the tag owns |
| People | `common/history/pops/` | pops per state per owner |
| Economy | `common/history/buildings/` | starting buildings, levels, PMs, ownership |
| Politics | `common/history/countries/` | laws, techs, taxes, ruling IGs (effects run at game start) |
| Wealth/literacy | `common/history/population/` | starting pop wealth/literacy effects |
| Diplomacy | `common/history/diplomacy/`, `treaties/` | pacts, subjects, relations, treaties |
| Map geometry | `map_data/state_regions/` | provinces, resources, hubs per STATE_X (static, not per-country) |
| Name | `localization/<lang>/` | `TAG:0 "Name"`, `TAG_ADJ:0 "Adj"` |

`common/country_creation/` (releasables) and `common/country_formation/` (formables) let tags that own no land at start enter the game later.

---

## 2. Map data: `map_data/state_regions/`

One `STATE_X` block per state region, split into 16 regional files (`00_west_europe.txt` … `15_russia.txt`, plus `99_seas.txt`). Paradox ships an official format doc at `game/map_data/state_regions/state_regions.md`. Real example:

```
# game/map_data/state_regions/00_west_europe.txt
STATE_SVEALAND = {
    id = 1                                          # unique numeric id, required
    subsistence_building = "building_subsistence_pasture"
    provinces = { "x0974E5" "x216569" ... }         # province hex color ids
    traits = { "state_trait_bergslagen" "state_trait_scandinavian_forests" "state_trait_natural_harbors" }
    city = "x9686A5"      # hub provinces: city/farm/mine/wood required for land,
    port = "x93C3BC"      # port required only if coastal
    farm = "xF48646"
    mine = "x6F40EC"
    wood = "x4C9918"
    arable_land = 30
    arable_resources = { "building_rye_farm" "building_livestock_ranch" }
    capped_resources = {                            # fixed max levels
        building_iron_mine = 60
        building_lead_mine = 18
        building_logging_camp = 45
        building_fishing_wharf = 11
    }
    naval_exit_id = 3000  # sea region id, required for coastal land states
}
```

Discoverable/depletable resources use repeatable `resource` blocks instead of `capped_resources` entries:

```
# game/map_data/state_regions/05_north_america.txt (STATE_CALIFORNIA area)
resource = {
    type = "building_gold_field"
    depleted_type = "building_gold_mine"   # optional: what it becomes when depleted
    undiscovered_amount = 12               # deposits found by exploration/events
}
resource = {
    type = "building_oil_rig"
    undiscovered_amount = 20
}
```

Other verified optional fields (from `state_regions.md`): `graphical_culture`, `impassable = { "xHEX" ... }`, `prime_land = { ... }`, `center_province`, `discovered_amount`/`depleted_amount`/`discover_chance_mult`/`deplete_chance_mult` inside `resource`, `blockade_locator`, and for sea regions `diorama_radius_multiplier`/`diorama_center_offset`.

**Sea regions** (`99_seas.txt`): exactly one province, usually just `id` + `provinces`; `impassable` blocks naval travel.

**Strategic regions** (`common/strategic_regions/*.txt` — note: *common*, not map_data): every state must belong to exactly one.

```
# game/common/strategic_regions/europe_strategic_regions.txt
region_western_europe = {
    capital_province = xA0A0C0
    map_color = { 1 0 0 }        # percentages, not 0-255
    states = { STATE_WALES STATE_MIDLANDS ... }
}
```

**State traits** (`common/state_traits/*.txt`) are icon + modifier bundles referenced by name from `traits = { }`:

```
# game/common/state_traits/01_scandinavia_traits.txt
state_trait_bergslagen = {
    icon = "gfx/interface/icons/state_trait_icons/resources_ore.dds"
    modifier = {
        building_iron_mine_throughput_add = 0.15
        building_lead_mine_throughput_add = 0.1
    }
}
```

Loc keys: `STATE_SVEALAND` → `localization/english/map/states_l_english.yml`; `state_trait_bergslagen` → `localization/english/map/state_traits_l_english.yml`; hub names → `HUB_NAME_STATE_SVEALAND_city: "Stockholm"` in `localization/english/dynamic_state_and_hub_names_l_english.yml`.

---

## 3. `common/history/` subfolder tour

There is **no generic `HISTORY = {}` wrapper**. Each subfolder's files open with their own top-level keyword; the contents are effects executed at game start. All wrappers verified from first lines of vanilla files:

| Folder | Wrapper | Contains |
|---|---|---|
| `states/` | `STATES = {` | `create_state`, homelands, claims |
| `pops/` | `POPS = {` | `create_pop` per state per owner |
| `buildings/` | `BUILDINGS={` | `create_building` per state per owner |
| `countries/` | `COUNTRIES = {` | laws, techs, taxes, IGs (one file per tag) |
| `population/` | `POPULATION = {` | starting pop wealth/literacy effects per tag |
| `diplomacy/` | `DIPLOMACY = {` | pacts, subjects, relations, truces, embargos, rivalries |
| `trade/` | `TRADE = {` | initial import/export orders |
| `treaties/` | `TREATIES = {` | `create_treaty` (Holy Alliance etc.) |
| `military_formations/` | `MILITARY_FORMATIONS = {` | armies/fleets + units |
| `military_deployments/` | `MILITARY_DEPLOYMENTS = {` | moving formations to HQs |
| `characters/` | `CHARACTERS = {` | `create_character` (one file per tag) |
| `governments/` | `GOVERNMENT = {` | parties (note: folder plural, wrapper singular) |
| `government_setup/` | `GOVERNMENT_SETUP = {` | government tweaks |
| `ai/` | `AI = {` | `set_strategy` per tag |
| `conscription/` | `CONSCRIPTION = {` | conscription setup |
| `cultures/` | `CULTURES = {` | culture-related start effects (fervor etc.) |
| `diplomatic_plays/` | `DIPLOMATIC_PLAYS = {` | in-progress plays (Carlist war etc.) |
| `political_movements/` | `POLITICAL_MOVEMENTS = {` | starting movements |
| `lobbies/` | `LOBBIES = {` | `create_political_lobby` |
| `power_blocs/` | `POWER_BLOCS = {` | `create_power_bloc` |
| `production_methods/` | `PRODUCTION_METHODS = {` | `activate_production_method` country-wide |
| `global/` | `GLOBAL = {` | misc effects; file comment: "This is executed last among all history" |

Scope references inside history: states as `s:STATE_X`, countries as `c:TAG` (use `c:TAG ?= { }` so the block is skipped if the tag doesn't exist), cultures as `cu:culture_key`, goods as `g:goods` / state-goods as `sg:goods`, laws as `law_type:law_x`, IGs as `ig:ig_x`.

### 3.1 `history/states` — territory, homelands, claims

```
# game/common/history/states/00_states.txt
STATES = {
    s:STATE_MINSK = {
        create_state = {
            country = c:RUS
            owned_provinces = { x0161E0 x0A89D7 ... }   # subset of the region's provinces
        }
        add_homeland = cu:russian
        add_homeland = cu:byelorussian
    }
    s:STATE_BALUCHISTAN = {                # a split state: several create_state blocks
        create_state = {
            country = c:OMA
            state_type = unincorporated     # also seen: incorporated (rarely explicit)
            owned_provinces = { xB7B2BD }
        }
        create_state = {
            country = c:KAL
            owned_provinces = { x0279A0 ... }
        }
        add_claim = c:BIC                   # start-date claim on the whole region
        add_homeland = cu:baluchi
    }
}
```

- Every province of every land region should be assigned to exactly one `create_state` across all files.
- `add_homeland`/`add_claim` sit at the `s:STATE_X` level, not inside `create_state`.
- Quote marks around province ids are optional here ("unnecessary, but harmless" per vanilla file comment).

### 3.2 `history/pops` — starting population

```
# game/common/history/pops/00_west_europe.txt
POPS = {
    s:STATE_SVEALAND = {
        region_state:SWE = {              # the SWE-owned part of the state
            create_pop = {
                culture = swedish
                size = 1081208
            }
            create_pop = {
                culture = finnish
                size = 32000
            }
        }
    }
}
```

Optional keys (verified in `02_east_europe.txt`, `01_south_europe.txt`):

```
create_pop = {
    culture = ugrian
    religion = orthodox          # optional; defaults to the culture's religion
    size = 4187
}
create_pop = {
    culture = afro_brazilian
    pop_type = slaves            # optional; also seen: aristocrats
    size = 12012
}
```

### 3.3 `history/buildings` — starting industry

```
# game/common/history/buildings/00_west_europe.txt
BUILDINGS={
    s:STATE_SVEALAND={
        region_state:SWE={
            create_building={
                building="building_government_administration"
                add_ownership={
                    country={ country="c:SWE" levels=4 }        # state-owned levels
                }
                reserves=1
                activate_production_methods={ "pm_professional_bureaucrats" "pm_religious_bureaucrats" "pm_horizontal_drawer_cabinets" }
            }
            create_building={
                building="building_iron_mine"
                add_ownership={
                    building={                                   # owned by another building
                        type="building_manor_house"
                        country="c:SWE"
                        levels=5
                        region="STATE_SVEALAND"
                    }
                }
                reserves=1
                activate_production_methods={ "pm_picks_and_shovels_building_iron_mine" "pm_no_explosives" "pm_no_steam_automation" "pm_road_carts" }
            }
        }
    }
}
```

Total level = sum of `levels` across `add_ownership` entries. One PM per PM group must be listed in `activate_production_methods` or the building falls back to defaults.

### 3.4 `history/countries` + `history/population` — politics and society

```
# game/common/history/countries/swe - sweden.txt
COUNTRIES = {
    c:SWE ?= {
        effect_starting_technology_tier_2_tech = yes   # scripted effect: whole tech tier
        add_technology_researched = dialectics         # individual techs on top
        effect_starting_politics_conservative = yes

        add_taxed_goods = g:liquor
        set_export_tariff_level = {
            goods = g:iron
            level = no_tariffs_or_subventions
        }

        activate_law = law_type:law_monarchy           # one per law group
        activate_law = law_type:law_oligarchy
        activate_law = law_type:law_per_capita_based_taxation
        # ... (one activate_law per lawgroup you want non-default)

        set_institution_investment_level = {
            institution = institution_schools
            level = 3
        }
        ig:ig_devout ?= { add_ruling_interest_group = yes }
        ig:ig_landowners ?= { add_ruling_interest_group = yes }
    }
}
```

Also verified in this folder (Victorian Century's `gbr - great britain.txt`): `set_tax_level = medium`, `set_import_tariff_level`, `set_next_election_date = 1836.2.1`, `set_variable`, `add_ruling_interest_group` for multiple IGs.

```
# game/common/history/population/swe - sweden.txt
POPULATION = {
    c:SWE ?= {
        effect_starting_pop_wealth_high = yes
        effect_starting_pop_literacy_very_high = yes
    }
}
```

### 3.5 `history/diplomacy` — subjects, relations, pacts

```
# game/common/history/diplomacy/00_subject_relationships.txt
DIPLOMACY = {
    c:SWE ?= {
        create_diplomatic_pact = {
            country = c:NOR
            type = personal_union
        }
    }
    c:RUS ?= {
        create_diplomatic_pact = { country = c:FIN type = personal_union }
        create_diplomatic_pact = { country = c:UBD type = puppet }
        create_diplomatic_pact = { country = c:ALK type = chartered_company }
        create_diplomatic_pact = { country = c:KZH type = protectorate }
    }
}
```

Subject `type`s seen in vanilla: `colony`, `personal_union`, `puppet`, `protectorate`, `dominion`, `chartered_company`; plus the non-subject pact `grant_own_market`. Relations:

```
# game/common/history/diplomacy/00_relations.txt
DIPLOMACY = {
    c:AUS ?= {
        set_relations = { country = c:TUR value = -30 }
        set_relations = { country = c:BAV value = 30 }
    }
}
```

Files `00_truces.txt`, `00_embargos.txt`, `00_rivalries.txt`, `00_favors.txt` use the same `DIPLOMACY = { c:TAG ?= { ... } }` shell. Formal treaties live separately:

```
# game/common/history/treaties/00_historical_treaties.txt
TREATIES = {
    create_treaty = {
        name = treaty_name_holy_alliance
        first_country = c:RUS
        second_country = c:AUS
        is_draft = no
        entered_into_force_on = 1815.10.26
        binding_period = { years = 35 }
        articles_to_create = {
            { article = defensive_pact }
        }
    }
}
```

### 3.6 `history/trade` and `history/military_formations`

```
# game/common/history/trade/00_historical_trade.txt
TRADE = {
    s:STATE_SVEALAND={
        region_state:SWE={
            sg:iron = { add_exports = 25 }
        }
    }
}
```

```
# game/common/history/military_formations/99_military_formations_example.txt (vanilla's own commented example)
MILITARY_FORMATIONS = {
    c:FRA ?= {
        create_military_formation = {
            type = army                      # or fleet
            hq_region = sr:region_southern_europe
            name = "Big_Bad_Army"
            combat_unit = {
                type = unit_type:combat_unit_type_skirmish_infantry
                state_region = s:STATE_BURGUNDY
                count = 5
            }
            combat_unit = {
                type = unit_type:combat_unit_type_skirmish_infantry
                service_type = conscript     # optional; default is regular
                state_region = s:STATE_BURGUNDY
                count = 5
            }
            mobilization_options = { mobilization_option:mobilization_option_extra_supplies }
            save_scope_as = big_bad
        }
        create_character = { template = FRA_thomas_bugeaud save_scope_as = kasper }
        scope:kasper = { transfer_to_formation = scope:big_bad }
    }
}
```

### 3.7 `history/global` — runs last

```
# game/common/history/global/00_global.txt  ("This is executed last among all history")
GLOBAL = {
    add_contextless_journal_entry = je_uneasy_raj
    every_country = {
        limit = { NOT = { has_law_or_variant = law_type:law_slavery_banned } }
        ig:ig_landowners ?= { add_ideology = ideology_pro_slavery }
    }
}
```

Use `global/` for cross-country fixups that must see the finished world (iterators, conditional modifiers, journal entries).

---

## 4. `common/country_definitions/` — tag anatomy

```
# game/common/country_definitions/00_countries.txt
# File header warning: "Only use capital letters and numbers for tags, or else
# you may get weird bugs in civil wars"
GBR = {
    color = hsv{ 0.99  0.7  0.9 }     # also: { 147 130 110 } rgb, hsv360{ 16 80 80 }
    country_type = recognized          # recognized / unrecognized / colonial / decentralized / company
    tier = empire                      # city_state / principality / grand_principality / kingdom / empire / hegemony
    cultures = { british scottish }    # primary cultures
    capital = STATE_HOME_COUNTIES
}

ULS = {
    color = hsv360{ 16  80  80 }
    country_type = recognized
    tier = principality
    cultures = { scottish irish }
    religion = protestant              # optional (56 of ~725 tags set it)
    capital = STATE_ULSTER
    is_named_from_capital = yes        # optional
}
```

Other verified optional fields: `social_hierarchy = ...` (43 uses; e.g. Victorian Century's BIC uses `british_indian_caste_system`), `valid_as_home_country_for_separatists`, `primary_unit_color`/`secondary`/`tertiary_unit_color`. `99_dynamic.txt` defines 100 placeholder tags `D00`–`D99` containing only `dynamic_country_definition = yes` (used by revolts/dynamic tags — do not remove).

**Dynamic country names** (`common/dynamic_country_names/00_dynamic_country_names.txt`): a `DEFAULT = { }` block or per-tag blocks with repeatable entries:

```
dynamic_country_name = {
    name = csa_revolt_name             # loc key
    adjective = csa_revolt_name_adj
    is_revolutionary = yes
    priority = 100
    trigger = { exists = c:CSA ... scope:actor ?= { c:CSA ?= THIS } }
}
```

**Localization:** every tag needs `TAG: "Name"` and `TAG_ADJ: "Adjective"` (vanilla `localization/english/countries_l_english.yml`; Victorian Century adds its own in `localization/english/joi_countries_l_english.yml`).

---

## 5. Cultures and religions (referenced by pops and definitions)

```
# game/common/cultures/00_cultures.txt
north_german= {
    color= rgb{ 62 77 100 }
    religion = protestant              # default pop religion
    heritage = heritage_germanic       # discrimination grouping
    language = language_germanophone
    obsessions = { meat }              # optional
    traditions = { }
    male_common_first_names = { Adelbert Adolf ... }
    female_common_first_names = { Adelheid ... }
    noble_last_names = { von_Bismarck-Bohlen ... }
    common_last_names = { Abegg ... }
    graphics = european
    ethnicities = { 1 = caucasian }
}
```

Optional per survey of all files: `male_regal_first_names`, `female_regal_first_names`, `seal_and_signature_texture`. Religions are simpler:

```
# game/common/religions/religion.txt
sunni = {
    icon = "gfx/interface/icons/religion_icons/sunni.dds"
    heritage = heritage_islamic
    color = { 0.1 0.5 0.3 }
    taboos = { liquor wine }           # optional
}
```

---

## 6. Releasables and formables

### `common/country_creation/00_releasable_countries.txt` — released via diplomacy/war/decision

```
UBD = {
    states = { STATE_KAUNAS STATE_VILNIUS STATE_TALINN STATE_TARTU STATE_RIGA STATE_COURLAND }
    required_num_states = 3
    ai_will_do = { always = no }
    possible = {
        OR = {                                   # vanilla's pattern for asymmetric checks:
            scope:war_goal_holder ?= {           # set when released via war goal
                has_technology_researched = pan-nationalism
            }
            AND = {
                NOT = { exists = scope:war_goal_holder }
                has_technology_researched = pan-nationalism
            }
        }
    }
}
AUS = {
    use_culture_states = yes                     # alternative to explicit states list:
    required_num_states = 2                      # all homelands of the tag's cultures
    ai_will_do = { always = no }
}
```

File header comments: `Root` = the country giving up land; `scope:war_goal_holder` = the country pressing the war goal (unset outside war).

### `common/country_formation/` — formed by the player/AI from the map

```
# game/common/country_formation/00_formable_countries.txt
SWE = {
    states = { STATE_SVEALAND STATE_GOTALAND STATE_SCANIA STATE_NORRLAND }
    required_states_fraction = 0.75
    ai_will_do = { always = no }
}
UBD = {
    use_culture_states = yes
    required_states_fraction = 1
    ai_will_do = { always = yes }
    possible = { has_technology_researched = pan-nationalism }
}
```

Major unifications (`00_major_formables.txt`) add unification-play plumbing:

```
GER = {
    geographic_region = geographic_region_greater_germany   # instead of a states list
    is_major_formation = yes
    unification_play = dp_unify_germany
    leadership_play = dp_leadership_germany
    required_states_fraction = 0.73
    ai_will_do = { has_technology_researched = nationalism }
    possible = { ... }                                       # tech + tooltip checks
    max_num_formation_candidates = 3
    can_be_formation_candidate = { country_rank >= rank_value:major_power }
    can_be_unification_target = { NOR = { has_government_type = gov_dual_monarchy ... } }
    should_target_state_in_unification_play = {}
}
ITA = { use_culture_states = yes  is_major_formation = yes  potential = { ... }  ... }
```

The tag being releasable/formable must already exist in `country_definitions` (and have loc). It needs **no** `history/states` entry — it starts landless.

---

## 7. How Victorian Century organizes its overrides (patterns worth copying)

Mod root:
- Windows: `C:\Users\<username>\OneDrive\Documents\Paradox Interactive\Victoria 3\mod\3219394272`
- Mac: `~/Documents/Paradox Interactive/Victoria 3/mod/3219394272`

1. **Full-file override by identical filename** — for files where entries can't be merged. `common/history/countries/gbr - great britain.txt` (and 13 others: aus, bic, chi, fra, jap, nep, net, pru, rus, spa, tur, usa) match vanilla filenames exactly, replacing the whole file. Likewise all 16 `map_data/state_regions/*.txt` are copies of vanilla with edits (added traits, raised `arable_land`, converted `capped_resources` mines into discoverable `resource` blocks with `discovered_amount`/`undiscovered_amount`).
2. **`REPLACE_OR_CREATE:` prefix for database entries** — used in `common/country_definitions/zz_imp_countries.txt`, `common/country_formation/joi_imperial_federation.txt` / `jol_major_formables.txt`, `common/cultures/joi_cultures.txt`:
   ```
   # mod/3219394272/common/country_definitions/zz_imp_countries.txt
   REPLACE_OR_CREATE:IMP = {
       color = hsv{ 1  1  0.5 }
       country_type = recognized
       tier = hegemony
       cultures = { british scottish irish anglo_canadian franco_canadian australian boer }
       capital = STATE_HOME_COUNTIES
   }
   ```
   This lets a uniquely-named mod file redefine or add an entry without copying the whole vanilla file.
3. **Prefixed new files for pure additions** — `joi_global.txt` (extra `GLOBAL = { }` block: history folders accept multiple files, all executed), `joi_strategy.txt` (`AI = { c:BIC ?= { set_strategy = ... } }`), `joi_lobbies.txt`, `joi_power_blocs.txt`, `joi_countries_l_english.yml`. New content never touches vanilla-named files unless a full replace is intended.
4. Gating formables on journal/variable state: the mod's `IMP` formable requires `has_variable = allow_to_form_imp` set by its journal content — a clean way to script-gate formation.

---

## 8. Practical recipes

### A. Add a new releasable country (no land at start)

1. `common/country_definitions/<mymod>_countries.txt` — new file: `XYZ = { color/country_type/tier/cultures/capital }` (capital must be a real `STATE_X`; tag = capital letters/numbers only).
2. `common/country_creation/<mymod>_releasables.txt` — `XYZ = { states = { STATE_A STATE_B } required_num_states = 1 ai_will_do = { always = no } possible = { ... } }` (or `use_culture_states = yes`).
3. Optional: make its states homelands of its culture — new `common/history/states/<mymod>_homelands.txt` with `STATES = { s:STATE_A = { add_homeland = cu:myculture } }` (additive; do not re-`create_state`).
4. `localization/english/<mymod>_countries_l_english.yml` — `XYZ: "Name"`, `XYZ_ADJ: "Adj"` (see `08-localization.md` for BOM/encoding rules).
5. Optional flavor: entry in `common/history/countries/` (runs only once the tag exists — guard with `c:XYZ ?=`), coat of arms in `common/coat_of_arms/` (see `01-mod-structure.md`).

### B. Give an existing country different start laws

1. Copy vanilla `common/history/countries/<tag> - <name>.txt` into your mod at the **same relative path and filename** (full-file override).
2. Edit the `activate_law = law_type:...` lines — one active law per law group; also adjust `effect_starting_politics_*` / ruling IG lines so government matches the laws.
3. No localization needed. Do not rename the file, or you'll get both versions' effects.

### C. Add a state trait to a state

1. Define the trait: `common/state_traits/<mymod>_traits.txt` — `state_trait_my_thing = { icon = "gfx/.../x.dds" modifier = { ... } }`.
2. Copy the vanilla `map_data/state_regions/NN_region.txt` containing the state into your mod (same filename — full-file override; state_regions entries can't be partially patched) and append the trait to that state's `traits = { }`.
3. Loc: `state_trait_my_thing: "My Thing"` in `localization/english/<mymod>_l_english.yml` (vanilla keeps these in `map/state_traits_l_english.yml`).

### D. Change a country's starting buildings

1. Find the state in vanilla `common/history/buildings/NN_region.txt`; copy that file into your mod with the same filename.
2. Inside `BUILDINGS={ s:STATE_X={ region_state:TAG={ ... } } } }` add/edit `create_building` blocks: `building=`, `add_ownership` (`country={country="c:TAG" levels=N}` or `building={type= country= levels= region=}`), `reserves=1`, `activate_production_methods={ ... }` (one PM per group).
3. Check PMs are unlocked by the country's start techs (`history/countries` tier effects), or the building will switch PMs on day one.

### E. Move territory between countries at start

1. Copy `common/history/states/00_states.txt` (same filename) and edit the relevant `s:STATE_X` block: change `country = c:TAG` or split into multiple `create_state` blocks with disjoint `owned_provinces`.
2. Update `common/history/pops/NN_region.txt` for that state: `region_state:NEWTAG = { create_pop ... }` — pops keyed to a `region_state:` that doesn't exist are lost.
3. Update `common/history/buildings/NN_region.txt` the same way.
4. Check `history/diplomacy` and `history/military_formations` for references to the old arrangement.

---

## Common pitfalls

- **Province lists must match the map.** `owned_provinces` in `history/states` must be a subset of that region's `provinces` in `map_data/state_regions`. Unassigned provinces or provinces listed in two `create_state` blocks cause broken states.
- **`region_state:TAG` must exist.** Pops/buildings/trade under `region_state:SWE` silently vanish if SWE doesn't own part of that state in `history/states`.
- **Same-filename = full replace.** A mod file named like a vanilla file replaces it entirely — including everything you didn't copy. Conversely, a *renamed* copy of a history file means both run (duplicate pops/buildings). Pick one: identical name to replace, unique prefixed name to add.
- **Missing homeland → no releasable via culture.** `use_culture_states = yes` in country_creation/formation resolves through `add_homeland` entries in `history/states`; a culture with no homelands yields nothing.
- **Pop totals**: `create_pop` sizes are the state's whole population; forgetting to rebalance after splitting a state doubles population. Vanilla annotates estimates with comments — keep totals plausible per `arable_land`.
- **One law per group.** Two `activate_law` from the same lawgroup is invalid setup; also keep laws consistent with `effect_starting_politics_*` scripted effects.
- **Guard with `?=`.** Vanilla writes `c:TAG ?=`, `ig:ig_x ?=` everywhere in history so setups survive missing tags/DLC content (see `02-script-language.md`).
- **Tag format**: capitals and digits only (vanilla warns of civil-war bugs otherwise). Don't reuse `D00`–`D99` (reserved dynamic tags).
- **PM lists**: `activate_production_methods` needs a valid PM for each group of that building; misspelled PMs revert to defaults at start.
- **Loc keys are separate files**: new tags need `TAG`/`TAG_ADJ`, new states `STATE_X` (+ `HUB_NAME_STATE_X_city` etc.), new traits `state_trait_x` — see `08-localization.md`.
- **Strategic region membership**: if you add a brand-new state region, it must also be added to exactly one region in `common/strategic_regions/` and needs `naval_exit_id` if coastal.
