# Victoria 3 Event Triggering, on_actions, Chains & Pacing

**Read this file when:** deciding *how and when* an event fires — hooking events to pulses/on_actions, choosing weights and cooldowns, building multi-event chains, or adding on_action entries from a mod without clobbering vanilla. For the inside of an event (options, text, anatomy) read `03-events.md`. Journal entries and decisions in depth: `05-journal-entries-and-decisions.md`. Timed modifiers: `06-modifiers.md`.

Primary sources: `game/common/on_actions/_on_actions.md` (Paradox's own in-repo documentation — authoritative), `game/common/on_actions/00_code_on_actions.txt` (7928 lines: every code-fired on_action), the pulse list files, and the Victorian Century mod (`mod/3219394272/common/on_actions/`).

## 1. All the ways an event can fire

1. **on_actions** — hooks called from game code (pulses, or reactions like `on_battle_won`). The main delivery system for "flavor at the right time". §2–4.
2. **`trigger_event`** from any effect block — event options, `immediate`, on_action `effect`, journal entries, decisions, scripted effects. §5.
3. **Journal entries** — JEs have their own `on_weekly_pulse` / `on_monthly_pulse` / `on_yearly_pulse` blocks with `events`/`random_events` lists, plus `immediate`/`on_complete`/`on_fail` effect blocks that call `trigger_event`. §6.
4. **Decisions** — `when_taken = { ... trigger_event = { id = cold.101 popup = yes } }` (game/common/decisions/antarctica_expedition_decision.txt). Decision anatomy is documented in `game/common/decisions/000_decisions_help.txt`; see `05-journal-entries-and-decisions.md`.
5. **Console** (debug): not covered here.

An event fires only if its own `trigger` passes at fire time — every mechanism above respects it.

## 2. The pulse on_actions (what exists, what scope)

From `game/common/on_actions/_on_actions.md` and `00_code_on_actions.txt`:

| Pulse | Root |
|---|---|
| `on_monthly_pulse`, `on_yearly_pulse` | none (global; use `every_country` etc.) |
| `on_monthly_pulse_country`, `on_half_yearly_pulse_country`, `on_yearly_pulse_country`, `on_five_year_pulse_country`, `on_decade_pulse_country` | country |
| `on_monthly_pulse_country_elections` (+ half_yearly/yearly/five_year/decade variants) | country — "Only fires for countries with Elections enabled" (comment in 00_code_on_actions.txt) |
| `on_monthly_pulse_character`, `on_half_yearly_pulse_character`, `on_yearly_pulse_character`, `on_five_year_pulse_character`, `on_decade_pulse_character` | character |
| `on_monthly_pulse_state`, `on_half_yearly_pulse_state`, `on_yearly_pulse_state`, `on_five_year_pulse_state`, `on_decade_pulse_state` | state |

Also `on_game_started` (bookmark init, players unknown, no root) and `on_game_started_after_lobby` (players known, no root) — both used for setup effects, not events, in vanilla and in the mod (`mod/3219394272/common/on_actions/joi_code_on_actions.txt` does its world-state setup in `on_game_started`).

Besides pulses, ~200 code-fired reaction on_actions exist (full list: top-level keys of `00_code_on_actions.txt`). Frequently useful, with root scopes from vanilla's own comments:

- `on_acquired_technology` — "Root = The applicable country, scope:technology = the technology type" ; vanilla hangs `historical_events.1`, `marx_events.1` on it.
- `on_battle_won` / `on_battle_lost` — root = attacker/defender country; `scope:enemy_country`, `scope:battle`, `scope:attacker`, `scope:defender` (commanders), `scope:state` (comments in `ip4_on_actions.txt`).
- `on_building_built` — Root = Building.
- `on_resource_discovered` / `on_resource_depleted` — Root = State (fires `goldrush.1/.6` and `goldrush.2/.7`).
- `on_war_end` — Root = Diplomatic Play; `scope:actor`, `scope:target`. `on_capitulation` — Root = Country.
- `on_law_activated`, `on_law_enactment_pass`/`_fail`, `on_law_checkpoint_success` — law lifecycle (mod hooks `joi_flavor_guide.1` on `on_law_enactment_pass`).
- `on_new_ruler`, `on_heir_born`, `on_character_death` — Root = Character.
- `on_rank_changed`, `on_country_formed`, `on_revolution_start` (`scope:target` = uprising country), `on_state_incorporation`, `on_state_owner_change`, `on_diplomatic_play_started` (root = the play; `scope:initiator`, `scope:target`), `on_journal_entry_activated`/`_completed`/`_failed` (Root = journal entry).

## 3. on_action structure (weights, delays, sub-on_actions)

Full grammar from `game/common/on_actions/_on_actions.md` (vanilla's own doc), all features confirmed in live files:

```
# structure per game/common/on_actions/_on_actions.md
my_on_action = {
	trigger = { ... }                # if false when fired, nothing happens

	weight_multiplier = {            # scales this on_action's weight inside a random_on_actions list
		base = 1
		modifier = { add = 1 <trigger_conditions> }
	}

	events = {                       # ALL of these fire (each still checks its own trigger)
		event_id.1
		delay = { days = 365 }       # delay applies to all entries AFTER it; overrides previous delay
		event_id.2
		delay = { months = { 6 12 } }# random range supported
		event_id.3
	}

	random_events = {                # ONE event is picked from the list
		chance_to_happen = 25        # % chance the list is evaluated at all
		chance_of_no_event = { value = 0 if = { limit = {...} add = 10 } }  # script value form
		100 = event_id.1             # number = weight; factored by the event's weight_multiplier (default 1)
		200 = event_id.2
		100 = 0                      # weight for "no event" even when others are valid
	}

	first_valid = { event_id.1 event_id.2 fallback_event_without_trigger }

	on_actions = { on_action_1 delay = { days = 7 } on_action_2 }   # fire other on_actions (delays work here too)
	random_on_actions = { 100 = on_action_1 200 = on_action_2 100 = 0 }
	first_valid_on_action = { on_action_1 on_action_2 }

	effect = { ... }                 # runs concurrently with fired events, NOT before them;
	                                 # scopes/variables set here do NOT carry into events fired by the same on_action
	fallback = another_on_action     # called if nothing fired; avoid infinite fallback loops
}
```

**Weight semantics** (from the doc + observed lists): within `random_events`, an entry's chance = its weight / sum of weights of *valid* entries (invalid events drop out). `N = 0` entries reserve probability mass for "nothing happens" so rare events don't fire merely because everything else was invalid. IMPORTANT: for performance, a delayed event must be valid **both** when the on_action executes **and** when the delay completes.

**Events can carry `weight_multiplier`** to scale their weight in every `random_events` list they appear in — vanilla has it only commented out (`game/events/suffragist_events.txt`), so treat as documented-but-unused.

## 4. How vanilla wires pulses, and how a mod adds entries safely

### 4.1 Vanilla layering

`00_code_on_actions.txt` defines the pulse and hangs *named sub-on_actions* on it, with delays to spread events out over the year:

```
# from game/common/on_actions/00_code_on_actions.txt
on_yearly_pulse_country = {
	events = { utopian.2 austria_events.40 ... }     # always-fire (trigger-gated) story events
	effect = { ... }                                  # bookkeeping (variables, coin tosses)
	on_actions = { # delay ensures events won't fire simultaneously
		on_yearly_events
		delay = { days = 1 }
		russian_monarchy_yearly_events
		...
		delay = { days = 90 }
		japan_yearly_events
	}
}
```

The sub-on_actions live in sibling files (`00_on_actions_yearly.txt`, `00_on_actions_monthly.txt`, `00_on_actions_half_yearly.txt`, `00_on_actions_election.txt`) and hold the `random_events` weight lists:

```
# from game/common/on_actions/00_on_actions_yearly.txt
on_yearly_events = {
	random_events = {
		chance_to_happen = 65
		20 = government_conflicts.1
		...
		1 = vampire_panic.1
		100 = prostitution.2
	}
}
```

### 4.2 Merging rules — adding your own entries WITHOUT overwriting vanilla

From `_on_actions.md` (MODDING INFO section), verified by the live files:

- Data for one named on_action **can be declared in multiple files** — the `events` / `random_events` / `on_actions` lists merge additively. Proof: `on_monthly_pulse_country` is extended by vanilla `00_code_on_actions.txt`, and independently by BOTH mod files `headlines_on_actions.txt` and `joi_code_on_actions.txt` in `mod/3219394272/common/on_actions/`, none of which copy vanilla's contents.
- You **cannot** have multiple `trigger` or `effect` blocks for one named on_action — that is a conflict. The sanctioned pattern to append effects:

```
# from game/common/on_actions/_on_actions.md (MODDING INFO)
some_vanilla_on_action = {
	on_actions = { some_modded_on_action }
}
some_modded_on_action = {
	effect = { some_fun_modding_effect = yes }
}
```

This is exactly what the mod does:

```
# from mod/3219394272/common/on_actions/headlines_on_actions.txt
on_monthly_pulse_country = {
	on_actions = { headlines_action }
}
headlines_action = {
	effect = { ... post_notification = headlines_paris_commune_news ... }
}
```

and what vanilla itself does across files (`ip4_on_actions.txt` defines `ip4_lands_of_anarchy_remove_on_state_lost`; `00_code_on_actions.txt` hooks it via `on_state_owner_change = { on_actions = { ip4_lands_of_anarchy_remove_on_state_lost } }`).

A mod can also add a `random_events` list directly to a vanilla pulse **if vanilla's own block of that pulse doesn't already have one** (vanilla's `on_monthly_pulse_country` has only `events`/`effect`/`on_actions`, so this merges cleanly):

```
# from mod/3219394272/common/on_actions/joi_code_on_actions.txt
on_monthly_pulse_country = {
	random_events = {
		25 = 0                 # "nothing" weight keeps the pool rare
		2 = joi_great_man.1
		1 = joi_great_man.2
		...
	}
	on_actions = { joi_gbr_monarchy_action joi_pru_monarchy_action joi_add_law_a_action }
}
```

Caution: `joi_code_on_actions.txt` also declares `on_game_started = { effect = { ... } }` while vanilla's `on_game_started` has `effect = {}` — per `_on_actions.md` two effect blocks are a conflict (here harmless only because vanilla's is empty). Prefer the wrapper pattern for effects, always.

**Never copy a whole vanilla on_actions file into your mod to add one line** — your copy would freeze vanilla's list at that patch and drop future additions. Create a NEW file in `<mod>/common/on_actions/` that re-opens the on_action name and adds only your entries.

## 5. trigger_event (script-fired events and chains)

Forms observed in vanilla and mod:

```
trigger_event = ottoman_monarchs.1                              # bare id, immediate  (00_code_on_actions.txt)
trigger_event = { id = government_petition_events.1 }           # block, immediate
trigger_event = { id = dreyfus.3 days = 7 popup = yes }         # delayed follow-up   (dreyfus_events.txt)
trigger_event = { id = dreyfus.2 years = 2 popup = yes }        # long-delay follow-up
trigger_event = { id = ryukyu_rivalry.6 days = 1 popup = yes }  # from an on_action effect, to another country:
                                                                #   c:JAP ?= { trigger_event = { ... } }
trigger_event = { id = caucasus_expulsions.2 days = 3 popup = yes }  # from JE immediate (mod 03_russia.txt)
trigger_event = { on_action = on_action_name days = X }         # can fire an ON_ACTION too (per _on_actions.md;
                                                                #   days/months/years optional)
```

- The event fires **for the country/state in whose scope `trigger_event` runs** — scope into the target first (`c:HAN ?= { trigger_event = { id = victoria.2 } }`, mod victoria_events.txt).
- `popup = yes` is set on story-critical fired events throughout vanilla (forces full popup presentation; exact UI semantics unverified).
- Vanilla wraps chain-continuation `trigger_event` in `hidden_effect = { ... }` inside options so tooltips don't spoil the next event.
- The delayed event's trigger is (re)checked on delivery — a delayed follow-up silently vanishes if it became invalid (see §3 note on double validation for on_action delays).

## 6. Journal entries and decisions as event drivers

JEs embed the same pulse machinery, scoped to the JE's owner and lifetime (see `05-journal-entries-and-decisions.md` for JE anatomy):

```
# from game/common/journal_entries/00_niger_river.txt (je_niger_river_expedition)
on_weekly_pulse = {
	effect = { niger_river_expedition_location = yes }   # scripted effect re-saves scope:current_expedition_location
}
on_monthly_pulse = {
	random_events = {
		70 = 0                        # ~41% "nothing" per month
		30 = expedition_events.20
		20 = expedition_events.30     # local guides
		10 = expedition_events.41     # malaria
		2  = expedition_events.110    # rare: new leader
		...
	}
}
on_complete = {
	trigger_event = { id = expedition_events.11 }
	remove_variable = on_expedition
	...
}
```

JE pulse usage across vanilla journal_entries: `on_monthly_pulse` 167, `on_weekly_pulse` 66, `on_yearly_pulse` 33. This is the right tool for a dense event chain with a clear start/end: the events only ever fire while the JE is active, so no extra gating needed. The mod does the same (`mod/3219394272/common/journal_entries/03_russia.txt`: weekly `events` list for end-conditions, yearly `random_events = { 90 = 0 10 = caucasuswar.1 ... }` for flavor). Note the mod's `REPLACE_OR_CREATE:je_circassian_expulsions = { ... }` key prefix for overriding-or-adding a JE.

Decisions: `when_taken` effect fires the kickoff event (`trigger_event = { id = cold.101 popup = yes }` + `set_variable = on_expedition`, antarctica_expedition_decision.txt) — the standard "player opts into a chain" entry point.

## 7. Chain construction: flags, scopes, once-only guards

### 7.1 What persists: variables on objects (NOT saved scopes)

`save_scope_as` lasts only for the current event/effect chain. **Across a delayed `trigger_event`, saved scopes are gone.** Vanilla's pattern (Dreyfus chain): tag the object with a variable, then RE-find and RE-save it in the next event's `immediate`:

```
# from game/events/agitators_events/dreyfus_events.txt
# dreyfus.1 immediate:
create_character = {
	template = canonic_dreyfus_character_template
	save_scope_as = alfred_dreyfus_scope
	on_created = {
		place_character_in_void = 10000
		set_variable = alfred_dreyfus_var        # durable tag
	}
}
random_country = {
	limit = { has_diplomatic_pact = { who = root type = rivalry } }
	save_scope_as = dreyfus_rival_country_scope
	set_variable = dreyfus_rival_country_var     # durable tag
}
set_variable = dreyfus_convicted                 # once-only guard for dreyfus.1 itself

# dreyfus.2 (fired 2 years later) immediate — re-establish everything:
random_character_in_void = { limit = { has_variable = alfred_dreyfus_var } save_scope_as = alfred_dreyfus_scope }
random_country =           { limit = { has_variable = dreyfus_rival_country_var } save_scope_as = dreyfus_rival_country_scope }
```

Vanilla's variable toolkit for chains (all heavily used in events/on_actions):
- `set_variable = name` / `set_variable = { name = X value = Y }` / `set_variable = { name = X days/months/years = N }` (**timed variable — auto-expires; the workhorse cooldown**), `has_variable`, `remove_variable`, `change_variable = { name = X add = 1 }`, `var:X` reads (`var:rennes_retrial_var >= 35`).
- Global (world-visible) versions for cross-country chains: `set_global_variable` (plain, `{ name value }`, and timed `{ name = ryukyu_rivalry_training_incident years = 5 }`), `has_global_variable`, `remove_global_variable`, `change_global_variable`, `global_var:X`, plus list forms `add_to_global_variable_list` / `clear_global_variable_list` / `any_in_global_list` (00_code_on_actions.txt).
- Storing a scope in a variable: `set_variable = { name = expedition_leader_storage_var value = prev }` (00_expedition_effects.txt) — later testable with `exists = var:...`.

### 7.2 Once-only and family-cooldown guards

```
# once-only: trigger NOT has_variable + immediate set_variable  (mod joi_great_man.txt, vanilla everywhere)
trigger  = { NOT = { has_variable = great_man_1_var } }
immediate = { set_variable = great_man_1_var }

# shared cooldown for a whole event family (game/events/government_conflicts_events.txt):
trigger = { NOR = { ... has_variable = ongoing_government_conflicts } }
immediate = { set_variable = { name = ongoing_government_conflicts months = 3 } }

# once-globally, with variable + cooldown combo (game/common/on_actions/00_code_on_actions.txt, gov petition):
set_variable = { name = gov_petition_cooldown years = 10 }
set_variable = { name = gov_petition_fired months = 3 }
trigger_event = { id = government_petition_events.1 }
```

Plus per-event `cooldown = { days = ... }` (see `03-events.md` §3) — vanilla combines a per-event cooldown ("this popup, this state") with variable cooldowns ("this storyline, this country": `goldrush_active` for `very_long_modifier_time` = 20 years).

## 8. Timing & pacing principles (observed numbers)

How often things actually fire — use these as calibration when you want "the right event at the right time":

- **Layered probability.** A pulse event's real frequency = pulse interval × `chance_to_happen` × (weight / total valid weight) × its own trigger. Vanilla's generic yearly pulse `on_yearly_events`: `chance_to_happen = 65`, **154 entries, total weight 2918**. A typical weight-20 entry is at most 65% × 20/2918 ≈ 0.4%/year if everything were valid — real odds are higher because most entries' triggers fail, but the design intent is clear: any single generic event is a rare treat. Weight extremes in that list: `1 = vampire_panic.1`, `100 = prostitution.2`.
- **Typical `chance_to_happen` values:** 3 (krakatoa yearly), 10 (tunguska, lobbies proposals, movement events), 20–30 (regional/monarchy pulses), 50 (coup, tech monthly), 65 (generic yearly & half-yearly). Monthly pulses use LOW weights and big `N = 0` entries (mod: `25 = 0` vs weights of 1–2 → a great-man event roughly every few years, not monthly).
- **Explicit "nothing" weights** keep event pools from over-firing when few entries are valid: `50 = 0` (japan_monarchy_monthly), `70 = 0` (niger JE monthly), `90 = 0` (mod caucasus yearly), `25 = 0` (mod great men).
- **Spread within the pulse day.** Vanilla staggers sub-on_actions with `delay = { days = 1..90 }` on the pulse (`# delay ensures events won't fire simultaneously`, 00_code_on_actions.txt) so a country doesn't get 3 popups on January 1st. Do the same if you hook several lists to one pulse.
- **Cooldowns are LONG.** Repeatable flavor: `normal_modifier_time` (5y) to `very_long_modifier_time` (20y). Semi-unique: `stupidly_long_modifier_time` (50y). One-time: `never_fire_again_modifier_time` or variable guards. Election events use a 3-month cooldown value (`election_event_cooldown_months = 3`, event_values.txt).
- **Not at game start.** Date gates (`game_date >= 1850.1.1`, `year >= 1850`) and tech gates delay content past 1836; `on_game_started_after_lobby` only does setup. The generic pulses' first roll is inherently ≥1 interval in. Vanilla also gates one-shot windows with end dates (`game_date < 1895.12.31`, belle_epoque_events.5; `year <= 1855`, kamehameha).
- **War awareness.** Code on_actions maintain 5-year (1825-day) timed variables: `recently_lost_war` (set in `on_capitulation`), `recently_had_war` (set on both sides in `on_war_end`) — events key off them (`dreyfus.1` requires a recent lost/inconclusive war). Peacetime-flavor events gate with `is_at_war = no` (36 uses); revolution-sensitive chains use `is_revolutionary = no` / `NOR = { is_revolutionary = yes is_secessionist = yes }` (gov petition, headlines_action).
- **Right audience.** `is_player = yes` for pure-flavor popups the AI shouldn't waste (Emperor Norton in 00_code_on_actions.txt; the mod's `headlines_action` gates on `is_ai = no`), `is_ai = yes` branches for automation (antarctica decision). Rank/tag gates (`c:FRA ?= ROOT`, `country_rank >= rank_value:great_power`) keep national flavor at home.
- **Chain rhythm.** Story beats inside an active chain arrive fast (`days = 3`, `days = 7`); dramatic time-skips use `years = 2` (Dreyfus). JE-driven chains pace via monthly `random_events` with a large 0-weight instead of delays.

## Common pitfalls

- **Overwriting instead of extending on_actions** — shipping a modified copy of `00_on_actions_yearly.txt` (same filename or full-content copy) replaces/duplicates vanilla's lists and breaks on every patch. Add a NEW file that re-opens the on_action and contributes only your `events`/`random_events`/`on_actions` entries.
- **Two `effect`/`trigger` blocks on one on_action** — explicitly a conflict per `_on_actions.md`. Append effects via the wrapper pattern (`vanilla_on_action = { on_actions = { my_wrapper } }`).
- **Typos in on_action names fail silently** — an on_action key that matches nothing in code and is referenced by nothing is simply dead. Real case: `mod/3219394272/common/on_actions/joi_code_on_actions.txt:361` declares `on_law_checkpoint_succes` (missing `s`; vanilla's hook is `on_law_checkpoint_success`) — that events list can never fire. Always copy hook names from `00_code_on_actions.txt`.
- **Expecting saved scopes to survive a delayed `trigger_event`** — they don't. Tag objects with variables and re-save scopes in the follow-up's `immediate` (Dreyfus pattern, §7.1). Same for loc text in the follow-up: it can only read scopes saved by that event's own `immediate`.
- **Relying on on_action `effect` to set up scopes/variables for events fired by the same on_action** — `_on_actions.md` states the effect runs *concurrently*, not before, and its scopes/locals do NOT carry into those events.
- **Delayed events double-check validity** — an event queued with `delay`/`days` must have its trigger true at fire time too; if your trigger consumes its own precondition (variable set in `immediate` of a previous event), the follow-up may never arrive.
- **No `0 =` / low `chance_to_happen` in a random_events pool** — if most entries are usually invalid, the few valid ones fire near-every pulse. Vanilla reserves "no event" weight precisely to prevent this.
- **Forgetting a once-only guard on pulse events** — a pulse event without `cooldown` or a variable guard can repeat every pulse tick. Everything on vanilla's pulses has one or the other (usually both).
- **Firing at another country without scoping into it** — `trigger_event` targets the current scope; wrap it: `c:CHI ?= { trigger_event = { id = ryukyu_rivalry.6 days = 1 } }`.
- **Infinite `fallback` loops** — `_on_actions.md` warns a fallback cycle "may be prevented from advancing time". Never make two on_actions each other's fallback.
