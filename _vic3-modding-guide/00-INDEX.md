# Victoria 3 Modding Guide — Index / Yönlendirme

> **TR:** Bu klasör, Claude Code ile Victoria 3 modu geliştirirken kullanılacak referans dokümanlarıdır. Herhangi bir moda kopyalanabilir (`_vic3-modding-guide` klasörünü olduğu gibi taşı). Ajanlar TÜM dosyaları değil, sadece yapılan işle ilgili dosyayı okumalıdır — aşağıdaki tablo bunun için var.

**For Claude Code agents — how to use this guide:**

1. **Do NOT read every file.** Find your task in the routing table below and read ONLY the matching file(s). Each file is self-contained and cross-references siblings when needed.
2. All content was **empirically verified against Victoria 3 v1.13.9 (Matcha)** game files (`C:\Program Files (x86)\Steam\steamapps\common\Victoria 3\game`) and the "Victorian Century" mod in August 2026. Anything the authors could not verify is explicitly marked `(unverified)` in the docs.
3. Victoria 3 script is **NOT** the same as CK3/EU4/HOI4 script. When in doubt about a keyword, do not trust memory of other Paradox games — grep the vanilla game folder for a real usage example.
4. When writing new content, always finish by checking `09-design-and-balance.md`'s checklist (timing, pacing, reward magnitudes) — working script is not the same as good content.

## Routing table

| Your task | Read |
|---|---|
| Create a new mod / add folders or files / "my change does nothing" / debug via error.log | `01-mod-structure.md` |
| Write any script: scopes, triggers, effects, variables, script values, `$PARAM$`, if/random_list | `02-script-language.md` |
| Create or edit an **event** (structure, options, dynamic text, hidden events) | `03-events.md` |
| Decide **when/how an event fires**: on_actions, pulses, weights, cooldowns, multi-event chains | `04-event-chains-and-triggering.md` |
| **Journal entries**, JE groups, **decisions**, scripted buttons, scripted progress bars | `05-journal-entries-and-decisions.md` |
| **Modifiers**: add_modifier rewards, new modifier types, durations, magnitude norms | `06-modifiers.md` |
| **1836 start setup**: states, pops, buildings, countries, diplomacy, releasables/formables, map data | `07-history-states-countries.md` |
| Any **player-visible text**: loc keys, formatting codes, `[bracket]` functions, icons | `08-localization.md` |
| **Design quality**: right timing, pacing frequency, balanced rewards, option design, anti-frustration | `09-design-and-balance.md` |
| Benchmark: how a large polished mod (Victorian Century) structures its content | `10-case-study-victorian-century.md` |

Typical combos: new event = `03` + `04` (+ `08` for text, + `09` before finalizing values). New JE content = `05` + `04` + `09`. New country/alt-history start = `07` + `01` + `08`.

## Ten facts that prevent the most common mistakes

1. Every game `.txt` and `.yml` file is **UTF-8 with BOM, LF line endings**. Loc files must be named `*_l_english.yml` under `localization\english\` and start with `l_english:`.
2. There is **no `character_event`** in Vic3 (only `country_event` / `state_event`) and **no `fire_only_once`** — use variable guards or `cooldown = { days = ... }`.
3. Named modifiers used by `add_modifier` live in **`common/static_modifiers/`** (the old `common/modifiers/` folder no longer exists). Modifier *types* are in `common/modifier_type_definitions/`.
4. To hook events onto a vanilla on_action from a mod **without clobbering it**, define a wrapper on_action and append it: `vanilla_on_action = { on_actions = { my_wrapper } }` — lists merge across files; duplicate `effect`/`trigger` blocks conflict. Full grammar ships in `game/common/on_actions/_on_actions.md`.
5. Saved scopes (`save_scope_as`) do **not** survive a delayed `trigger_event` — persist identity with variables and re-save scopes in the next event's `immediate`.
6. Vanilla duration/magnitude norms: timed modifiers usually run `normal_modifier_time` (5 years); event money rewards are GDP-scaled expense modifiers, radicals/loyalists 0.01–0.3 of a scaling value, IG approval ±2 typical. Details + tables: `06-modifiers.md`, `09-design-and-balance.md`.
7. Overriding vanilla: same relative path + filename = full file replacement; a `#nothing` comment-only file blanks a vanilla file; `REPLACE_OR_CREATE:key` / `REPLACE:key` prefixes override single database entries (engine-supported, semantics partly unverified).
8. Debug with `Documents\Paradox Interactive\Victoria 3\logs\`: `error.log` (script errors with file:line), `game.log`, `database_conflicts.log` ("Overriding entry" lines show what your mod replaced).
9. Paradox ships format docs inside the game folder itself (`_on_actions.md`, `journal_entries.md`, `script_values.md`, `modifier_types.md`, `state_regions.md`, …) — they are authoritative; read them when a doc here marks something unverified.
10. Decisions have exactly 4 keys: `is_shown`, `possible`, `when_taken`, `ai_chance`. There is no `effect` or `ai_will_do`.

## Using this guide from another mod (CLAUDE.md snippet)

Copy `_vic3-modding-guide\` into the mod root, then add to that mod's `CLAUDE.md`:

```markdown
## Victoria 3 modding reference
Before writing any Vic3 script, open `_vic3-modding-guide/00-INDEX.md`, find the
task in the routing table, and read ONLY the matching file(s). Follow the balance
checklist in `09-design-and-balance.md` before finalizing numbers. Never guess
syntax from other Paradox games; verify against
`C:\Program Files (x86)\Steam\steamapps\common\Victoria 3\game`.
```
