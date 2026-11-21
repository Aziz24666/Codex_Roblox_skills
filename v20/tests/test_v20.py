import copy
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
V20_ROOT = REPO / "v20"
SPEC = importlib.util.spec_from_file_location("v20_cli_tests", V20_ROOT / "tools" / "v20.py")
V20 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V20)


def fixture_root(temp: str) -> Path:
    root = Path(temp)
    for path in (
        "v18/tools", "v18/workflow", "v20/tools", "v20/workflow",
        "v20/evals", "v20/schemas", "v20/examples", ".agents/skills"
    ):
        (root / path).mkdir(parents=True, exist_ok=True)

    copies = [
        (REPO / "v18/tools/v18.py", root / "v18/tools/v18.py"),
        (REPO / "v18/workflow/skill-routing.json", root / "v18/workflow/skill-routing.json"),
        (V20_ROOT / "workflow/routing-additions.json", root / "v20/workflow/routing-additions.json"),
        (V20_ROOT / "evals/routing-cases.json", root / "v20/evals/routing-cases.json"),
        (V20_ROOT / "schemas/production-contract.schema.json", root / "v20/schemas/production-contract.schema.json"),
        (V20_ROOT / "examples/production-contract.example.json", root / "v20/examples/production-contract.example.json"),
    ]
    for source, destination in copies:
        shutil.copy2(source, destination)

    routing = json.loads((root / "v18/workflow/skill-routing.json").read_text(encoding="utf-8"))
    additions = json.loads((root / "v20/workflow/routing-additions.json").read_text(encoding="utf-8"))
    skill_names = {
        skill
        for domain in routing["domains"].values()
        for skill in domain.get("skills", [])
    }
    skill_names.update(
        skill
        for domain in additions["additions"].values()
        for skill in domain.get("skills", [])
    )
    skill_names.update({
        "roblox-end-to-end-development-orchestrator",
        "roblox-task-intake-and-requirements",
        "roblox-impact-aware-skill-routing",
        "roblox-evidence-first-completion",
        "roblox-game-builder",
        "roblox-cross-system-contract-governance",
        "roblox-dependency-aware-workstream-planning",
        "roblox-risk-and-approval-gating",
    })
    V20.merge_routing(root)
    for name in skill_names:
        skill_dir = root / ".agents/skills" / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text("fixture\n", encoding="utf-8")
    return root


class V20ProductionContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = fixture_root(self.temp.name)
        self.example = json.loads(
            (self.root / "v20/examples/production-contract.example.json").read_text(encoding="utf-8")
        )

    def tearDown(self):
        self.temp.cleanup()

    def write_contract(self, data):
        path = self.root / "contract.json"
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return path

    def test_example_contract_passes(self):
        result = V20.validate_contract(self.root, Path("v20/examples/production-contract.example.json"))
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["remote_operations"], 1)
        self.assertEqual(result["fixed_price_products"], 1)

    def test_paid_random_rewards_are_rejected(self):
        data = copy.deepcopy(self.example)
        data["economy"]["paid_random_rewards"] = True
        with self.assertRaises(ValueError):
            V20.validate_contract(self.root, self.write_contract(data))

    def test_nonproduction_environment_must_be_isolated(self):
        data = copy.deepcopy(self.example)
        data["environments"]["development"]["data_store_mode"] = "production"
        with self.assertRaisesRegex(ValueError, "development must use an isolated"):
            V20.validate_contract(self.root, self.write_contract(data))

    def test_side_effecting_remote_requires_idempotency_key(self):
        data = copy.deepcopy(self.example)
        data["authority"]["remote_operations"][0]["idempotency_key"] = False
        with self.assertRaisesRegex(ValueError, "no idempotency key"):
            V20.validate_contract(self.root, self.write_contract(data))

    def test_duplicate_remote_identifiers_are_rejected(self):
        data = copy.deepcopy(self.example)
        data["authority"]["remote_operations"].append(copy.deepcopy(data["authority"]["remote_operations"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate remote operation_id"):
            V20.validate_contract(self.root, self.write_contract(data))

    def test_migration_gap_is_rejected(self):
        data = copy.deepcopy(self.example)
        data["persistence"]["schema_version"] = 4
        migration = copy.deepcopy(data["persistence"]["migrations"][0])
        migration["from_version"] = 3
        migration["to_version"] = 4
        data["persistence"]["migrations"].append(migration)
        with self.assertRaisesRegex(ValueError, "migration chain gap"):
            V20.validate_contract(self.root, self.write_contract(data))

    def test_rollout_order_is_enforced(self):
        data = copy.deepcopy(self.example)
        data["rollout"]["stages"] = ["development", "canary", "staging", "production"]
        with self.assertRaisesRegex(ValueError, "rollout stages must be ordered"):
            V20.validate_contract(self.root, self.write_contract(data))

    def test_required_operational_metrics_are_enforced(self):
        data = copy.deepcopy(self.example)
        data["observability"]["required_metrics"] = ["request_latency"]
        with self.assertRaisesRegex(ValueError, "observability is missing required metrics"):
            V20.validate_contract(self.root, self.write_contract(data))

    def test_routing_benchmark_passes_all_v20_cases(self):
        report = V20.evaluate_routing(self.root)
        self.assertEqual(report["status"], "PASS", json.dumps(report["cases"], indent=2))
        self.assertEqual(report["summary"]["failed_cases"], 0)
        self.assertEqual(report["summary"]["total_cases"], 5)


if __name__ == "__main__":
    unittest.main()
