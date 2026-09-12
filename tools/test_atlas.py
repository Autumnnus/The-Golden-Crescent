"""Small deterministic regressions for map geometry and scenario contracts.

Run: .venv/bin/python -m unittest discover -s tools -p 'test_atlas.py' -v
No world/ writes; fixtures are synthetic, geometry-cache tests use temp dirs.
"""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from vic3 import atlas, geo, scenario
from vic3.build import Resolved
from vic3.mapdraw import _crop_box, _religion_color
from vic3.paths import VANILLA
from vic3.world import Country, World, WorldError


def fixture():
    return {
        "states": {
            "STATE_A": {"is_sea": False, "provinces": ["x010101", "x020202", "x030303"],
                        "impassable": ["x030303"], "file": "01_test.txt"},
            "STATE_SEA": {"is_sea": True, "provinces": ["x040404"], "impassable": [], "file": "99_sea.txt"}},
        "countries": {"AA": {"color": [20, 80, 120], "religion": "sunni"},
                      "BB": {"color": [230, 120, 40], "religion": "catholic"}},
        "state_history": {"STATE_A": {"owners": [{"country": "AA", "provinces": ["x010101", "x020202"], "state_type": None}]}},
        "loc": {}, "defs": {"religions": {}},
    }


def plan(spec, countries=None):
    data = {"version": 1, "states": {"STATE_A": spec}, "countries": countries or {}}
    result = scenario.overlay(World(), data)
    scenario.validate_world(result, fixture())
    return result


class ScenarioTests(unittest.TestCase):
    def test_whole_state_and_rest_match_generator(self):
        w = plan({"split": [{"owner": "BB", "provinces": ["x010101"]}, {"owner": "AA", "rest": True}]})
        resolved = Resolved(w, fixture(), contents=False)
        self.assertEqual(atlas.owner_map(resolved), {("STATE_A", "x010101"): "BB", ("STATE_A", "x020202"): "AA"})
        self.assertEqual(resolved.state_pops, {})
        self.assertEqual(resolved.state_buildings, {})

    def test_country_overlay_does_not_mutate_or_reset_base(self):
        base = World(countries={"AA": Country("AA", name="Old", phase=None, cultures=["turkish"], color=[10,20,30])})
        result = scenario.overlay(base, {"version":1,"countries":{"AA":{"name":"New"}}})
        self.assertEqual(base.countries["AA"].name, "Old")
        self.assertEqual(result.countries["AA"].cultures, ["turkish"])
        self.assertIsNone(result.countries["AA"].phase)
        self.assertEqual(result.countries["AA"].color, [10,20,30])

    def test_duplicate_province_rejected(self):
        with self.assertRaisesRegex(WorldError, "assigned twice"):
            plan({"split":[{"owner":"AA","provinces":["x010101","x010101"]},{"owner":"BB","rest":True}]})

    def test_unknown_province_rejected(self):
        with self.assertRaisesRegex(WorldError, "not in this state"):
            plan({"split":[{"owner":"AA","provinces":["xFFFFFF"]},{"owner":"BB","rest":True}]})

    def test_missing_land_rejected(self):
        with self.assertRaisesRegex(WorldError, "no owner"):
            plan({"split":[{"owner":"AA","provinces":["x010101"]}]})

    def test_unassigned_impassable_is_valid(self):
        plan({"split":[{"owner":"AA","provinces":["x010101","x020202"]}]})

    def test_unknown_owner_rejected(self):
        with self.assertRaisesRegex(WorldError, "unknown owner"):
            plan("ZZ")

    def test_new_country_can_own_land(self):
        w=plan("ZZ", {"ZZ":{"name":"New","color":[1,100,200]}})
        self.assertEqual(Resolved(w, fixture(), contents=False).state_owners["STATE_A"][0][0], "ZZ")

    def test_ambiguous_rest_rejected(self):
        for spec in [
            {"split":[{"owner":"AA","rest":True,"provinces":["x010101"]}]},
            {"split":[{"owner":"AA","rest":"false"}]},
            {"split":[{"owner":"AA","rest":True},{"owner":"BB","rest":True}]},
            {"split":[]}, {"owner":"AA","split":[]}, {"split":"AA"},
        ]:
            with self.subTest(spec=spec), self.assertRaises(WorldError):plan(spec)

    def test_duplicate_keys_fail_even_in_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"scenario.json"
            p.write_text('{"version":1,"states":{"STATE_A":"AA","STATE_A":"BB"}}')
            with self.assertRaisesRegex(WorldError, "duplicate key"):scenario.load(p)

    def test_alias_collision_in_same_document(self):
        with self.assertRaisesRegex(WorldError, "already defined"):
            scenario.overlay(World(), {"version":1,"states":{"A":"AA","STATE_A":"BB"}})

    def test_unknown_state_sea_bad_fields_and_version(self):
        for data in [{"version":3}, {"version":True}, {"version":1,"typo":{}},
                     {"version":1,"states":{"WRONG":"AA"}},
                     {"version":1,"states":{"STATE_SEA":"AA"}},
                     {"version":1,"countries":{"AA":{"color":[0,1,999]}}}]:
            with self.subTest(data=data), self.assertRaises(WorldError):
                scenario.validate_world(scenario.overlay(World(),data),fixture())

    def test_geometry_patches_fail_explicitly(self):
        with self.assertRaisesRegex(WorldError, "geometry patches"):
            scenario.validate_world(World(region_patches={"STATE_A":{"provinces":[]}}),fixture())

    def test_null_phase_is_not_string_none(self):
        w = plan({"owner":"AA","phase":None})
        self.assertIsNone(w.states["STATE_A"].phase)


class RenderTests(unittest.TestCase):
    def snapshot(self):
        s=atlas.Snapshot.__new__(atlas.Snapshot)
        s.index=fixture();s.world=plan({"split":[{"owner":"BB","provinces":["x010101"]},{"owner":"AA","rest":True}]})
        s.res=Resolved(s.world,s.index,contents=False)
        s.before=Resolved(World(),s.index,contents=False);s.base=s.before
        s.order=["STATE_A","STATE_SEA"]
        s.adjacency={"STATE_A":["STATE_SEA"],"STATE_SEA":["STATE_A"]}
        s.provinces=[None,
            {"hex":"x010101","state":0,"owner":"BB","before":"AA","impassable":False},
            {"hex":"x020202","state":0,"owner":"AA","before":"AA","impassable":False},
            {"hex":"x030303","state":0,"owner":None,"before":None,"impassable":True},
            {"hex":"x040404","state":1,"owner":None,"before":None,"impassable":False}]
        return s

    def test_split_render_uses_province_owner_not_majority(self):
        s=self.snapshot();view={"pixels":np.array([[1,2,3,4]],dtype=np.uint32)}
        pixels=np.asarray(s.image(view,borders="none"))
        self.assertEqual(pixels[0,0].tolist(),[230,120,40])
        self.assertEqual(pixels[0,1].tolist(),[20,80,120])
        self.assertNotEqual(pixels[0,2].tolist(),pixels[0,1].tolist())
        self.assertEqual(np.asarray(s.image(view,before=True,borders="none"))[0,0].tolist(),[20,80,120])

    def test_changes_only_highlights_transferred_provinces(self):
        colors=self.snapshot().colors("changes")
        self.assertEqual(colors[1].tolist(),[230,174,78])
        self.assertEqual(colors[2].tolist(),[96,116,123])

    def test_state_phase_takes_precedence(self):
        s=self.snapshot();s.world.states["STATE_A"].phase="2"
        colors=s.colors("phase")
        np.testing.assert_array_equal(colors[1],colors[2])

    def test_region_state_does_not_include_entire_adjacent_sea(self):
        s=self.snapshot();meta={"states":{"STATE_A":{"bbox":[100,100,200,200]},"STATE_SEA":{"bbox":[0,0,8000,3000]}}}
        box,label=_crop_box("A",s.index,meta,s.adjacency)
        self.assertLess(box[2],300)
        self.assertEqual(label,"STATE_A")

    def test_country_crop_and_empty_country_error(self):
        s=self.snapshot();meta={"states":{"STATE_A":{"bbox":[100,100,200,200]}}}
        box,label=_crop_box("BB",s.index,meta,s.adjacency,world=s.world,owners=s.res.state_owners)
        self.assertEqual(label,"BB")
        with self.assertRaisesRegex(ValueError,"no land"):
            _crop_box("BB",s.index,meta,s.adjacency,owners={})

    def test_safe_output_refuses_install(self):
        with self.assertRaises(SystemExit):atlas.write_output(VANILLA/"never-write-atlas-test.json","test")

    def test_cache_requires_all_files_and_matching_signature(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths={key:Path(tmp)/key for key in ("STATE_IDS","GEO_META","ADJACENCY","PROVINCE_CODES")}
            for path in paths.values():path.touch()
            paths["GEO_META"].write_text(json.dumps({"meta":{"signature":{"version":2}}}))
            with patch.multiple(geo,**paths),patch.object(geo,"_signature",return_value={"version":2}):
                self.assertTrue(geo.is_current(fixture()))
                paths["ADJACENCY"].unlink()
                self.assertFalse(geo.is_current(fixture()))
            paths["ADJACENCY"].touch()
            with patch.multiple(geo,**paths),patch.object(geo,"_signature",return_value={"version":3}):
                self.assertFalse(geo.is_current(fixture()))

    def test_stable_color_hash(self):
        self.assertEqual(atlas.stable_number("test"),2949673445)
        self.assertEqual(_religion_color("fictional",fixture()),_religion_color("fictional",fixture()))


if __name__ == "__main__":
    unittest.main()
