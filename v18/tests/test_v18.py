import importlib.util, subprocess, sys, tempfile, unittest
from pathlib import Path

V18_ROOT=Path(__file__).resolve().parents[1]
PACKAGE_ROOT=V18_ROOT.parent
SPEC=importlib.util.spec_from_file_location('v18_cli',V18_ROOT/'tools'/'v18.py')
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
PATCHER_SPEC=importlib.util.spec_from_file_location('v18_package_patcher',V18_ROOT/'tools'/'patch_cumulative_package.py')
PATCHER=importlib.util.module_from_spec(PATCHER_SPEC)
PATCHER_SPEC.loader.exec_module(PATCHER)

class V18Tests(unittest.TestCase):
    def test_routing_always_selects_orchestrator(self):
        result=MODULE.route_task(PACKAGE_ROOT,'Build a character customization system with inventory UI')
        self.assertEqual(result['primary_skill'],'roblox-end-to-end-development-orchestrator')
        self.assertIn('roblox-task-intake-and-requirements',result['selected_skills'])

    def test_workstream_graph_is_topologically_sorted(self):
        graph=[{'id':'a','depends_on':[]},{'id':'b','depends_on':['a']},{'id':'c','depends_on':['b']}]
        self.assertEqual(MODULE.topo(graph),['a','b','c'])

    def test_dependency_cycle_is_rejected(self):
        graph=[{'id':'a','depends_on':['b']},{'id':'b','depends_on':['a']}]
        with self.assertRaises(ValueError): MODULE.topo(graph)

    def test_overlapping_owned_paths_are_rejected(self):
        graph=[{'id':'a','depends_on':[],'owned_paths':['src/client']},{'id':'b','depends_on':['a'],'owned_paths':['src/client/UI']}]
        with self.assertRaises(ValueError): MODULE.topo(graph)

    def test_task_plan_conforms_to_schema_and_acyclic_graph(self):
        task=MODULE.make_work_item(PACKAGE_ROOT,'Add an inventory UI that reads server-owned inventory data')
        order=MODULE.validate_task(PACKAGE_ROOT,task)
        self.assertEqual(order[0],'discovery')
        self.assertEqual(task['status'],'DRAFT')

    def test_monetization_task_routes_to_all_economy_safety_specialists(self):
        result=MODULE.route_task(PACKAGE_ROOT,'Design a Robux shop with game passes, developer products, subscriptions, fixed prices, and no gambling')
        self.assertIn('economy',[domain['name'] for domain in result['domains']])
        for name in ('roblox-player-friendly-monetization','roblox-deterministic-progression-shop',
                     'roblox-tiered-catalog-progression','roblox-earned-currency-economy'):
            self.assertIn(name,result['selected_skills'])

    def test_skill_frontmatter_is_well_formed(self):
        paths=sorted((V18_ROOT/'codex-skills').glob('*/SKILL.md'))
        self.assertEqual(len(paths),16)
        for path in paths:
            name,desc,body=MODULE.parse_skill(path)
            self.assertEqual(name,path.parent.name)
            self.assertTrue(desc)
            self.assertIn(MODULE.CONTRACT,body)

    def test_v17_audit_migration_updates_count_and_v18_source_parity(self):
        original=PACKAGE_ROOT/'v17'/'tools'/'audit_cumulative_package.py'
        self.assertTrue(original.is_file(), 'The pinned V17 audit must be present in the cumulative package')
        with tempfile.TemporaryDirectory() as tmp:
            migrated=Path(tmp)/'audit_cumulative_package.py'
            migrated.write_text(original.read_text(encoding='utf-8'),encoding='utf-8')
            PATCHER.upgrade_v17_audit(migrated)
            result=migrated.read_text(encoding='utf-8')
        self.assertIn('EXPECTED_INSTALLED_SKILLS = 175',result)
        self.assertIn('V18_UPGRADED_SKILLS',result)
        self.assertIn('source_version = "v18" if skill_name in V18_UPGRADED_SKILLS else "v17"',result)
        self.assertIn('CURRENT_MANIFESTS',result)
        self.assertNotIn('EXPECTED_INSTALLED_SKILLS = 163',result)

    def test_read_only_routing_works_without_optional_python_packages(self):
        result=subprocess.run(
            [sys.executable,'-S',str(V18_ROOT/'tools'/'v18.py'),'route',
             '--root',str(PACKAGE_ROOT),'--task','Inspect a Roblox character customization project'],
            cwd=PACKAGE_ROOT,capture_output=True,text=True,check=False,timeout=15
        )
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('roblox-end-to-end-development-orchestrator',result.stdout)

    def test_remote_validation_example_has_no_unfinished_authorization_todo(self):
        sample=V18_ROOT/'examples'/'luau-patterns'/'RemoteRequestValidation.server.luau'
        source=sample.read_text(encoding='utf-8')
        for required in (
            'CollectionService:HasTag','MAX_COLLECTION_DISTANCE','processedRequestIds',
            'MAX_REQUESTS_PER_WINDOW','REWARD_AMOUNT','HumanoidRootPart'
        ):
            self.assertIn(required,source)
        self.assertNotIn('TODO:',source)
        self.assertNotIn('requestedAmount',source)

if __name__=='__main__': unittest.main()
