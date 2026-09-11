# Victoria 3 Localization

**Read this file when:** adding or editing any player-visible text — event titles/descriptions, journal entries, decisions, modifiers, concepts, country names — or when text shows up in-game as a raw key like `my_event.1.t`.

All facts verified on this machine (vanilla 168-file `localization\english` + the "Victorian Century" mod) unless marked **(unverified)**.

## 1. File format

A localization file is a pseudo-YAML text file:

```yaml
# game\localization\english\content_1_l_english.yml (trimmed)
l_english:
  # Coronation of Queen Victoria
 victoria.1.t:0 "The Coronation of Queen Victoria"
 victoria.1.d:0 "The King is dead. With the ascension of his young niece [SCOPE.sCharacter('queen_victoria').GetFirstName], the realm rejoices and the crown of Hanover passes outside of British control. Long may she reign!"
 victoria.1.a:0 "God save the Queen!"
 edward_vii_death_tt: "Edward VII dies"
```

Rules observed across vanilla and mod files:

- **Line 1 is the language header** `l_english:` (nothing above it except the invisible BOM).
- **Every key line is indented by at least one space.** Vanilla uses 1 space; this mod uses 4 spaces — both load. Tabs were not observed in loc files; use spaces.
- Key format: `key:VERSION "text"` — the `:0` / `:1` / `:2` number is optional (`edward_vii_death_tt:` has none). Observed values 0–2; it acts as a translation revision counter for Paradox's tooling and does not change in-game behavior **(interpretation unverified; both forms demonstrably load)**.
- One pair of surrounding double quotes. Literal quotes *inside* the text are written as-is (vanilla: `victoria.1.f:0 ""Since it has pleased Providence…""` renders with quote marks).
- `#` at the start of a line (after optional spaces) = comment. Inside a quoted string, `#` starts a formatting code (section 4).
- Keys are flat — no nesting, no YAML lists. Duplicate keys: last one loaded wins **(winner ordering unverified — see section 7)**.

## 2. File naming and folder layout

- Folder: `localization\<language>\` — subfolders allowed and freely nameable. Vanilla `english\` has subfolders `character`, `frontend`, `historical`, `interest_groups`, `map`; the mod nests per-country folders (`localization\english\gbr\gbr_events_l_english.yml`).
- Filename convention: `<anything>_l_english.yml`. **All 168 vanilla english files and all mod english files follow it**, and the inner header must match the language of the folder/suffix. (Whether the suffix is technically required for loading is unverified — never deviate.)
- A `replace\` subfolder (a commonly cited mechanism where keys override without conflict warnings) was **not found anywhere** in vanilla `game\localization` or in this mod — **(unverified, test in game before relying on it)**.
- Special non-language folders in `game\localization\`: `jomini\` (script-system strings) and `modifiers\` (`modifiers_l_english.yml`, `modifiers_v2_l_english.yml`, … one per language) — engine-level strings like `MODIFIER_DESCRIPTION_ENTRY:0 "$VALUE$ $HEADER$"`. Plus `languages.yml` at the root.

## 3. Languages and encoding

`game\localization\languages.yml` registers: `l_english`, `l_braz_por`, `l_french`, `l_german`, `l_polish`, `l_russian`, `l_spanish`, `l_japanese`, `l_simp_chinese`, `l_korean`, **`l_turkish`**. Matching folders exist for all of them — **the game DOES ship Turkish localization** (`localization\turkish\`, 168 files, e.g. `content_1_l_turkish.yml`: `queen_victoria_mod: "Victoria Ahlakı"`).

For mods in this project: **write `localization\english\*_l_english.yml`**. This mod ships `english` and `simp_chinese` only; players on other languages then see either English text or raw keys depending on engine fallback **(fallback behavior unverified)**. If you want the mod readable on a Turkish client too, the same text can be duplicated to `localization\turkish\*_l_turkish.yml` with an `l_turkish:` header.

**Encoding — verified by byte inspection:** vanilla `content_1_l_english.yml` and mod `gbr_events_l_english.yml` both begin `EF BB BF` = **UTF-8 with BOM**, and use **LF-only** line endings (zero CRLF found). Save every `.yml` as UTF-8 with BOM; a BOM-less loc file is the classic silent failure (keys show raw in-game, no error.log entry) **(failure mode unverified from logs, encoding requirement itself observed universally)**.

```powershell
[System.IO.File]::ReadAllBytes("my_l_english.yml")[0..2] | % { '{0:X2}' -f $_ }   # want EF BB BF
```

## 4. Formatting codes (`#code text#!`)

A `#code` inside a string starts a style; **`#!` ends it**. Survey of codes actually used in vanilla english files (occurrence counts):

| Code | Count | Observed use |
|---|---|---|
| `#v` | 3230 | value styling, e.g. `#v [ScriptValue(...)|0%]#!` |
| `#BOLD` / `#bold` / `#b` | 3050 / ~30 / 2151 | bold |
| `#header` | 1894 | section headers in tooltips |
| `#variable` | 1816 | variable-styled text |
| `#tooltippable` + `#tooltip` | 1316 / 994 | compound: `#tooltippable;tooltip:<KEY_OF_TOOLTIP> shown text#!` |
| `#title` | 657 | title style |
| `#indent_newline` | 575 | indented line break, takes a value: `#indent_newline:2` **(argument form observed in gui-related strings)** |
| `#N` / `#P` | 386 / 116 | negative / positive coloring |
| `#italic` / `#i` | 315 / 71 | italics |
| `#lore` | 206 | flavor-text styling (used by this mod's headlines too) |
| `#R` / `#r` | ~13 / 174 | red |
| `#g` | 100 | green |
| `#instruction`, `#tooltip_header`, `#concept`, `#negative_value`, `#positive_value`, `#black`, `#u` | <100 each | misc styles |

Real compound examples:

```yaml
# mod headlines_l_english.yml
notification_headlines_acw_begin_csa_name:0 "#b American Civil War #!"
notification_headlines_acw_begin_csa_tooltip:0 "#header $notification_headlines_acw_begin_csa_name$#!\n$TOOLTIP_DELIMITER$\n$notification_headlines_acw_begin_csa_desc$"
```

- **Newline** inside a string is the two-character sequence `\n`; `\n\n` makes a paragraph break (heavily used in this mod's event flavor text).
- **Icons**: `@icon_name!` inlines an icon. Top vanilla usages: `@money!` (864), `@warning!`, `@battalions!`, `@red_cross!`, `@ships!`, `@information!`, `@green_checkmark!`, `@arrow_right!`, plus per-good icons. Icon names are declared in `game\gui\texticons.gui` (`texticon = { icon = market_balance ... texture = "gfx/interface/icons/trade_icons/balance.dds" }`) and `goods_texticons.gui`.

## 5. `$key$` substitution and `[bracket]` data functions

**`$key$`** pastes another loc key (or an engine-provided variable) inline:

```yaml
# game\localization\english\modifiers_l_english.yml
interest_group_ig_armed_forces_pol_str_mult:2 "$ig_variant_armed_forces$ [concept_political_strength]"
# game\localization\modifiers\modifiers_l_english.yml
MODIFIER_ENTRY_DESCRIPTION:0 "$VALUE$ from $HEADER$"
```

**`[...]` runs a data function chain** at display time. Root objects found in vanilla english by frequency: `SCOPE` (10166), `Concept` (8678), `Country`, `ROOT` (2710), `TARGET_COUNTRY`, `GetPlayer`, `STATE`, `SelectLocalization`, `GetLawType`, `MilitaryFormation`, `Goods`, `Character`, `GetStaticModifier`, `Building`, `GetCulture`, `Pop`, … (full list dumpable to `logs\data_types\`, see 01-mod-structure.md §6).

Real patterns to copy:

```yaml
[ROOT.GetCountry.GetName]                                  # event-owner country name (mod uses this constantly)
[ROOT.GetCountry.GetRuler.GetPrimaryRoleTitle]             # chains keep going
[SCOPE.sCharacter('queen_victoria').GetFirstName]          # sX('name') = saved scope from save_scope_as
[SCOPE.sCountry('hannover_victoria_scope').GetAdjective]
[SCOPE.sState('cda_state').GetName]
[SCOPE.gsInterestGroup('cda_ig').GetName]                  # gs = global saved scope (save_global_scope_as) (naming inferred)
[concept_customs_union]                                    # bare concept key = linked concept name
[Concept('concept_pop', '$concept_pops$')]                 # concept link with custom display text
[SelectLocalization(GetPlayer.IsValid,'KEY_IF_TRUE','KEY_IF_FALSE')]
[GetBuildingType('building_manor_house').GetName]
[GetPlayer.MakeScope.ScriptValue('acw_reincorporate_dixie_loyalist_min')|0%]
```

The `|suffix` before `]` formats numbers. Suffixes observed in vanilla (counts): `|v` (771), `|D`, `|0` (107), `|U`, `|v0`, `|dv`, `|0%` (72), `|1`, `|vD`, `|%0`, `|Kv`, `|+=`, `|v%0`. Obvious readings: digits = decimal places, `%` = percent, `+` = force sign, `v` = value-color; exact semantics of each **(unverified)** — copy a vanilla usage of the shape you need.

## 6. How script references loc keys (conventions)

**Events** (see 03-events.md) name their keys explicitly; vanilla and this mod both use `<namespace>.<n>.<letter>`:

```
# game\events\victoria_events.txt
victoria.1 = {
    title  = victoria.1.t
    desc   = victoria.1.d
    flavor = victoria.1.f
    option = { name = victoria.1.a  ... custom_tooltip = victoria.1.tt }
}
```

Convention: `.t` title, `.d` desc (alt versions `.d2` exist), `.f` flavor, options `.a`/`.b`/`.c`…, `.tt` custom tooltips. The mod adds `joi_flavor_gbr.1.t/.d/.f/.a` in the same style.

**Journal entries**: loc key = the JE key itself, plus suffixed keys — observed `je_schleswig_holstein_question: "The Schleswig-Holstein Question"` and `je_schleswig_holstein_question_reason: "…"`; `custom_tooltip = { text = some_key }` points at any loc key.

**Static modifiers** (see 06-modifiers.md): loc key = the modifier's script name. Vanilla `common\static_modifiers\content_1_modifiers.txt` defines `queen_victoria_mod = { … }` → `localization\english\content_1_l_english.yml` has `queen_victoria_mod:0 "Victorian Propriety"`. The mod does the same (`guerra_dos_farrapos_modifier: "Guerra dos Farrapos"`).

**Modifier types** (`common\modifier_type_definitions`): loc key = the modifier-type key, plus `_desc`:

```yaml
interest_group_ig_armed_forces_pol_str_mult:2 "$ig_variant_armed_forces$ [concept_political_strength]"
interest_group_ig_armed_forces_pol_str_mult_desc:2 "A bonus or penalty to the total [concept_political_strength] of the …"
```

**Countries**: `TAG: "Name"` + `TAG_ADJ: "Adjective"` (mod: `IMP: "Imperial Federation"`, `IMP_ADJ: "Imperial Federal"`); dynamic names use `dyn_c_*` / `dyn_c_*_adj` keys referenced from `common\dynamic_country_names`.

**Concepts**: keys `concept_*` defined under `common\game_concepts`, referenced in text as `[concept_x]` or `[Concept('concept_x','text')]`.

## 7. Overriding vanilla text from a mod

Observed in Victorian Century: the mod re-defines **94 keys that already exist in vanilla english** from its own differently-named files (e.g. `goods_output_radios_mult` in mod `joi2_modifiers_l_english.yml` vs vanilla `modifiers_l_english.yml`; many first names in `joi_names_l_english.yml` vs vanilla `names_l_english.yml`). The mod plainly relies on its copy winning; the precise load-order rule for same-key loc collisions is **(unverified, test in game — the vanilla `replace\` mechanism was not observed, section 2)**. To override vanilla text, define the same key in your own `*_l_english.yml`.

## 8. Recipe: localization for a new event with dynamic country names

Script (`events\mymod_events.txt` — structure per 03-events.md):

```
namespace = mymod

mymod.1 = {
    type = country_event
    title  = mymod.1.t
    desc   = mymod.1.d
    flavor = mymod.1.f
    immediate = {
        random_country = {           # whatever picks your target
            save_scope_as = mymod_rival
        }
    }
    option = { name = mymod.1.a }
}
```

Localization (`localization\english\mymod_l_english.yml`, **UTF-8 with BOM**, LF endings):

```yaml
l_english:
 mymod.1.t:0 "An Ultimatum"
 mymod.1.d:0 "[SCOPE.sCountry('mymod_rival').GetName] has issued demands that [ROOT.GetCountry.GetName] cannot ignore. The #b [SCOPE.sCountry('mymod_rival').GetAdjective]#! ambassador awaits our answer."
 mymod.1.f:0 ""We shall see who blinks first.""
 mymod.1.a:0 "Never!"
```

Checklist: header `l_english:` on line 1; every key indented; `[ROOT.GetCountry.GetName]` = the country receiving the event; `[SCOPE.sCountry('name')...]` requires a matching `save_scope_as = name` executed **before** the text renders (put it in `immediate`); `#b …#!` pairs closed; file saved into `localization\english\` with `_l_english.yml` suffix. Launch to main menu → fire the event via console (`-debug_mode`, see 01-mod-structure.md §6) → any raw `mymod.1.t` on screen or `error.log` "Missing localization" line means a key/path/encoding problem.

See also: `01-mod-structure.md` (encoding, override model, error.log), `03-events.md`, `06-modifiers.md`, `07-history-states-countries.md`.

## Common pitfalls

- **No BOM → file silently ignored.** Every working loc file inspected starts `EF BB BF`. Symptom: raw keys in-game, nothing in error.log. Byte-check first, always.
- **Filename/header/folder language mismatch.** `*_l_english.yml` containing `l_english:` must sit under `localization\english\`. Any mismatch (e.g. file in `localization\` root, or header `l_english:` in a `_l_french.yml`) loses the keys.
- **Missing or unbalanced quotes.** The whole text must sit in one pair of `"…"`; a stray unclosed quote eats the rest of the line (and inner quotes are best written sparingly, vanilla-style `""quote""`).
- **Unclosed `#b`/`#v` (no `#!`)** bleeds formatting into the rest of the tooltip.
- **Key collisions.** 71,791 keys exist in vanilla english alone. An unprefixed key like `hamilton` or `frederick` (both real vanilla keys this mod knowingly overrides) will override or be overridden. Prefix everything: `mymod_...` / `mymod.1.t`.
- **Zero-indented keys.** The single leading space before each key is part of the format; vanilla never omits it. A key at column 0 risks being read as a new language header **(exact failure unverified — never observed in any working file)**.
- **`[SCOPE.sX('name')]` with a scope never saved** renders broken text; the `save_scope_as` must run in `immediate` before display (vanilla `victoria.1` does exactly this — scope saved in `immediate`, used in `victoria.1.d`).
- **Editing loc of an already-fired event in an ongoing save**: title/desc are often baked at fire time **(unverified)** — test on a fresh fire.
- **Forgetting `_desc`** for a new modifier type: name shows but tooltip description falls back to nothing (vanilla always pairs `<key>` with `<key>_desc`).
