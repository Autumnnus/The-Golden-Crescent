# Victoria 3 Mod Structure, Override Rules, and Debugging

**Read this file when:** creating a new mod folder, adding/renaming files inside a mod, deciding whether to copy a vanilla file or create a new one, fixing "my change does nothing" problems, or debugging with error.log.

All facts below were verified on this machine (game files + the "Victorian Century" mod) on 2026-08-02 unless marked **(unverified)**.

## 1. Where things live

| What | Windows | Mac |
|---|---|---|
| Game files | `C:\Program Files (x86)\Steam\steamapps\common\Victoria 3\game` | `~/Library/Application Support/Steam/steamapps/common/Victoria 3/game` |
| User/mod dir | `C:\Users\<username>\OneDrive\Documents\Paradox Interactive\Victoria 3` | `~/Documents/Paradox Interactive/Victoria 3` |
| Mods | `...\Documents\Paradox Interactive\Victoria 3\mod\<folder>` | `~/Documents/Paradox Interactive/Victoria 3/mod/<folder>` |
| Logs | `...\Documents\Paradox Interactive\Victoria 3\logs` | `~/Documents/Paradox Interactive/Victoria 3/logs` |
| Saves | `...\Documents\Paradox Interactive\Victoria 3\save games` | `~/Documents/Paradox Interactive/Victoria 3/save games` |

Other folders that exist under the Documents dir: `crashes`, `dumps`, `exceptions`, `playsets_backup`, `cache`, `screenshots`.

## 2. Mod anatomy: `.metadata\metadata.json` + thumbnail

Every mod has a `.metadata` folder containing exactly one required file. Real example:

```json
// C:\Users\prost\...\Victoria 3\mod\3219394272\.metadata\metadata.json
{
  "name" : "Victorian Century",
  "id" : "",
  "version" : "",
  "picture": "thumbnail.png",
  "supported_game_version" : "",
  "short_description" : "",
  "tags" : [],
  "relationships" : [],
  "game_custom_data" : {
    "multiplayer_synchronized" : true
  }
}
```

Observed points:
- `picture` points at `thumbnail.png` sitting at the **mod root** (not inside `.metadata`).
- Empty strings for `id`, `version`, `supported_game_version` are accepted (this mod runs with them empty).
- `game_custom_data.multiplayer_synchronized: true` marks the mod as checksum-affecting for MP **(interpretation unverified; the field itself is observed)**.

## 3. Mirror-the-game-folder principle

A mod is an overlay over `game\`. **Every path inside the mod must exactly mirror the path inside `game\`.** Top-level folders in vanilla `game\`:

```
common/  content_source/  data_binding/  dlc/  dlc_metadata/  events/
fonts/  gfx/  gui/  input_profile/  interface/  licenses/  localization/
map_data/  music/  notifications/  sound/  soundtrack/  tools/
```

This mod uses (all mirroring vanilla exactly): `common/`, `dlc/`, `dlc_metadata/`, `events/`, `gfx/`, `gui/`, `localization/`, `map_data/`, `music/`, `soundtrack/` plus `.metadata/` and `thumbnail.png`.

`common\` in vanilla has ~140 subfolders — each one is a "database" of script objects. The ones most content mods touch:

```
common/buildings            common/journal_entries      common/scripted_effects
common/building_groups      common/journal_entry_groups common/scripted_triggers
common/character_templates  common/laws                 common/script_values
common/character_traits     common/modifier_type_definitions
common/company_types        common/on_actions           common/static_modifiers
common/country_definitions  common/parties              common/technology
common/decisions            common/production_methods   common/history/   (see 07-history-states-countries.md)
common/defines              common/game_concepts        common/ai_strategies
common/diplomatic_actions   common/goods                common/customizable_localization
```

Others that exist and may matter: `cultures`, `religions`, `pop_types`, `pop_needs`, `interest_groups`, `interest_group_traits`, `ideologies`, `government_types`, `institutions`, `decrees`, `diplomatic_plays`, `war_goal_types`, `strategic_regions`, `state_traits`, `coat_of_arms`, `dna_data`, `dynamic_country_names`, `flag_definitions`, `named_colors`, `treaty_articles`, `power_bloc_*`, `political_movements`, `political_lobbies`, `company_charter_types`, `harvest_condition_types`, `mobilization_options`, `combat_unit_types`, `ship_*`.

## 4. Override model — what this mod actually does

Three distinct patterns are observable in Victorian Century:

### 4a. Same relative path → the mod file replaces the vanilla file wholesale

- `events\victoria_events.txt` exists in both. The mod copy is the **entire vanilla file re-pasted with edits** (it replaces `template = HAN_ernest_augustus_hannover` with an inline `first_name = Ernest_Augustus ...` character block and adds a trait). Everything the mod wants to keep from vanilla had to be kept in the copy.
- `common\decisions\manifest_destiny.txt`: vanilla is 4 KB of decisions; the mod's file is **11 bytes**: a UTF-8 BOM plus the text `#nothing`. This *removes* the vanilla decisions by shadowing the whole file with an effectively empty one. This is the observed idiom for deleting vanilla content.
- The mod overrides 35 vanilla files this way, including 15 `common\history\countries\*.txt` files, several `common\journal_entries\*.txt`, all four `common\parties\*.txt`, and 2 event files.

Conclusion (observed): **a mod file at the same relative path fully replaces the vanilla file — vanilla objects defined only in that file cease to exist unless re-declared.**

### 4b. New filename, same object key → later definition overrides, logged as a conflict

`logs\database_conflicts.log` (from an older session on this machine) shows the engine doing exactly this:

```
[16:36:45][gamedatabase.h:314]: Overriding entry 'join_customs_union' for database
  'common/diplomatic_actions' in ' file: common/diplomatic_actions/35_EU_union.txt line: 601'
```

So defining an object with an existing key in a *differently named* file overrides the earlier definition and writes a warning to `database_conflicts.log`. Which file "wins" between two mods, or the exact file ordering rule (alphabetical? mod after vanilla?), **cannot be verified from files alone (unverified, test in game — but mod-overrides-vanilla is strongly implied by the mod relying on it)**.

### 4c. `REPLACE_OR_CREATE:` prefix on the object key

The mod prefixes object keys with `REPLACE_OR_CREATE:` when redefining vanilla objects from **new** files:

```
# mod: common\buy_packages\joi_buy_packages.txt  (vanilla wealth_1 lives elsewhere)
REPLACE_OR_CREATE:wealth_1 = {
    ...
}
```

Also used in `common\parties\liberal_party.txt` (`REPLACE_OR_CREATE:liberal_party = {`) and `common\treaty_articles\31_ship_transfer.txt`. The prefix appears **nowhere in vanilla script**, and current logs show no errors about it. Apparent purpose: override-or-add without a database-conflict warning **(semantics unverified — engine feature not documented in game files; test in game)**.

### 4d. Adding brand-new files (the safe default)

248 of the mod's 283 `common\`/`events\` files are **new filenames** that don't exist in vanilla (e.g. `common\ai_strategies\joi_flavor_strategies.txt`, `common\country_definitions\zz_imp_countries.txt`, `events\...` with new namespaces). New files with new object keys simply add content. Prefer a unique prefix (`joi_`, `zz_`, your own) on filenames and keys to avoid collisions.

## 5. File encoding (verified by raw byte inspection)

Checked first bytes of vanilla + mod `.txt` and `.yml` files with PowerShell (`[System.IO.File]::ReadAllBytes`):

| File | First bytes | Meaning |
|---|---|---|
| `game\events\victoria_events.txt` | `EF BB BF 6E 61 6D ...` | UTF-8 **with BOM** |
| `game\common\parties\liberal_party.txt` | `EF BB BF 23 ...` | UTF-8 with BOM |
| `game\localization\english\content_1_l_english.yml` | `EF BB BF 6C 5F ...` | UTF-8 with BOM |
| mod `events\victoria_events.txt` | `EF BB BF ...` | UTF-8 with BOM |
| mod `localization\english\gbr\gbr_events_l_english.yml` | `EF BB BF ...` | UTF-8 with BOM |
| mod `common\decisions\manifest_destiny.txt` (11 bytes) | `EF BB BF 23 6E 6F 74 68 69 6E 67` | BOM + `#nothing` |

- **Every file inspected, vanilla and mod, .txt and .yml, starts with the UTF-8 BOM (`EF BB BF`).** Write all mod files as UTF-8 with BOM. (Whether the engine tolerates BOM-less script `.txt` is unverified; BOM-less localization `.yml` is widely reported to fail silently — see 08-localization.md.)
- **Line endings: LF only.** Counted line endings in each file above: 0 CRLF, hundreds of bare LF — even though this is a Windows install. Both vanilla and this mod use Unix LF. CRLF tolerance is (unverified); safest to emit LF.
- Script `.txt` files use tabs for indentation (observed in vanilla and mod).

PowerShell one-liner to check any file:

```powershell
[System.IO.File]::ReadAllBytes("path\to\file.yml")[0..2] | ForEach-Object { '{0:X2}' -f $_ }
# want: EF BB BF
```

## 6. Logs and how to debug with them
 
The logs directory:
- Windows: `C:\Users\<username>\OneDrive\Documents\Paradox Interactive\Victoria 3\logs\`
- Mac: `~/Documents/Paradox Interactive/Victoria 3/logs/`

It exists and contains (observed):

- `error.log` — the main modding feedback channel. Rotates: `error.1.log` … `error.5.log` are previous sessions.
- `game.log` — script-system errors **with file + line number**.
- `database_conflicts.log` — every "Overriding entry X for database Y" event (see 4b).
- `debug.log`, `warning.log`, `system.log`, `gui.log`, `ai.log`, `multiplayer.log`, `text.log`, etc. (same rotation scheme).
- `data_types\` — dumped documentation files `data_types_common.txt`, `data_types_gui.txt`, `data_types_script.txt`, `data_types_uncategorized.txt`, `data_types_internalclausewitzgui.txt`. These list the `[bracket]` data functions usable in localization/GUI. (Generated by a debug console command, `DumpDataTypes` **(command name unverified)** — the dump files themselves are observed.)

Real `error.log` line format — `[HH:MM:SS][source.cpp:line]: message`:

```
[20:06:22][religion.cpp:92]: Missing religion sol static modifier mujtahidiyya_standard_of_living_modifier_positive
[20:07:12][jomini_effect.cpp:1139]: Variable 'daimyo_chain_id' is used but is never set. Setting it in an unused scripted trigger or effect does not count
```

Real `game.log` script error — note it names the offending mod file and line:

```
[20:07:42][jomini_script_system.cpp:247]: Script system error!
  Error: create_building effect [ Invalid state in STATE_HOME_COUNTIES for Kingdom of Mysore for building ownership ]
  Script location: common/history/buildings/tgc_buildings_10_india.txt:2103
```

### Debug workflow

1. Launch the game with your mod enabled, get to the main menu (most script is parsed by then), then read `error.log` **top to bottom** — errors from your own key prefix are the ones to fix first.
2. `Missing localization` / `Missing ... modifier` style lines usually mean a key typo or a loc key you forgot to add.
3. Check `database_conflicts.log` to confirm whether your override actually registered (or whether you are accidentally overriding something).
4. `game.log` for runtime script errors with exact `file:line`.
5. `-debug_mode` launch option (set in Steam launch options or the launcher) enables the in-game console and error display **(unverified from files alone — standard Paradox practice; the logs above are written even without it)**. The vanilla folder `common\console_command_macros\` exists, confirming a console subsystem is present.
6. Logs rotate per session — `error.1.log` is the previous run, useful after a crash.

## 7. Recommended folder checklist for a new content mod

```
mod\my_mod\
├── .metadata\
│   └── metadata.json          # REQUIRED — see section 2
├── thumbnail.png              # referenced by metadata.json "picture"
├── common\
│   ├── <db_folder>\my_prefix_things.txt      # new files, unique prefix
│   └── ...                    # only the db folders you actually touch
├── events\
│   └── my_prefix_events.txt   # new namespace(s) — see 03-events.md
├── localization\
│   └── english\
│       └── my_prefix_l_english.yml           # see 08-localization.md
└── gfx\                       # only if you add icons/art (mirror vanilla paths)
```

Rules of thumb (all grounded in the observations above):
- New content → new files with a unique filename prefix + unique object keys.
- Editing one vanilla object from a new file → redefine the key (expect a `database_conflicts.log` entry) or use `REPLACE_OR_CREATE:` as this mod does (unverified semantics).
- Removing vanilla content or heavy surgery on one file → copy the vanilla file to the identical relative path and edit it (or blank it with `#nothing`). This breaks whenever a patch changes that vanilla file, so keep the list of full-file overrides short and documented.
- Everything UTF-8 with BOM, LF line endings, tabs in script files.

See also: `03-events.md` (event structure whose loc keys are wired in section 4a's example), `06-modifiers.md` (modifier_type_definitions incl. the shipped doc `game\common\modifier_type_definitions\modifier_types.md`), `07-history-states-countries.md` (the `common\history\` overrides this mod makes), `08-localization.md`.

## Common pitfalls

- **File saved as UTF-8 without BOM or as ANSI.** Every single vanilla and mod file inspected carries `EF BB BF`. A missing BOM is the classic cause of a loc file being silently ignored (localization especially — see 08-localization.md). Always byte-check with the one-liner in section 5.
- **Path doesn't mirror vanilla exactly.** `common\decision\` instead of `common\decisions\`, or loc files outside `localization\english\`, load nothing and print no error.
- **Accidental full-file override.** Naming your file the same as a vanilla file (`victoria_events.txt`) replaces the *whole* vanilla file. If you only wanted to add an event, every vanilla event in that file disappears. Use fresh filenames unless replacement is the goal.
- **Accidental key collision.** Two files defining `liberal_party` = last one silently wins (with only a `database_conflicts.log` note). Prefix your object keys.
- **Full-file overrides rot on game patches.** This mod overrides 15 history-country files and 4 party files wholesale; each game update that touches those vanilla files silently reverts to the mod's stale copy. Re-diff after every patch.
- **Editing files while OneDrive syncs the mod folder** (this mod lives under OneDrive): file locks/partial syncs can hand the game a truncated file. If bizarre parse errors appear, pause sync **(failure mode unverified, flagged from the observed path)**.
- **Reading the wrong log.** Parse/DB problems: `error.log` + `database_conflicts.log` at main menu. Runtime effect/trigger problems: `game.log` after the event fires. Previous session: `*.1.log`.
