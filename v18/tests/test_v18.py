import importlib.util, unittest
from pathlib import Path

V18_ROOT=Path(__file__).resolve().parents[1]
PACKAGE_ROOT=V18_ROOT.parent
SPEC=importlib.util.spec_from_file_location('v18_cli',V18_ROOT/'tools'/'v18.py')
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

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

if __name__=='__main__': unittest.main()
