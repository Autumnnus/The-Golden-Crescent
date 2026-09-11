# 06 – Modifiers: Types, Named Modifiers, Timed Modifiers, Balance

**Read this file when:** you need to buff/debuff a country, state, interest group, character or building — via an event reward (`add_modifier`), a state trait, a law/tech/JE effect block, or a brand-new modifier type — and you need to know where things are defined, the exact syntax, and what magnitudes/durations vanilla considers normal.

Cross-references: `02-script-language.md` (scopes, script values), `03-events.md` (event options where `add_modifier` usually lives), `09-design-and-balance.md` (overall balance philosophy).

---

## 1. The three layers of the modifier system

1. **Modifier TYPE definitions** — `common/modifier_type_definitions/` — declare every *modifier key* the engine knows (`country_authority_mult`, `state_migration_pull_mult`, ...) with display metadata (decimals, color, percent, boolean). ~2350 types in vanilla.
2. **Named modifiers** — `common/static_modifiers/` — bundles of type entries with a name and icon. This is where every modifier used by `add_modifier` lives. (Older guides mention `common/modifiers/` — that folder **does not exist** in the current game; `common/static_modifiers/` is the one folder for both code-hook statics and event/JE/decision modifiers.)
3. **Application** — effect blocks. Either *implicit* (a law, technology, production method, state trait, institution etc. has a `modifier = { ... }` block of raw type entries) or *explicit and usually timed* (`add_modifier = { name = X days = Y }` in events, journal entries, decisions, history files).

Verified by grepping: `state_gold_rush` is used by `game/events/gold_rush.txt` and defined in `game/common/static_modifiers/02_event_modifiers.txt`.

---

## 2. Modifier type definitions

Folder:
- Windows: `C:\Program Files (x86)\Steam\steamapps\common\Victoria 3\game\common\modifier_type_definitions\`
- Mac: `~/Library/Application Support/Steam/steamapps/common/Victoria 3/game/common/modifier_type_definitions/`
Files: `00_modifier_types.txt`, `01_building_modifier_types.txt`, `02_modifier_types_rules.txt` (booleans), `03_modifier_types_script_only.txt`, `04_label_modifier_types.txt`, `05_power_bloc_modifier_types.txt`, `06_country_modifier_types.txt`, `07_description_modifier_types.txt`, `08_movement_modifier_types.txt`, `09_social_class_modifier_types.txt`, `10/11_*_culture_modifier_types.txt`, `12_ip4_script_modifiers.txt`, `13_ep2_script_modifiers.txt`, `99_todo_sort_into_other_files.txt`, plus `modifier_types.md` (Paradox's own format doc).

### Anatomy (from `modifier_types.md`, annotated by Paradox)

```
# game/common/modifier_type_definitions/modifier_types.md (vanilla format doc, trimmed)
modifier_type_key = {
    decimals = 0        # decimal points shown
    color = neutral     # good / neutral / bad  (which direction is "green")
    percent = no        # yes -> displayed *100 with % sign (raw value unchanged)
    prefix = "MONEY_PREFIX"   # optional display prefix
    suffix = "PER_CAPITA"     # optional display suffix
    boolean = yes       # value is a flag; only `yes` is valid as an entry value
    game_data = {
        ai_value = 0            # AI desirability weight (only some types)
        translate = battle_offense_add   # treat as another type in bespoke code
        type_set = { cultural_acceptance }
    }
}
```

A real one:

```
# game/common/modifier_type_definitions/00_modifier_types.txt
country_bureaucracy_add = {
	decimals = 1
	color = good
	game_data = { ai_value = 20 }
}
```

`03_modifier_types_script_only.txt` additionally uses `script_only = yes` (e.g. `character_battle_condition_dug_in_mult`), and `04_label_modifier_types.txt` shows `translate` in action (`unit_offense_flat_add` translates to `unit_offense_add`).

### Naming grammar

The **prefix decides which object the entry attaches to and how it flows through the modifier graph** (comment at top of `modifier_types.md`: a `country_` entry on a power-bloc modifier flows to member countries and stops; a `state_` entry flows through countries down to their states).

Approximate prefix counts in vanilla (grep of all definition keys):

| Prefix | Count | Example (real key) |
|---|---|---|
| `country_` | ~1087 | `country_authority_mult`, `country_legitimacy_base_add` |
| `state_` | ~569 | `state_migration_pull_mult`, `state_infrastructure_add` |
| `building_` / `building_group_` | ~300 | `building_gold_field_throughput_add`, `building_group_bg_agriculture_throughput_add` |
| `goods_` | ~125 | `goods_output_tools_mult`, `goods_input_ironclads_mult` (mod) |
| `ship_` | ~68 | `ship_movement_speed_mult` |
| `unit_` | ~55 | `unit_offense_mult`, `unit_morale_loss_mult` |
| `character_` | ~40 | `character_popularity_add`, `character_health_add` |
| `power_bloc_` | ~38 | `power_bloc_leader_can_force_state_religion_bool` |
| `interest_group_` | ~32 | `interest_group_approval_add`, `interest_group_pol_str_mult` |
| `battle_` | ~12 | `battle_defense_owned_province_mult` |
| `military_formation_` | ~11 | `military_formation_army_movement_speed_mult` |
| `political_movement_` | ~6 | `political_movement_radicalism_add` |

Suffix grammar (counted across all vanilla definitions):

| Suffix | Count | Meaning as used |
|---|---|---|
| `_add` | ~1630 | flat addition |
| `_mult` | ~621 | multiplier; nearly always paired with `percent = yes` |
| `_bool` | ~87 | flag, `boolean = yes`, entry value must be `yes` (e.g. `country_forbid_electoral_fraud_bool`) |
| `_factor` | ~5 | rare (e.g. `country_bureaucracy_investment_cost_factor_mult` family) |

Many keys are **pattern-based**: the middle of the key names a concrete game object — `goods_output_<good>_mult`, `building_group_bg_<group>_throughput_add`, `interest_group_ig_<ig>_approval_add`, `unit_combat_unit_type_<type>_offense_mult`, `state_<culture|religion>_standard_of_living_add`. Vanilla only defines the instances it uses (e.g. `goods_output_tools_mult` exists, `goods_output_iron_mult` does not) — see §9 for how the Victorian Century mod adds missing instances.

---

## 3. Named modifiers (`common/static_modifiers/`)

One folder holds two things:

### 3a. Code-hook static modifiers (`00_code_static_modifiers.txt`)

Header comment: *"these names can NOT be removed or changed, as the code uses them"*. They are applied automatically by game features — `base_values` (global baseline: `country_bureaucracy_add = 100`, `state_infrastructure_add = 3`, ...), `prestige_ranking`, `top_prestige_ranking`, `character_base_values`, `character_noble`, `character_historical`, `coastal_state`, `incorporated_state`, `working_conditions`, etc. Other code-referenced files sit alongside (`01_loans.txt`, `05_rule_modifiers.txt`, `06_conscription_modifiers.txt`, `07/08_*_standard_of_living.txt`, ...).

A modder touches these only to **rebalance game-wide baselines by overriding the block**. Victorian Century does exactly this:

```
# mod/3219394272/common/static_modifiers/joi_code_static_modifiers.txt (trimmed)
REPLACE_OR_CREATE:base_values = {
	country_authority_add = 300      # vanilla: 100
	country_influence_add = 300      # vanilla: 100
	country_minting_add = 1000       # vanilla: 500
	...
}
REPLACE_OR_CREATE:incorporated_state = {
	state_allow_assimilation_without_presence_bool = yes
	...
}
```

`REPLACE_OR_CREATE:` is an engine-recognized database prefix (the string exists in `binaries/victoria3.exe`; vanilla script never uses it). Semantics inferred from name and mod usage: replace the same-named vanilla entry, or create it if absent. Victorian Century prefixes nearly every overriding top-level key with it.

### 3b. Ordinary named modifiers — the `add_modifier` pool

Everything else in `static_modifiers/` (`02_event_modifiers.txt`, `04_decision_modifiers.txt`, dozens of content files like `agitators_1_modifiers.txt`, `morocco_modifiers.txt`, ...). Full anatomy is just **key + icon + modifier-type entries** — there is no category/duration field; duration comes from the `add_modifier` call:

```
# game/common/static_modifiers/02_event_modifiers.txt
state_gold_rush = {
	icon = gfx/interface/icons/timed_modifier_icons/modifier_flag_positive.dds
	state_migration_pull_mult = 1.25
}

army_resources_modifier = {
	icon = gfx/interface/icons/timed_modifier_icons/modifier_rifle_positive.dds
	country_bureaucracy_mult = 0.05
	country_prestige_from_army_power_projection_mult = 0.1
}
```

Icons are almost always from `gfx/interface/icons/timed_modifier_icons/` with a `_positive` / `_negative` variant (`modifier_flag_`, `modifier_statue_`, `modifier_documents_`, `modifier_coins_`, `modifier_rifle_`, `modifier_fist_`, `modifier_gear_`, `modifier_fire_`...). Mods can use custom icons (Victorian Century: `icon = gfx/interface/icons/joi_icons/house_of_habsburg.png`).

Victorian Century keeps all its ~12,000 lines of named modifiers in `mod/3219394272/common/static_modifiers/joi_modifiers.txt`:

```
# mod/3219394272/common/static_modifiers/joi_modifiers.txt
super_angry_in_springtime = {
	icon = gfx/interface/icons/timed_modifier_icons/modifier_statue_negative.dds
	interest_group_approval_add = -10
	political_movement_radicalism_add = 0.25
}
```

---

## 4. Applying and removing modifiers

All forms below are copied from vanilla script.

### add_modifier — timed (the standard event-reward form)

```
# game/events/gold_rush.txt
add_modifier = {
	name = state_gold_rush
	days = normal_modifier_time      # script value = 1825 days (5 years)
}
```

`days`, `months`, or `years` (one of them) set the duration; script values are allowed for `days` (vanilla always uses the named durations, §7). Explicit forms seen in vanilla: `months = 12`, `years = 3`, `days = 365`. The Victorian Century mod prefers explicit years: `add_modifier = { name = super_angry_in_springtime years = 5 }` (`mod/3219394272/events/joi_flavor_aus.txt`).

### Optional keys: is_decaying, multiplier

```
# game/common/journal_entries/00_sick_man.txt
on_timeout = {
	remove_modifier = sick_man_of_europe
	add_modifier = {
		name = dead_man_of_europe
		days = very_long_modifier_time
		is_decaying = yes          # value winds down over the duration
	}
}
```

`multiplier` scales every numeric entry in the named modifier. Vanilla uses plain numbers (`0.5`, `2`, `-1` to flip a modifier into its mirror), money script values, and full script-value blocks:

```
# game/events/1848.txt — money modifier: definition has country_expenses_add = 1,
# the multiplier supplies the actual amount (% of GDP script values, see §7)
add_modifier = {
	name = government_food_dole
	multiplier = money_amount_multiplier_small
	days = short_modifier_time
}
```

```
# game/events/iberia_events/morocco_makhzen_events.txt — scaled by JE progress bar
add_modifier = {
	name = state_of_anarchy_scaled_mod
	multiplier = {
		value = "scope:journal_entry.scripted_bar_progress(lands_of_anarchy_tribes_of_marrakech_bar)"
		divide = -100
		add = 5.15
	}
}
```

### add_modifier — permanent

Omit the duration (block form or shorthand). Used in history files and for flags removed manually later:

```
# game/common/history (trimmed)
add_modifier = { name = modifier_ryotwari_system }
add_modifier = { name = modifier_regency_intelligentsia }

# shorthand, game/events + mod events:
add_modifier = garibaldi_popularity_modifier_tier_1
add_modifier = aus_dirct_rule        # mod/3219394272/events/joi_flavor_aus.txt
```

### Target scope

`add_modifier` applies to the current scope — country (event root), state, interest group, or character. Real scoping seen in vanilla:

```
# game/events/acceptance_events.txt
ig:ig_landowners = {
	add_modifier = {
		name = modifier_royal_customs_respected
		days = long_modifier_time
		is_decaying = yes
	}
}
```

### remove_modifier / has_modifier

```
remove_modifier = state_gold_rush            # effect; always this one-line form
has_modifier = state_gold_rush               # trigger, on the owning scope
NOT = { has_modifier = upset_royalist_hardliners }
```

Vanilla frequently does `remove_modifier` then re-`add_modifier` (see the Morocco snippet's `hidden_effect`) to refresh/rescale a modifier.

### Special add_*_modifier effect variants (counts across vanilla events + JEs)

`add_enactment_modifier` (625 — law-enactment modifiers, `name = modifier_wasted_session`, removed with `remove_enactment_modifier`), `add_fervor_target_modifier` (41), `add_culture_standard_of_living_modifier` (31 — `{ culture = scope:x days = short_modifier_time multiplier = -1 }`), `add_culture_acceptance_modifier` (9), `add_religion_standard_of_living_modifier` (7), `add_regency_modifier` (6), `add_plague_modifier` (4). These pull from pre-made static modifiers in files like `07_culture_standard_of_living.txt`.

---

## 5. Opinion modifiers (brief)

`game/common/opinion_modifiers/opinion_modifiers.txt` — only 6 entries; anatomy per `opinion_modifiers.md`:

```
opinion_friendly_nation = {
	opinion = { value = 50 ... }   # value applied, supports if/limit + multiply
	decay = { value = 1 ... }      # per-tick decay; omit = never decays
}
```

No `add_opinion_modifier`-style effect exists anywhere in vanilla script — these entries (rivals, interest markers) appear to be engine-driven. Rarely modder-relevant; edit values only.

## 6. Scripted modifiers (brief)

`game/common/scripted_modifiers/` contains **only** `scripted_modifiers.md` in the current version — no actual entries ship. The .md shows the format: a named block of `if = { limit = {...} factor = 0.2 }` weight adjustments (`is_accepted_culture_and_religion`), i.e. a reusable *score multiplier function* for script — not a gameplay modifier. (Usage sites unverified; vanilla currently has none.)

## 7. State traits (brief)

`game/common/state_traits/` (regional files, `00_generic_traits.txt` first). Anatomy: icon, optional tech gates, and a `modifier = {}` block of raw type entries — state traits are *not* addable via `add_modifier`; they attach to state regions in `map_data/state_regions/*.txt` via `traits = { "state_trait_natural_harbors" ... }`.

```
# game/common/state_traits/00_generic_traits.txt
state_trait_severe_malaria = {
	icon = "gfx/interface/icons/state_trait_icons/severe_malaria.dds"
	required_techs_for_colonization = { "quinine" }
	disabling_technologies = { "malaria_prevention" }
	modifier = {
		state_non_homeland_colony_growth_speed_mult = -0.95
		state_non_homeland_mortality_mult = 0.25
	}
}

state_trait_good_soils = {
	icon = "gfx/interface/icons/state_trait_icons/good_soils.dds"
	modifier = {
		building_group_bg_agriculture_throughput_add = 0.1
		building_group_bg_plantations_throughput_add = 0.1
	}
}
```

Victorian Century adds rivers/canals/resources the same way (`mod/3219394272/common/state_traits/joi_river_traits.txt` etc.): rivers give `state_infrastructure_add = 20–40` + `state_market_access_price_impact = 0.025–0.05`; ore fields give `building_iron_mine_throughput_add = 0.15–0.25`.

---

## 8. BALANCE REFERENCE (surveyed from vanilla files)

### 8a. Durations

Vanilla never hardcodes common durations — it uses script values from `game/common/script_values/event_values.txt`:

| Script value | Days | = Years | Uses in vanilla events (`days = X`) |
|---|---|---|---|
| `very_short_modifier_time` | 365 | 1 | ~0 (defined, almost unused) |
| `short_modifier_time` | 913 | 2.5 | 693 |
| `normal_modifier_time` | 1825 | 5 | **2313 (~58% of all timed)** |
| `long_modifier_time` | 3650 | 10 | 545 |
| `moderately_long_modifier_time` | 5475 | 15 | 20 |
| `very_long_modifier_time` | 7300 | 20 | 234 |
| `even_longer_modifier_time` | 10950 | 30 | 3 |
| `stupidly_long_modifier_time` | 18250 | 50 | 33 |
| `never_fire_again_modifier_time` | 73000 | 200 | 222 — but almost entirely as event `cooldown = { days = never_fire_again_modifier_time }`, not add_modifier |

Explicit durations are rare in vanilla (39× `months = 12`, 16× `months = 36`, 5× `years = 3`, ...). Of ~4185 `add_modifier` in vanilla events, roughly 200–400 have **no duration** (permanent flags/markers removed by script). `is_decaying = yes` appears 384× (events + JEs) — use it when a shock should fade rather than cliff-drop.

**Rule of thumb: a vanilla event reward/penalty lasts 5 years (normal) — use 2.5 years for minor/temporary, 10 years for major, 20+ only for era-defining consequences.** Victorian Century's own events overwhelmingly use explicit `years = 5` (275×), `years = 10` (256×), `years = 20` (139×) — same buckets, longer tail.

### 8b. Magnitudes — typical values per modifier type in vanilla named modifiers

Counted across all of `game/common/static_modifiers/*.txt` (the add_modifier pool). "Typical" = the mode ± the common band; extremes are rare and reserved for catastrophic/heroic content.

| Modifier type | Typical | Strong | Notes |
|---|---|---|---|
| `interest_group_approval_add` | ±1 to ±3 (mode **±2**, 865 uses) | ±5, rare ±10 | the single most-used effect |
| `interest_group_pol_str_mult` | ±0.10 to ±0.25 | ±0.25+ | |
| `interest_group_pop_attraction_mult` | ±0.10 to ±0.25 | | |
| `country_law_enactment_success_add` | ±0.10 to ±0.20 | | petition/agitator events |
| `country_authority_mult` | ±0.05 to ±0.20 (mode 0.10) | ±0.25 | |
| `country_influence_mult` | ±0.05 to ±0.25 | | |
| `country_prestige_mult` | +0.05 to +0.25 / −0.10 to −0.25 | | |
| `country_legitimacy_base_add` | ±5 to ±10 | ±20 | |
| `country_bureaucracy_mult` | ±0.05 to ±0.10 | | |
| `character_popularity_add` | ±15 to ±50 (modes 25/50) | ±50 | |
| `state_migration_pull_mult` | +0.10 to +0.50 | 1.0–1.25 (gold rush) | |
| `state_radicals/loyalists_from_political_movements_mult` | ±0.05 to ±0.25 | | |
| `political_movement_radicalism_add` | ±0.05 to ±0.15 | ±0.25 | |
| `state_mortality_mult` | 0.02–0.10 | 0.5 (plague) | |
| `unit_morale_loss_mult` | ±0.05 to ±0.20 | | |
| building/`building_group_*_throughput_add` (events) | ±0.05 to ±0.20 | ±0.3–0.4 | |
| state traits `*_throughput_add` | 0.10 (122×), 0.15 (48×), 0.20 (47×) | 0.25–0.30 | penalties −0.1/−0.2 |
| state traits `state_infrastructure_add` | +10 to +20 | +25 (mod rivers up to +40) | |
| state traits `state_infrastructure_mult` | −0.10 to −0.25 | | bad terrain |

Penalties are **symmetric with buffs** in vanilla — the same magnitudes with flipped sign (often literally the same modifier applied with `multiplier = -1`), e.g. `interest_group_approval_add`: 2 (182×) vs −2 (231×); negative slightly more frequent.

### 8c. Money modifiers

Convention: the named modifier carries `country_expenses_add = 1` (102 of 137 uses are exactly 1) and the real amount comes from GDP-scaled multipliers in `event_values.txt`:

| Script value | % of GDP |
|---|---|
| `money_amount_multiplier_very_small` | 0.015% |
| `money_amount_multiplier_small` | 0.025% |
| `money_amount_multiplier_medium` | 0.05% |
| `money_amount_multiplier_large` | 0.1% |
| `money_amount_multiplier_more_large` | 0.2% |
| `money_amount_multiplier_very_large` | 0.5% |

Multiplier usage counts in events: `0.5` (140), `2` (130), `1` (68), `money_amount_multiplier_small` (57), `_medium` (51), `-1` (49), script-value blocks (31), `_very_small` (18), `_large` (10).

### 8d. Concrete guidance

- **Small event reward:** one effect at the "typical" low end (e.g. `interest_group_approval_add = 2` or `country_authority_mult = 0.05`) for `short_modifier_time`–`normal_modifier_time` (2.5–5 y).
- **Medium:** 1–2 effects at mode values (`±0.10 mult` / `±2 approval` / `±10 legitimacy`) for 5 y. This is the vanilla default reward.
- **Large / era-defining:** 2–3 effects at 0.15–0.25 mult for `long_modifier_time`–`very_long_modifier_time` (10–20 y), usually `is_decaying = yes` for the biggest ones.
- Vanilla almost never exceeds ±25% on a `_mult` in a timed event modifier; Victorian Century's AI-only handicap modifiers (`great_power_ai_buff` in `joi_modifiers.txt`: `country_construction_add = 500`, `state_tax_capacity_mult = 0.5`, `country_tax_income_add = 30000`) show what deliberately *out-of-band* values look like — do not use such numbers for player-facing content.

---

## 9. New modifier type vs reusing an existing one

**Reuse whenever possible** — 2350 types exist; grep `modifier_type_definitions` before inventing anything.

Create a new type when you need a *pattern instance* vanilla never defined. Victorian Century's `mod/3219394272/common/modifier_type_definitions/joi_modifier_types.txt` is entirely this:

```
# mod/3219394272/common/modifier_type_definitions/joi_modifier_types.txt
REPLACE_OR_CREATE:goods_output_iron_mult = {   # vanilla has goods_output_tools_mult but not iron
	decimals = 1
	color = good
	percent = yes
	game_data = { ai_value = 0 }
}

REPLACE_OR_CREATE:unit_combat_unit_type_lancers_offense_mult = {
	decimals = 0
	color = good
	percent = yes
	game_data = { ai_value = 0 }
}

REPLACE_OR_CREATE:country_disallow_trade_outside_kyushu_bool = {
	decimals = 1
	color = bad
	boolean = yes
	game_data = { ai_value = 0 }
}
```

Patterns the mod successfully extends: `goods_output_<good>_mult`, `goods_input_<good>_mult`, `unit_combat_unit_type_<type>_offense/defense_mult`, `building_group_<bg>_employee_mult`, plus `state_working_adult_ratio_add`. Every observed new type follows an existing engine naming pattern; there is no example (vanilla or mod) of an arbitrary free-form type name acquiring gameplay behavior by itself — the key's structure is what the engine interprets. `_bool` types are the exception: script/GUI can test them, so a novel `country_<anything>_bool` is a common modder trick (observed: `country_disallow_trade_outside_kyushu_bool`).

After defining the type: give it localization (below) and use it inside any named modifier / `modifier = {}` block.

---

## 10. Localization

Two patterns, both plain keys in any `localization/english/*_l_english.yml`:

**Modifier types** — key + `_desc`, conventionally in `modifiers_l_english.yml`:

```
# game/localization/english/modifiers_l_english.yml
 country_authority_mult:2 "@aut![Nbsp][concept_authority]"
 country_authority_mult_desc:2 "The amount of @aut![Nbsp][concept_authority] is modified up or down"
```

(`@aut!` = inline text icon; `[concept_authority]` = game-concept link; `$key$` reuses another loc string.) Mod equivalent, `mod/3219394272/localization/english/joi2_modifiers_l_english.yml`:

```
 goods_output_iron_mult: "Building@iron!Iron Output"
 goods_output_iron_mult_desc: "Bonus or penalty to the amount of @iron!Iron output by the building"
```

**Named modifiers** — just the key, anywhere (this is the name shown on the timed-modifier icon; the entries render themselves via their type loc):

```
# game/localization/english/events_l_english.yml
 state_gold_rush:0 "Gold Rush"
# game/localization/english/agitators_1_l_english.yml
 government_food_dole: "Government Food Dole"
# mod: localization/english/joi_modifiers_l_english.yml
 super_angry_in_springtime: "Reject Pillersdorf Constitution"
```

State traits use the same named pattern (`state_trait_x: "..."`).

---

## Common pitfalls

- **Looking for `common/modifiers/`** — it no longer exists. Named modifiers go in `common/static_modifiers/`; types in `common/modifier_type_definitions/`.
- **Using a modifier type that isn't defined** — `goods_output_iron_mult` in a modifier block does nothing/errors until a type definition exists. Grep `modifier_type_definitions` (vanilla + your mod) first.
- **Forgetting `percent = yes` on a `_mult` type** — the tooltip shows `0.1` instead of `10%`. Conversely `_mult` values are written as decimals in script (`0.1` = +10%), never `10`.
- **Wrong `color`** — `color = good` means *positive value displays green*. A cost/penalty type (e.g. `goods_input_manowars_mult`) needs `color = bad` so increases show red.
- **Expecting duration or icon on `add_modifier`** — duration lives in the `add_modifier` call; icon lives in the static modifier definition. You cannot set an icon per-application.
- **`remove_modifier = { name = X }`** — wrong; the effect takes a bare key: `remove_modifier = X`. The block form is only for `add_modifier`.
- **Boolean entries with numbers** — `_bool` types accept only `yes` as entry value (per `modifier_types.md`).
- **Re-adding without removing** — vanilla wraps refreshes as `hidden_effect = { remove_modifier = X }` then `add_modifier` (see `morocco_makhzen_events.txt`) to avoid stacking/keeping the old timer.
- **Missing loc** — an unlocalized named modifier shows its raw key in the UI. Add `<key>: "Name"`; types need `<key>` *and* `<key>_desc`.
- **Out-of-band balance** — anything beyond ±25% mult or ±3 IG approval on a 5-year timer is *large* by vanilla standards (§8). Escalate duration before magnitude.
- **Editing vanilla static hook names** — the entries in `00_code_static_modifiers.txt` "can NOT be removed or changed" (their names, that is); override the whole block in your mod (Victorian Century uses `REPLACE_OR_CREATE:base_values = { ... }`) rather than renaming or deleting.
