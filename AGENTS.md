# The Golden Crescent — mod instructions

This repository contains the mod and its scenario sources. Reusable Atlas/Flavor implementations live in a separate Victoria 3 Mod Tools repository. Read `docs/TOOLS.md`; run `python3 scripts/tools.py docs` to locate shared documentation, then read its `docs/WORKFLOWS.md` and the relevant tool guide. Run `python3 scripts/tools.py doctor` to verify the selected mod before tool work.

## Read-only sources and workspace

- Never write to the Victoria 3 installation or game logs. They may be searched and read as reference. `doctor` prints the resolved paths; normal Mac defaults are `~/Library/Application Support/Steam/steamapps/common/Victoria 3/game` and `~/Documents/Paradox Interactive/Victoria 3/logs`.
- All game content changes belong in this mod. Tool implementation changes belong in the separately configured tool repo. Never edit another mod as a side effect.
- Preserve unrelated user changes; inspect `git status --short` before edits. Do not use destructive Git cleanup/reset operations or overwrite user work.
- Before introducing syntax, mechanics or GUI overrides, inspect the relevant installed vanilla implementation. Prefer narrow additive definitions; document overridden source blocks.
- Use this mod's existing `ve_` prefix for new custom content, with unique stable event namespaces. Keep generator-owned filenames/prefixes intact.

## Source and authoring

- Scenario design: `docs/scenario/senaryo.md`, `senaryo_afrika.md`, `senaryo_amerika.md`; state notes: `docs/reference/states.md`. `docs/archive/` is historical evidence, not current instructions.
- Atlas's active source is `world/` (V2: `world/scenario.yml`). Generated history/country/localization/map files must not be hand-edited. Generator cleanup replaces its own prior output.
- Before inventing YAML identifiers, use `python3 scripts/tools.py atlas find <name>` / `show <state>` and `rules`. Never guess STATE IDs or province hex values. Free-form aliases belong in `world/_aliases.yml`.
- Prose/screenshot map requests require a reference map and verified state names. Preview hypothetical scenarios before active integration. Use `atlas preview --scenario ...` and `atlas map --scenario ... --mode changes --data` as needed.
- After authorized changes to `world/`, run `python3 scripts/tools.py atlas build`, then `python3 scripts/tools.py atlas check`; zero errors required. Do not blindly change metadata replace_paths: generated history directories need matching complete output. Country overrides use REPLACE_OR_CREATE; state-region patches regenerate vanilla-named files. Detailed contracts are in the external Atlas guide.
- Economy, population, literacy, military, laws, technology, interest groups and diplomacy belong in V2 scenario fields. Exact GDP/clout and runtime behavior are not simulated by the atlas.
- Flavor plans belong in `flavor/projects/`. Follow the external Flavor LLM and syntax guides. **Generate a diagram first; explicit approval of that exact revision is required before approve/build/install.** Never invent user approval or reuse test receipts. Tool work or generic continuation does not approve example stories.
- When using both tools, pass a full unfiltered Atlas report from this mod through Flavor's `--context`. Activate new country definitions before dependent Flavor installation. Each tool owns only its generated files and manifests.
- Keep recurring logic bounded and performant. Reuse scripted triggers/effects/values rather than duplicating expensive pulse scopes.

## Verification

- Run suitable static checks and the external tool test runner for code changes; it uses disposable mods. Do not run ad hoc destructive tests against this mod.
- Check changed identifiers, localization keys, braces and source patterns. Inspect relevant read-only logs directly when debugging failures; never truncate or delete them.
- Static checks are not engine execution. Request runtime testing only for material unresolved engine-dependent behavior (event dispatch/timing/scopes, risky GUI, save/multiplayer, crashes). Do not repeatedly request game launches for ordinary changes.
- Report what changed, tests performed and material limitations. Bundled examples and regression fixtures are never implicitly active user scenarios.
