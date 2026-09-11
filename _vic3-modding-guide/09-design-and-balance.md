# 09 — Content Design & Balance Principles

**Read this file when:** you are designing NEW events/journal entries/decisions and need to know what "good" looks like — how often content should fire, how big rewards/penalties should be, how to structure options, and how to avoid frustrating the player. For syntax see `03-events.md` and `05-journal-entries-and-decisions.md`; for chain wiring see `04-event-chains-and-triggering.md`; for modifier plumbing see `06-modifiers.md`.

Everything below is extracted empirically from vanilla Victoria 3 (`game/events`, `game/common/on_actions`, `game/common/script_values/event_values.txt`, `game/common/static_modifiers`) and the Victorian Century mod (`mod/3219394272`, see `10-case-study-victorian-century.md`). Every claim cites at least one real file.

---

## 1. Trigger timing — fire at the right moment

Vanilla almost never gates an event on date alone. The standard is a **stack of 2–5 gates** combining *systemic state* (laws, tech, economy) with *situation* (characters, buildings, IG status), so the event reads as a consequence of the player's world, not a timer.

Observed gate types, each with a real example:

| Gate | Example | Source |
|---|---|---|
| Law state | `NOT = { has_law_or_variant = law_type:law_worker_protections }` — factory fire only under unregulated industry | `game/events/industrial_accidents_events.txt` (event .1) |
| Technology | `has_technology_researched = rotary_valve_engine` before Lord Kelvin appears | `mod/3219394272/events/joi_great_man.txt` (joi_great_man.1) |
| Economic condition | grain `market_goods_pricier > 0.25` activates the Corn Laws JE | `game/common/journal_entries/00_corn_laws.txt` (`possible`) |
| Political situation | `ig:ig_landowners = { is_powerful = yes is_in_government = yes }` (same JE) | same file |
| Date window, combined | `game_date >= 1875.1.1` **plus** ruler template, IG anger, low legitimacy | `game/common/on_actions/00_code_on_actions.txt` (below) |
| Building/PM present | `has_building = building_textile_mill` and not on `pm_traditional_looms` | `industrial_accidents_events.txt` |
| Character available | `any_scope_character = { has_role_of_type = politician is_ruler_of_own_country = no ... }` | same file |
| Territory | `owns_entire_state_region = STATE_LOWLANDS` (Kelvin lives in Glasgow) | `joi_great_man.txt` |
| Rank / war state | `country_rank < rank_value:great_power` as JE fail; `is_at_war` zeroing decision ai_chance | mod `british_empire.txt`; `game/common/decisions/00_decisions.txt` |

A fully worked example of *historical event with systemic justification* — the coup of Abdulaziz fires on a date **and** only if the Ottomans are actually in the crisis that historically caused it:

```paradox
# game/common/on_actions/00_code_on_actions.txt (on_monthly_pulse_country effect)
if = { # Coup of Abdulaziz, Murad becomes the ruler
    limit = {
        has_dlc_feature = ip3_content
        c:TUR ?= this
        ruler ?= { has_template = tur_abdulaziz_osmanoglu_template }
        game_date >= 1875.1.1
        c:TUR ?= {
            ig:ig_intelligentsia ?= { ig_approval <= -5 }
            ig:ig_armed_forces ?= { ig_approval < 0 }
            legitimacy < 65
        }
    }
    trigger_event = ottoman_monarchs.1
}
```

And the Corn Laws JE — a *systemic* trigger that happens to reproduce history when the player plays historically:

```paradox
# game/common/journal_entries/00_corn_laws.txt
possible = {
    market_capital.market = {
        mg:grain = { market_goods_pricier > 0.25 }   # bread actually expensive
    }
    OR = {
        has_law_or_variant = law_type:law_protectionism
        has_law_or_variant = law_type:law_mercantilism
    }
    ig:ig_landowners ?= { is_powerful = yes is_in_government = yes }
}
complete = { has_law_or_variant = law_type:law_free_trade }
```

**Date gates in vanilla events are historical anchors, not pacing.** A tally of `game_date`/`year` comparisons across `game/events` shows ~100 uses, all tied to specific history (`>= 1850.1.1`, `< 1880.1.1`, `>= 1904.8.12`, etc.), always alongside other conditions. There is no generic "not in the first N months" guard in vanilla event triggers — early firing is instead prevented by tech/law/economy gates that are naturally false in 1836 (e.g. Springtime of the Peoples requires `egalitarianism` researched somewhere in Europe, `00_peoples_springtime_je.txt`; Victorian Century's great men need mid-game techs plus `game_date >= 1848–1856`).

**"Slightly off-cycle" repeat timers** are a deliberate trick — note the vanilla comment:

```paradox
# game/events/industrial_accidents_events.txt (Triangle Shirtwaist fire)
set_variable = {
    name = triangle_shirtwaist_factory_fire
    value = yes
    months = 51 # keep near but slightly off 4 year intervals
}
```

### Once-only and cooldown patterns

Three coexisting mechanisms; use the one that matches the scope:

1. **`cooldown = { days = <constant> }`** on the event — per-country re-fire delay. Tally over all of `game/events`:

| Cooldown constant | Days | Uses in vanilla events |
|---|---|---|
| `normal_modifier_time` | 1825 (5 y) | 510 |
| `stupidly_long_modifier_time` | 18250 (50 y) | 263 |
| `very_long_modifier_time` | 7300 (20 y) | 227 |
| `never_fire_again_modifier_time` | 73000 (200 y) | 217 |
| `long_modifier_time` | 3650 (10 y) | 94 |
| `short_modifier_time` | 913 (2.5 y) | 56 |
| literal values (`180`, `365`, `months = 3`…) | — | ~15 total |

   (Constants defined in `game/common/script_values/event_values.txt`.) Rule of thumb from these numbers: a repeatable flavor event gets a 5-year cooldown; a "should really only happen once per campaign" event gets 50 years or `never_fire_again`.

2. **Country variable set in `immediate`** — survives even if cooldown would allow a re-fire, and can encode nuance (the 51-month example above). Pattern: trigger has `NOT = { has_variable = X }`, `immediate` has `set_variable = X`. Victorian Century uses this for every one of its 22 "great man" events (`joi_great_man.txt`: `NOT = { has_variable = great_man_1_var }` → `set_variable = great_man_1_var`).

3. **Global variable** — for world-once events: `NOT = { has_global_variable = peoples_springtime_happened }` (`00_peoples_springtime_je.txt`), or Victorian Century's shared crisis cooldown `set_global_variable = { name = economic_crisis_colddown_var years = 20 }` (`common/journal_entries/economic_crisis.txt`). Note that variables can carry their own expiry (`years = 20`, `months = 51`) — cheaper than remembering to clean up.

**Decisions** use the same layering with different keywords: `is_shown` = broad identity gate, `possible` = the real conditions, and once-only via `hidden_trigger = { NOT = { has_variable = revive_olympics_decision_taken } }` + `when_taken = { set_variable = ... }` (`game/common/decisions/00_decisions.txt`, Olympics).

---

## 2. Pacing — pulses, weights, and expected frequency

### How the pulse system actually works

From `game/common/on_actions/_on_actions.md` (read it — it is the authoritative doc): code fires `on_monthly_pulse_country`, `on_half_yearly_pulse_country`, `on_yearly_pulse_country` (plus state/character variants). Inside, a `random_events` block **picks at most ONE event per tick**:

- `chance_to_happen = 25` — % chance the block does anything at all this tick.
- `20 = my_event.1` — relative weight among *currently valid* events (each event's own `trigger` is checked at selection time).
- `100 = 0` — a weighted "no event" entry; per the doc, "Good for making sure that rare events don't always fire just because every other possible event is invalid."

Vanilla staggers its many yearly on_actions with `delay` so a country doesn't get five popups on January 1st:

```paradox
# game/common/on_actions/00_code_on_actions.txt (~line 1829, inside on_yearly_pulse_country)
on_actions = { # delay ensures events won't fire simultaneously
    ryukyu_rivalry_coin_toss
    kamehameha_coin_toss
    on_yearly_events
    ep1_misc_yearly_events
    delay = { days = 1 }
    russian_monarchy_yearly_events
    ...
    delay = { days = 8 }
    historical_agitators_yearly_events
    famine_yearly_events
    delay = { days = 13 }
    ...
    delay = { days = 90 }
    japan_yearly_events
}
```

### Observed configurations (all real)

| Pulse | chance_to_happen | Typical weights | Source |
|---|---|---|---|
| Generic yearly (`on_yearly_events`) | 65 | mostly 10–20, range 1–100 (outlier: `300 = historical_agitators.8`) | `00_on_actions_yearly.txt` |
| Generic half-yearly | 65 | 1–50 | `00_on_actions_half_yearly.txt` |
| Country flavor pulses (Japan, exiles, lobbies…) | 20–50 | 5–20 flat | `00_on_actions_yearly.txt` |
| Rare disaster: Krakatoa | **3** | single event, weight 1 | same |
| Rare disaster: Tunguska | **10** | single event, weight 1 | same |
| Springtime of Peoples seed | **20** | single event, weight 1 | same |
| Monthly flavor (Garibaldi) | 30 | 30/30/2/1 | `00_on_actions_monthly.txt` |
| Monthly with explicit no-event (Japan monarchy) | 50 | `50 = 0`, `50 = shogunate.8` | same |
| JE-scoped monthly pulse (Corn Laws) | — | `100 = 0` + 10/10/10 | `00_corn_laws.txt` |
| JE-scoped monthly pulse (VC economic crisis) | — | `100 = 0` + six × 10 | mod `economic_crisis.txt` |
| VC addition to global monthly pulse | — | `25 = 0` + ~26 events at weight 1–2, all once-only | mod `common/on_actions/joi_code_on_actions.txt` |
| Effect-based coin toss (IG petitions) | — | `random_list = { 1 = {...fire} 9 = {} }` yearly + 10-year cooldown var | `00_code_on_actions.txt` (~line 1662) |

That last row is a third pacing idiom worth knowing: a yearly `random_list` with 1-in-10 odds plus `set_variable = { name = gov_petition_cooldown years = 10 }` = "on average once a decade, hard-capped at once a decade."

### Practical frequency table

The math: per tick, `P(specific event) = (chance_to_happen/100) × w / Σ(weights of all currently-valid entries incl. the 0-entry)`. Expected waiting time = `1/P` ticks (geometric distribution — the median is ~30% sooner than the mean).

**For a dedicated pulse or JE `on_monthly_pulse` you control the denominator, so you can compute exactly.** With the vanilla-standard `100 = 0` baseline and one event of weight `w` on a *monthly* pulse:

| Want the event roughly every… | Use weight (vs `100 = 0`) | Expected wait |
|---|---|---|
| ~3 months | `50` | (100+50)/50 = 3 months |
| ~6 months | `20` | 6 months |
| ~1 year | `10` | 11 months — the vanilla Corn Laws / VC crisis-pulse standard |
| ~2 years | `5` | 21 months |
| ~4+ years | `2` | 51 months |

With several events sharing the pulse, each event's wait stretches accordingly (Corn Laws: three weight-10 events vs `100 = 0` → any event ≈ every 4.3 months, a *specific* one ≈ every 13 months).

On a *yearly* pulse with a single event, `chance_to_happen` **is** the pacing knob, and vanilla's choices are good anchors: `20` = "fires ~5 years in on average" (Springtime seed), `10` = ~once a decade (Tunguska), `3` = ~once per 33 years, i.e. "maybe once per campaign, maybe never" (Krakatoa).

**Honest limits of this math:**
1. In shared pulses like `on_yearly_events` the denominator is the sum of *all valid* entries, which varies per country and per date. That pulse has ~150 entries; for an industrialized great power several dozen are typically valid simultaneously, so a weight-20 entry there fires perhaps once in 20–50 years — and that is intentional. Generic-pulse events are seasoning, not systems. Do not put must-see content there.
2. Only one event per `random_events` block per tick fires, so adding your event to a vanilla pulse slightly dilutes every vanilla event in it.
3. Weights are relative — `10` in a small pulse fires more often than `100` in a crowded one. Always compute against the actual block.

If your content must fire reliably, give it its own on_action (with a `trigger`) or a JE-scoped pulse instead of joining `on_yearly_events`, and hook it non-destructively:

```paradox
# the append-safe pattern, quoted from game/common/on_actions/_on_actions.md
some_vanilla_on_action = { on_actions = { some_modded_on_action } }
some_modded_on_action = { effect = { some_fun_modding_effect = yes } }
```

Victorian Century follows exactly this: its `on_monthly_pulse_country` block adds only `random_events` + `on_actions = { joi_gbr_monarchy_action ... }` wrappers, never a second `effect` block (`joi_code_on_actions.txt`). See `04-event-chains-and-triggering.md` for full wiring.

---

## 3. Choice design

### Shape

- **Two options is the vanilla norm.** Random sample of 25 vanilla event files: average 2.0 options/event (min 1.0 `misc_unifications.txt` — notification beats; max 4.3 `french_pretenders.txt` — branching political drama). Victorian Century matches: ~708 events / ~1,350 options ≈ 1.9.
- **Exactly one option carries `default_option = yes`** — it fires on event timeout (`duration` expiry) and should be the status-quo/safe choice, not the spicy one. Vanilla `duration = 3` is near-universal; Victorian Century drops to `duration = 1` for urgent crisis beats (`joi_flavor_gbr.83/.84`).
- **Conditional options** (option-level `trigger`) add a third path only when it makes sense: the Dyeworks accident offers a Trade Unions option only if `ig:ig_trade_unions = { is_insurrectionary = no is_revolutionary = no }` (`industrial_accidents_events.txt` .2); VC's great-man events hide the "fund his research" option once the tech is already researched (`joi_great_man.txt`).

### Trade-off patterns actually used

| Pattern | Real example |
|---|---|
| Radicals now vs IG power shift | Triangle Shirtwaist: option A = `medium_radicals` (lower strata, state) **and** guilty IG gets `ig_gaining_support`; option B = retire the guilty character, his IG gets `ig_power_challenged` (−3 approval, −10% pol str) — `industrial_accidents_events.txt` |
| Pay money vs eat radicals | Corn Laws bread crisis (below) |
| Which class do you please | VC Imperial Conference: Federation = `add_loyalists 0.1` to Industrialists + Petty Bourgeoisie; Dominion Autonomy = same to Intelligentsia + Trade Unions — `mod/events/joi_flavor_gbr.txt` (.31) |
| Short buff vs long investment | VC great men: free 5-year national modifier **or** `add_treasury = -100000` + `add_technology_progress = { progress = 4800 technology = electrical_generation }` — `joi_great_man.txt` |
| Empower vs suppress a movement | Corn Laws agitator: boost the liberal movement, or please aristocrats (`add_loyalists value = large_radicals pop_type = aristocrats`) and hamstring the agitator with a debuff modifier — `corn_laws_events.txt` (.2) |

The money-vs-radicals archetype in full:

```paradox
# game/events/corn_laws_events.txt (corn_laws.4 — "Poor people struggle to buy bread")
option = {                       # intervene: pay for it
    name = corn_laws.4.a
    add_modifier = { name = temporary_minimum_wages days = normal_modifier_time }
}
option = {                       # do nothing: political cost
    name = corn_laws.4.b
    default_option = yes
    add_radicals = { strata = lower value = medium_radicals }
}
```

### `ai_chance` conventions

724 occurrences across 115 vanilla event files. Observed grammar and values:

- **`base = 10` on every option** = "AI picks uniformly at random" — by far the most common (whole files of `agitators_events` use it).
- **Asymmetric splits** for flavored outcomes: `25/75`, `33/66` (`game/events/1848.txt`).
- **`base = 0` or `1`** on options that exist for player expression but the AI should (almost) never take (`agitators_events/algeria_events.txt`).
- **Modifiers adjust for context.** The regicide option checks whether the AI would be shooting itself in the foot:

```paradox
# game/events/1848.txt (1848.1.a — assassinate the monarch)
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
# ...option b (spare him): ai_chance = { base = 75 }
```

- Victorian Century's variant for "great powers always take this": `base = 10` + `modifier = { trigger = { country_rank >= rank_value:great_power } add = 200 }` (`joi_flavor_expand.txt` ~line 982), and `ai_chance = { value = 100 }` on JE scripted buttons so the AI presses them (`joi_great_britain_buttons.txt`).
- **Decisions**: `ai_chance` is a script value; vanilla multiplies by 0 during wars so the AI does not take flavor decisions mid-conflict: `if = { limit = { OR = { is_diplomatic_play_committed_participant = yes is_at_war = yes } } multiply = 0 }` (`game/common/decisions/00_decisions.txt`, Olympics + land reclamation).

---

## 4. Reward & penalty magnitudes

**Never hardcode magnitudes that vanilla has a script value for.** Everything below is from `game/common/script_values/event_values.txt` unless noted.

### Radicals / loyalists (fraction of affected pops)

| Script value | Amount | Uses in vanilla events | Use for |
|---|---|---|---|
| `very_small_radicals` | 0.01 | 5 | trivial |
| `small_radicals` | 0.02 | 373 | minor upset |
| `medium_radicals` | 0.05 | 491 | **the default event consequence** |
| `large_radicals` | 0.1 | 193 | serious, usually one strata/state |
| `very_large_radicals` | 0.2 | 77 | crisis-tier |
| `huge_radicals` | 0.3 | 3 | almost never |

The same values are passed to `add_loyalists`. Scope the effect to sharpen the story: `strata = lower`, `pop_type = laborers`, `interest_group = ig:ig_industrialists`, or `add_radicals_in_state` (all patterns visible in `corn_laws_events.txt` and `joi_flavor_gbr.31`). Country-wide unscoped `add_loyalists = { value = 0.1 }` is reserved for campaign milestones (VC `first_economic_crisis.on_complete`, vanilla Corn Laws repeal); consolation prizes are quartered: `0.025` on timeout/fail (`economic_crisis.txt`).

### Money — % of GDP, not flat numbers

Vanilla events cost/give money two ways:

1. **Timed expense modifier** (most common): a static modifier with `country_expenses_add = 1` (e.g. `supplying_colonists`, `game/common/static_modifiers/105_modifiers.txt`) attached with a GDP-scaled multiplier:

```paradox
# game/events/africa_colonial_events_03.txt
add_modifier = {
    name = supplying_colonists
    days = normal_modifier_time
    multiplier = money_amount_multiplier_medium   # scales the weekly expense
}
```

2. **Flat `add_treasury`** — rare (28 uses total in vanilla events), for fixed historical sums (`add_treasury = 100000`, Alaska-scale purchases) or tiny bribes (±1,000…15,000). Victorian Century uses flat `-100000` for its great-man tech investments — acceptable because those events are Great-Britain-tier gated.

The multipliers (from `event_values.txt`, all with `min = 100` so minors still feel something):

| Script value | Size | Vanilla event uses |
|---|---|---|
| `money_amount_multiplier_very_small` | 0.015% of GDP | 18 |
| `money_amount_multiplier_small` | 0.025% of GDP | 57 |
| `money_amount_multiplier_medium` | 0.05% of GDP | 51 |
| `money_amount_multiplier_large` | 0.1% of GDP | 10 |
| `money_amount_multiplier_more_large` | 0.2% of GDP | 0 (defined, unused in events) |
| `money_amount_multiplier_very_large` | 0.5% of GDP | 3 |

GDP scaling means the same event is fair for Belgium and for Britain. Copy this pattern for any new mod content that touches money.

### IG approval — small numbers, named modifiers

All event-driven IG opinion swings are named static modifiers in `game/common/static_modifiers/03_event_ig_opinion_modifiers.txt`, applied with `days = normal_modifier_time` (5 y) typically. Observed distribution over that whole file (~100 modifiers):

| `interest_group_approval_add` | Meaning | Examples |
|---|---|---|
| ±1 | token | `ig_gaining_support` (+1, plus +15% pol str), `rejected_mission` (−1) |
| ±2 | standard minor | `slowed_down_production`, `absolved_of_responsibility` |
| ±3 | standard major — **most common value in the file** | `ig_power_challenged` (−3, −10% pol str), `hawkish_neighbor_relations` (+3) |
| ±4 to ±5 | strong | `ig_furious_at_cowardice` (−5), `ig_powerbrokers` (+5, +15% pol str), `deporting_disloyal_igs` (−5, −20% pol str) |
| −7 to −10 | extreme, near-unique | `ig_unappeased` (−7), `ig_mass_arrests` (−10, −15% pol str) |

Note the pairing convention: approval changes frequently ride with `interest_group_pol_str_mult` ±0.1–0.25 (occasionally `interest_group_pop_attraction_mult` ±0.15–0.2) in the same modifier — anger *and* weaken, or please *and* strengthen.

### Prestige

Events grant prestige via timed modifiers, not a direct effect. Across `game/common/static_modifiers`: `country_prestige_add` clusters at **+15/+20/+25/+50** (50 is the single most common positive value, 15 uses) with −10…−100 for disasters; `country_prestige_mult` clusters at **±0.05–0.25** (0.05 most common: 35 uses; nothing above 0.3). Pick `add` for flat flavor rewards, `mult` for rank-scaling states.

### Duration constants (use these, never raw day counts)

`very_short` 1 y · `short` 2.5 y · `normal` 5 y · `long` 10 y · `moderately_long` 15 y · `very_long` 20 y · `stupidly_long` 50 y · `never_fire_again` 200 y — `event_values.txt`, which also ships `display_*` twins for showing the years in loc strings. **`normal_modifier_time` (5 years) is the default for both option-effect modifiers and event cooldowns.** Victorian Century writes the same magnitudes as literals (`years = 5`, `years = 10` — `railway_mania`: `add_modifier = { name = mania_railway_boom years = 10 }`); prefer the constants.

---

## 5. Escalation in chains — raise stakes step by step

### Vanilla walkthrough: Springtime of the Peoples

Files: `game/common/on_actions/00_on_actions_yearly.txt`, `game/common/journal_entries/00_peoples_springtime_je.txt`, `game/events/peoples_springtime.txt`, `game/events/1848.txt`.

1. **Quiet seed, low probability:** yearly on_action `springtime_of_peoples_yearly_events` = `chance_to_happen = 20`, single entry `1 = peoples_springtime.6` → expected ~5 years after its gates open. The seed event has `cooldown = { days = never_fire_again_modifier_time }` and its single option *hidden-effect propagates itself* to every other involved country with `trigger_event = { id = peoples_springtime.6 days = 1 }` — a continental wave from one spark.
2. **The JE raises the ceiling:** `je_springtime_of_the_peoples` (weight 10000, pinned, `timeout = 1095` — three years of pressure) creates national/liberal movements in `immediate_all_involved`, then runs an internal escalation clock the *player's counterplay controls*:

```paradox
# game/common/journal_entries/00_peoples_springtime_je.txt (on_monthly_pulse effect, trimmed)
if = {
    limit = {  # radicals suppressed AND leaderless?
        scope:radical_movement_scope ?= { political_movement_support <= 0.10 is_being_suppressed = yes }
        NOT = { any_interest_group = { leader = { has_ideology = ideology:ideology_radical } ... } }
    }
    change_variable = { name = springtime_timer_var add = 1 }
}
else = { set_variable = { name = springtime_timer_var value = 0 } }
### Event Pulse
random_list = {
    100 = { }
    10 = { trigger_event = peoples_springtime.3 }
    10 = { trigger_event = peoples_springtime.4 }
    10 = { trigger_event = peoples_springtime.5 }
}
```

3. **Pressure events during, not before:** the `100 = {}` vs `10/10/10` roll = a stakes-raising beat roughly once a quarter, only while the crisis lasts.
4. **Three distinct endings, each with a payoff event:** `complete` (liberal outcome: revolution happened or liberals in government + census/universal suffrage) → peoples_springtime.10; `fail` (movements crushed + `springtime_timer_var >= 12`) → .8 "The Revolution Vanquished"; `on_timeout` → .8 as well. Every exit fires a closure event — the chain never just disappears.
5. **A follow-up JE (`je_red_summer`) escalates further** with two competing `scripted_progress_bar`s (revolution vs counter-revolution) and victory/defeat events .7/.71/.8 — the resolution mechanic changes at the climax, not just the numbers.

Design lessons: rare seed → self-propagation → player-influenced timer → periodic pressure beats → guaranteed narrative closure on every exit path → climax with a different mechanic.

### Victorian Century walkthrough: Railway Mania → Economic Crisis

Files: `mod/3219394272/common/journal_entries/united_kingdom.txt` (railway_mania), `common/journal_entries/economic_crisis.txt`, `events/joi_flavor_gbr.txt` (.83–.91). Full tour in `10-case-study-victorian-century.md` §3.

1. **Opt-in boom:** `railway_mania` (GBR only; needs `railways` + interventionism/laissez-faire; `possible` = 75% of British homeland states have a railway *or* `year >= 1838`). While active Britain gets a boom modifier and every other railway country gets `railway_mania_others_modifier` for 10 years — the bubble is exported before it pops.
2. **Race against a visible clock:** `on_monthly_pulse` `effect` runs `change_variable = { name = railway_mania_var add = 1 }` against `goal_add_value = 120` with `progressbar = yes` — a literal 10-year countdown. Win = railway level ≥ 15, `occupancy >= 1`, `earnings >= 50` in 92% of British homeland states.
3. **Failure escalates instead of ending:** `on_fail` → `joi_flavor_gbr.83`, whose only option removes the global crisis cooldown, tags Britain `this_is_railway_mania_country`, applies a 5-year bust modifier, and previews the incoming avalanche with `show_as_tooltip = { add_journal_entry = { type = first_economic_crisis } }`.
4. **The crisis JE is a full system:** contagion to other great powers via globals; a JE monthly pulse rolling `100 = 0` + six weight-10 misery events (.85–.90); escape by GDP growth (progress bar goal = `root.gdp × 0.01`, minimum 1 year in crisis); `timeout = 1825`; `fail` when three great powers recover first; `invalid` on bankruptcy with `on_invalid = { add_radicals = { value = 0.05 } add_modifier = { name = declare_bankruptcy_during_economic_cirsis years = 5 } }`. **Every** exit sets `economic_crisis_colddown_var years = 20` — a global pacing valve — and sequels `second_…fifth_economic_crisis` unlock behind the previous `…_ended` global plus a game-rule off-switch.

Design lessons: boom before bust; failure converts to new content rather than a dead end; a shared global cooldown paces repeatable crises; full vs consolation rewards sit ~4:1 apart (0.1 vs 0.025 loyalists).

---

## 6. Player communication — telegraph consequences

- **`custom_tooltip` for anything script can't auto-describe.** Vanilla: `custom_tooltip = corn_laws_agitator_appears_tt` on both options of corn_laws.2 (an agitator spawn has no auto-tooltip). VC uses it pervasively — 81 uses in `joi_flavor_gbr.txt` alone — and wraps *JE goal triggers* in custom_tooltips so the journal shows "Achieve at least 50 relations with 5 Canadian subjects" instead of raw trigger soup (`british_empire.txt`, `stabilize_british_empire.complete`).
- **`hidden_effect` hides bookkeeping, never consequences.** Vanilla hides variable-setting, self-propagating `trigger_event`s, and mechanical cleanup *when the tooltip already says it in prose*:

```paradox
# game/events/industrial_accidents_events.txt (option .1.b)
option = {
    name = industrial_accident_events.1.b
    default_option = yes
    custom_tooltip = industrial_accident_events.1.b.tt   # tells the player in words
    hidden_effect = {
        scope:guilty_factory_owner = { retire_character = yes }  # the mechanic
    }
    scope:guilty_factory_owner_ig = {
        add_modifier = { name = ig_power_challenged days = normal_modifier_time }  # visible
    }
}
```

- **`show_as_tooltip` previews effects that happen elsewhere.** The Corn Laws JE `on_complete` shows the loyalist/modifier effects of the *event it triggers* so the journal tooltip is honest (`00_corn_laws.txt`); VC's crash event shows the incoming crisis JE (`joi_flavor_gbr.83`, §5 above).
- **JEs narrate their own state:** `status_desc` with `triggered_desc` branches, `custom_completion_header` / `event_outcome_completed_desc` / `event_outcome_failed_desc` (`00_peoples_springtime_je.txt` uses all of them), `progressbar` + `current_value`/`goal_add_value` for anything countable (VC uses these on nearly every campaign JE).
- **Default option = least surprising.** On `duration` expiry the game auto-picks `default_option`; vanilla consistently makes it the passive/status-quo choice (corn_laws.4 default = do nothing and eat radicals — not "spend money").

---

## 7. Anti-frustration patterns — kill stale content

- **`cancellation_trigger` on events** — 1,077 uses across vanilla events. The event silently dies if its subject became invalid between queueing and showing. Standard bodies: saved character died (`cancellation_trigger = { scope:guilty_factory_owner = { is_character_alive = no } }`, `industrial_accidents_events.txt`), saved scope missing (`NOR = { exists = scope:arguing_commander_one exists = scope:arguing_commander_two }`, `commander_events.txt`), situation resolved (`NOT = { has_journal_entry = je_springtime_of_the_peoples }`, `1848.txt`), pops gone (`NOR = { exists = scope:discriminated_culture_pop ... }`, `discrimination_events.txt`). **Any event whose `immediate` saves a scope should have one.**
- **JE `invalid` + `on_invalid` cleanup.** ACW entries invalidate when no Dixie-homeland states remain and `clear_variable_list = acw_dixie_states` in `on_invalid` (`game/common/journal_entries/00_acw_entries.txt`); VC invalidates the crisis JE on bankruptcy but still applies consequences in `on_invalid`; the Rule Britannia JE goes `invalid` for AI Britain after 1857 yet still resolves the arc via `on_invalid = { hidden_effect = { trigger_event = { id = joi_flavor_gbr.31 } } }` (`british_empire.txt`).
- **Every JE exit has a handler.** Vanilla JEs define `on_complete` / `on_fail` / `on_timeout` with closure events — a pinned JE must never vanish without feedback (`00_peoples_springtime_je.txt` fires peoples_springtime.8 from both fail and timeout).
- **`timeout =` bounds every open-ended crisis:** 1095 (3 y, Springtime), 1825 (5 y, VC crises), 4380 (12 y, ACW reincorporation).
- **Delayed events revalidate.** From `_on_actions.md`: an event fired with `delay` "will only successfully fire if it is valid both when the on_action is executed AND once the delay is complete" — so keep the real conditions in the event `trigger`, not only in the on_action.
- **`?=` everywhere a tag might not exist** (`c:TUR ?= this`, `ig:ig_landowners ?= { ... }`) — vanilla and VC both do this reflexively; a hard `c:XXX =` reference misbehaves when the country is dead.
- **Player/AI segregation:** VC's headline system runs only under `is_ai = no` (`headlines_on_actions.txt`); vanilla fires Emperor Norton only for `is_player = yes` (`00_code_on_actions.txt` ~1685). Don't run player-flavor loops on 200 AI countries.
- **Let players opt out of whole systems:** VC ships game rules (`common/game_rules`: `economic_crisis_rules`, `headlines_minor_events`, `berlin_conference_rules`…) checked via `has_game_rule = enable_economic_crisis` in the JE's `is_shown_when_inactive`.

---

## Common pitfalls

- Flat money amounts (`add_treasury = 5000`) in generic content — meaningless for Britain, ruinous for Serbia. Use the GDP multipliers via expense modifiers (§4).
- Weight math ignoring the `X = 0` entry, or omitting it entirely — without a no-event weight, your rare event fires *every* pulse whenever it's the only valid one (explicit warning in `_on_actions.md`).
- Adding a second `effect = {}` block to a vanilla on_action — a documented conflict; use the `on_actions = { wrapper }` append pattern instead (`_on_actions.md`, "MODDING INFO").
- One-sided options: an option that is strictly better with no cost. Every vanilla example above prices the good outcome in radicals, money, IG anger, or forgone opportunity.
- `default_option` on the aggressive/spending choice — timeouts then punish AFK players.
- Saved-scope events without `cancellation_trigger` — the classic "dead character gives a speech" bug.
- Once-only enforced *only* by cooldown — long campaigns re-fire it. Pair with a variable when it must truly be once.
- Date-only triggers — the event fires into a world state that no longer makes sense (player already reformed/collapsed). Always add systemic gates.
- Forgetting `is_ai = no` / `is_player` filters on player-facing-only notification content.
- Radicals above `large_radicals` (0.1) for routine events — vanilla uses 0.2+ only 80 times total, all crisis-tier.
- Escalation chains without closure events — a JE that silently disappears on fail reads as a bug to players.

## Pre-release balance checklist

- [ ] Every event: `trigger` gates cover tech/law/economy so it cannot fire absurdly in 1836; date gates only as historical anchors, never alone.
- [ ] Every event: once-only via variable, repeatable via a cooldown constant from `event_values.txt` — decided consciously, not defaulted.
- [ ] Every event with saved character/state/country scopes: `cancellation_trigger` present; `?=` used for optional tags.
- [ ] Pulse wiring: added via wrapper on_action (never a second `effect` on a vanilla on_action), `X = 0` entry present, weight chosen from the §2 frequency table and sanity-checked with `(chance/100)×w/Σweights`.
- [ ] Nothing that *must* be seen lives in a shared generic pulse; must-see content has its own on_action or JE pulse.
- [ ] Options: usually 2, max ~4; exactly one `default_option` (the passive one); every option has a cost or forgone benefit; conditional options guarded by option-level `trigger`.
- [ ] `ai_chance` on every option (base 10 = random; 0–1 = player-only flavor; 25/75-style splits for flavored outcomes; modifiers for context); decision `ai_chance` multiplied to 0 during wars.
- [ ] Magnitudes: radicals/loyalists from the six script values (default `medium_radicals`, scoped to strata/pop/IG/state); money via `money_amount_multiplier_*` expense modifiers; IG approval within ±1…±5 (±7/−10 reserved for once-per-mod extremes), paired with pol-str where thematic; prestige within vanilla clusters (add 15–50, mult 0.05–0.25).
- [ ] Modifier durations use the named constants; `normal_modifier_time` (5 y) unless there's a reason; nothing permanent unless `days = -1` is intentional.
- [ ] Chains: every JE exit (`complete`/`fail`/`timeout`/`invalid`) has an `on_*` handler with player feedback; crisis JEs have `timeout`; repeatable crises share a global cooldown variable (VC standard: 20 years); failure paths convert into content, not dead ends.
- [ ] Effects invisible to auto-tooltips explained with `custom_tooltip`; `hidden_effect` hides only bookkeeping; cross-JE/cross-event effects previewed with `show_as_tooltip`; countable goals get `progressbar`.
- [ ] Player-only spam filtered with `is_ai = no`; optional systems behind a game rule.
- [ ] Localization exists for every `.t/.d/.f`, option name, and custom_tooltip key, in every language folder you ship (see `03-events.md`).
