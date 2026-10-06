import json
import unittest
from pathlib import Path

from governance import register as reg
from governance.classify import ANNEX_I_DATE, ANNEX_III_DATE, classify

ROOT = Path(__file__).resolve().parent.parent
SYSTEMS = {s["id"]: s for s in json.loads((ROOT / "assessment" / "systems.json")
                                         .read_text(encoding="utf-8"))["systems"]}
ROWS = reg.load(ROOT / "assessment" / "risk_register.csv")


def refs(result):
    return {o["ref"]: o["applies_from"] for o in result["obligations"]}


class ClassifyTests(unittest.TestCase):
    def test_policy_assistant_is_transparency_tier(self):
        result = classify(SYSTEMS["A"])
        self.assertEqual(result["tiers"], ["transparency (Art. 50)"])
        r = refs(result)
        self.assertEqual(r["Art. 50(1)"], "2026-08-02")
        self.assertIn("Art. 4", r)
        self.assertNotIn("Art. 9", r)  # no high-risk obligations
        self.assertTrue(any("model provider" in n for n in result["notes"]))

    def test_triage_is_high_risk_with_earliest_date(self):
        result = classify(SYSTEMS["B"])
        self.assertTrue(any("Annex I" in t for t in result["tiers"]))
        self.assertTrue(any("Annex III" in t for t in result["tiers"]))
        r = refs(result)
        # Both routes apply; the earlier deadline (Annex III, 2 Dec 2027) governs.
        self.assertEqual(r["Art. 9"], ANNEX_III_DATE)
        self.assertIn("Art. 26", r)   # deployer obligations
        self.assertIn("Art. 14", r)   # human oversight

    def test_annex_i_only_uses_2028_date(self):
        system = dict(SYSTEMS["B"], annex_III_area=None)
        self.assertEqual(refs(classify(system))["Art. 9"], ANNEX_I_DATE)

    def test_prohibited_stops_everything(self):
        result = classify({"name": "x", "prohibited_practice": "social scoring"})
        self.assertEqual(result["tiers"], ["prohibited"])

    def test_minimal_risk(self):
        result = classify({"name": "spam filter", "roles": ["deployer"]})
        self.assertEqual(result["tiers"], ["minimal risk"])
        self.assertIn("Art. 4", refs(result))


class RegisterTests(unittest.TestCase):
    def test_register_is_valid(self):
        self.assertEqual(reg.validate(ROWS), [])

    def test_appetite_bands(self):
        self.assertEqual(reg.appetite(8), "ACCEPTED")
        self.assertEqual(reg.appetite(9), "BOARD SIGN-OFF")
        self.assertEqual(reg.appetite(15), "BLOCK")

    def test_no_risk_blocks_go_live_and_triage_needs_board(self):
        decisions = {r["id"]: reg.appetite(reg.score(r)) for r in ROWS}
        self.assertNotIn("BLOCK", decisions.values())
        self.assertEqual(decisions["R09"], "BOARD SIGN-OFF")   # 2 x 5 = 10

    def test_validation_catches_errors(self):
        bad = [dict(ROWS[0], owner="", likelihood="7"), dict(ROWS[1], id=ROWS[0]["id"], nist_function="PLAN")]
        problems = reg.validate(bad)
        self.assertTrue(any("missing owner" in p for p in problems))
        self.assertTrue(any("likelihood must be 1-5" in p for p in problems))
        self.assertTrue(any("duplicate id" in p for p in problems))
        self.assertTrue(any("nist_function" in p for p in problems))

    def test_residual_higher_than_inherent_rejected(self):
        bad = [dict(ROWS[0], likelihood="1", impact="1")]
        self.assertTrue(any("higher than inherent" in p for p in reg.validate(bad)))

    def test_heatmap_counts_every_risk(self):
        grid = reg.heatmap(ROWS)
        self.assertEqual(sum(sum(row.values()) for row in grid.values()), len(ROWS))


if __name__ == "__main__":
    unittest.main()
