# Victoria 3 Events: Files, Anatomy, Options

**Read this file when:** creating or editing any event (`events/*.txt`) — you need the exact structure of a `country_event`/`state_event`, option blocks, dynamic titles/descs, hidden events, or loc-key conventions. For *how events get fired* (on_actions, pulses, chains, pacing) read `04-event-chains-and-triggering.md`. For scopes/effects/triggers syntax see `02-script-language.md`; for loc file format see `08-localization.md`.

All syntax below is taken verbatim from vanilla Victoria 3 (`game/events`, `game/common`) or the Victorian Century mod (`mod/3219394272`). Vic3 event syntax differs from CK3/EU4/HOI4 — do not import keywords from those games.

## 1. File and namespace conventions

- Event files live in `events/` (subfolders allowed and common: `game/events/agitators_events/`, `game/events/law_events/`, ...). Any `.txt` file under `events/` is loaded; filenames are free-form.
- Every file starts with one or more `namespace = <name>` declarations. Event IDs are `<namespace>.<number>`:

```
# from game/events/gold_rush.txt
namespace = goldrush

goldrush.1 = { ... }
goldrush.2 = { ... }
```

- One file may declare **multiple namespaces**; each applies to the events following it:

```
# from mod/3219394272/events/victoria_events.txt
namespace = victoria
victoria.1 = { ... }
victoria.2 = { ... }

namespace = britain_monarchy
britain_monarchy.1 = { ... }
```

- Numbers need not be consecutive (vanilla has `expedition_events.560`, `expedition_events.695`, `decree_events.100`–`109`). Vanilla groups related events by number ranges within a namespace.
- Mod event files simply add new namespaces; there is no merge issue as long as your namespace is unique. Prefix your namespace (Victorian Century uses `joi_` for most of its namespaces: `joi_great_man`, `joi_flavor_gbr`, ...).

## 2. Event types

Counted across all of `game/events`:

| type | count | root scope |
|---|---|---|
| `type = country_event` | 2346 | country |
| `type = state_event` | 14 | state |

**There is no `character_event` type in Victoria 3.** Vanilla's `character_events.txt` uses `type = country_event` and displays characters via `gui_window`/`left_icon` (see §5). Events about characters run in country scope and reach characters via saved scopes.

`state_event` examples: `goldrush.1/.2/.5/.6/.7` (game/events/gold_rush.txt), oil rush, rubber events, spanish flu. In a `state_event`, root is the state; `owner` reaches the country (`owner = { NOT = { has_variable = goldrush_active } }`).

## 3. Full anatomy (annotated)

```
# from game/events/gold_rush.txt (trimmed)
goldrush.1 = {                       # id = namespace.number
	type = state_event
	placement = ROOT                 # where the map camera/banner points (a state or country scope)
	title = goldrush.1.t             # loc key (see §4)
	desc = goldrush.1.d
	flavor = goldrush.1.f            # third text block (quote/flavor text)

	duration = 3                     # almost always 3 (2198 of 2303 uses); how long the event stays available, in months (unverified unit)

	cooldown = { days = stupidly_long_modifier_time }   # min time before THIS event can fire again for this root

	event_image = {
		video = "europenorthamerica_gold_prospectors"   # all 2027 vanilla event_images use video = "..."
	}

	on_created_soundeffect = "event:/SFX/UI/Alerts/event_appear"

	icon = "gfx/interface/icons/event_icons/event_trade.dds"

	trigger = {                      # checked when an on_action / pulse tries to fire it
		has_building = building_gold_field
		owner = { NOT = { has_variable = goldrush_active } }
	}

	immediate = {                    # runs when the event is created, BEFORE the player sees it.
		set_variable = gold_rush_state          # set up scopes & bookkeeping here
		save_scope_as = goldrush_state
		owner = {
			save_scope_as = goldrush_country
			set_variable = { name = goldrush_active days = very_long_modifier_time }
		}
	}

	option = {                       # 1..n option blocks (see §6)
		name = goldrush.1.a
		default_option = yes
		add_modifier = { name = state_gold_rush days = normal_modifier_time }
	}
	option = {
		name = goldrush.1.b
		...
	}
}
```

Top-level keys and vanilla usage counts (from `grep` over `game/events`): `option` 4761, `type` 2203, `icon` 2170, `on_created_soundeffect` 2157, `immediate` 2131, `desc` 2073, `flavor` 2072, `title` 2071, `duration` 2064, `trigger` 2013, `placement` 1905, `event_image` 1894, `cooldown` 1395, `cancellation_trigger` 1074, `dlc` 763, `category` 352, `left_icon` 170, `gui_window` 154, `on_opened_soundeffect` 151, `after` 62, `hidden` 49, `orphan` 28, `right_icon` 9, `minor_left_icon` 5, `is_popup` 3, `minor_right_icon` 2.

Key details:

- **`placement`** — `root`/`ROOT` (both used, 874+630 times) or a saved scope: `placement = scope:university_state` (game/events/character_events.txt), `placement = scope:current_expedition_location` (expedition events). For a country_event you can place on a state scope to point the event at a location.
- **`duration`** — nearly always `3`. Other observed values: 1, 2, 4, 5, 6, 9, 10, 30.
- **`cooldown`** — `cooldown = { days = <script value> }`. Vanilla uses named script values from `game/common/script_values/event_values.txt`:

```
# from game/common/script_values/event_values.txt
very_short_modifier_time = 365        # 1 year
short_modifier_time = 913             # 2.5 years
normal_modifier_time = 1825           # 5 years
long_modifier_time = 3650             # 10 years
moderately_long_modifier_time = 5475  # 15 years
very_long_modifier_time = 7300        # 20 years
even_longer_modifier_time = 10950     # 30 years
stupidly_long_modifier_time = 18250   # 50 years
never_fire_again_modifier_time = 73000 # "Nevermore" — de-facto fire_only_once
```
  The cooldown applies per root object (state cooldown for state_events — vanilla comments say e.g. `cooldown = { days = very_long_modifier_time } #state cooldown`). **There is no `fire_only_once` key in Vic3** — use `never_fire_again_modifier_time` or a variable guard (§7 of 04-event-chains-and-triggering.md).
- **`dlc = dlc004`** — hard-gates the event on a DLC (values seen: `dlc004`...`dlc018`, matching folders in `game/dlc/`). Vanilla also gates via trigger: `has_dlc_feature = voice_of_the_people_content` (also: `lobbies`, `ep2_content`, `ip2_content`, `ip3_content`, `ip4_content`, `ep1_content`, `rp1_content`, `power_bloc_features`). The Victorian Century mod declares itself as a DLC (`mod/3219394272/dlc/dlc_vc/dlc_vc.dlc`) and gates its own events with `dlc = dlc_vc`.
- **`category`** — only two values in vanilla: `category = enactment` (278, law-enactment events) and `category = revolution` (75). Omit unless writing those systems.
- **`cancellation_trigger`** — a trigger that, when true, cancels the pending event (heavily used in election/enactment events, 1074 uses). Example use case: event becomes invalid before the player answers.
- **`after = { ... }`** — effect block that runs after an option is taken, shared by all options:

```
# from game/events/crime_events.txt (crime_events.1)
after = {
	clear_generated_names = yes
}
```
- **`orphan = yes`** — only in `game/events/debug_events.txt`, together with `hidden = yes` (suppresses "who owns this event" checks; debug use only, unverified semantics).

## 4. Localization mapping

`title`, `desc`, `flavor`, and option `name` are **loc keys**, freely chosen. Vanilla convention: `<eventid>.t`, `.d`, `.f`, options `.a`, `.b`, `.c`, `.e`..., custom tooltips `.tt`, `.tt_1`....

```
# from game/localization/english/events_l_english.yml
 goldrush.1.t:0 "Gold Rush!"
 goldrush.1.d:1 "Gold has been discovered in [SCOPE.sState('goldrush_state').GetName]. ..."
 goldrush.1.a:1 "Spread the word!"
```

Note `[SCOPE.sState('goldrush_state').GetName]` — loc text reads **saved scopes** created in `immediate`. This is why nearly every event saves scopes in `immediate` even when effects don't need them: the text does. Missing loc keys show as raw key names in game. Mod example: `mod/3219394272/localization/english/greatman/greatman_events_l_english.yml` (`joi_great_man.1.t: "Lord Kelvin"`). See `08-localization.md`.

### Dynamic text: first_valid / random_valid / triggered_desc

`title`, `desc`, and `flavor` each accept a block instead of a bare key:

```
# from game/events/belle_epoque_events.txt (belle_epoque_events.4)
title = {
	first_valid = {                      # picks the FIRST triggered_desc whose trigger passes
		triggered_desc = {
			desc = belle_epoque_events.4.t
			trigger = { country_has_primary_culture = cu:french }
		}
		triggered_desc = {
			desc = belle_epoque_events.4.t2
			trigger = { NOT = { country_has_primary_culture = cu:french } }
		}
	}
}
desc = belle_epoque_events.4.d          # blocks and bare keys can be mixed per-field
```

`random_valid` picks randomly among valid entries — vanilla uses it to assemble a random poem in `game/events/fascism_events.txt` ("Rise of Radicalism"), with several `random_valid` blocks inside one `flavor`:

```
# from game/events/fascism_events.txt
flavor = {
	random_valid = {
		triggered_desc = { trigger = { var:first_and_second_lines = 1 } desc = first_line_rhyme_a_1 }
		triggered_desc = { trigger = { var:first_and_second_lines = 1 } desc = first_line_rhyme_a_2 }
	}
	random_valid = { ... }               # second line of the poem
}
```

The same `first_valid`/`triggered_desc` structure is used in journal entries (`status_desc` in `game/common/journal_entries/00_niger_river.txt`) — see `05-journal-entries-and-decisions.md`.

## 5. Character-style presentation (gui_window, portraits)

"Character events" are country_events with a character window:

```
# from game/events/character_events.txt (character_events.2)
type = country_event
placement = scope:university_state
gui_window = event_window_1char_tabloid
left_icon = scope:university_benefactor          # a saved CHARACTER scope -> portrait
on_opened_soundeffect = "event:/SFX/Events/misc/1Character_Banner"
```

```
# from game/events/character_events.txt (character_events.3 "The duel")
gui_window = event_window_2char
left_icon = scope:duel_participant_1
right_icon = scope:duel_participant_2
```

`gui_window` values in vanilla: `event_window_1char_tabloid` (150), `event_window_2char` (8), `event_window_1char_propaganda` (5), `event_window_1char_tabloid_halloween` (4), `event_window_1char_lord_kitchener` (2), `event_window_big_icon_center` (1), `event_window_2char_halloween` (1). `left_icon` can also be a direct link: `left_icon = ruler` (mod/3219394272/events/victoria_events.txt). The scopes referenced must be saved in `immediate` before the window renders.

## 6. The option block

```
# from game/events/agitators_events/dreyfus_events.txt (dreyfus.1, trimmed)
option = {
	name = dreyfus.1.a                   # loc key (required)
	highlighted_option = yes             # gold highlight; used for "special/conditional" options
	trigger = {                          # option only appears if true
		any_scope_state = { state_region = s:STATE_GUAYANA }
	}
	custom_tooltip = {                   # show text INSTEAD of auto-generated effect tooltip;
		text = dreyfus.1.tt_1            # effects inside still execute but are hidden
	}
	ig:ig_armed_forces ?= {              # effects, in event root scope
		add_modifier = { name = army_honor_defended days = normal_modifier_time multiplier = 2 }
	}
	hidden_effect = {                    # executes, never shown in tooltip
		trigger_event = { id = dreyfus.2 years = 2 popup = yes }
	}
	random_list = {                      # weighted random outcome inside an option
		50 = { scope:alfred_dreyfus_scope = { add_trait = psychological_affliction } }
		50 = { }
	}
}
option = {
	name = dreyfus.1.b
	default_option = yes                 # the pre-selected / AI-fallback option; one per event
	...
}
```

- **`default_option = yes`** — exactly one option usually has it; it is what auto-resolve picks.
- **`highlighted_option = yes`** — visual emphasis; in vanilla, almost always on options that also have a `trigger` (conditional bonus choices).
- **`trigger`** inside an option hides it when false (e.g. `joi_great_man.1.b` only shows if `NOT = { has_technology_researched = electrical_generation }` — mod/3219394272/events/joi_great_man.txt).
- **`custom_tooltip`** — two forms, both in vanilla and mod: `custom_tooltip = victoria.1.tt` (bare key, mod/3219394272/events/victoria_events.txt) and `custom_tooltip = { text = <key> <effects...> }` where the wrapped effects run but display only the text.
- **`show_as_tooltip`** — the inverse: display effects in the tooltip **without executing them** (used when the real effect happened in `immediate` or elsewhere):

```
# from mod/3219394272/events/victoria_events.txt (victoria.1.a)
show_as_tooltip = {
	c:HAN ?= {
		remove_diplomatic_pact = { country = c:GBR type = personal_union }   # already done in immediate
	}
}
```
- **`hidden_effect`** — run silently; vanilla wraps `trigger_event` follow-ups in it so the chain isn't spoiled in the tooltip.

### ai_chance

```
# from game/events/1848.txt (1848.1)
option = {
	name = 1848.1.a
	ai_chance = {
		base = 25
		modifier = {
			trigger = {
				is_enacting_law = law_type:law_presidential_republic
				any_interest_group = {
					law_stance = { law = law_type:law_presidential_republic value < neutral }
					is_powerful = yes
				}
			}
			add = -15
		}
	}
	...
}
option = {
	name = 1848.1.b
	ai_chance = { base = 75 }
}
```

`ai_chance = { base = N modifier = { trigger = {...} add = ±N } ... }`. Weights are relative among the event's valid options. Only ~115 vanilla event files use `ai_chance` at all — when omitted, options are (observed) equally weighted with `default_option` as the fallback (exact default behavior unverified). Give AI-relevant events explicit `ai_chance` when one option is clearly "correct".

## 7. Hidden events and effect-only events

`hidden = yes` events have no window, no title/desc/options — only `trigger` + `immediate` (and optionally `cooldown`). Vanilla uses them as "the same event, but the player already automated the choice":

```
# from game/events/gold_rush.txt
goldrush.6 = { # hidden event that does the effects if the player chose "always exploit/attract"
	type = state_event
	hidden = yes
	cooldown = { days = stupidly_long_modifier_time }
	trigger = {
		has_building = building_gold_field
		owner = {
			OR = { has_variable = gold_always_exploit has_variable = gold_always_attract }
			NOT = { has_variable = goldrush_active }
		}
	}
	immediate = {
		set_variable = gold_rush_state
		save_scope_as = goldrush_state
		# Notification is done directly in on-action
		owner = { set_variable = { name = goldrush_active days = very_long_modifier_time } }
		if = { limit = { owner = { has_variable = gold_always_exploit } }
			add_modifier = { name = state_gold_rush_less_migration days = normal_modifier_time }
		}
		else = { add_modifier = { name = state_gold_rush days = normal_modifier_time } }
	}
}
```

Both `goldrush.1` (visible) and `goldrush.6` (hidden) are listed on the same on_action (`on_resource_discovered` in `game/common/on_actions/00_code_on_actions.txt`); their mutually exclusive triggers decide which fires. For player feedback without a window, hidden events / on_actions use `post_notification = <notification_type>` (see the mod's `headlines_on_actions.txt` which is built entirely on this).

## 8. Typical trigger gating (vanilla patterns)

Real gates seen in `trigger` blocks:

```
# technology + date + once-only variable + territory  (mod/3219394272/events/joi_great_man.txt)
trigger = {
	has_technology_researched = rotary_valve_engine
	game_date >= 1850.1.1
	NOT = { has_variable = great_man_1_var }
	owns_entire_state_region = STATE_LOWLANDS
}
```

```
# country identity, tech, war-history variables, IG power, law  (game/events/agitators_events/dreyfus_events.txt)
trigger = {
	has_dlc_feature = voice_of_the_people_content
	c:FRA ?= ROOT
	has_technology_researched = political_agitation
	OR = { has_variable = recently_lost_war ... }
	ig:ig_armed_forces ?= { ig_counts_as_marginal = no }
	NOT = { has_law_or_variant = law_type:law_multicultural }
	NOT = { has_variable = dreyfus_convicted }        # once-only guard
	any_country = { has_diplomatic_pact = { who = root type = rivalry } }
}
```

Other recurring gates: `year >= 1850` / `year <= 1855` (kamehameha_coin_toss, 00_on_actions_yearly.txt), `game_date < 1895.12.31` (belle_epoque_events.5), `country_rank > rank_value:minor_power`, `is_at_war = no` (36 uses in events), `is_player = yes`, `has_journal_entry = je_x`, `has_law = law_type:law_monarchy`, `has_modifier`, `has_global_variable`, scripted triggers like `character_is_valid_for_events` (defined in `game/common/scripted_triggers/00_ep2_victoria_scripted_triggers.txt`: not emperor of Japan, not golpista, `is_adult = yes`).

An empty trigger with a comment marks directly-fired chain events:

```
# from game/events/agitators_events/dreyfus_events.txt (dreyfus.2)
trigger = {
	# Triggered by dreyfus.1
}
```

For pulse-fired events the `trigger` is the ONLY gate — write it as if the event could fire for any country at any time.

## Common pitfalls

- **Missing `namespace` declaration** — events with IDs like `mymod.1` require `namespace = mymod` earlier in the same file. Vanilla declares it in every file even when the namespace already exists elsewhere.
- **Using `character_event`** — does not exist in Vic3 (0 hits in all of `game/`). Use `type = country_event` + `gui_window = event_window_1char_tabloid` + `left_icon = scope:<character>`.
- **Using `fire_only_once`** — does not exist (0 hits). Use `NOT = { has_variable = my_var }` in trigger + `set_variable = my_var` in immediate (the `joi_great_man` pattern), or `cooldown = { days = never_fire_again_modifier_time }`.
- **Referencing a scope in `title`/`desc` loc, `placement`, or `left_icon` that `immediate` didn't save** — text renders broken and portraits are empty. Save every scope the loc/text/window needs in `immediate`.
- **Missing loc keys** — every `title`/`desc`/`flavor`/option `name`/`custom_tooltip` text key needs a matching entry in `localization/<lang>/*_l_<lang>.yml`; otherwise the raw key displays. Mods must at minimum ship `english` (Victorian Century ships `english` + `simp_chinese`).
- **Visible event without options** — every non-hidden vanilla event has at least one `option` with a `name`. Only `hidden = yes` events omit options.
- **Putting choice-independent setup in options instead of `immediate`** — anything the text/tooltip needs (scopes, created characters) must be in `immediate`; option effects run only after the player clicks.
- **Forgetting `?=`** — vanilla consistently uses `ig:ig_landowners ?= { ... }`, `c:HAN ?= { ... }` (only execute if scope exists). A plain `=` on a possibly-dead country/IG can log errors or fail; see `02-script-language.md`.
- **All options gated by triggers** — if every option can be hidden, ensure at least one option (usually the `default_option`) has no trigger, or the event can present nothing selectable (vanilla always keeps an unconditional option).
- **Wrong root type for effects** — a `state_event` runs in state scope: use `owner = { ... }` for country effects (gold_rush.txt does exactly this). A country_event needs `random_scope_state`/saved scopes to touch states.
