# Journal Entries and Decisions

**Read this file when:** creating or editing journal entries (JEs), journal entry groups, decisions, scripted buttons, or scripted progress bars — i.e. anything under `common/journal_entries`, `common/journal_entry_groups`, `common/decisions`, `common/scripted_buttons`, `common/scripted_progress_bars`. For trigger/effect syntax see 02-script-language.md; for the events JEs fire see 03-events.md; for `modifiers_while_active` modifier definitions see 06-modifiers.md; for loc keys see 08-localization.md.

Paradox ships its own reference files — read them when in doubt, they are authoritative:
- `game/common/journal_entries/journal_entries.md`
- `game/common/scripted_buttons/scripted_buttons.md`
- `game/common/scripted_progress_bars/scripted_progress_bars.md`
- `game/common/decisions/000_decisions_help.txt`

## 1. Journal entry anatomy

All fields observed in vanilla (usage counts from all 145 vanilla JE files) and in the Victorian Century mod. Root scope for most blocks = the owning country (or no scope for contextless JEs). `scope:journal_entry` = the JE itself; `scope:target` = the target passed to `add_journal_entry`.

| Field | Type | Semantics (as used in real files) |
|---|---|---|
| `icon` | path string | Icon shown in the journal widget (`.dds` in vanilla, the mod also uses `.png`) |
| `group` | key | Journal entry group from `common/journal_entry_groups` (determines context + UI grouping) |
| `is_shown_in_lobby` | trigger | Country-scope trigger; shows the JE as advertised content in the pre-game lobby for matching countries (inferred from usage on major flavor JEs) |
| `is_shown_when_inactive` | trigger | If true (and JE not active), JE is visible as inactive. **Default = no**: a JE without it can only enter play via the `add_journal_entry` effect. Ignored when added via `add_journal_entry` |
| `possible` | trigger | When both this and `is_shown_when_inactive` are true, the JE **activates**. Default = yes. Ignored when added via `add_journal_entry` |
| `immediate` | effect | Runs on activation (whether by triggers or `add_journal_entry`). Standard place to `save_scope_as` scopes used by later blocks and loc |
| `complete` | trigger | Completion condition; if absent the JE cannot complete. Use `scope:journal_entry = { is_goal_complete = yes }` for goal-value JEs |
| `on_complete` | effect | Runs when `complete` becomes true (JE is then removed) |
| `fail` | trigger | Failure condition (player-visible failure) |
| `on_fail` | effect | Runs when `fail` becomes true |
| `invalid` | trigger | Silent cleanup condition — no player notification, JE just disappears |
| `on_invalid` | effect | Runs when `invalid` becomes true |
| `timeout` | int days or script value | Days until forced transition. Vanilla uses literal days (365…25550) and named script values (`normal_modifier_time`, `very_long_modifier_time`). 0/absent = never times out |
| `on_timeout` | effect | Runs at timeout |
| `on_weekly_pulse` / `on_monthly_pulse` / `on_yearly_pulse` | on_action | Inline on_action fired on the first day of week/month/year while active. Sub-keys observed: `events = { … }`, `random_events = { … }`, `effect = { … }` |
| `current_value` | script value | Goal metric, re-evaluated continuously |
| `goal_add_value` | script value | Evaluated **once at activation** and added to `current_value`-at-activation to form the goal total |
| `progressbar` | yes/no | Show the built-in goal progress bar |
| `display_progressbar_as_months` | yes/no | Render the goal value as months (1 use: `00_opium_wars.txt`) |
| `progress_desc` | loc key / triggered_desc | Text over the progress bar; default loc key `<je_key>_progress` |
| `is_progressing` | trigger | If defined and true, UI shows "progressing" state (used heavily in `00_tutorial.txt`, player-objective JEs) |
| `scripted_progress_bar` | key (repeatable) | Attach a scripted progress bar (see §5) |
| `scripted_button` | key (repeatable) | Attach a scripted button (see §4) |
| `modifiers_while_active` | list of modifier keys | Static modifiers applied to the owner while the JE is active (see 06-modifiers.md) |
| `status_desc` | `first_valid`/`triggered_desc` block | Dynamic status line; default loc key `<je_key>_status` |
| `weight` | int | Highest-weighted active JE appears in the goal tracker on the main screen. Vanilla values: 10 (background flavor), 100–200 (important), 1000–10000 (crisis/must-see) |
| `transferable` | yes/no | Whether the JE follows the **player** when switching country (revolution/releasing a subject). `transferable = yes` blocks revolution inheritance |
| `can_revolution_inherit` | yes/no | Whether a victorious revolution inherits the JE (revolutions inherit country variables regardless) |
| `can_deactivate` | yes/no | If yes, an active JE returns to inactive when `possible` becomes false again (4 uses in vanilla) |
| `should_be_pinned_by_default_uninvolved_or_context` | yes/no | Auto-pin in outliner for uninvolved countries / country-context JEs (most common field of all — 392 uses in vanilla) |
| `should_be_pinned_by_default_involved` | yes/no | Auto-pin for involved countries (contextless JEs) |
| `should_update_on_player_command` | yes/no | Re-evaluates the JE on player commands (only in `00_tutorial.txt`, semantics inferred) |
| `custom_completion_header` / `custom_failure_header` / `custom_on_completion_header` / `custom_on_failure_header` | loc key | Replace the generic "Completed"/"Failed"/"On completion"/"On failure" headers |
| `event_outcome_completed_desc` / `_failed_desc` / `_timeout_desc` (+ `_effect_desc` variants, plus `activated`/`invalidated` variants) | desc or effect block | Tooltip preview of what will happen on that outcome. `_effect_desc` form takes `header = <loc>` + `effect = { … }` where the effect is **only rendered as a tooltip, never executed** |
| `how_tutorial` / `why_tutorial` | lesson key | Tutorial lessons explaining how/why (tutorial JEs) |
| `widget` | block | Custom GUI widget: `gui = "gui/…"` + `name` + `container = "custom_widget_container_N"` (2 uses) |
| Contextless-JE fields | | `should_be_involved`, `should_show_when_not_involved`, `immediate_all_involved`, `on_complete_all_involved`, `on_fail_all_involved`, `on_invalid_all_involved`, `on_timeout_all_involved`, `on_become_involved_after_activation`, `on_no_longer_involved` — see §7 |

There is **no** `active_update`, `on_activate`, `goal_add`, `effect`, or `ai_will_do` field on journal entries — activation effects go in `immediate`, the goal delta is `goal_add_value`.

### Minimal complete example (goal-tracking JE)

```
# game/common/journal_entries/00_standard_of_living.txt (trimmed)
je_sol_1 = {
	icon = "gfx/interface/icons/event_icons/event_protest.dds"
	group = je_group_crises

	is_shown_when_inactive = {
		NOT = { has_variable = completed_sol_je }
		root.average_sol < 10
	}
	possible = {
		root.average_sol < 7
		OR = {
			has_law_or_variant = law_type:law_no_social_security
			has_law_or_variant = law_type:law_no_health_system
		}
	}
	immediate = {
		trigger_event = { id = sol_events.1 }
	}
	complete = {
		custom_tooltip = {
			text = je_sol_goal_desc
			scope:journal_entry = { is_goal_complete = yes }
		}
	}
	on_complete = {
		set_variable = { name = completed_sol_je days = normal_modifier_time }
		trigger_event = { id = sol_events.2 }
	}
	invalid = {
		has_variable = dismissed_poverty_variable
	}
	on_monthly_pulse = {
		random_events = {
			100 = 0            # weighted "nothing happens"
			10 = sol_events.3
			10 = sol_events.4
		}
	}
	current_value = { value = root.average_sol }
	goal_add_value = { add = 3 }          # goal = SoL at activation + 3
	weight = 200
	should_be_pinned_by_default_uninvolved_or_context = yes
	transferable = no
	progressbar = yes
}
```

A `goal_add_value` can also encode a **timer**: `je_belle_epoque` (`00_belle_epoque.txt`) sets `goal_add_value = { add = 120 }` with a `current_value` counting a variable incremented `+1` per `on_monthly_pulse` → a 10-year countdown rendered as a progress bar.

## 2. Lifecycle

1. **Inactive/visible**: `is_shown_when_inactive` true, `possible` false → shown greyed-out with `possible` as the to-do list. JEs without `is_shown_when_inactive` never self-activate.
2. **Activation**: either both triggers become true, or an effect runs `add_journal_entry = { type = je_key }` (optionally `target = scope:x`, readable as `scope:target` inside the JE). `immediate` fires now; `modifiers_while_active` apply; scripted buttons/bars appear; pulses start.
   ```
   # game/events/assassination_events.txt
   add_journal_entry = {
   	type = je_assassination
   	target = scope:assassination_ruler_scope
   }
   ```
3. **While active**: `on_weekly/monthly/yearly_pulse` fire; `complete`/`fail`/`invalid` are continuously tested (their tooltips are what the player sees as win/lose conditions); `timeout` counts down (shown in UI).
4. **End states**: `complete` → `on_complete`; `fail` → `on_fail`; timeout → `on_timeout`; `invalid` → `on_invalid` (silent). All remove the JE. `can_deactivate = yes` alone allows returning to inactive instead.
5. **Chaining**: end effects typically `trigger_event` (whose options may `add_journal_entry` the next step) or add the next JE directly. Vanilla chain example: decision `survey_the_suez_canal_site` → `add_journal_entry = { type = je_suez_survey }` (`canal_decisions.txt`) → `je_suez_survey` `on_complete` fires `canal_events.100` → event grants `je_suez_canal` (`00_canals.txt`, `canal_events.txt`).

Useful cross-file tools observed: `has_journal_entry = je_key` (trigger), `je:je_key ?= { … }` (scope link into an active JE), `scope:journal_entry = { set_variable/add_modifier/has_variable … }` (JEs hold their own variables and modifiers, e.g. `je_law_imposition` in `00_impose_law.txt`).

### Localization keys (see 08-localization.md)

Observed in `game/localization/english/content_104_l_english.yml` and `journal_entries.md`:

| Key | Purpose |
|---|---|
| `<je_key>` | Title ("Poverty Crisis") |
| `<je_key>_reason` | Flavor description shown in the entry |
| `<je_key>_goal` | Goal line ("Improve the [concept_sol] in your country.") |
| `<je_key>_status` | Default for `[JournalEntry.GetStatusDesc]` if no `status_desc` block |
| `<je_key>_progress` | Default for `[JournalEntry.GetProgressDesc]` if no `progress_desc` |

Loc functions for goal JEs: `[JournalEntry.GetTotalGoalValue]`, `[JournalEntry.CalcCurrentGoalValue]`, `[JournalEntry.GetGoalAddValue]`, `[JournalEntry.GetGoalProgressValue]`, `[JournalEntry.GetGoalProgressPercent]`. Saved scopes from `immediate` are usable in JE loc via `SCOPE.sCountry('scope_name')` / `JournalEntry.GetTopScope…`.

## 3. Journal entry groups (`common/journal_entry_groups`)

Tiny files. Each group sets the JE's **context**:

```
# game/common/journal_entry_groups/00_journal_entries.txt
je_group_crises = {
	context = country                       # normal, owned by one country
	updates_strategic_region_stances = yes  # optional AI hint flag
}
je_group_global_international_situations = {
	context = none                          # contextless/global JE (see §7)
	updates_strategic_region_stances = yes
}
```

Only two keys observed: `context = country|none` and optional `updates_strategic_region_stances = yes`.

The Victorian Century mod redefines every group with a `REPLACE_OR_CREATE:` key prefix (`mod/3219394272/common/journal_entry_groups/00_journal_entries.txt`), e.g. `REPLACE_OR_CREATE:je_group_crises = { context = country }`, while its JEs reference the plain key `je_group_crises`. Vanilla never uses this prefix; its exact semantics are (unverified) — apparently "override if exists, else create". When writing your own mod, plain keys in a uniquely-named file work fine; same-named files fully replace the vanilla file.

## 4. Scripted buttons (`common/scripted_buttons`)

Player-clickable actions rendered inside a JE (attach with `scripted_button = key`, repeatable). Fields observed across all 216 vanilla + 391 mod buttons — exactly these eight: `name`, `desc`, `visible`, `possible`, `effect`, `ai_chance`, `selected`, `cooldown`.

```
# game/common/scripted_buttons/00_scripted_buttons.txt (trimmed)
je_the_paris_commune_france_button_a = {
	name = "je_the_paris_commune_repress_communard_sympathizers"      # loc key, quoted
	desc = "je_the_paris_commune_repress_communard_sympathizers_desc"

	visible = { has_variable = paris_commune_fra_perspective }  # hides button entirely
	cooldown = { days = 90 }                                    # greys out after click

	effect = {
		custom_tooltip = cooldown_three_months_tt
		add_radicals = { value = small_radicals strata = lower }
		change_global_variable = { name = paris_commune_progress_var add = -10 }
	}
}
```

```
# game/common/scripted_buttons/french_monarchy buttons, same file (trimmed)
french_monarchy_bonapartist_button = {
	name = "bonapartist_button"
	desc = "bonapartist_button_desc"
	visible = { owner = { has_variable = chose_initial_french_dynasty } }
	possible = {
		any_interest_group = {
			is_in_government = yes
			leader = { has_ideology = ideology:ideology_bonapartist }
		}
	}
	selected = { has_variable = supporting_bonapartist_var }   # renders as toggled-on
	effect = {
		set_variable = supporting_bonapartist_var
		je:je_divided_monarchists = {
			add_progress = { value = 10 name = divided_monarchists_bonapartist_progress_bar }
		}
	}
}
```

Notes:
- `cooldown = { days = 90 }`, `{ days = normal_modifier_time }`, and `{ years = 5 }` all occur (years form: `mod/3219394272/common/scripted_buttons/joi_prussia_buttons.txt`).
- `ai_chance` in real files is always the script-value form (`value = N` + `if`/`add`/`multiply`), evaluated in country scope; AI clicks when it evaluates favorably. `base`/`modifier` form appears only in Paradox's `scripted_buttons.md` (unverified in shipped script). AI-relevant example: `00_wild_je_buttons.txt` uses `add = { value = "c:RUS.relations(root)" }`.
- Triggers/effects generally use bare country-scope triggers (`is_at_war`, `has_technology_researched`, `add_modifier`, `var:x >= 25` — see `joi_prussia_buttons.txt`), but some vanilla buttons wrap checks in `owner = { … }` (which scope the button root formally is, is unverified; both styles ship and work).
- Button-driven mini-economies: the mod pattern is a country variable as "points" (`pru_general_staff_var`), buttons that `change_variable` to spend them and grant timed modifiers — a national-focus-like tree entirely in one JE.
- Loc: only `name` and `desc` keys; the effect tooltip is auto-generated (use `custom_tooltip` inside `effect` for flavor lines, `show_as_tooltip` for preview-only effects, e.g. `sakoku_buttons.txt`).

## 5. Scripted progress bars (`common/scripted_progress_bars`)

Attach with `scripted_progress_bar = key` (repeatable — expeditions attach a progress bar *and* a peril bar). Fields observed: `name`, `desc`, `second_desc`, `is_inverted`, `start_value`, `min_value`, `max_value`, one style flag (`default`, `default_green`, `default_bad`, `double_sided_gold`, `double_sided_two_spains`), and `weekly_progress` / `monthly_progress` blocks (`yearly_progress` exists in Paradox's md only, unused in shipped files; `double_sided_bad` likewise md-only).

```
# game/common/scripted_progress_bars/00_victoria_progress_bars.txt
expedition_progress_bar = {
	name = "expedition_progress_bar"     # loc key, quoted
	desc = "expedition_progress_bar_desc"
	default_green = yes
	start_value = 0
	min_value = 0
	max_value = 8
}
```

```
# game/common/scripted_progress_bars/00_greece_progress_bars.txt (trimmed)
bavarocracy_progress_bar = {
	name = "bavarocracy_progress_bar"
	desc = "bavarocracy_progress_bar_desc"
	default_bad = yes
	is_inverted = yes                     # low = good; player wants to keep it down

	monthly_progress = {                  # a script value with desc'd contributions
		if = {
			limit = { ruler = { NOT = { religion = rel:orthodox } } }
			add = { desc = "bavarocracy_catholic_ruler_tt" value = 1 }
		}
		if = {
			limit = { has_variable = recently_won_war }
			add = { desc = "bavarocracy_winning_wars_tt" value = -1 }
		}
		# … every add = { desc = … value/every_scope_x } shows as a tooltip line
	}
	start_value = 10
	min_value = 0
	max_value = 100
}
```

- `weekly_progress`/`monthly_progress` run **before** the JE's weekly/monthly pulses (per `scripted_progress_bars.md`). Each `add = { desc = "…" value = N }` line becomes an itemized tooltip row; `every_scope_state = { add = this.turmoil }` style aggregation works inside.
- **Changing progress from effects** (JE scope): `add_progress = { value = 1 name = expedition_progress_bar }` — used via `je:je_antarctica ?= { add_progress = … }` in `game/common/scripted_effects/00_expedition_effects.txt` and from scripted buttons (§4). No `set_progress` effect exists in shipped files.
- **Reading progress in triggers** (JE scope): the quoted-trigger form
  ```
  je:je_congo_expedition ?= {
  	"scripted_bar_progress(expedition_progress_bar)" >= 3
  }
  ```
  (`game/events/expedition_events/congo_river_expedition_events.txt`; also comparable bar-vs-bar, see `mod …/journal_entries/01_french_monarchism.txt` complete trigger). Works in `complete`, event triggers, and customizable_localization.
- Loc: `name` and `desc` (left label); `second_desc` = right-side label.
- Mod example of a purely passive bar: `mod/3219394272/common/scripted_progress_bars/joi_usa_scripted_progress_bars.txt` gains +1/month while `company:company_united_fruit` is prosperous.

## 6. Decisions (`common/decisions`)

One-shot buttons in the Decisions panel. **Exactly four fields exist** across all 60 vanilla decisions: `is_shown`, `possible`, `when_taken`, `ai_chance` (3 vanilla decisions omit `ai_chance`; it defaults to 1). There is no `effect`, `ai_will_do`, `cooldown`, or `days_remaining` key. Country scope throughout. Repeatability is manual: set a variable in `when_taken` and gate `is_shown`/`possible` on it.

```
# game/common/decisions/00_decisions.txt (trimmed)
revive_olympic_games_decision = {
	is_shown = {                       # visible at all?
		exists = c:GRE
		c:GRE ?= THIS
	}
	possible = {                       # clickable? (failed lines shown as to-do)
		has_technology_researched = organized_sports
		hidden_trigger = {
			NOT = { has_variable = revive_olympics_decision_taken }
		}
	}
	when_taken = {
		set_variable = { name = revive_olympics_decision_taken value = yes }
		add_modifier = { name = modifier_olympic_games }
		add_modifier = { name = modifier_olympic_games_bureaucracy days = short_modifier_time }
	}
	ai_chance = {
		value = 0
		if = { limit = { bureaucracy > 0 } add = 5 }
		if = {
			limit = { OR = { is_diplomatic_play_committed_participant = yes is_at_war = yes } }
			multiply = 0               # common vanilla idiom: AI ignores decisions in wartime
		}
	}
}
```

Decisions frequently start JE chains: `lowlands_land_reclamation` (`00_decisions.txt`) runs `add_journal_entry = { type = je_land_reclamation }`; the mod's `claiming_the_right_of_holy_places` (`mod/3219394272/common/decisions/crimean_war_decisions.txt`) adds `change_infamy = 10`, a decaying modifier (`add_modifier = { name = claim_of_the_holy_land years = 10 is_decaying = yes }`), a follow-up JE, and `trigger_event` on another country — a decision as a war-of-choice trigger. Mod decisions also gate on other JEs: `possible = { has_journal_entry = peter_instruction }`.

Localization (from `000_decisions_help.txt`, verified in `decisions_l_english.yml`): `<key>` (title), `<key>_desc` (description), optional `<key>_tooltip` (extra tooltip text fed into `DECISION_TOOLTIP_FORMAT`). Convention: key ends in `_decision` (not enforced; the mod often omits it).

## 7. Contextless (global) journal entries

A JE whose `group` has `context = none` belongs to no single country; countries become "involved". Complete worked example: `game/common/journal_entries/99_test_global_je.txt` (plus `99_test_global_je_button.txt`):

```
# game/common/journal_entries/99_test_global_je.txt (trimmed)
je_global_test = {
	group = je_group_global_test              # context = none
	should_be_involved = {                    # root = each candidate country
		country_rank >= rank_value:great_power
	}
	should_show_when_not_involved = {
		country_rank >= rank_value:major_power
	}
	immediate_all_involved = {                # per-involved-country variant of immediate
		change_relations = { country = c:LIP value = -10 }
	}
	on_complete_all_involved = {
		add_modifier = { name = lippe_crisis_averted years = 10 }
	}
	on_become_involved_after_activation = { … }
	on_no_longer_involved = { … }
	on_weekly_pulse = {
		effect = {
			scope:journal_entry = {
				every_scope_je_involved = {                    # iterate involved countries
					limit = { NOT = { country_rank >= rank_value:great_power } }
					scope:journal_entry = { remove_involved_country = prev }
				}
				add_involved_country = c:ARG
			}
		}
	}
	timeout = 1825
}
```

Every `on_*` hook has an `_all_involved` twin that fires once per involved country (country scope). `modifiers_while_active` propagate to all involved countries. Effects on the JE scope: `add_involved_country`, `remove_involved_country`; iterator `every_scope_je_involved`. Real production uses: `00_treaty_of_london.txt`, `05_great_eastern_crisis.txt`, iberia/british-india global groups.

## 8. Design and pacing observations

**Timeouts are always in days.** Vanilla spread: 365 (1yr, rare pressure JEs), 730/1095 (2–3yr crises: coups, Paris Commune phases, fascism window), 1825 (5yr, the most common "mission" deadline), 3650 (10yr, the standard flavor-arc deadline — most frequent overall), 4380/5475 (12–15yr arcs), 7300–10950 (20–30yr era journals), up to 25550 (70yr, `02_brazil_navy.txt`). Named script values (`normal_modifier_time`, `very_long_modifier_time`) are also legal. The Victorian Century mod adds a fast cadence vanilla lacks: `timeout = 90` days (16 uses) for reactive "answer within a season" entries, alongside 10950–18615-day era arcs.

**Weights** sort the goal tracker: 10 = background flavor, 100–200 = notable national arcs, 1000 = major situations (law imposition, Schleswig-Holstein), 10000 = wars/crises that must top the tracker (`00_opium_wars.txt`).

**Reward scaling**: on_complete rewards in both sources are mostly (a) timed country modifiers, often `is_decaying = yes` (`00_impose_law.txt`), (b) a follow-up event delivering the narrative payoff (`trigger_event = { id = … days = 5 }`), (c) permanent state modifiers for construction JEs (`months = -1` / `days = -1` = permanent, `mining_development.txt`, `00_decisions.txt`), (d) unlocking the next JE. Failure paths mirror with radicals/infamy/negative modifiers.

**Chaining patterns**:
- decision → JE → event → JE (Suez/Panama canal chain, §2).
- JE pulse `random_events` with a large weighted `0` entry (e.g. `100 = 0` vs several `10 = event.x`) is the standard "sometimes nothing happens" flavor drip (`00_belle_epoque.txt` has an 18-event monthly table).
- `immediate` can add sibling JEs conditionally (mod `deutsch_bundestag` adds `carlsbad_decrees_journal` if censorship laws are active, `expand_journal.txt`).
- Buttons drive bars, bars gate `complete` — the French monarchism triangle (three faction bars, three buttons, winner decided by comparing `scripted_bar_progress(...)` values) exists in both vanilla (`01_french_monarchism.txt`, `00_scripted_buttons.txt`) and the mod's expanded copy.

**Mod-scale observation**: Victorian Century builds per-country "grand journals" (60–97 KB files like `ottoman_empire.txt`, `british_empire.txt`) where nearly every JE carries `scripted_button` entries (554 button references vs vanilla's 169) — buttons + variables + cooldowns replace tech-tree-style focus systems. It also blanks vanilla files by shipping a same-named file containing only `#nothing` (`common/journal_entries/00_canada_australia.txt`, `common/decisions/manifest_destiny.txt`) — full-file override is the only way to remove vanilla content.

## Common pitfalls

- **Forgetting that omitting `is_shown_when_inactive` makes the JE add-only.** Default is `no`: without the trigger (or an `add_journal_entry` call somewhere), the JE never appears. Conversely, `add_journal_entry` **ignores** both `is_shown_when_inactive` and `possible`.
- **`goal_add_value` is snapshotted at activation** and added on top of the activation-time `current_value` — it is a delta, not an absolute target. `goal_add_value = { add = 3 }` on SoL means "current SoL + 3", not "SoL 3".
- **A JE with no `complete` trigger can never complete** (and no `fail` = can never fail). Add-only utility JEs like `je_suez_canal` rely on `invalid` for cleanup — always give long-lived JEs an `invalid` escape hatch or they linger forever after their premise dies.
- **`invalid` is silent; `fail` is loud.** Use `invalid` for "premise no longer applies", `fail` for player-meaningful defeat (frame it with an event or `on_fail` consequences).
- **Decisions have only `is_shown` / `possible` / `when_taken` / `ai_chance`.** No `effect =`, no `ai_will_do =` — those keywords are from other Paradox games and will not work.
- **Decisions are not one-shot by themselves.** Guard with a variable set in `when_taken` (`NOT = { has_variable = x_taken }` in `is_shown` or `possible`) or the AI/player can take them repeatedly.
- **Loc suffixes differ per database**: JEs use `<key>` / `<key>_reason` / `<key>_goal` / `<key>_status` / `<key>_progress`; decisions use `<key>` / `<key>_desc` / `<key>_tooltip`; buttons and bars take explicit quoted loc keys in `name` / `desc`. Writing `je_x_desc` for a journal entry does nothing.
- **Scripted button/bar keys are referenced by bare name** from the JE (`scripted_button = my_button`), and the bar name inside `add_progress` / `scripted_bar_progress(...)` must match the bar's script key exactly — typos fail silently.
- **`add_progress` and `scripted_bar_progress(...)` only work in journal-entry scope** — reach the JE first via `je:je_key ?= { … }` or `scope:journal_entry`. Use `?=` since the JE may not exist.
- **Progress bar ticks fire before JE pulses** — if a monthly pulse event reads the bar, it sees the already-updated value.
- **Timeout is in days**, not months (despite `display_progressbar_as_months` existing for goal display). `timeout = 12` is 12 days, not a year.
- **`transferable = yes` and revolution inheritance are mutually exclusive** — transferable JEs stay with the player, so `can_revolution_inherit` is effectively ignored for them. Variables the JE depends on are *not* auto-transferred with a transferable JE, but *are* inherited by revolutions.
- **Blanking vanilla content** requires overriding the whole file with a same-named file (`#nothing`); you cannot delete a single vanilla JE/decision from a differently-named file.
- **`event_outcome_*_effect_desc` blocks never execute** — they are tooltip generators only. Putting a real reward there gives the player a promise the game will not keep; duplicate it in `on_complete`.
