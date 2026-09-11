# Victoria 3 Script Language Reference

**Read this file when:** writing or editing any Victoria 3 script `.txt` — events, journal entries, decisions, scripted effects/triggers, script values, on_actions. This is the core language reference (scopes, triggers, effects, variables, script values). For file-format specifics see `03-events.md`, `05-journal-entries-and-decisions.md`, `06-modifiers.md`.

All syntax below was verified against vanilla 1.9-era files in `C:\Program Files (x86)\Steam\steamapps\common\Victoria 3\game\` (Mac: `~/Library/Application Support/Steam/steamapps/common/Victoria 3/game/`) and the "Victorian Century" mod (`mod\3219394272`). Victoria 3 is NOT CK3/EU4/HOI4 — do not import syntax from other Paradox games.

## 1. Basic syntax

- Files are UTF-8 **with BOM** (verified on vanilla and mod files). Extension `.txt`.
- Structure is `key = value` and nested `key = { ... }` blocks. No semicolons, no commas.
- Comments: `#` to end of line.
- Booleans: `yes` / `no`.
- Comparison operators (all observed): `=`, `<`, `>`, `<=`, `>=`, `!=`, and `?=` (see below).

```
# common\journal_entries\00_warlord_china.txt
country_rank != rank_value:unrecognized_power
# common\journal_entries\05_montenegro_je.txt
owner != c:TUR
var:last_week_raiding_income != raiding_income
# common\scripted_triggers\00_scripted_triggers.txt
country_rank >= rank_value:unrecognized_major_power
```

- `?=` is the "if exists" operator. As a scope entry `c:CHI ?= { ... }` runs the block only if China exists; as a comparison `power_struggle_contender ?= $TARGET$` or `c:MGL ?= this` it is safe when either side may not exist. Vanilla consistently uses `?=` for country tags, saved scopes and links that can be absent.
- String quoting: file paths and sound ids are quoted (`icon = "gfx/interface/icons/event_icons/event_map.dds"`), loc keys are unquoted (`name = joi_flavor_rus.1.a`). Quotes also wrap "function-call" values (section 8) and occasionally `text = "some_tt"`.
- `@name = value` file-local constants exist and are referenced as `@name`:

```
# common\script_values\occupation_values.txt
@max_battles_to_win_state = 4
@hazardous_terrain_factor = 0.03
```

- Case: keywords appear both lower and upper case in vanilla (`root` / `ROOT`, `prev` / `PREV`). Both work.

## 2. Scopes

Every trigger/effect evaluates in a *scope* (a country, state, character, interest group, pop, building, war, journal entry...). You change scope with links, list builders, saved scopes, or data prefixes.

### Scope keywords (verified)

| Keyword | Meaning | Example source |
|---|---|---|
| `root` / `ROOT` | Object the whole block was called on (event owner, JE country...) | `owner = ROOT` (`common\scripted_effects\00_scripted_effects.txt`) |
| `this` | Current scope | `c:MGL ?= this`, `this.state_region = s:STATE_OREGON` (`common\journal_entries\00_canada_australia.txt`) |
| `prev` / `PREV` | Scope before the last scope change | `country = prev`, `PREV = { any_scope_state = { ... } }` (`common\scripted_effects\00_scripted_effects.txt`) |

**`FROM` does not exist in Victoria 3 script.** It appears nowhere in vanilla `scripted_effects` (verified by search). Event targets are passed via *saved scopes* (`scope:name`) instead.

### Scope links (all observed in vanilla/mod)

Country: `capital`, `ruler`, `heir`, `market`, `market_capital`, `power_bloc`, `overlord`, `top_overlord`, `home_country` (of a character).
State: `owner`, `state_region`, `region` (strategic region, e.g. `region = sr:region_balkans`).
Character: `interest_group`, `owner` (country), `culture`, `religion`.
Interest group: `leader`.
Civil war / movement: `political_movement`, `civil_war`.
Power bloc: `power_bloc_leader`, `power_struggle_contender`.
Building: `state`, `owner`.

```
# events\peoples_springtime.txt (country event scope)
immediate = {
	save_scope_as = relevant_country
	capital = { save_scope_as = relevant_state }
	ruler = { save_scope_as = ruler_scope }
}
```

Links chain with dots, in triggers and in script values:

```
# common\script_values\je_values.txt
value = ROOT.power_bloc.num_power_bloc_members
# mod common\scripted_effects\joi_gov_scripted_effects.txt
market_capital.market = { market_trade = { value >= 250000 } }
# common\script_values\event_values.txt
divide = c:RUS.var:count_casian_countries
```

### Data prefixes (all observed)

| Prefix | Resolves to | Example |
|---|---|---|
| `c:TAG` | Country | `c:GBR ?= { add_treasury = 100000 }` |
| `s:STATE_X` | State region | `state_region = s:STATE_KHIVA` |
| `s:STATE_X.region_state:TAG` | That country's state in the region | `state = s:STATE_HILL_PUNJAB.region_state:BIC` (`00_sepoy_mutiny_scripted_effects.txt`) |
| `sr:region_x` | Strategic region | `region = sr:region_balkans` |
| `cu:culture` | Culture | `add_primary_culture = cu:han` |
| `ig:ig_x` | Interest group | `ig:ig_devout ?= { is_powerful = yes }` |
| `law_type:x` | Law type | `activate_law = law_type:law_autocracy` |
| `ideology:x` | Ideology | `has_ideology = ideology:ideology_liberal` |
| `g:goods` | Goods | `leading_producer_of = g:tobacco` (mod) |
| `pop_type:x` | Pop type | `change_poptype = pop_type:slaves` |
| `scope:name` | Saved scope | `scope:target_country = { ... }` |
| `var:x`, `global_var:x` | Variable value/target | section 4 |
| `modifier:x` | Current value of a modifier on this object | `modifier:country_voting_power_base_add > 0` |
| `rank_value:x` | Country-rank constant | `country_rank >= rank_value:major_power` |
| `relations:X` | Relations value with X | `c:RUS.relations:ROOT >= relations_threshold:friendly` |
| `relations_threshold:x` | Named relations threshold | `friendly`, `amicable`, `cordial` observed |
| `bt:building_type` | Building type | seen in `common\script_values\je_values.txt` comment |

## 3. List builders: `every_` / `any_` / `random_` / `ordered_`

Each list exists in four forms: `any_X` (trigger), `every_X` (effect iterator), `random_X` (effect on one random member), `ordered_X` (effect on member(s) by ranking). `limit = { <triggers> }` filters candidates in all of them.

List names observed in vanilla/mod script:
`any_/every_/random_ scope_state, scope_pop, scope_character, scope_building, scope_theater, scope_culture, scope_treaty, scope_article, scope_play_involved` (contextual "of this object"); `country` (all countries), `state` (all states globally), `interest_group`, `primary_culture`, `political_movement`, `political_lobby`, `civil_war`, `neighbouring_state`, `subject_or_below`, `overlord_or_above`, `diplomatically_relevant_country`, `diplomatic_play`, `active_party`, `member` (power bloc), `lobby_member`, `character_in_exile_pool`, `character_in_void`, `company`, `province`, `military_formation`, `combat_unit`, `power_bloc`, `in_list` (variable lists).

```
# common\scripted_effects\00_scripted_effects.txt — effect iterator with limit
every_scope_pop = {
	limit = {
		is_pop_type = laborers
		pop_has_primary_culture = no
		pop_acceptance < acceptance_status_4
	}
	change_poptype = pop_type:slaves
}
```

### `any_` trigger parameters: `count`, `percent`, `filter`

```
# common\journal_entries\00_canada_australia.txt
any_subject_or_below = {
	capital = { is_in_geographic_region = geographic_region_greater_canada }
	count >= 2
}
# common\journal_entries\00_alaska.txt
count = all      # every member must match
# common\journal_entries\00_belle_epoque.txt — percent of the filtered set
any_scope_state = {
	filter = { is_incorporated = yes }   # filter defines the denominator
	average_sol >= 15
	percent > 0.5
}
```

### `ordered_` parameters

```
# events\peoples_springtime.txt — pick the IG with highest clout
ordered_interest_group = {
	limit = { has_ideology = ideology:ideology_liberal }
	order_by = ig_clout        # a script value evaluated per member
	position = 0               # 0 = first (highest)
	check_range_bounds = no    # don't error if list is empty/smaller
	add_modifier = { name = modifier_springtime_kick_out_of_insurrection days = 75 }
}
```

In script values, `ordered_` lists take `order_by` and `max` (top N) — see `common\script_values\script_values.md`.

## 4. Saved scopes and variables

### Saved scopes

- `save_scope_as = name` — saves current scope as `scope:name` for the lifetime of the current event/JE chain (used heavily in `immediate = {}` so options and loc can reference `scope:name`).
- `save_temporary_scope_as = name` — same but only for the current evaluation (usable inside trigger blocks; see `violate_sovereignty_war_check` in `common\scripted_triggers\00_scripted_triggers.txt`).
- `save_temporary_scope_value_as = { name = X value = <script value> }` — saves a *number* as `scope:X`:

```
# common\on_actions\00_on_actions_monthly.txt
save_temporary_scope_value_as = {
	name = exile_pool_size
	value = { add = 0 every_character_in_exile_pool = { add = 1 } }
}
```

A non-temporary `save_scope_value_as` was **not observed** in vanilla script (unverified — prefer the temporary form or variables).
- Test existence with `exists = scope:name`; enter safely with `scope:name ?= { ... }`.

### Variables

Variables live on any object (country, state, character, state_region...). Two forms:

```
# flag form (existence only) — events\peoples_springtime.txt
set_variable = had_springtime_revolution

# valued/timed form — common\scripted_effects\00_chris_scripted_effects.txt / 00_krakatoa_effects.txt
set_variable = { name = balkan_got_tech_cooldown years = 5 }     # auto-expires -> cooldown
set_variable = { name = natural_disaster_cooldown days = normal_modifier_time }
set_variable = { name = expedition_leader_storage_var value = prev }  # value can be a scope target
set_variable = { name = help_from_locals value = no }

change_variable = { name = raiding_intensity add = 25 }           # add/subtract/multiply/divide
remove_variable = dutch_land_reclaimer
```

Read/test:

```
has_variable = raiding_intensity                     # trigger
var:last_week_raiding_income != raiding_income       # compare value (trigger)
multiply = c:MON.var:raiding_intensity               # use in script values
```

Global variables (stored on the game, same forms, prefix `global_var:`):

```
# common\scripted_effects\00_sepoy_mutiny_scripted_effects.txt
set_global_variable = sepoy_mutiny_sikh_uprising_global_var
# common\scripted_effects\00_chris_scripted_effects.txt
set_global_variable = { name = mon_raid_state value = scope:raid_target }
remove_global_variable = mon_raid_state
# common\journal_entries\00_player_objectives_great_game.txt
change_global_variable = { name = great_game_rus_progress subtract = global_var:great_game_gbr_progress }
# triggers
has_global_variable = x
exists = global_var:krakatoa_temperature_drop
global_var:je_conference_of_london_timer >= 1
global_var:chinese_central_government ?= this        # variables can hold scopes
```

Variable **lists** (`common\journal_entries\07_korea_colonization.txt`, `common\amendments\00_amendments_content_04.txt`):

```
add_to_variable_list = { name = colonize_korea_states_states target = prev }
clear_variable_list = colonize_korea_states_states
has_variable_list = spain_accepted_cultures           # trigger
any_in_list = { variable = spain_accepted_cultures cu:basque ?= this }   # trigger
every_in_list = { variable = spain_accepted_cultures ... }               # effect iterator
remove_from_list = tsunami_list                        # (00_krakatoa_effects.txt)
```

## 5. Control flow (effect context)

```
# if / else_if / else — condition goes in limit
if = {
	limit = { has_law_or_variant = law_type:law_serfdom }
	activate_law = law_type:law_tenant_farmers
}
else_if = { limit = { ... } ... }
else = { ... }

# while — common\scripted_effects\00_victoria_scripted_effects.txt
while = {
	limit = { any_state = { has_variable = potemkin_destination_state } }
	...effects...
}

# random — percentage chance to run at all (common\on_actions\00_code_on_actions.txt)
random = {
	chance = 10          # can be a script value (00_on_actions_monthly.txt)
	set_variable = var_jack_ripper_possible
}

# random_list — weighted outcomes; weights adjusted by modifier blocks
# events\prostitution_events.txt
random_list = {
	50 = {
		modifier = {                       # modifies THIS branch's weight
			if = { limit = { has_law_or_variant = law_type:law_protected_speech } add = 25 }
		}
		add_modifier = { name = coverup_discovered months = 12 }
	}
	50 = { ... }
}
# minimal form — common\scripted_effects\00_scripted_effects.txt
random_list = {
	80 = { }
	20 = { add_trait = bandit }
}
```

`switch` was **not found** anywhere in vanilla events/scripted_effects/journal_entries — do not use it; chain `if`/`else_if` instead.

Journal-entry pulses use a weighted event picker (not general control flow but common):

```
# common\journal_entries\00_land_reclamation.txt
on_yearly_pulse = {
	random_events = {
		4 = 0                    # weight 4: nothing
		1 = land_reclamation.1   # weight 1: fire this event
	}
}
```

## 6. Trigger combinators (trigger context)

All observed: `AND`, `OR`, `NOT`, `NOR`, `NAND`.

```
# common\scripted_effects\00_scripted_effects.txt
NOR = { c:MGL ?= this  c:TUV ?= this  c:ALI ?= this }
# common\journal_entries\07_korea_colonization.txt uses NAND the same way
```

Top level of a `trigger`/`limit` block is an implicit AND.

`calc_true_if` — "at least N of these":

```
# events\utopians.txt
calc_true_if = {
	amount >= 2
	has_law_or_variant = law_type:law_autocracy
	has_law_or_variant = law_type:law_oligarchy
	has_law = law_type:law_monarchy
}
```

Conditional triggers (triggers, not effects — note the different keywords):

```
# common\scripted_triggers\00_scripted_triggers.txt
trigger_if = {
	limit = { is_country_type = decentralized }
	NOT = { is_country_type = decentralized }
}
# trigger_else_if / trigger_else also observed (e.g. token counts in vanilla triggers)
```

`hidden_trigger = { ... }` — evaluated but not shown in tooltips (observed in `common\scripted_rules\00_scripted_rules.txt`).

## 7. Script values (`common\script_values\`)

Anatomy (from Paradox's own `common\script_values\script_values.md` plus live files):

- **Static:** `medium_radicals = 0.05` — referenced by name: `add_radicals = { value = medium_radicals }`.
- **Formula:** operations execute *in order written*. Keys: `value`, `add`, `subtract`, `multiply`, `divide`, `modulo`, `min`, `max` (clamps), `round = yes`, `ceiling`, `floor`, `round_to`, `if/else_if/else` (with `limit`), `fixed_range`/`integer_range` (random in range).

```
# common\script_values\event_values.txt — 0.05% of GDP rounded to nearest 100
money_amount_multiplier_medium = {
	value = root.gdp
	divide = 100000
	multiply = 0.25
	round = yes
	multiply = 100
	min = 100
}

# common\script_values\je_values.txt — if/else_if/else + scope chains
russian_aid_income = {
	if = {
		limit = { c:RUS ?= { is_country_alive = yes } }
		if =      { limit = { c:RUS.relations:ROOT >= relations_threshold:friendly } value = 1000 }
		else_if = { limit = { c:RUS.relations:ROOT >= relations_threshold:amicable } value = 700 }
		else =    { value = 200 }
	}
}

# lists inside formulas — je_values.txt
barracks_levels_to_leave_unburned = {
	value = {
		c:MON ?= {
			every_scope_building = {
				limit = { is_building_type = building_barrack }
				add = this.level
			}
		}
		multiply = 0.60
		round = yes
	}
}
```

- **Quoted function-call values** — triggers that take arguments can be read as numbers by quoting:

```
# common\script_values\event_values.txt
dixie_loyalist_fraction   = { value = 0 add = "loyalist_fraction(cu:dixie)" }
japanese_culture_fraction = { value = 0 add = "culture_percent_state(cu:japanese)" }
```

- **Inlining:** formulas can be written inline anywhere a number is accepted (`add_modifier = { ... multiplier = money_amount_multiplier_medium }`, or a full `{ value = ... }` block inline, e.g. the `change_relations` value block in `00_scripted_effects.txt`).
- **Referenced from events/JEs:** by bare name (`days = normal_modifier_time`, `cooldown = { days = normal_modifier_time }`), in JE `current_value`/`goal_add_value` blocks:

```
# common\journal_entries\00_land_reclamation.txt
current_value =  { value = global_var:land_reclamation_global }
goal_add_value = { add = 10 }
progressbar = yes
```

- Chaining: named script values can be read through a scope: `value = mother.example_age` (script_values.md); `value = barracks_levels_to_leave_unburned` inside `save_temporary_scope_value_as` (`00_chris_scripted_effects.txt`).

## 8. Scripted effects and scripted triggers

Definition files: `common\scripted_effects\*.txt`, `common\scripted_triggers\*.txt`. A definition is just a named block of effects (or triggers). Call it like a normal effect/trigger with `= yes`:

```
# common\scripted_effects\00_scripted_effects.txt
resign_and_retire = {
	remove_character_role = politician
	remove_character_role = ruler
	on_remove_ruler_effects = yes     # scripted effects can call other scripted effects
	retire_character = yes
}
# call site:  resign_and_retire = yes
```

### `$PARAMETER$` substitution

Parameters are `$NAME$` placeholders, filled at the call site with `NAME = value`:

```
# definition — common\scripted_triggers\00_ep2_victoria_scripted_triggers.txt
country_has_springtime_revolution = {
	any_civil_war = {
		is_civil_war_type = revolution
		civil_war_progress >= $THRESHOLD$
	}
}
# call — events\peoples_springtime.txt
trigger = {
	country_has_springtime_revolution = { THRESHOLD = 0.25 }
}
```

Parameters can also be whole trigger blocks (`$CRITERIA$` in `save_neighbor_with_state`, `00_scripted_effects.txt`) or scope references (`$TARGET$ = { is_in_power_bloc = yes }`, `00_scripted_triggers.txt`).

### Overriding a single vanilla entry from a mod

The mod uses the `REPLACE:` key prefix to override one scripted trigger without copying the whole vanilla file:

```
# mod common\scripted_triggers\joi_gbr_triggers.txt
REPLACE:country_has_springtime_revolution = {
	any_civil_war = { ... }
}
```

## 9. Scripted lists (`common\scripted_lists\`)

A scripted list derives a new `any_/every_/random_/ordered_` family from a base list plus conditions:

```
# common\scripted_lists\victoria_scripted_lists.txt
princely_state = {
	base = country
	conditions = { is_princely_state = yes }
}
scope_barracks = {
	base = scope_building
	conditions = { is_building_type = building_barrack }
}
```

Usage: `every_princely_state = { change_relations = { country = ROOT value = 30 } }` (`events\east_indies_je_events.txt`). Observed bases: `country`, `interest_group`, `scope_building`, `character_in_void`.

## 10. Scripted modifiers (`common\scripted_modifiers\`)

Named weight-modification blocks for use where score/chance modifiers are accepted. Vanilla ships only the example doc (`scripted_modifiers.md`) — no active `.txt` in that folder:

```
# common\scripted_modifiers\scripted_modifiers.md
is_accepted_culture_and_religion = {
	if = { limit = { is_accepted_culture = no } factor = 0.20 }
	if = { limit = { is_state_religion = no }   factor = 0.20 }
}
```

## 11. Scripted rules (`common\scripted_rules\00_scripted_rules.txt`)

Fixed hook points the game engine consults; each is a named trigger block with an engine-defined root scope (documented in comments). You override them, you cannot invent new ones.

```
# Root = Country
can_form_power_bloc = { country_can_form_power_bloc = yes }
# Root = Country, scope:target_country / scope:region provided by engine
can_start_diplomatic_plays_against = { NOT = { ... } OR = { ... } }
```

## 12. Tooltip control

All three observed forms:

```
# custom_tooltip — effect form: show loc text instead of (or besides) effects
custom_tooltip = PARTIES_EMERGENCE                       # common\scripted_effects\00_scripted_effects.txt
custom_tooltip = { text = form_third_rome_tt }           # mod events\joi_flavor_rus.txt

# custom_tooltip — trigger form: wrap triggers under one loc line
custom_tooltip = {
	text = is_democratic_tt
	OR = { modifier:country_voting_power_base_add > 0 ... }
}                                                        # common\scripted_triggers\00_scripted_triggers.txt

# hidden_effect — executes, never shown in tooltip
hidden_effect = { retire_character = yes }               # events\belle_epoque_events.txt

# show_as_tooltip — shown in tooltip, NOT executed
show_as_tooltip = {
	add_modifier = { name = land_reclamation_complete days = long_modifier_time }
}                                                        # common\journal_entries\00_land_reclamation.txt
```

A plain `tooltip = key` effect key was not observed (unverified — use `custom_tooltip`).

## 13. Common effects (verified in vanilla events/JEs/scripted_effects)

Scope column = scope the effect was observed running in.

| Effect | Scope | Meaning |
|---|---|---|
| `add_modifier = { name = X days/months/years = N }` | country/state/IG/character/building/JE | Add timed modifier; `months = -1` = permanent; extras: `is_decaying = yes`, `multiplier = <script value>` |
| `remove_modifier = X` | same | Remove modifier by name |
| `save_scope_as = name` | any | Save current scope as `scope:name` |
| `set_variable` / `change_variable` / `remove_variable` | any | See section 4 |
| `set_global_variable` / `change_global_variable` / `remove_global_variable` | any | Global variables |
| `trigger_event = { id = ns.1 days = 5 popup = yes }` | country | Fire event (delay/popup optional; `trigger_event = ns.1` short form also seen) |
| `custom_tooltip` / `hidden_effect` / `show_as_tooltip` | any | Section 12 |
| `activate_law = law_type:X` | country | Instantly enact law |
| `change_relations = { country = X value = N }` | country | Change bilateral relations |
| `add_radicals = { value = X }` (+ optional `culture =`, `pop_type =`, `strata =`) | country | Add radicals; `add_radicals_in_state` = state version |
| `add_loyalists` / `add_loyalists_in_state` | country/state | Same for loyalists |
| `add_journal_entry = { type = X }` (+ optional `target =`) | country | Start a journal entry |
| `add_treasury = N` | country | Add/remove money (`journal_entries.md`, test events) |
| `create_character = { ... }` | country | Create character (name/ruler/ig/ideology/traits/template params) |
| `kill_character` / `retire_character` / `transfer_character` | character | Remove / retire / move to another country |
| `set_character_as_ruler = yes` | character | Make ruler |
| `add_trait = X` / `remove_trait = X` | character | Character traits |
| `set_ideology = ideology:X` / `add_ideology` / `remove_ideology` | character/IG | Change ideology |
| `add_ruling_interest_group = yes` / `remove_ruling_interest_group = yes` | IG | Put IG in/out of government |
| `add_claim = s:STATE_X` / `remove_claim` | country | State-region claims |
| `add_homeland = cu:X` / `remove_homeland` | state_region | Culture homelands |
| `add_primary_culture = cu:X` / `remove_primary_culture` | country | Primary cultures |
| `set_state_owner = c:TAG` | state | Transfer state |
| `annex = c:TAG` / `annex_with_incorporation` | country | Annex another country |
| `make_independent = yes` | country | Break subject status |
| `create_country = { tag = X origin = root state = ... }` | any | Spawn a country |
| `play_as = c:TAG` | country | Switch player control |
| `add_technology_researched = X` / `add_technology_progress = { progress = N technology = X }` | country | Tech |
| `add_war_goal = { holder = ... type = ... }` | diplomatic play | War goals |
| `create_diplomatic_pact = { country = X type = Y }` / `remove_diplomatic_pact` | country | Subject/pact creation |
| `create_diplomatic_play = { ... }` / `create_diplomatic_catalyst` | country | Start plays / catalysts |
| `add_liberty_desire = N` | subject country | Liberty desire |
| `change_infamy = N` | country | Infamy |
| `add_devastation = N` | state | Devastation |
| `kill_population_percent_in_state = { percent = 0.05 pop_type = X }` | state | Kill pops |
| `move_pop = X` / `change_poptype = pop_type:X` | pop | Pop manipulation |
| `add_momentum = { party = X value = N }` | country | Election momentum |
| `call_election = { months = 2 }` | country | Force election |
| `add_civil_war_progress` / `add_progress = { name = X value = N }` | country/JE | Progress counters |
| `add_enactment_modifier = { name = X }` | country | Law-enactment checkpoint modifiers |
| `set_strategy = ai_strategy_x` | country | Set AI strategy |
| `post_notification = X` | country | Feed message |
| `set_state_name` / `set_hub_name` / `reset_state_name` | state(_region) | Dynamic renaming |

## 14. Common triggers (verified)

| Trigger | Scope | Meaning |
|---|---|---|
| `exists = scope:x` / `exists = c:RUS` | any | Object exists |
| `always = yes/no` | any | Constant |
| `has_variable` / `has_global_variable` / `has_variable_list` | any | Section 4 |
| `has_modifier = X` | any | Has named modifier |
| `has_law = law_type:X` / `has_law_or_variant` | country | Law checks (variant = column sibling) |
| `is_enacting_law = law_type:X` | country | Currently enacting |
| `has_technology_researched = X` / `can_research` | country | Tech |
| `has_journal_entry = je_x` | country | JE active |
| `country_rank >= rank_value:major_power` | country | Rank compare |
| `is_country_type = recognized/decentralized/unrecognized` | country | Country type |
| `is_country_alive = yes` | country | Alive |
| `is_player = yes` | country | Human-controlled |
| `is_at_war = yes` / `has_war_with = c:X` | country | War status |
| `is_subject = yes` / `is_subject_of = c:X` / `is_subject_type = X` | country | Subject status |
| `is_direct_subject_of` / `is_indirect_subject_of` | country | Subject chains |
| `country_has_primary_culture = cu:X` | country | Primary culture |
| `country_has_state_religion = rel:X` | country | State religion |
| `has_diplomatic_pact = { who = X type = Y }` | country | Pacts |
| `is_in_power_bloc = yes` / `is_power_bloc_leader` | country | Power blocs |
| `has_interest_marker_in_region = region_x` | country | Declared interest |
| `government_legitimacy >= N` | country | Legitimacy |
| `in_election_campaign = yes` | country | Election ongoing |
| `has_party = X` / `is_party_type` / `party_has_members` | country/party | Parties |
| `game_date >= 1863.1.1` / `year >= 1880` | any | Date |
| `has_dlc_feature = X` | any | DLC gate |
| `is_incorporated = yes` | state | Incorporation |
| `is_capital = yes` | state | Capital state |
| `state_region = s:STATE_X` | state | Region identity |
| `is_in_geographic_region = geographic_region_x` | state/country(capital) | Geography |
| `owns_entire_state_region = STATE_X` | country | Full ownership (bare name, no `s:`) |
| `has_state_in_state_region = STATE_X` | country | Partial ownership |
| `is_homeland = cu:X` | state | Homeland |
| `has_building = building_x` | state | Building present |
| `has_state_trait = x` | state | State trait |
| `turmoil >= 0.25` / `devastation > 0` / `average_sol >= 15` | state | State metrics |
| `is_building_type = building_x` | building | Type check |
| `occupancy >= 0.9` / `level >= N` / `weekly_profit` / `cash_reserves_ratio` | building | Building metrics |
| `is_production_method_active = { building_type = X production_method = Y }` | state | PM check (state) |
| `has_active_production_method = pm_x` | building | PM check (building) |
| `is_pop_type = laborers` / `pop_has_primary_culture` / `pop_acceptance < N` / `standard_of_living` / `strata` | pop | Pop checks |
| `pop_employment_building_group = bg_x` | pop | Employment |
| `has_ideology = ideology:X` | character/IG | Ideology |
| `has_trait = x` | character | Trait |
| `has_role_of_type = general/admiral/agitator/politician` | character | Role |
| `is_ruler_of_own_country` / `is_heir_of_own_country` / `is_character_alive` / `age` / `is_female` | character | Character status |
| `is_interest_group_type = ig_x` / `is_in_government` / `is_powerful` / `is_insurrectionary` / `ig_approval` / `ig_clout` | IG | Interest groups |
| `is_political_movement_type = movement_x` / `political_movement_radicalism >= N` | movement | Movements |
| `is_civil_war_type = revolution/secession` / `civil_war_progress >= N` | civil war | Civil wars |
| `is_diplomatic_play_type = X` | play | Plays |
| `has_claim = s:X` / `has_claim_by = c:X` | country/state | Claims |
| `has_decree = decree_x` | state | Decrees |
| `is_revolutionary = yes` / `is_secessionist` | country | Revolt status |
| `literacy_rate < 0.15` / `gdp` / `army_size >= N` / `navy_size` / `tax_level <= low` | country | Country metrics (mod `joi_gov_scripted_effects.txt`; note enum compare `tax_level <= low`) |

## 15. Defines (`common\defines\`)

Plain named-category files of engine tuning constants — not scopes/triggers:

```
# common\defines\00_defines.txt
NGame = {
	START_DATE = "1836.1.1"
	END_DATE = "1936.1.1"
}
NCountry = {
	MOVE_CAPITAL_COOLDOWN_YEARS = 5
	...
}
```

Observed categories: `NGame`, `NJominiMap`, `NCountry`, `NEconomy`, `NPops`, `NDiplomacy`, `NCities`, `NMilitary`, `NCharacters`, plus AI/graphics/interface files and `defines\jomini\` (tooltips, fog of war, rivers). **Mods override single defines** by shipping their own file in `common\defines\` re-declaring only the keys they change — verified in the mod:

```
# mod common\defines\joi_defines.txt — partial category override
NEconomy = {
	BASE_RESOURCE_DISCOVER_CHANCE = 0.015
	MIN_POPS_PER_PROFESSION = 999
}
NCharacters = {
	MIN_POPULARITY = -1000
	MAX_POPULARITY = 1000
}
```

## Common pitfalls

1. **Trigger vs effect context.** `if/else_if/else/while/random/random_list` are *effects*; conditions go inside `limit = { }`. In *trigger* context use `trigger_if/trigger_else_if/trigger_else` (see `country_can_form_power_bloc`). Putting effects inside a `trigger`/`limit` block, or bare triggers inside an option body, breaks the file.
2. **No `FROM`, no `switch`.** Neither exists in Victoria 3 script (verified absent). Pass context with `save_scope_as` + `scope:name`; branch with `if/else_if`.
3. **Use `?=` for anything that can be missing.** `c:CHI = { ... }` on a dead/annexed tag logs errors; vanilla always writes `c:CHI ?= { ... }` or guards with `exists = c:CHI`. Same for saved scopes (`scope:x ?=`), `power_bloc ?=`, `interest_group ?=`.
4. **`scope:` prefix is mandatory for saved scopes.** `save_scope_as = foo` is later read as `scope:foo`, never bare `foo`. Saved scopes from an event's `immediate` last for that event (options + loc); use `save_temporary_scope_as` inside trigger evaluation.
5. **Script value operations run strictly in order.** `min`/`max` are clamps applied at their position, not global bounds (`script_values.md`: a `max = 10` before a final `add = 5` yields 15). Don't divide/modulo by 0 — vanilla guards with `if = { limit = { num_states > 0 } divide = num_states }`.
6. **`limit` filters lists; forgetting it hits everything.** `every_scope_state = { add_modifier = ... }` touches every state. Also remember `every_scope_state` iterates the *current country's* states, `every_state` iterates all states in the world (see `00_victoria_scripted_effects.txt`).
7. **`percent`/`count`/`filter` belong to `any_` triggers only** (`percent > 0.5`, `count >= 2`, `count = all`); they were never observed as parameters of `every_`/`random_` effect iterators. In `ordered_` effects use `order_by`/`position`/`check_range_bounds`.
8. **Weight blocks are not effect blocks.** `ai_chance` and `random_list` weights are adjusted with `modifier = { trigger = { ... } add/factor = N }` (events) or `modifier = { if = { limit ... add ... } }` (`prostitution_events.txt`) — you cannot put effects there.
9. **Variables vs saved scopes.** `scope:x` dies with the event chain; variables persist (and can store scopes: `set_variable = { name = x value = prev }`, read back via `var:x ?= this`). Timed variables (`days =`/`years =`) silently disappear — that is the standard cooldown idiom (`set_variable = { name = cd years = 5 }` + `NOT = { has_variable = cd }`).
10. **Tooltip traps.** Effects inside `hidden_effect` run but don't show; `show_as_tooltip` shows but doesn't run — vanilla pairs them to restructure what the player sees (`peoples_springtime.txt`). Forgetting the pairing causes "phantom" or silently-missing effects.
11. **Two different `custom_tooltip` shapes.** Effect form: `custom_tooltip = loc_key` or `{ text = loc_key }`. Trigger form: `{ text = loc_key <triggers> }` — the triggers still evaluate.
12. **File encoding.** Save as UTF-8 with BOM like every vanilla/mod file; other encodings can break parsing of non-ASCII text.
13. **Overriding vanilla script.** Same-named database entries from mods override vanilla wholesale; for a single entry inside a big vanilla file prefer a mod file with just that entry, or the `REPLACE:name` prefix as used in this mod's `joi_gbr_triggers.txt`.
