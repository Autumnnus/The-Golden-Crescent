#!/usr/bin/env python
"""Regression suite for the toolchain itself.

    python tools/tgc.py selftest

Run this after touching anything under tools/. It works on the real vanilla
install and on a temporary world/ that it creates and removes, so it must be
run with a clean working tree — it rewrites .metadata/metadata.json and
world/*/t_selftest.yml while it runs, and restores both at the end.

Each check below exists because the corresponding mistake once shipped:
a rule that never fires is worse than no rule at all.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from vic3 import pdx                                          # noqa: E402
from vic3.paths import MOD, VANILLA                           # noqa: E402

META = MOD / ".metadata" / "metadata.json"
TMP_COUNTRIES = MOD / "world" / "countries" / "t_selftest.yml"
TMP_STATES = MOD / "world" / "states" / "t_selftest.yml"


class Suite:
    def __init__(self):
        self.failed = 0
        self.passed = 0

    def check(self, label: str, cond: bool, detail: str = "") -> None:
        if cond:
            self.passed += 1
            print(f"  pass  {label}")
        else:
            self.failed += 1
            print(f"  FAIL  {label}")
            if detail:
                for line in str(detail).strip().splitlines()[:12]:
                    print(f"        {line}")

    def section(self, title: str) -> None:
        print(f"\n{title}")


def run(*args) -> tuple:
    r = subprocess.run([sys.executable, str(MOD / "tools" / "tgc.py"), *args],
                       cwd=MOD, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def clear_world() -> None:
    TMP_COUNTRIES.unlink(missing_ok=True)
    TMP_STATES.unlink(missing_ok=True)


# ---------------------------------------------------------------------------


def test_parser(s: Suite) -> None:
    s.section("parser")
    src = ('GER = { color = hsv{ 0.99 0.7 0.9 } cultures = { a b } }\n'
           'X = { k = 1 k = 2 l = { "q" w } n = { { p } { r } } c > 3 t ?= yes }')
    n = pdx.parse(src)
    g = n.get_node("GER")
    s.check("list values", g.get_list("cultures") == ["a", "b"])
    s.check("typed block", g.get("color").node.values() == ["0.99", "0.7", "0.9"])
    x = n.get_node("X")
    s.check("repeated keys preserved", x.getall("k") == ["1", "2"])
    s.check("later key wins", x.get_str("k") == "2")
    s.check("quoted and bare mix", x.get_list("l") == ["q", "w"])
    s.check("anonymous blocks", [b.values() for b in x.get_node("n").blocks()]
            == [["p"], ["r"]])
    s.check("comparison operator", [(i.op, i.value) for i in x.items
                                    if i.key == "c"] == [(">", "3")])
    s.check("round trip is stable", pdx.dumps(pdx.parse(pdx.dumps(n)))
            == pdx.dumps(n))

    # The whole install must parse, except vanilla's own broken dna_data files
    # (they ship with unbalanced braces; the portrait loader is lenient).
    bad = []
    for d in ("common", "map_data"):
        for f in (VANILLA / d).rglob("*.txt"):
            if "dna_data" in f.parts:
                continue
            try:
                pdx.parse_file(f)
            except pdx.PdxSyntaxError as e:
                bad.append(f"{f.name}: {e}")
    s.check(f"every vanilla common/ and map_data/ file parses", not bad,
            "\n".join(bad[:5]))


def test_generator(s: Suite) -> None:
    s.section("generator: output fidelity")
    write(TMP_COUNTRIES,
          "TUR:\n  country_type: recognized\n  tier: empire\n  cultures: [turkish]\n"
          "  religion: sunni\n  capital: EASTERN_THRACE\n"
          "  religion_split:\n    orthodox: {sunni: 0.35, orthodox: 0.65}\n"
          "ZZT:\n  country_type: decentralized\n  tier: principality\n"
          "  cultures: [turkish]\n  capital: ERZURUM\n"
          "ZZS:\n  country_type: unrecognized\n  tier: principality\n"
          "  cultures: [bulgarian]\n  religion: orthodox\n  capital: BULGARIA\n"
          "  overlord: TUR\n  subject_type: puppet\n")
    write(TMP_STATES,
          "STATE_EASTERN_THRACE: TUR\n"
          "STATE_ERZURUM:\n  owner: ZZT\n"
          "STATE_BULGARIA:\n  split:\n"
          "    - {owner: ZZS, provinces: [xC59A98, xF0A0A0, x64275F]}\n"
          "    - {owner: TUR, rest: true}\n")
    rc, out = run("build")
    s.check("build succeeds", rc == 0, out)

    index = json.loads((MOD / "build" / "index.json").read_text(encoding="utf-8"))
    states = pdx.parse_file(MOD / "common/history/states/tgc_states.txt").get_node("STATES")
    pops = pdx.parse_file(MOD / "common/history/pops/tgc_pops.txt").get_node("POPS")
    blds = pdx.parse_file(MOD / "common/history/buildings/tgc_buildings.txt").get_node("BUILDINGS")

    def owners(name):
        node = states.get_node(f"s:{name}")
        return [(cs.get_str("country").removeprefix("c:"),
                 cs.get_list("owned_provinces"))
                for cs in node.getall("create_state")] if node else []

    touched = {"STATE_EASTERN_THRACE", "STATE_ERZURUM", "STATE_BULGARIA"}
    differ = [n for n, rec in index["state_history"].items()
              if n not in touched
              and [(o["country"], o["provinces"]) for o in rec["owners"] if o["country"]]
              and owners(n) != [(o["country"], o["provinces"])
                                for o in rec["owners"] if o["country"]]]
    s.check("untouched states are byte-identical to vanilla ownership",
            not differ, f"{len(differ)} differ, e.g. {differ[:3]}")

    land = {n for n, st in index["states"].items() if not st["is_sea"]}
    emitted = {k.removeprefix("s:") for k in states.keys()}
    s.check("the whole land world is emitted (replace_paths wipes vanilla)",
            len(emitted) >= len(land) - 5, f"{len(emitted)} of {len(land)}")
    s.check("no sea region is emitted",
            not (emitted & {n for n, st in index["states"].items() if st["is_sea"]}))

    s.check("split: named provinces went to the vassal",
            sorted(dict(owners("STATE_BULGARIA")).get("ZZS", []))
            == sorted(["x64275F", "xC59A98", "xF0A0A0"]))
    o = dict(owners("STATE_BULGARIA"))
    s.check("split: rest went to the other owner and nothing overlaps",
            not (set(o.get("ZZS", [])) & set(o.get("TUR", [])))
            and set(o.get("ZZS", [])) | set(o.get("TUR", []))
            == set(index["states"]["STATE_BULGARIA"]["provinces"]))

    s.check("decentralized owner gets no buildings block",
            blds.get_node("s:STATE_ERZURUM") is None)
    s.check("...and vanilla did have buildings there",
            len(index["buildings"]["STATE_ERZURUM"]["by_country"]["TUR"]["types"]) > 0)

    et = pops.get_node("s:STATE_EASTERN_THRACE").get_node("region_state:TUR")
    got = [{"religion": p.get_str("religion"), "size": p.get_int("size")}
           for p in et.getall("create_pop")]
    van = index["pops"]["STATE_EASTERN_THRACE"]["by_country"]["TUR"]
    s.check("religion conversion preserves total population",
            sum(p["size"] for p in got) == sum(p["size"] for p in van))
    cul = index["defs"]["cultures"]
    van_orth = sum(p["size"] for p in van
                   if (p["religion"] or (cul.get(p["culture"]) or {}).get("religion"))
                   == "orthodox")
    got_orth = sum(p["size"] for p in got if p["religion"] == "orthodox")
    s.check("religion_split applies the declared fraction",
            abs(got_orth - van_orth * 0.65) <= 2, f"{got_orth} vs {van_orth * 0.65}")
    s.check("every generated pop carries an explicit religion",
            all(p["religion"] for p in got))

    cd = pdx.parse_file(MOD / "common/country_definitions/tgc_countries.txt")
    s.check("vanilla tag overridden with REPLACE_OR_CREATE",
            "REPLACE_OR_CREATE:TUR" in cd.keys(), str(cd.keys()))
    s.check("new tag written plainly", "ZZT" in cd.keys(), str(cd.keys()))

    meta = json.loads(META.read_text(encoding="utf-8"))
    s.check("replace_paths generated from what was actually written",
            sorted(meta["game_custom_data"]["replace_paths"])
            == ["common/history/buildings", "common/history/pops",
                "common/history/states"],
            str(meta["game_custom_data"]["replace_paths"]))

    rc, out = run("check")
    s.check("check is clean on a valid world", rc == 0, out)


def test_rules(s: Suite) -> None:
    s.section("check: every rule fires when it should")
    base_country = ("T1:\n  country_type: recognized\n  tier: kingdom\n"
                    "  cultures: [turkish]\n  capital: {cap}\n")

    meta_backup = META.read_text(encoding="utf-8")
    clear_world()
    run("build")
    m = json.loads(META.read_text(encoding="utf-8"))
    m["game_custom_data"]["replace_paths"] = ["common/history/military_formations"]
    META.write_text(json.dumps(m, indent="\t") + "\n", encoding="utf-8")
    rc, out = run("check")
    s.check("declared replace_paths with no mod file is an error",
            rc == 1 and "military_formations" in out, out)
    META.write_text(meta_backup, encoding="utf-8")

    write(TMP_COUNTRIES, base_country.format(cap="SVEALAND"))
    write(TMP_STATES, "STATE_ERZURUM:\n  owner: T1\n")
    run("build")
    rc, out = run("check")
    s.check("capital a country does not own is an error",
            rc == 1 and "STATE_SVEALAND is not owned by T1" in out, out[:800])

    write(TMP_COUNTRIES,
          "T1:\n  country_type: recognized\n  tier: empire\n  cultures: [turkish]\n"
          "  capital: ERZURUM\n"
          "T2:\n  country_type: recognized\n  tier: kingdom\n  cultures: [turkish]\n"
          "  capital: KONYA\n  overlord: T1\n  subject_type: vassal\n")
    write(TMP_STATES, "STATE_ERZURUM:\n  owner: T1\nSTATE_KONYA:\n  owner: T2\n")
    run("build")
    rc, out = run("check")
    s.check("vassal under a recognized overlord is an error",
            rc == 1 and "vassal needs an overlord of type" in out, out[:800])

    write(TMP_COUNTRIES, (MOD / "world/countries/t_selftest.yml")
          .read_text(encoding="utf-8").replace("vassal", "puppet"))
    run("build")
    rc, out = run("check")
    s.check("...and puppet under the same overlord is accepted", rc == 0, out[:800])

    write(TMP_COUNTRIES, "T1:\n  country_type: recognized\n  tier: kingdom\n"
                         "  cultures: [klingon]\n  religion: pastafarian\n"
                         "  capital: ERZURUM\n")
    write(TMP_STATES, "STATE_ERZURUM:\n  owner: T1\n")
    run("build")
    rc, out = run("check")
    s.check("unknown culture and religion are errors",
            rc == 1 and "klingon" in out and "pastafarian" in out, out[:800])

    write(TMP_STATES, "STATE_ERZURUM:\n  split:\n"
                      "    - {owner: T1, provinces: [xFFFFFF]}\n"
                      "    - {owner: TUR, rest: true}\n")
    rc, out = run("build")
    s.check("province not in the state is refused at build time",
            "not in this state region" in out, out[-500:])

    write(TMP_STATES, "STATE_ERZURUM:\n  owner: T1\n  poops: inherit\n")
    rc, out = run("build")
    s.check("an unknown world/ field is refused, never ignored",
            "unknown field" in out, out[-500:])

    META.write_text(meta_backup, encoding="utf-8")


def test_cleanup(s: Suite) -> None:
    s.section("build owns its output")
    write(TMP_COUNTRIES, "T1:\n  country_type: recognized\n  tier: kingdom\n"
                         "  cultures: [turkish]\n  capital: ERZURUM\n"
                         "  name: X\n  name_tr: Y\n")
    write(TMP_STATES, "STATE_ERZURUM:\n  owner: T1\n")
    run("build")
    tr = MOD / "localization/turkish/tgc_generated_countries_l_turkish.yml"
    s.check("a Turkish localization file is written for name_tr", tr.exists())
    write(TMP_COUNTRIES, "T1:\n  country_type: recognized\n  tier: kingdom\n"
                         "  cultures: [turkish]\n  capital: ERZURUM\n  name: X\n")
    run("build")
    s.check("...and removed again when name_tr is dropped", not tr.exists())

    clear_world()
    run("build")
    leftover = (list(MOD.glob("common/**/*.txt"))
                + list(MOD.glob("localization/**/*.yml")))
    s.check("an empty world/ leaves no generated game file at all",
            not leftover, str(leftover))
    meta = json.loads(META.read_text(encoding="utf-8"))
    s.check("...and replace_paths is emptied with it",
            meta["game_custom_data"]["replace_paths"] == [],
            str(meta["game_custom_data"]["replace_paths"]))


def test_read_only(s: Suite) -> None:
    s.section("the Victoria 3 install is never written to")
    import time
    recent = [p for d in ("common", "map_data", "localization")
              for p in (VANILLA / d).rglob("*")
              if p.is_file() and time.time() - p.stat().st_mtime < 7200]
    s.check("no file in the install was modified in the last two hours",
            not recent, str(recent[:3]))
    from vic3.paths import assert_read_only
    try:
        assert_read_only(VANILLA / "common" / "anything.txt")
        s.check("the write guard refuses install paths", False)
    except SystemExit:
        s.check("the write guard refuses install paths", True)


def main() -> int:
    s = Suite()
    dirty = [p for p in (TMP_COUNTRIES, TMP_STATES) if p.exists()]
    if dirty:
        print(f"refusing to run: {dirty} already exist")
        return 2
    meta_backup = META.read_text(encoding="utf-8")
    try:
        test_parser(s)
        test_generator(s)
        test_rules(s)
        test_cleanup(s)
        test_read_only(s)
    finally:
        clear_world()
        META.write_text(meta_backup, encoding="utf-8")
        run("build")
    print(f"\n{s.passed} passed, {s.failed} failed")
    return 1 if s.failed else 0


if __name__ == "__main__":
    sys.exit(main())
