"""Real-source integration and adversarial tests; all writes stay under build/.

Approval receipts here are synthetic test fixtures, never user approvals.
"""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from vic3 import pdx
from vic3.paths import MOD
from studio import compiler
from studio.model import Plan, load
from studio.preview import write_preview
from studio.source import Sources, FlavorError

EXAMPLE=MOD/'tools/flavor/examples/academy.yml'


class FlavorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=Sources();cls.document=load(EXAMPLE)
        (MOD/'build/flavor-tests').mkdir(parents=True,exist_ok=True)

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=MOD/'build/flavor-tests')
        self.root=Path(self.temp.name)

    def tearDown(self):self.temp.cleanup()

    def plan(self,doc=None,path=EXAMPLE):
        sources=copy.copy(self.source);sources.used=dict(self.source.used);sources.countries_used=set()
        return Plan(copy.deepcopy(self.document if doc is None else doc),path,sources)

    def receipt(self,plan):
        p=self.root/'synthetic-test-approval.json'
        p.write_text(json.dumps({'kind':'flavor-approval-v1','approved':True,'namespace':plan.namespace,'fingerprint':plan.fingerprint()}))
        return p

    def invalid(self,change,pattern=None):
        doc=copy.deepcopy(self.document);change(doc)
        with self.assertRaisesRegex(FlavorError,pattern or '.'):self.plan(doc)

    def test_example_is_connected_and_has_all_outcomes(self):
        p=self.plan();self.assertEqual(len(p.nodes),5);self.assertEqual(len(p.edges),5)
        self.assertFalse(p.report()['runtime_tested']);self.assertEqual(p.report()['validation_scope'],'static_source')

    def test_unknown_keys_never_silently_disappear(self):
        self.invalid(lambda d:d['nodes']['petition'].update(triger={'always':True}),'triger')
        self.invalid(lambda d:d.update(events={}),'events')

    def test_duplicate_yaml_and_json_keys_fail(self):
        for raw in ('version: 1\nversion: 1\n','{"version":1,"version":1}'):
            path=self.root/'plan.yml';path.write_text(raw)
            with self.assertRaises(FlavorError):load(path)

    def test_recursive_yaml_alias_fails_cleanly(self):
        path=self.root/'plan.yml';path.write_text('loop: &a [*a]')
        with self.assertRaisesRegex(FlavorError,'alias'):load(path)

    def test_missing_graph_target(self):
        self.invalid(lambda d:d['nodes']['petition']['options'][0]['next'][0].update(to='missing'),'hedef')

    def test_unreachable_event(self):
        self.invalid(lambda d:d['nodes']['petition']['options'][1].pop('next'),'ulaşılamayan')

    def test_cycle_is_rejected(self):
        self.invalid(lambda d:d['nodes']['opening']['options'][0].update(next=[{'to':'petition'}]),'döngüsü')

    def test_entry_required(self):
        self.invalid(lambda d:d['nodes']['petition'].pop('entry'),'entry')

    def test_duplicate_event_number(self):
        self.invalid(lambda d:d['nodes']['opening'].update(number=1),'number')

    def test_boolean_is_not_a_number(self):
        self.invalid(lambda d:d['nodes']['petition'].update(number=True),'sayı')

    def test_zero_delay_is_rejected(self):
        self.invalid(lambda d:d['nodes']['petition']['options'][0]['next'][0].update(delay_days=0),'delay_days')

    def test_default_cannot_be_conditional(self):
        self.invalid(lambda d:d['nodes']['petition']['options'][0].update(when={'always':True}),'varsayılan')

    def test_missing_and_multiple_defaults(self):
        self.invalid(lambda d:d['nodes']['petition']['options'][0].pop('default'),'varsayılan')
        self.invalid(lambda d:d['nodes']['petition']['options'][1].update(default=True),'varsayılan')

    def test_unknown_country_technology_culture_religion(self):
        self.invalid(lambda d:d['nodes']['petition'].update(country='XYZ404'),'countries')
        for op in ('technology','primary_culture','state_religion'):
            with self.subTest(op=op):self.invalid(lambda d:d['nodes']['petition'].update(trigger={op:'made_up'}),'Bilinmeyen')

    def test_country_and_population_culture_have_different_scopes(self):
        p=self.plan()
        self.assertEqual(p.condition({'primary_culture':'misri'}),'country_has_primary_culture = cu:misri')
        self.assertEqual(p.condition({'has_culture_pop':'misri'}),'any_scope_pop = { culture = cu:misri }')
        self.assertEqual(p.condition({'state_religion':'sunni'}),'country_has_state_religion = rel:sunni')

    def test_variable_typo_and_bad_type(self):
        for value in ('unwritten',[]):
            self.invalid(lambda d:d['nodes']['petition'].update(trigger={'has_variable':value}),'değişken')

    def test_calendar_and_empty_windows(self):
        self.invalid(lambda d:d['nodes']['petition'].update(trigger={'after':'1836.2.31'}),'tarih')
        self.invalid(lambda d:d['nodes']['petition'].update(trigger={'after':'1850.1.1','before':'1836.1.1'}),'aralığı')

    def test_no_unchecked_raw_pdx(self):
        self.invalid(lambda d:d['nodes']['petition'].update(immediate=[{'raw':'bad_effect=yes'}]),'raw')

    def test_no_unbound_localization_scopes(self):
        self.invalid(lambda d:d['nodes']['petition']['title'].update(tr='[SCOPE.bad.GetName]'),'localization')

    def test_missing_translation(self):
        self.invalid(lambda d:d['nodes']['petition']['title'].pop('en'),'metin')

    def test_wrong_journal_and_event_fields(self):
        self.invalid(lambda d:d['nodes']['academy'].update(options=[]),'geçersiz alan')
        self.invalid(lambda d:d['nodes']['academy'].pop('timeout_days'),'timeout_days')

    def test_gfx_is_resolved_from_real_game(self):
        p=self.plan();self.assertTrue(any('media_aliases' in path for path in p.sources.used))
        self.assertTrue(any(path.endswith('.bk2') for path in p.sources.used))
        self.invalid(lambda d:d['nodes']['petition'].update(media={'alias':'imaginary_media'}),'media')
        self.invalid(lambda d:d['nodes']['petition'].update(icon='gfx/missing.dds'),'bulunamadı')

    def test_asset_traversal_and_fake_bink(self):
        p=self.plan()
        with self.assertRaises(FlavorError):p.local_asset('../README.md',{'.md'})
        (self.root/'fake.bk2').write_bytes(b'not a bink')
        doc=copy.deepcopy(self.document);doc['nodes']['petition']['media']={'video':'fake.bk2','fallback':'middleeast_engineer_blueprint'}
        with self.assertRaisesRegex(FlavorError,'Bink'):self.plan(doc,self.root/'plan.yml')

    def test_custom_dds_is_checked_and_bundled(self):
        from PIL import Image
        Image.new('RGBA',(64,64),(40,80,120,255)).save(self.root/'icon.dds')
        doc=copy.deepcopy(self.document);doc['nodes']['petition']['icon']={'file':'icon.dds'}
        p=self.plan(doc,self.root/'plan.yml');files=compiler.render(p)
        self.assertEqual(len([n for n in files if n.endswith('.dds')]),1)

    def test_approval_required_and_mutations_invalidate(self):
        p=self.plan();receipt=self.receipt(p);compiler.approval(p,receipt)
        doc=copy.deepcopy(self.document);doc['nodes']['petition']['description']['tr']+=' Yeni cümle.'
        with self.assertRaisesRegex(FlavorError,'eski'):compiler.approval(self.plan(doc),receipt)
        with self.assertRaises(FlavorError):compiler.approval(p,self.root/'missing.json')

    def test_false_receipt_is_not_approval(self):
        p=self.plan();receipt=self.receipt(p);data=json.loads(receipt.read_text());data['approved']=False;receipt.write_text(json.dumps(data))
        with self.assertRaises(FlavorError):compiler.approval(p,receipt)

    def test_dependency_change_invalidates_receipt(self):
        p=self.plan();receipt=self.receipt(p);p.sources.used['some/game/source']='new content hash'
        with self.assertRaises(FlavorError):compiler.approval(p,receipt)

    def test_preview_never_creates_game_files(self):
        p=self.plan();root=MOD/'build/flavor'/self.root.name/'review'
        try:
            path=write_preview(p,root);self.assertTrue(path.is_file())
            self.assertEqual({f.suffix for f in root.iterdir()},{'.html','.json','.mmd'})
            self.assertEqual(json.loads((root/'review.json').read_text())['fingerprint'],p.fingerprint())
        finally:
            import shutil;shutil.rmtree(root.parent)

    def test_preview_escapes_script_closing_tag(self):
        doc=copy.deepcopy(self.document);doc['title']='</script><script>window.PWN=1</script> /*SCRIPT*/'
        p=self.plan(doc);root=MOD/'build/flavor'/self.root.name/'review'
        try:
            raw=write_preview(p,root).read_text();self.assertNotIn('</script><script>window.PWN',raw)
            self.assertIn(r'\u003c/script>',raw)
            embedded=raw.split('<script id="flavor-data" type="application/json">',1)[1].split('</script>',1)[0]
            self.assertEqual(json.loads(embedded)['plan']['title'],doc['title'])
        finally:
            import shutil;shutil.rmtree(root.parent)

    def test_emitted_scripts_roundtrip_and_bom(self):
        p=self.plan();files=compiler.render(p)
        for name,data in files.items():
            self.assertTrue(data.startswith(b'\xef\xbb\xbf'))
            if name.endswith('.txt'):
                tree=pdx.parse(data.decode('utf-8-sig'));self.assertEqual(tree,pdx.parse(pdx.dumps(tree)))
        self.assertNotIn('.metadata/metadata.json',files)

    def test_country_pulse_is_additive_and_scoped(self):
        p=self.plan();files=compiler.render(p)
        nodes=pdx.parse(files[f'common/on_actions/ve_flavor_{p.namespace}.txt'].decode('utf-8-sig'))
        hook=nodes.get_node('on_monthly_pulse_country')
        self.assertEqual(hook.keys(),['on_actions'])
        own=nodes.get_node(p.namespace+'_monthly')
        self.assertIn('c:EGY',pdx.dumps(own.get_node('trigger')))

    def test_delayed_dispatch_rechecks_conditions_and_once_flag(self):
        p=self.plan();files=compiler.render(p)
        text=files[f'common/on_actions/ve_flavor_{p.namespace}.txt'].decode('utf-8-sig')
        dispatch=pdx.parse(text).get_node(p.generated('academy','dispatch')).get_node('effect')
        branch=dispatch.get_node('if');limit=pdx.dumps(branch.get_node('limit'))
        self.assertIn(p.var('support'),limit);self.assertIn(p.generated('academy','seen'),limit)
        self.assertLess(branch.keys().index('set_variable'),branch.keys().index('add_journal_entry'))
        self.assertIn('remove_variable',dispatch.keys())

    def test_cross_country_edge_uses_recipient_scope(self):
        doc=copy.deepcopy(self.document);doc['nodes']['declined']['country']='PER'
        p=self.plan(doc);text=compiler.enqueue(p,'declined',15)
        self.assertTrue(text.startswith('c:PER ?='));self.assertIn('days = 15',text)

    def test_journal_all_outcomes_and_localization(self):
        p=self.plan();files=compiler.render(p)
        node=pdx.parse(files[f'common/journal_entries/ve_flavor_{p.namespace}.txt'].decode('utf-8-sig')).get_node(p.je('academy'))
        self.assertTrue({'complete','fail','timeout','on_complete','on_fail','on_timeout'}<=set(node.keys()))
        self.assertNotIn('possible',node.keys())  # manual add_journal_entry only
        loc=files[f'localization/english/ve_flavor_{p.namespace}_l_english.yml'].decode('utf-8-sig')
        self.assertIn(p.je('academy')+'_reason:0',loc)

    def test_journal_progress_is_initialized_and_goals_are_combined(self):
        doc=copy.deepcopy(self.document);doc['variables']['months']=0
        doc['nodes']['academy']['progress']={'variable':'months','goal':12,'monthly_increment':1}
        p=self.plan(doc);files=compiler.render(p)
        node=pdx.parse(files[f'common/journal_entries/ve_flavor_{p.namespace}.txt'].decode('utf-8-sig')).get_node(p.je('academy'))
        self.assertIn('set_variable',node.get_node('immediate').keys())
        self.assertIn('on_monthly_pulse',node.keys());self.assertIn('current_value',node.keys())
        complete=pdx.dumps(node.get_node('complete'));self.assertIn('is_goal_complete = yes',complete);self.assertIn('has_law',complete)

    def test_context_accepts_prospective_tag_but_install_requires_definition(self):
        sources=copy.copy(self.source);sources.used=dict(self.source.used);sources.countries_used=set()
        sources.context={'countries':{'ZQX':{},'EGY':{}},'states':{}}
        doc=copy.deepcopy(self.document);doc['nodes']['declined']['country']='ZQX'
        p=Plan(doc,EXAMPLE,sources);receipt=self.receipt(p)
        with self.assertRaisesRegex(FlavorError,'etkin modda yok'):compiler.install(p,receipt)

    def test_context_rejects_removed_country(self):
        sources=copy.copy(self.source);sources.used=dict(self.source.used);sources.countries_used=set()
        sources.context={'countries':{'PER':{}},'states':{}}
        with self.assertRaisesRegex(FlavorError,'toprağı'):Plan(copy.deepcopy(self.document),EXAMPLE,sources)

    def test_context_file_is_bound_to_approval(self):
        # Exercise real context loading separately from the shallow shared catalogue.
        context=self.root/'context.json';context.write_text(json.dumps({'version':2,'validation':'passed','countries':{'EGY':{}},'states':{}}))
        sources=Sources(context);p=Plan(copy.deepcopy(self.document),EXAMPLE,sources)
        self.assertIn(str(context),p.sources.used)
        self.assertEqual(p.report()['context'],str(context))

    def test_conversation_approval_binds_existing_review(self):
        p=self.plan();review=self.root/'review.json';review.write_text(json.dumps(p.report()))
        out=MOD/'build/flavor'/self.root.name/'approval.json'
        try:
            compiler.record_approval(p,review,'SYNTHETIC TEST — not actual user approval',out)
            compiler.approval(p,out)
            data=json.loads(review.read_text());data['fingerprint']='old';review.write_text(json.dumps(data))
            with self.assertRaisesRegex(FlavorError,'eşleşmiyor'):compiler.record_approval(p,review,'test only',out)
        finally:
            if out.exists():out.unlink()
            if out.parent.exists():out.parent.rmdir()

    def test_bundle_requires_approval_and_stays_isolated(self):
        p=self.plan();receipt=self.receipt(p);out=MOD/'build/flavor'/self.root.name/'bundle'
        try:
            compiler.write_bundle(p,receipt,out)
            meta=json.loads((out/'flavor-manifest.json').read_text())
            self.assertEqual(meta['fingerprint'],p.fingerprint());self.assertGreater(len(meta['files']),5)
            self.assertTrue((out/f'events/ve_flavor_{p.namespace}.txt').is_file())
            with self.assertRaises(FlavorError):compiler.write_bundle(p,receipt,MOD)
        finally:
            import shutil
            if out.parent.exists():shutil.rmtree(out.parent)

    def test_installer_preserves_atlas_and_detects_manual_edits(self):
        p=self.plan();receipt=self.receipt(p)
        atlas=self.root/'common/history/countries/tgc_test.txt';atlas.parent.mkdir(parents=True);atlas.write_bytes(b'ATLAS')
        meta=self.root/'.metadata/metadata.json';meta.parent.mkdir();meta.write_text('{"game_custom_data":{"replace_paths":["common/history/countries"]}}')
        before=meta.read_bytes()
        with patch.object(compiler,'MOD',self.root):
            compiler.install(p,receipt);compiler.check_installed(p.namespace)
            self.assertEqual(atlas.read_bytes(),b'ATLAS');self.assertEqual(meta.read_bytes(),before)
            output=self.root/f'events/ve_flavor_{p.namespace}.txt';output.write_bytes(output.read_bytes()+b'\n# manual')
            with self.assertRaisesRegex(FlavorError,'değiştirilmiş'):compiler.install(p,receipt)

    def test_installer_does_not_overwrite_unowned_file(self):
        p=self.plan();receipt=self.receipt(p);target=self.root/f'events/ve_flavor_{p.namespace}.txt';target.parent.mkdir();target.write_text('user content')
        with patch.object(compiler,'MOD',self.root),self.assertRaisesRegex(FlavorError,'korunuyor'):compiler.install(p,receipt)
        self.assertEqual(target.read_text(),'user content')

    def test_manifest_cannot_claim_other_files(self):
        path=self.root/'manifest.json';path.write_text(json.dumps({'namespace':'ve_test','files':{'AGENT.md':'a'*64}}))
        with self.assertRaisesRegex(FlavorError,'başka içeri'):compiler.read_manifest(path,'ve_test')

    def test_write_failure_rolls_back(self):
        p=self.root/'a.txt';p.write_bytes(b'old');q=self.root/'b.txt';real=compiler.atomic;calls=0
        def flaky(path,data):
            nonlocal calls
            calls+=1
            if calls==2:raise OSError('simulated write failure')
            return real(path,data)
        with patch.object(compiler,'atomic',side_effect=flaky),self.assertRaises(OSError):compiler.transaction({p:b'new',q:b'new'})
        self.assertEqual(p.read_bytes(),b'old');self.assertFalse(q.exists())

    def test_symlink_output_refused(self):
        link=self.root/'symlink';link.symlink_to(self.root,target_is_directory=True)
        with self.assertRaisesRegex(FlavorError,'Symlink'):compiler.destination(self.root,'symlink/file')


if __name__=='__main__':unittest.main()
