"""Adversarial regressions discovered during the 2026-09-12 source audit."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import atlas_launcher
import selftest
from vic3 import build, check, development as dev, history, index, mechanics, pdx, scenario, worldplan
from vic3.world import World, WorldError


class ParserAudit(unittest.TestCase):
    def test_install_snapshot_compares_this_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'common').mkdir();file=root/'common/.DS_Store'
            file.write_bytes(b'pre-existing Finder file')
            before=selftest.install_snapshot(root)
            self.assertEqual(before,selftest.install_snapshot(root))
            file.write_bytes(b'changed during test')
            self.assertNotEqual(before,selftest.install_snapshot(root))
            file.unlink()
            self.assertNotEqual(before,selftest.install_snapshot(root))

    def test_unclosed_quote_and_unknown_delimiter_fail(self):
        for text in ('x = "unfinished', 'x = yes !'):
            with self.assertRaises(pdx.PdxSyntaxError):pdx.parse(text)

    def test_quoted_delimiters_and_backslashes_roundtrip(self):
        for text in (r'x = "<3"', r'x = "a\\b"', r'x = "a\"b"', r'"strange>key" = "v"'):
            tree=pdx.parse(text)
            self.assertEqual(tree,pdx.parse(pdx.dumps(tree)))
            self.assertEqual(pdx.dumps(tree),text)

    def test_spaced_typed_blocks_remain_typed(self):
        tree=pdx.parse('color = hsv { 0.1 0.2 0.3 }')
        self.assertIsInstance(tree.get('color'),pdx.TypedBlock)
        self.assertEqual(tree,pdx.parse(pdx.dumps(tree)))

    def test_all_ownership_blocks_count_and_scale(self):
        tree=pdx.parse('building = building_textile_mill add_ownership = { country = {country=c:FRA levels=4} } add_ownership = { country = {country=c:EGY levels=6} }')
        self.assertEqual(dev.level(tree),10)
        dev.set_levels(tree,5)
        self.assertEqual(dev.level(tree),5)
        self.assertEqual([n.get_node('country').get_int('levels') for n in tree.getall('add_ownership')],[2,3])


class EngineInputsAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=index.load();cls.data=mechanics.catalog()
        cls.world=scenario.overlay(World(),scenario.load(Path(__file__).parent/'tests/fixtures/ve_subjects_regression.yml'))
        cls.compiled=worldplan.compile_world(cls.world,cls.index)

    def test_level_edit_keeps_existing_methods_and_ownership(self):
        state='STATE_NEW_CASTILE';entry=self.index['buildings'][state]['by_country']['SPA']
        before=next(n for n in dev.building_records(entry['script']) if n.get_str('building')=='building_wheat_farm')
        self.assertEqual(len(before.getall('add_ownership')),2)
        result=dev.industry_plan(entry['script'],{'buildings':{'building_wheat_farm':10}},'SPA',state,self.data)
        after=next(n for n in dev.building_records(result) if n.get_str('building')=='building_wheat_farm')
        self.assertEqual(dev.level(after),10)
        self.assertEqual(before.get_list('activate_production_methods'),after.get_list('activate_production_methods'))
        self.assertEqual(len(after.getall('add_ownership')),2)

    def test_technology_grants_precede_companies_and_dependencies(self):
        node=worldplan.history_nodes(self.compiled[1]['common/history/countries/ve_scenario_countries.txt'])['EGY']
        keys=node.keys();self.assertLess(keys.index('add_technology_researched'),keys.index('add_company'))
        values=node.getall('add_technology_researched')
        self.assertLess(values.index('stock_exchange'),values.index('corporate_charters'))

    def test_inherited_company_cannot_keep_lost_headquarters(self):
        world=scenario.overlay(World(),{'version':2,'states':{'STATE_ALSACE_LORRAINE':'PRU'}})
        res=build.Resolved(world,self.index)
        with self.assertRaisesRegex(WorldError,'headquarters.*no longer owned'):
            history.compile_countries(res,self.data)

    def test_inherited_institution_requires_enabling_law(self):
        world=scenario.overlay(World(),{'version':2,'countries':{'FRA':{'laws':{'mode':'replace','values':['law_monarchy']}}}})
        with self.assertRaisesRegex(WorldError,'inherited.*no enabling law'):
            history.compile_countries(build.Resolved(world,self.index),self.data)

    def test_laws_precede_inherited_institution_effects(self):
        world=scenario.overlay(World(),{'version':2,'countries':{'FRA':{'laws':{'values':['law_public_schools']}}}})
        text=history.compile_countries(build.Resolved(world,self.index),self.data)[0]
        keys=worldplan.history_nodes(text)['FRA'].keys()
        institutions=[i for i,k in enumerate(keys) if k=='set_institution_investment_level']
        self.assertTrue(institutions)
        self.assertLess(max(i for i,k in enumerate(keys) if k=='activate_law'),min(institutions))

    def test_headquarters_needs_owned_state(self):
        res=self.compiled[0];techs={t:set(c['technologies']) for t,c in self.compiled[2]['countries'].items()}
        far=next(k for k,v in self.data['strategic_regions'].items() if v['states'] and not any(history.owns(res,'EGY',s) for s in v['states']))
        plan={'mode':'replace','formations':[{'type':'army','hq_region':far,'units':[{'type':'combat_unit_type_irregular_infantry','state':'LOWER_EGYPT','count':1}]}]}
        with patch.object(self.world.countries['EGY'],'military',plan),self.assertRaisesRegex(WorldError,'headquarters.*no owned state'):
            history.compile_military(res,self.data,techs,[])

    def test_no_country_specific_default_subject_type(self):
        _,_,types,actions,loc=history.custom_subjects(World(version=2),self.data)
        self.assertEqual((types,actions,loc),('','',[]))
        bad=World(version=2,subject_types={'ve_generic':{'overlord_types':['not_a_country_type']}})
        with self.assertRaises(WorldError):history.custom_subjects(bad,self.data)

    def test_generated_snapshot_detects_edit_and_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);build.build(False,world_override=self.world,output_root=root,compiled=self.compiled)
            changed=root/'common/history/countries/ve_scenario_countries.txt'
            changed.write_text(changed.read_text(encoding='utf-8')+'\n# manual edit')
            (root/'common/history/pops/tgc_pops.txt').unlink()
            rep=check.Report()
            with patch.object(check,'MOD',root):check._rule_generated_snapshot(rep,self.world,self.index,self.compiled)
            self.assertTrue(any('Stale or edited' in m for _,m in rep.errors))
            self.assertTrue(any('Missing' in m for _,m in rep.errors))

    def test_changed_source_invalidates_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);build.build(False,world_override=self.world,output_root=root,compiled=self.compiled)
            world=copy.deepcopy(self.world);world.countries['EGY'].population['literacy']=.2
            compiled=worldplan.compile_world(world,self.index);rep=check.Report()
            with patch.object(check,'MOD',root):check._rule_generated_snapshot(rep,world,self.index,compiled)
            self.assertTrue(any('population/ve_scenario_population' in m for _,m in rep.errors))

    def test_failed_write_restores_entire_previous_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);build.build(False,world_override=self.world,output_root=root,compiled=self.compiled)
            before={p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()}
            original=build.write_text;calls=0
            def fail_second(*args,**kwargs):
                nonlocal calls
                calls+=1
                if calls==2:raise OSError('simulated disk failure')
                return original(*args,**kwargs)
            with patch.object(build,'write_text',side_effect=fail_second),self.assertRaisesRegex(OSError,'simulated'):
                build.build(False,world_override=self.world,output_root=root,compiled=self.compiled)
            after={p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before,after)

    def test_cache_refreshes_for_changed_game(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'index.json';path.write_text(json.dumps({'meta':{'source_signature':'old'}}))
            with patch.multiple(index,INDEX_PATH=path,_INDEX_CACHE=None),patch.object(index,'source_signature',return_value='new'),patch.object(index,'build_index',return_value={'fresh':True}) as rebuild:
                self.assertEqual(index.load(),{'fresh':True});rebuild.assert_called_once()


class LauncherAudit(unittest.TestCase):
    def test_preview_command_does_not_build_active_mod(self):
        with patch.object(atlas_launcher,'environment',return_value=Path('/fake/python')),patch.object(atlas_launcher,'execute') as run,patch.object(atlas_launcher.webbrowser,'open') as browser:
            self.assertEqual(atlas_launcher.main(['--no-browser']),0)
            self.assertEqual(run.call_args.args[0][2],'atlas')
            browser.assert_not_called()

    def test_dragged_path_with_spaces(self):
        with tempfile.TemporaryDirectory(prefix='atlas test ') as tmp:
            path=Path(tmp)/'senaryo örnek.yml';path.write_text('version: 2')
            self.assertEqual(atlas_launcher.input_path('"'+str(path)+'"'),path.resolve())

    def test_preview_cannot_accidentally_apply_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'scenario.yml';path.write_text('version: 2')
            with self.assertRaises(ValueError):atlas_launcher.main([str(path),'--build'])


if __name__=='__main__':unittest.main()
