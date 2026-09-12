"""Regression tests against installed startup syntax and exact scenario semantics.

Run: PYTHONPATH=tools .venv/bin/python -m unittest tools/test_scenario.py -v
Only generated preview files in temporary directories are written.
"""
import copy
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from vic3 import build, development as dev, history, index, mechanics, pdx, scenario, worldplan
from vic3.world import World, WorldError


class PopulationTests(unittest.TestCase):
    def test_exact_integer_apportionment(self):
        self.assertEqual(dev.apportion(7,[.5,.3,.2]),[4,2,1])
        self.assertEqual(sum(dev.apportion(9999991,[.333333,.333333,.333334])),9999991)

    def test_joint_composition_is_not_independent(self):
        rows=dev.population_plan([],{'total':101,'composition':[
            {'culture':'misri','religion':'sunni','share':.8},
            {'culture':'misri','religion':'oriental_orthodox','share':.2}]})
        self.assertEqual([p['size'] for p in rows],[81,20])

    def test_marginals_cross_product(self):
        rows=dev.population_plan([],{'total':100,'cultures':{'a':.6,'b':.4},'religions':{'x':.7,'y':.3}})
        self.assertEqual([r['size'] for r in rows],[42,18,28,12])

    def test_narrower_plan_replaces_incompatible_population_fields(self):
        plan=dev.merged_population({'total':100,'composition':[{}],'literacy':.2}, {'scale':2,'cultures':{'a':1}}, {'literacy':.5})
        self.assertNotIn('total',plan);self.assertNotIn('composition',plan)
        self.assertEqual(plan['literacy'],.5)

    def test_bad_fractions_rejected(self):
        for fractions in ({'a':60,'b':40},{'a':.2,'b':.3},{'a':float('nan')},{'a':True}):
            with self.subTest(fractions=fractions),self.assertRaises(WorldError):dev.shares(fractions,'test')


class ScenarioIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=index.load();cls.data=mechanics.catalog()
        cls.doc=scenario.load(Path(__file__).parent/'tests/fixtures/ve_subjects_regression.yml')
        cls.world=scenario.overlay(World(),cls.doc)
        cls.compiled=worldplan.compile_world(cls.world,cls.index)

    def test_v2_partial_country_retains_vanilla_classification(self):
        world=scenario.overlay(World(),{'version':2,'countries':{'EGY':{'population':{'literacy':.6}}}})
        self.assertEqual(world.countries['EGY'].country_type,self.index['countries']['EGY']['country_type'])
        self.assertEqual(world.countries['EGY'].tier,self.index['countries']['EGY']['tier'])

    def test_example_exact_population_and_real_startup_effects(self):
        res,files,report=self.compiled
        egypt=report['states']['STATE_LOWER_EGYPT']['owners']['EGY']
        self.assertEqual(egypt['population'],2500000)
        self.assertEqual(egypt['cultures'],{'misri':2375000,'turkish':125000})
        self.assertEqual(egypt['religions']['oriental_orthodox'],375000)
        text=files['common/history/countries/ve_scenario_countries.txt']
        self.assertIn('add_company = company_type:company_misr',text)
        self.assertIn('activate_law = law_type:law_public_schools',text)
        self.assertIn('set_pop_literacy',files['common/history/population/ve_scenario_population.txt'])
        self.assertEqual(report['countries']['EGY']['military'],{'battalions':25,'ships':5})
        self.assertEqual(report['countries']['FRA']['building_levels'],0)
        self.assertEqual(res.country_type('EGY'),'unrecognized')

    def test_recognized_feudal_vassal_and_final_desire_order(self):
        _,files,report=self.compiled
        self.assertEqual(report['diplomacy']['overlords']['ZBR'],'FRA')
        typ=pdx.parse(files['common/subject_types/ve_scenario_subjects.txt']).get_node('subject_type_ve_feudal_vassal')
        self.assertIn('recognized',typ.get_list('valid_overlord_country_types'))
        self.assertIn('great_power',typ.get_list('valid_overlord_ranks'))
        text=files['common/history/diplomacy/ve_scenario_diplomacy.txt']
        self.assertLess(text.index('type = ve_feudal_vassal'),text.index('subtract = liberty_desire'))

    def test_empty_homelands_clear_and_economic_only_state_keeps_owner(self):
        world=scenario.overlay(World(),{'version':2,'states':{'LOWER_EGYPT':{'homelands':[],'state_type':'unincorporated','population':{'literacy':.9}}}})
        res=build.Resolved(world,self.index)
        self.assertEqual(res.state_homelands['STATE_LOWER_EGYPT'],[])
        self.assertEqual(res.state_owners['STATE_LOWER_EGYPT'][0][0],'EGY')
        self.assertEqual(res.state_owners['STATE_LOWER_EGYPT'][0][2],'unincorporated')
        self.assertEqual(res.population_settings['STATE_LOWER_EGYPT','EGY']['literacy'],.9)

    def test_unknown_ids_and_invalid_shapes_rejected(self):
        for plan in ({'cultures':{'nonexistent':1}}, {'by_owner':[]}, {'literacy':1.1}):
            with self.subTest(plan=plan),self.assertRaises(WorldError):dev.validate_population(plan,self.data,'test',True)
        with self.assertRaises(WorldError):dev.validate_industry({'buildings':{'building_iron_mine':{'level':2,'production_methods':['pm_basic_farming']}}},self.data,'test')

    def test_technology_removal_cannot_leave_dependent_technology(self):
        from vic3.world import Country
        c=Country('EGY',technology={'mode':'replace','add':['corporate_charters'],'remove':['stock_exchange']})
        with self.assertRaisesRegex(WorldError,'still required'):history.effective_tech(c,pdx.Node(),self.data)

    def test_unknown_or_duplicate_law_group(self):
        from vic3.world import Country
        c=Country('FRA',laws={'values':['law_monarchy','law_presidential_republic']})
        with self.assertRaisesRegex(WorldError,'Two selected laws'):history.effective_laws(c,pdx.Node(),self.data)

    def test_resource_cap_and_inland_port(self):
        for state,building,count,match in [('ERZURUM','building_iron_mine',999,'resource cap'),('ERZURUM','building_port',1,'coastal'),('LOWER_EGYPT','building_iron_mine',1,'no resource deposit')]:
            doc={'version':2,'countries':{'TUR':{'technology':{'tier':1}},'EGY':{'technology':{'tier':1}}},
                 'states':{state:{'industry':{'buildings':{building:count}}}}}
            with self.subTest(building=building,state=state),self.assertRaisesRegex(WorldError,match):worldplan.compile_world(scenario.overlay(World(),doc),self.index)

    def test_dependency_cycle_and_landless_target_rejected(self):
        res=self.compiled[0];defs,actions,*_=history.custom_subjects(self.world,self.data)
        for edges,match in [([{'overlord':'FRA','subject':'ZBR','type':'ve_feudal_vassal'}, {'overlord':'ZBR','subject':'FRA','type':'ve_feudal_vassal'}],'cycle'),
                            ([{'overlord':'FRA','subject':'ZZZ','type':'ve_feudal_vassal'}],'no land')]:
            with patch.object(self.world,'diplomacy_policy',{'mode':'replace','subjects':edges}):
                with self.assertRaisesRegex(WorldError,match):history.compile_diplomacy(res,self.data,defs,actions,[])

    def test_diplomacy_replace_removes_vanilla_subjects(self):
        res=self.compiled[0];defs,actions,*_=history.custom_subjects(self.world,self.data)
        with patch.object(self.world,'diplomacy_policy',{'mode':'replace'}):
            text,report=history.compile_diplomacy(res,self.data,defs,actions,[])
        self.assertEqual(report['overlords'],{});self.assertNotIn('create_diplomatic_pact',text)

    def test_bic_partition_preserves_other_owners_and_replaces_dependencies(self):
        countries={}
        for tag,capital,culture in [('ZBN','EAST_BENGAL','bengali'),('ZMD','MADRAS','tamil'),('ZBM','BOMBAY','marathi')]:
            countries[tag]={'name':tag,'color':[100,150,180],'capital':capital,'cultures':[culture],
                            'religion':'hindu','country_type':'unrecognized','technology':{'tier':1},
                            'military':{'mode':'replace'}}
        states={}
        for name,hist in self.index['state_history'].items():
            owners=hist.get('owners',[])
            if not any(o['country']=='BIC' for o in owners):continue
            tag='ZMD' if name in ('STATE_MADRAS','STATE_MYSORE','STATE_TRAVANCORE','STATE_KURNOOL','STATE_CIRCARS') else 'ZBM' if name in ('STATE_BOMBAY','STATE_GUJARAT','STATE_RAJPUTANA','STATE_CENTRAL_PROVINCES') else 'ZBN'
            states[name]={'split':[{'owner':tag if o['country']=='BIC' else o['country'],'provinces':o['provinces']} for o in owners]}
        doc={'version':2,'countries':countries,'states':states,
             'subject_types':{'ve_indian_vassal':{'base':'vassal','can_have_subjects':True}},
             'diplomacy':{'reset_countries':['BIC'],'subjects':[
                 {'overlord':'ZBN','subject':'ZMD','type':'ve_indian_vassal'},
                 {'overlord':'ZMD','subject':'ZBM','type':'ve_indian_vassal'}]}}
        res,files,report=worldplan.compile_world(scenario.overlay(World(),doc),self.index)
        self.assertNotIn('BIC',res.landed_tags)
        self.assertNotIn('BIC',report['diplomacy']['overlords'])
        self.assertNotIn('BIC',report['diplomacy']['overlords'].values())
        self.assertEqual(report['diplomacy']['overlords']['ZBM'],'ZMD')
        self.assertNotIn('c:BIC',files['common/history/diplomacy/ve_scenario_diplomacy.txt'])
        for state in states:
            for old in self.index['state_history'][state]['owners']:
                if old['country']=='BIC':continue
                preserved={p for t,provs,_ in res.state_owners[state] if t==old['country'] for p in provs}
                self.assertEqual(preserved,set(old['provinces']))

    def test_generated_bundle_replaces_complete_history_and_keeps_user_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);user=root/'common/history/countries/handwritten.txt';user.parent.mkdir(parents=True);user.write_text('# keep')
            result=build.build(False,world_override=self.world,output_root=root,compiled=self.compiled)
            meta=json.loads((root/'.metadata/metadata.json').read_text())
            self.assertEqual(set(result['replace_paths']),build.NEEDS_REPLACE_PATH)
            self.assertEqual(set(meta['game_custom_data']['replace_paths']),build.NEEDS_REPLACE_PATH)
            self.assertEqual(user.read_text(),'# keep')
            for rel in result['written']:
                if rel.endswith('.txt'):pdx.parse_file(root/rel)
            self.assertTrue((root/'common/history/pops/tgc_pops.txt').read_bytes().startswith(b'\xef\xbb\xbf'))
            from vic3 import check
            captured=io.StringIO()
            with patch.object(check,'MOD',root),patch.object(check,'load_world',return_value=self.world),contextlib.redirect_stdout(captured):
                code=check.check(False)
            self.assertEqual(code,0,captured.getvalue())

    def test_explicit_empty_building_world_still_replaces_vanilla(self):
        res,files,report=self.compiled
        empty=copy.copy(res);empty.state_buildings={}
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            result=build.build(False,world_override=self.world,output_root=root,compiled=(empty,files,report))
            self.assertIn('common/history/buildings',result['replace_paths'])
            self.assertEqual(pdx.parse_file(root/'common/history/buildings/tgc_buildings.txt').get_node('BUILDINGS').items,[])

    def test_manual_history_is_not_executed_twice(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            manual=root/'common/history/countries/manual.txt';manual.parent.mkdir(parents=True)
            manual.write_text('COUNTRIES = { c:EGY = { add_technology_researched = academia } }')
            old=manual.with_name('ve_scenario_countries.txt');old.write_text('# previous output')
            with self.assertRaisesRegex(build.BuildError,'execute twice'):
                build.build(False,world_override=self.world,output_root=root,compiled=self.compiled)
            self.assertEqual(old.read_text(),'# previous output')

    def test_invalid_build_leaves_previous_output_untouched(self):
        world=copy.deepcopy(self.world);world.countries['EGY'].population={'literacy':9}
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);old=root/'common/history/countries/ve_scenario_countries.txt';old.parent.mkdir(parents=True);old.write_text('keep prior output')
            with self.assertRaises(WorldError):build.build(False,world_override=world,output_root=root)
            self.assertEqual(old.read_text(),'keep prior output')

    def test_canonical_source_load_and_schema(self):
        from vic3 import world as world_module, schema
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'scenario.yml').write_text('version: 2\ncountries:\n  EGY:\n    population: {literacy: 0.6}\n')
            with patch.object(world_module,'WORLD',root):loaded=world_module.load_world()
            self.assertEqual(loaded.version,2);self.assertEqual(loaded.countries['EGY'].population['literacy'],.6)
        self.assertEqual(schema.document()['properties']['version'],{'const':2})


if __name__=='__main__':unittest.main()
