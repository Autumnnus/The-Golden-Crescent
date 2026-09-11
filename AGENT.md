## Non-negotiable: Victoria 3 installation is read-only

The vanilla game directory is:

```text
C:\Program Files (x86)\Steam\steamapps\common\Victoria 3\game
```

It is a **reference-only** source of truth. It may be searched, listed, and read to learn current game syntax, definitions, GUI templates, icons, localization keys, scripted GUI bindings, and comparable vanilla implementations.

Never modify, create, rename, move, delete, format, copy files into, or otherwise write to that directory or any of its descendants. Do not run tools that might write there (including editor formatters, generators, game launch commands with an output path there, or broad recursive operations). All implementation changes belong in this mod workspace only.

Before introducing a mechanic or overriding a vanilla GUI, inspect the relevant vanilla implementation in that directory and mirror its current Victoria 3 conventions. Treat a vanilla file as a dependency to reference, never an editable template.

## Workspace and safety

- The mod root is this repository/workspace. Make all edits here only.
- Preserve unrelated user changes. Start relevant work with `git status --short` and inspect the target files before editing.
- Prefer narrowly scoped, additive files over broad vanilla overrides. When an override is necessary, override only named blocks/nodes and document the vanilla file and blocks being extended in a nearby comment.
- Use the existing `ve_` prefix for new custom identifiers, filenames, variables, modifiers, scripted GUI names, GUI types, localization keys, and feature-specific assets. Keep event namespaces unique and stable.
- Do not use destructive git commands (`reset --hard`, `checkout --`, broad cleanup) or overwrite user work without explicit confirmation.
- Keep game content deterministic and performant: put recurring logic in appropriate `on_actions`, avoid expensive unbounded scopes in frequently fired pulses, and use scripted triggers/values/effects for reusable logic.

## Map data pipeline (mandatory for map work)

Map data — state ownership, pops, cultures, religions, buildings, country definitions,
country localization — is **generated**, not hand-written. The source of truth is `world/`.
Full documentation: `tools/README.md`.

```
world/*.yml   --( python tools/tgc.py build )-->   common/history/..., common/country_definitions/,
                                                   map_data/state_regions/, localization/
```

Rules:

- **Never hand-edit generated files.** Everything under `common/history/states/`,
  `common/history/pops/`, `common/history/buildings/`, `common/country_definitions/`, plus
  generated `map_data/state_regions/` files and `localization/**/tgc_generated_*`, carries an
  `OTOMATIK URETILDI` header. Edit the corresponding `world/` YAML and rebuild. `build` deletes
  its own previous output, so a stray hand-edit is silently lost.
- The vanilla-override mechanism differs per directory; do not generalize one to another
  (verified against the game logs, installed mods, and the game binary — see `tools/README.md`):
  - `common/history/{states,pops,buildings}` are executed history scripts, not keyed databases.
    Differently-named files do **not** override each other — they all run. Vanilla is disabled
    only via `game_custom_data.replace_paths` in `.metadata/metadata.json`, which is why output
    uses its own `tgc_*` filenames. Never remove those `replace_paths` entries.
  - `common/country_definitions` is a keyed database. A plain duplicate key in a differently-named
    file is **silently discarded** (`Duplicated key TUR will not be created`). Overrides must use
    the `REPLACE_OR_CREATE:TAG` prefix, which the generator emits.
  - `map_data/state_regions` supports neither; changing one state means regenerating that whole
    vanilla-named file. Use `world/state_regions/` patches sparingly.
- `common/history/{military_formations,characters,countries}` still run from vanilla and will
  error wherever ownership changed. Add them to `replace_paths` when that content is authored.
- After any change to `world/`, run in order:

```bash
python tools/tgc.py build && python tools/tgc.py check
```

  `check` must report zero errors before the task is considered done.
- Before writing YAML, resolve region names with `python tools/tgc.py find <name>` and inspect
  the target with `python tools/tgc.py show <state>` — never guess a `STATE_*` identifier or a
  province hex list.
- When the user describes a region in prose or via a screenshot, render a shared reference map
  first (`python tools/tgc.py map --mode reference --region ...`), confirm the state names
  against it, then edit `world/`. Render `--mode political` afterwards and show the result.
- Add new Turkish/free-form place names to `world/_aliases.yml` as they come up.
- `build/` is a regenerable cache (index, geometry, rendered maps) and is git-ignored.
  Re-run `python tools/tgc.py index` and `geo` after a Victoria 3 update.

## Testing and logs

- Do not repeatedly ask the user to launch the game or manually test routine changes. When syntax, identifiers, braces, localization references, modifier definitions, and comparable vanilla patterns can be checked statically, perform those checks yourself and treat them as sufficient for normal implementation work.
- Request or recommend user-run game testing only for important, critical, or genuinely runtime-dependent behavior that static inspection cannot establish. Examples include risky GUI overrides, save compatibility or migration, event/on-action dispatch, scope-dependent behavior, timing and pulse logic, multiplayer behavior, crashes, or a suspected engine-specific issue.
- Do not end every task with a generic “test this in game” requirement. If no critical runtime uncertainty remains, report the static verification performed and finish the task.
- When the user mentions errors, debugging, crashes, warnings, or logs—or when diagnosis requires game output—inspect the Victoria 3 logs at:

```text
C:\Users\<username>\OneDrive\Documents\Paradox Interactive\Victoria 3\logs
```

- Treat the logs directory as a diagnostic, read-only source. Inspect relevant files such as `error.log`, `debug.log`, `game.log`, and `system.log` when present; do not modify, delete, truncate, or clear them.

## Verification checklist

After an implementation, before reporting the task done:

1. Review every edited file and confirm nothing outside the workspace was touched.
2. Search for all new identifiers and localization keys to catch spelling or scope mismatches.
3. Check script braces and GUI block nesting; compare changed syntax with a known working vanilla or mod example.
4. Require Victoria 3 runtime validation only when the change is critical or cannot be verified reliably through static checks. When logs are relevant, inspect the configured Victoria 3 logs directory directly.
5. Report files changed, validation performed, and any game-runtime checks that remain for the user.
