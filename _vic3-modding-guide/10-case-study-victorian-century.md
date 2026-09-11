# 10 — Case Study: The Victorian Century Mod

**Read this file when:** you want a concrete quality benchmark for new content — what a large, polished flavor mod actually ships, how it organizes files, and which of its techniques are worth copying. All paths below are relative to the mod root (Windows: `C:\Users\<username>\OneDrive\Documents\Paradox Interactive\Victoria 3\mod\3219394272`, Mac: `~/Documents/Paradox Interactive/Victoria 3/mod/3219394272`) unless prefixed `game/` (vanilla). Design principles distilled from these observations live in `09-design-and-balance.md`; syntax in `03-events.md`, `04-event-chains-and-triggering.md`, `05-journal-entries-and-decisions.md`, `06-modifiers.md`.

Victorian Century (Steam Workshop ID 3219394272; `.metadata/metadata.json` name `"Victorian Century"`) is a Chinese-authored, fully bilingual (English + Simplified Chinese) country-flavor overhaul. Its internal prefix is `joi_` — expect it on nearly every file and identifier. Comments in script are Chinese; identifiers are self-describing English.

---

## 1. What it ships (surveyed counts)

| Content | Amount | Where |
|---|---|---|
| Events | ~708 in 20 files (~1,350 options) | `events/` |
| Journal entries | ~437 in 32 files | `common/journal_entries/` |
| Decisions | 42 | `common/decisions/` (`joi_flavor_decisions.txt` 18, `joi_gbr_decisions.txt` 17, `canada_australia.txt` 4…) |
| Scripted buttons | ~366 | `common/scripted_buttons/` — 13 per-country files, 454 KB total |
| Scripted progress bars | 26 | `common/scripted_progress_bars/` (Japan 31.6 KB, Ottomans 28.2 KB) |
| On-actions | 2 files | `common/on_actions/joi_code_on_actions.txt` (pulse hooks, monarch succession), `headlines_on_actions.txt` (40 KB news system) |
| Scripted effects | 13 per-country files, ~340 KB | `common/scripted_effects/joi_*_scripted_effects.txt` |
| Laws / amendments | 10 new laws, 42 amendment types | `common/laws/joi_*.txt`, `common/amendments/` |
| Companies | 107 blocks (new + vanilla overrides) | `common/company_types/joi_companies.txt` (185 KB) |
| Game rules | 6 rule groups | `common/game_rules/` |
| Reworked politics | interest_groups (8 files, 139 KB), parties (91 KB), ideologies (87 KB), state_traits (98 KB), static_modifiers (439 KB) | `common/…` |
| Localization | 41 English + 41 Chinese yml files in per-topic subfolders | `localization/english/…`, `localization/simp_chinese/…` |
| Fake DLC declaration | `dlc/dlc_vc/`, `dlc_metadata/` | see §8 |

### Event files (structure stats)

| File | Events | Options | custom_tooltip | ai_chance | Notes |
|---|---|---|---|---|---|
| `joi_flavor_gbr.txt` | 130 | 247 | 81 | 6 | Britain arc + economic crisis events |
| `joi_flavor_tur.txt` | 101 | 248 | 69 | 20 | Ottoman arc, heavy event-to-event chaining (38 `trigger_event`) |
| `joi_flavor_fra.txt` | 76 | 136 | 39 | 17 | France |
| `joi_flavor_jap.txt` | 56 | 117 | 62 | 0 | Japan |
| `joi_flavor_usa.txt` | 48 | 75 | 22 | 6 | USA |
| `joi_flavor_ger.txt` | 45 | 89 | 11 | 0 | Germany |
| `joi_flavor_expand.txt` | 39 | 70 | 38 | 33 | Cross-country unification/expansion chains (47 `trigger_event`) |
| `joi_flavor_chi.txt` | 38 | 61 | 14 | 8 | China |
| `joi_great_man.txt` | 22 | 37 | 0 | 0 | Great-people pulse events, all once-only |
| `russia_events.txt`, `victoria_events.txt` | 12 + 3 | — | — | — | **same-filename overrides of vanilla files** |

Average ≈ 1.9 options/event — matching the vanilla norm (see `09-design-and-balance.md` §3).

### Journal entry files (largest)

`ottoman_empire.txt` 44 JEs · `china_dynasty.txt` 39 · `british_empire.txt` 37 · `russia_mother.txt` 35 · `japan_empire.txt` 31 · `austrian_empire.txt` 30 · `united_kingdom.txt` 29 · `british_raj.txt` 28 · `french republic.txt` 25 · `french_empire.txt` 23 · `united_states.txt` 23 · plus system files: `economic_crisis.txt` (5 chained world crises), `berlin_conference.txt` (16), `expand_journal.txt` (15), `mining_development.txt` (14).

The center of gravity: **per-great-power flavor arcs**, each built from the same kit — a lobby-visible "empire" JE tree + scripted buttons + progress bars + a dedicated event namespace + a dedicated loc subfolder per language.

---

## 2. Deep dive 1 — "Rule, Britannia!" (British Empire JE tree)

Files: `common/journal_entries/british_empire.txt`, `events/joi_flavor_gbr.txt`, `common/scripted_buttons/joi_great_britain_buttons.txt`, loc `localization/english/gbr/british_journal_entries_l_english.yml`.

**Flow:** lobby-visible root JE → three parallel conquest sub-JEs feeding a counter → completion conference event → player-chosen empire path.

1. `stabilize_british_empire` is shown from the country-select lobby (`is_shown_in_lobby = { c:GBR ?= THIS }`) — the player sees the campaign promise before starting. Its `immediate` spawns the sub-JEs, zeroes tracking variables, and creates agitator John Stuart Mill with a guaranteed career:

```paradox
# common/journal_entries/british_empire.txt
immediate = {
    add_journal_entry = { type = conqueror_burma }
    add_journal_entry = { type = conqueror_punjab }
    add_journal_entry = { type = conqueror_baluchistan }
    set_variable = { name = british_empire_stability value = 0 }
    create_character = { template = agitator_john_stuart_mill save_scope_as = john_stuart_mill_scope }
    if = {  #防止其早死 ("prevent early death")
        limit = { exists = scope:john_stuart_mill_scope }
        scope:john_stuart_mill_scope = {
            set_career_length = { years = 30 random_range = { 1.0 1.5 } } # 30-45 years
        }
    }
}
```

2. Each sub-JE **grants the claims it asks you to press** in its own `immediate` (`s:STATE_MANDALAY = { add_claim = c:BIC add_claim = ROOT }`), accepts completion by ownership *or* vassalization (`c:BUR ?= { is_subject_of = c:GBR }`), and `on_complete` fires a flavor event + `change_variable = { name = stabilize_british_empire_var add = 1 }`.
3. The parent `complete` block wraps every requirement in `custom_tooltip` so the journal reads as human goals, and requires the counter via a visible progress bar:

```paradox
complete = {
    custom_tooltip = {
        text = stabilize_british_empire_complete_1_tt       # "50 relations with 5 Canadian subjects"
        any_subject_or_below = {
            OR = { country_has_primary_culture = cu:anglo_canadian
                   country_has_primary_culture = cu:franco_canadian }
            relations:root >= 50
            count >= 5
        }
    }
    ...
    custom_tooltip = {
        text = stabilize_british_empire_complete_4_tt       # "complete three Unify the Subcontinent objectives"
        var:stabilize_british_empire_var >= 3
    }
}
current_value  = { value = var:stabilize_british_empire_var }
goal_add_value = { add = 3 }
progressbar = yes
```

4. `on_complete` → event `joi_flavor_gbr.31` (Imperial Conference): two options, each a `custom_tooltip` naming the constitutional path and setting a branch variable — `choose_british_empire_act` (Imperial Federation; +0.1 loyalists to Industrialists and Petty Bourgeoisie, hidden claim grants for the unified empire tag) vs `choose_british_dominion_act` (Dominion Autonomy; +0.1 loyalists to Intelligentsia and Trade Unions). Downstream content keys off the branch variable.
5. Anti-frustration: `fail = { country_rank < rank_value:great_power }` with `on_fail` stripping the `rule_britannia` modifier and `add_radicals = { value = 0.1 }`; and

```paradox
invalid = { is_ai = yes  game_date >= 1857.1.1 }
on_invalid = {
    hidden_effect = { trigger_event = { id = joi_flavor_gbr.31 } }   # AI resolves the arc silently
}
```

6. Player agency beyond wars: sub-JEs mount **scripted buttons** — `british_empire_conqueror_punjab_button` ("Doctrine of Lapse", `joi_great_britain_buttons.txt` ~line 1441) is `possible` only after Punjab is gone (`NOT = { exists = c:PAN }`), once-only via global variable, `ai_chance = { value = 100 }` so AI Britain also presses it, and its `effect` annexes the leftover Sikh splinters into BIC with `exists`-checked branches for every GBR/BIC combination.

**Why it's good design:** a sandbox goal becomes staged, visible sub-goals with counters; claims are handed out so the wars are startable; both endings (player choice, AI silent resolution) are handled; and the payoff is a *fork* in the campaign, not just a buff.

---

## 3. Deep dive 2 — Railway Mania → recurring Economic Crises

Files: `common/journal_entries/united_kingdom.txt` (railway_mania), `common/journal_entries/economic_crisis.txt` (5 chained crisis JEs), `events/joi_flavor_gbr.txt` (.83–.91), `common/game_rules` (`economic_crisis_rules`).

This is the mod's most systemic invention — vanilla has nothing like a repeating global boom-bust cycle.

1. **Boom (GBR-only):** `railway_mania` activates once Britain has `railways` tech + a market economy (`law_interventionism`/`law_laissez_faire`), and either 75% of British homeland states have a railway or `year >= 1838`. While active Britain gets `railway_mania_modifier`; **every other railways-tech country gets `railway_mania_others_modifier` for 10 years** — the bubble is exported before it pops.
2. **Race against a visible clock:**

```paradox
# common/journal_entries/united_kingdom.txt (railway_mania)
on_monthly_pulse = {
    random_events = {
        100 = 0
        10 = joi_flavor_gbr.91   # "ambitious railway investor" pressure beat, ~yearly
    }
    effect = {
        change_variable = { name = railway_mania_var add = 1 }
    }
}
current_value  = { value = var:railway_mania_var }
goal_add_value = { value = 120 }        # 120 months = a literal 10-year countdown
progressbar = yes
weight = 100000
```

   Win condition: railway level ≥ 15 with `occupancy >= 1` and `earnings >= 50` in 92% of British/Irish/Scottish homeland states → `mania_railway_boom` for 10 years + `add_loyalists 0.05`.
3. **Failure escalates instead of ending:** `on_fail` → `joi_flavor_gbr.83` ("week of terror"), whose single option removes the global crisis cooldown, tags Britain `set_variable = this_is_railway_mania_country`, applies `end_of_railway_mania_modifier years = 5`, and previews the avalanche: `show_as_tooltip = { add_journal_entry = { type = first_economic_crisis } }`.
4. **The crisis JE is a full system** (`first_economic_crisis`): activates for stock-exchange economies when the mania pops *or* when a great power already fell (`great_power_cause_1st_crisis_var` global — set by the #1-ranked country, or #2 if it's the player: contagion by rank). `immediate` fires "Black Monday" (`joi_flavor_gbr.84`), which marks patient zero with `where_the_crisis_begin_modifier` (5 y). During the crisis, a JE monthly pulse rolls `100 = 0` + six weight-10 misery events (tariff dispute .85, credit crisis .86, bank failure .87, deficit crisis .88, farmer distress .89, .90) — roughly one beat every ~2 months.
5. **Exits, all handled:** escape by growing GDP 1% (progress bar goal = `root.gdp × 0.01`), minimum 1 year in crisis enforced by a timed variable (`fucking_economic_crisis_comming years = 1` — yes, really); `timeout = 1825`; `fail` when `first_economic_crisis_counter_var >= 3` (three great powers recovered first — you rode it out in their slipstream). Rewards scale with performance: `on_complete` = `add_loyalists 0.1` + `post_crisis_reconstruction years = 5`; fail/timeout = `0.025` + a weaker 5-year modifier; `invalid` (bankruptcy) = `add_radicals 0.05` + `declare_bankruptcy_during_economic_cirsis years = 5`. **Every** path sets the shared pacing valve:

```paradox
if = {
    limit = { NOT = { has_global_variable = economic_crisis_colddown_var } }
    set_global_variable = { name = economic_crisis_colddown_var years = 20 }
}
```

6. **Recurrence:** `second_` … `fifth_economic_crisis` unlock sequentially behind the previous crisis's `…_ended` global, add stricter entry conditions (trade reliance, incorporated manufacturing states), and the whole system checks `has_game_rule = enable_economic_crisis` so players can switch it off.

**Values worth copying:** 10-year visible deadline; ~yearly pressure beats via `100=0 / 10`; ~2-monthly beats during an active crisis via `100=0 / 6×10`; 20-year global cooldown between world crises; 5-year aftermath modifiers; 4:1 ratio between full and consolation rewards; `weight = 100000` so crisis JEs sort above everything (vanilla's ceiling is 10000 — see pitfalls).

---

## 4. Deep dive 3 — the Headlines system (player-facing world news)

Files: `common/on_actions/headlines_on_actions.txt` (40 KB), `common/messages/` (19 KB), loc `localization/english/headlines_l_english.yml` (46 KB in Chinese), game rule `headlines_minor_events`.

A monthly on_action appended non-destructively to the vanilla pulse:

```paradox
# common/on_actions/headlines_on_actions.txt
on_monthly_pulse_country = {
    on_actions = { headlines_action }
}
headlines_action = {
    effect = {
        if = {
            limit = { is_ai = no  is_revolutionary = no }   # player only
            if = {   #巴黎公社 (Paris Commune)
                limit = {
                    exists = c:FRA
                    OR = {
                        c:FRA = { has_variable = joi_paris_commune_should_happen }
                        exists = c:PRC
                    }
                    NOT = { has_variable = headlines_paris_commune_headline_var }
                }
                c:FRA ?= { save_scope_as = FRA_scope }
                c:PRC ?= { save_scope_as = PRC_scope }
                set_variable = headlines_paris_commune_headline_var
                post_notification = headlines_paris_commune_news
            }
            # ...dozens more if-blocks: Entente Cordiale, Sepoy Mutiny, Indian
            #    independence, unification of the subcontinent, French Syria...
        }
    }
}
```

The pattern per headline: (1) *content* scripts elsewhere set a global/tag variable when something notable happens; (2) the reporter action detects it, saves display scopes, marks a per-player "already reported" variable, and emits `post_notification` — **a feed item, not a popup**. Verbosity is player-controlled through the `headlines_minor_events` game rule (all/relevant/none).

**Why it's good:** world flavor reaches the player without pausing the game or spamming AI countries; the decoupling (content sets a flag, reporter consumes it) means event writers never touch notification code; per-player seen-variables make it save-safe and multiplayer-safe.

---

## 5. Deep dive 4 (short) — Deutsch Bundestag (a multi-country shared arc)

Files: `common/journal_entries/expand_journal.txt`, `events/joi_flavor_expand.txt`, `common/scripted_effects/joi_expand_scripted_effects.txt`.

Where the British arc is single-country, `deutsch_bundestag` shows the mod's pattern for content shared by a whole culture group — every German-culture country gets it (`any_primary_culture = { OR = { cu:south_german = this cu:north_german = this } }`), visible in the lobby, excluded for tags that shouldn't have it (`NOT = { c:UBD ?= THIS }`).

1. **Era-bounded by tech, not date:** `is_shown_when_inactive` and `possible` both require `NOT = { has_technology_researched = nationalism }` — the Confederation JE *exists only in the pre-national era* and naturally retires itself when the world moves on. Compare with the vanilla habit of tech gates that *open* content; here a tech gate *closes* it.
2. **Conditional sub-content on your laws:** its `immediate` adds `carlsbad_decrees_journal` only if you run `law_outlawed_dissent`/`law_censorship` — reactionary Germanies get the censorship sub-arc, liberal ones don't.
3. **Its monthly pulse mixes an event roll with a weighted effect roll:**

```paradox
# common/journal_entries/expand_journal.txt (deutsch_bundestag)
on_monthly_pulse = {
    random_events = {
        100 = 0
        50 = joi_flavor_expand.3        # Frankfurt Parliament, expected ~3 months
    }
    effect = {
        random_list = {
            25 = { }                     # nothing
            50 = { ... create Heinrich von Gagern ... }
            50 = { ... create Johann Gustav Droysen ... }
            50 = { ... create Friedrich Daniel Bassermann (PRU only) ... }
            50 = { ... create Eduard Simson ... }
        }
    }
}
```

   Each agitator branch is double-guarded — a per-country `deutsch_radical_agitator` variable (one agitator per country) *and* a per-person global (`deutsch_radical_first_number` etc., so each historical figure exists once in the world) — and gated on `has_technology_researched = nationalism`, so the radicals appear exactly when the JE is about to become obsolete. Each spawn is a full biographical `create_character` (name, culture, religion, birth date, traits, ideology) plus `add_radicals = { value = 0.1 }` — the 1848 generation arrives with a bang.
4. **Options escalate along country rank.** The Frankfurt follow-ups in `joi_flavor_expand.txt` use option triggers plus rank-weighted AI: joi_flavor_expand.8's interventionist option carries `ai_chance = { base = 10 modifier = { trigger = { country_rank >= rank_value:great_power } add = 200 } }` and costs `add_radicals = { value = 0.2 }` for North German countries, while the constitutional option `activate_law = law_type:law_census_voting` — AI great powers drive unification, AI minors take the safe reform.

**Why it's good design:** one JE serves ~30 countries with per-country divergence coming from laws, rank, and tag checks rather than 30 copies; historical characters emerge probabilistically inside a plausible window instead of on a fixed date; and the arc cleanly self-terminates on the `nationalism` tech watershed.

---

## 6. Localization quality — what "shipped prose" looks like

The mod's English is not placeholder text. From `localization/english/gbr/british_journal_entries_l_english.yml`:

```yaml
stabilize_british_empire:0 "Rule, Britannia!"
stabilize_british_empire_reason:0 "Since the #bold Congress of Vienna in 1815#!, [ROOT.GetCountry.GetName] has flourished as a global power... Beneath the radiant glow of the #bold Pax Britannica#!, our once-formidable rivals—from [SCOPE.sCountry('FRA_scope').GetName] to [SCOPE.sCountry('SPA_scope').GetName]...—have faded into obscurity... the world is bound together by our [concept_market]..."
stabilize_british_empire_complete_1_tt:0 "Achieve at least 50 [concept_relations] with 5 Canadian [concept_subject]s.\nIf insufficient subjects exist, this cannot be completed!"
```

Conventions on display, all worth copying:

- **Formatting markup used deliberately:** `#bold ... #!`, `#variable`, `#G`(green), `@green_checkmark!`/`@information!` icon tags — the same vocabulary vanilla loc uses.
- **Dynamic text everywhere:** `[ROOT.GetCountry.GetName]`, `[ROOT.GetCountry.GetRuler.GetPrimaryRoleTitle]`, saved-scope lookups `[SCOPE.sCountry('BUR_scope').GetName]` — text survives alt-history (a republic reads "President", subject names update).
- **Game concepts linked** (`[concept_market]`, `[concept_relations]`, `[concept_subject]`) so terms are hoverable in-game.
- **Goal tooltips state the failure condition too:** "If insufficient subjects exist, this cannot be completed!" — honest about dead ends.
- **Event bodies use the vanilla three-part structure** (`.t` title / `.d` summary / `.f` flavor quote): `joi_flavor_gbr.1.f` quotes "Rule, Britannia!" verse for the Pax Britannica event; `.a`/`.b` option texts are short in-voice lines ("Rule, Britannia!", "God Save the [ROOT.GetCountry.GetRuler.GetPrimaryRoleTitle]...").
- **Chinese and English trees are structurally identical** (41 files each, same subfolders, same keys) — parity is maintained per-file, not as an afterthought.

---

## 7. Conventions worth replicating

- **Prefix everything.** Files, on_actions, scripted effects, variables, modifiers all start `joi_` (or a system name like `headlines_`). Zero collision risk with vanilla or other mods.
- **One namespace + one file + one loc subfolder per country arc.** `events/joi_flavor_gbr.txt` ↔ `localization/english/gbr/gbr_events_l_english.yml` + `british_journal_entries_l_english.yml`, mirrored under `localization/simp_chinese/gbr/`. Loc keys follow vanilla exactly (`joi_flavor_gbr.1.t/.d/.f/.a`), and the English is real prose with vanilla formatting markup — `#bold`, `#variable`, `[concept_market]`, scope interpolation like `[SCOPE.sCountry('FRA_scope').GetName]` (see `gbr_events_l_english.yml`).
- **Variables end in `_var`; once-only flags read as sentences** (`first_economic_crisis_ended`, `edward_vii_heir_var`, `house_of_romanov_hannover`). Timed variables (`years = 20`, `months = 51`) replace manual cleanup.
- **`REPLACE_OR_CREATE:` for single-entry overrides** (38 uses in journal_entries alone, plus company_types and state_traits):

```paradox
# common/journal_entries/00_peoples_springtime_je.txt — rewrites ONE vanilla JE
REPLACE_OR_CREATE:je_springtime_of_the_peoples = { ... }
# common/state_traits/...:
REPLACE_OR_CREATE:state_trait_lorraine_ironfield = { modifier = { building_iron_mine_throughput_add = 0.25 } }
```

  Dramatically better patch-compatibility than copying whole vanilla files.
- **Empty-file deletion:** vanilla content is removed by shipping a same-named file containing only `#nothing` (`common/journal_entries/00_canada_australia.txt`, `common/decisions/manifest_destiny.txt`) — replacements then live under the mod's own filenames (`common/decisions/canada_australia.txt`).
- **Same-filename event overrides only where surgical edits are unavoidable:** `events/russia_events.txt` and `events/victoria_events.txt` shadow the vanilla files of the same name/namespace to rewrite specific vanilla events (Tsar succession chain, Victoria flavor).
- **Non-destructive pulse hooks:** the mod's own `on_monthly_pulse_country` block adds only `random_events` (with a `25 = 0` no-event entry and weight-1–2, once-only entries) and `on_actions` wrappers (`joi_gbr_monarchy_action`, `joi_pru_monarchy_action`, `joi_add_law_a_action`) — never a second `effect` block on a vanilla on_action, exactly as `game/common/on_actions/_on_actions.md` prescribes.
- **`on_game_started` for world setup** rather than history-file edits where possible (`joi_code_on_actions.txt`): 5-year character-death immunity for all IG leaders ("Memento Mori"), Wellington made immortal, start-date **amendments** applied per culture group (`amendment_landwehr_system` for German-culture armies, `amendment_family_register` for East Asian economies), a Dutch admiralty company created with a pre-built 5-level shipyard it owns.
- **Deterministic historical succession via monthly on_action:** heirs (Edward VII → George V; Wilhelm I → Friedrich III → Wilhelm II) are created by `game_date` + ruler-template checks with `_heir_var` once-flags, all inside law/tag guards (`has_law_or_variant = law_type:law_monarchy`, `c:GER ?= this` + `has_variable = this_is_formed_by_prussia`) — history stays on rails while laws and revolutions can legitimately derail it.
- **Game rules as feature switches** for every opt-in system (`common/game_rules`): `headlines_minor_events` (3 verbosity levels), `berlin_conference_rules`, `flavor_functional_decisions_rules`, `victorian_century_ai_enhancement_rules` (3 tiers), `invest_existing_buildings_only`, `economic_crisis_rules`.

### Decisions play two distinct roles

1. **Player utility toggles** (`joi_flavor_decisions.txt`): pairs like `joi_disable_private_investment` / `joi_enable_private_investment` just add/remove a modifier. All of them are `is_player = yes`, `ai_chance = { value = 0 }`, and double-gated (both `is_shown` *and* `possible`) behind the game rule with an honest warning tooltip:

```paradox
# common/decisions/joi_flavor_decisions.txt
is_shown = {
    is_player = yes
    custom_tooltip = {
        text = is_single_player_games_tt
        has_game_rule = enable_flavor_functional_decisions
    }
}
...
ai_chance = { value = 0 }
```

   This is how the mod ships "cheaty" quality-of-life controls without contaminating AI behavior or multiplayer defaults.

2. **Flavor decisions with real gates** (`joi_gbr_decisions.txt`): `direct_rule_of_malaya` requires `institution_investment_level = { institution = institution_colonial_affairs value >= 2 }`, checks a treaty situation via globals, transfers the states with `set_state_owner`, and is once-only by variable. Its AI weighting starts *negative* and is argued upward by capability: `ai_chance = { value = -10  if = { limit = { produced_bureaucracy > 1000 } add = 10 }  if = { limit = { has_technology_researched = monitor_tech } add = 20 } }` — the AI takes it only once it can actually administer the acquisition. Compare vanilla's war-time zeroing pattern in `09-design-and-balance.md` §3.

---

## 8. Techniques vanilla doesn't use

1. **Self-registering fake DLC.** The mod ships `dlc/dlc_vc/dlc_vc.dlc`:

```paradox
name = "Victorian Century"
path = "dlc/dlc_vc"
steam_id = "3219394272"
affects_save_compatibility = yes
```

   plus `dlc_metadata/vc_dlc_metadata.txt` (`dlc_vc = { type = minor }`) and a `dlc_vc.dlc.json` with display name/description. Every mod event then declares `dlc = dlc_vc` (all of `joi_flavor_gbr.txt`, `joi_great_man.txt`…). Result: the mod appears as an enabled "DLC" in-game, its content is cleanly tagged and toggleable as a set, and event headers self-document their origin. The `dlc_vc_desc` loc key doubles as an in-game about page with the mod's Discord link.
2. **The headlines/newspaper feed** (§4) — `post_notification`-based world news with a verbosity game rule.
3. **A recurring global boom-bust cycle** (§3) — chained, contagious, cooldown-gated crisis JEs. Vanilla ships isolated economic-crisis JEs (`game/common/journal_entries/06_economic_regeneration.txt`, `05_the_grand_collapse.txt`) but no repeating world system.
4. **Mass scripted-button UX** — ~366 buttons vs vanilla's handful: JEs become interactive dashboards ("enforce Doctrine of Lapse", "convene the conference") instead of passive checklists; each button once-only via variable, with `ai_chance = { value = 100 }` so the AI presses them too.
5. **Amendment-system content at scale** — 42 amendment types, some applied at game start per culture group (§7), effectively giving vanilla laws regional personality without new law types.
6. **Lobby-visible campaign JEs** — `is_shown_in_lobby` on the big arcs (`stabilize_british_empire`, `railway_mania`, `deutsch_bundestag` in `expand_journal.txt`) advertises each nation's content on the country-select screen before the player commits.
7. **Guaranteed-career historical characters** — `set_career_length = { years = 30 random_range = { 1.0 1.5 } }` (Mill), `set_character_immortal = yes` (Wellington) to keep story-critical people alive through their arcs; and JE-pulse `random_list` agitator spawning so 1848 Germany reliably produces Gagern/Droysen/Bassermann/Simson with full biographical data (`create_character` with historical names, birth dates, traits) without scripting a fixed date (`expand_journal.txt`, deutsch_bundestag `on_monthly_pulse`).
8. **Cross-file JE↔event↔button systems keyed on variables** — the mod's standard glue is a small vocabulary of globals (`great_power_cause_1st_crisis_var`, `choose_british_empire_act`, `bic_indepedence_become_bht_var`) that JEs set, events read, buttons flip, and the headlines system reports. Loose coupling keeps 437 JEs and 708 events from ever referencing each other's internals directly.

---

## Common pitfalls (visible even in this high-quality mod — avoid repeating them)

- **Full-file event overrides** (`russia_events.txt`) break whenever a patch touches the vanilla file; prefer `REPLACE_OR_CREATE:` (which the mod itself uses elsewhere) or on_action redirection when possible.
- **Empty `trigger = { }` blocks** on directly-triggered events (`joi_flavor_gbr.31`) are harmless but mean no revalidation; if the event could arrive late (delays, queues), give it a real trigger or `cancellation_trigger` (see `09-design-and-balance.md` §7).
- **Literal durations** (`years = 5`) instead of vanilla's script-value constants (`days = normal_modifier_time`) — works, but loses the single tuning point and the `display_*` loc helpers.
- **Copy-pasted if-chains** — the five near-identical crisis-JE lookups in `joi_flavor_gbr.84` (`first_` … `fifth_economic_crisis`) belong in a scripted effect; the mod uses scripted effects heavily elsewhere (13 files), so be consistent.
- **`weight = 100000`** on JEs is a sledgehammer; it wins "always on top" but two mods doing it fight each other. Vanilla's crisis ceiling is 10000 (`je_springtime_of_the_peoples`).
- **Profanity in identifiers** (`fucking_economic_crisis_comming`) — variable names leak into error logs and debugging sessions; keep them professional.

## Checklist (adopting Victorian Century's playbook for a new mod)

- [ ] Unique prefix on every file, namespace, variable, modifier, on_action, scripted effect.
- [ ] Per-arc organization: one event file + one JE file + one loc subfolder (per language) per country/system; loc keys `namespace.N.t/.d/.f/.a`.
- [ ] Vanilla touched only via: `REPLACE_OR_CREATE:` single entries, `#nothing` empty-file deletions, or wrapper `on_actions` appended to pulses — never a second `effect` on a vanilla on_action.
- [ ] Big campaign JEs: `is_shown_in_lobby`, `progressbar` with variable counters, sub-JEs feeding a parent counter via `change_variable`, claims granted by the JE that demands the conquest.
- [ ] Every JE: `complete`/`fail`/`timeout`/`invalid` all handled; AI resolution path included (`on_invalid` + `hidden_effect` event); full vs consolation rewards ≈ 4:1.
- [ ] Repeatable world systems: global cooldown variable (VC standard: 20 years), game-rule off-switch, `is_ai = no` on player-facing notification loops, contagion/pacing via globals rather than per-country duplication.
- [ ] Story-critical characters protected: `set_career_length` / immortality flags; heirs via dated on_action checks with `_var` once-flags inside law/tag guards.
- [ ] Player agency surfaces: scripted buttons on JEs (once-only variable + `ai_chance = 100`), branch variables set by conference-style choice events.
- [ ] All shipped languages in full parity (VC: english + simp_chinese mirror trees, 41 files each); English written as real prose with `#bold`/concept markup, not placeholder text.
- [ ] Optional: fake-DLC registration (`dlc/`, `dlc_metadata/`, `dlc = <id>` on events) for tagged, self-documenting content and an in-game about page.
