import unittest
from pathlib import Path

V18_ROOT = Path(__file__).resolve().parents[1]
SKILLS = V18_ROOT / "codex-skills"
POLICY = V18_ROOT / "docs" / "NO_GAMBLING_AND_FAIR_MONETIZATION.md"

class MonetizationPolicyTests(unittest.TestCase):
    def test_policy_is_explicitly_no_gambling(self):
        text = POLICY.read_text(encoding="utf-8").lower()
        self.assertIn("absolute no-gambling rule", text)
        self.assertIn("robux-funded path", text)
        self.assertIn("deterministic", text)
        self.assertIn("odds disclosure", text)

    def test_policy_lists_deterministic_monetization_methods(self):
        text = POLICY.read_text(encoding="utf-8").lower()
        for term in ("cosmetics and customization", "game passes", "developer products",
                     "subscriptions", "paid experience access", "private servers",
                     "avatar items / creator store"):
            with self.subTest(term=term):
                self.assertIn(term, text)

    def test_tier_unlock_requires_all_earlier_tier_items(self):
        text = (SKILLS / "roblox-tiered-catalog-progression" / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("every required item in every preceding tier", text)
        self.assertIn("non-robux route", text)
        self.assertIn("server", text)

    def test_shop_and_currency_are_fixed_and_auditable(self):
        shop = (SKILLS / "roblox-deterministic-progression-shop" / "SKILL.md").read_text(encoding="utf-8").lower()
        economy = (SKILLS / "roblox-earned-currency-economy" / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("fixed price", shop)
        self.assertIn("exactly the listed contents", shop)
        self.assertIn("fixed, documented amounts", economy)
        self.assertIn("idempotent", economy)

    def test_robux_value_never_funds_random_outcomes(self):
        for path in [POLICY, *(SKILLS / name / "SKILL.md" for name in (
            "roblox-player-friendly-monetization",
            "roblox-deterministic-progression-shop",
            "roblox-tiered-catalog-progression",
            "roblox-earned-currency-economy"))]:
            text = path.read_text(encoding="utf-8").lower()
            self.assertIn("random", text)
            self.assertTrue("robux" in text or "no-gambling" in text)

if __name__ == "__main__":
    unittest.main()
