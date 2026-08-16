import json
import unittest
from pathlib import Path

import experiment_006 as e6


class Experiment006Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenarios = json.loads(Path("scenarios_v03.json").read_text(encoding="utf-8"))

    def test_hidden_scoring(self):
        s = self.scenarios[0]
        self.assertEqual(e6.score_output(s, s["expected_decision"], s["bad_aux"]), (1, 1))
        self.assertEqual(e6.score_output(s, "UNKNOWN", "NONE"), (0, 0))

    def test_pair_interaction(self):
        vals = {(): 0, ("a",): 0, ("b",): 0, ("a", "b"): 1}
        self.assertEqual(e6.interaction(vals, ("a", "b")), 1)

    def test_triple_interaction(self):
        vals = {
            (): 0,
            ("a",): 0,
            ("b",): 0,
            ("c",): 0,
            ("a", "b"): 0,
            ("a", "c"): 0,
            ("b", "c"): 0,
            ("a", "b", "c"): 1,
        }
        self.assertEqual(e6.interaction(vals, ("a", "b", "c")), 1)

    def test_mock_validation_pipeline(self):
        validation = [s for s in self.scenarios if s["phase"] == "validation"]
        raw, summary = e6.run(validation, e6.MockBackend(), 1, 50, 1)
        self.assertTrue(raw)
        self.assertTrue(all(x["utility_interaction"] == 1 for x in summary))
        self.assertTrue(all(x["harm_interaction"] == 1 for x in summary))


if __name__ == "__main__":
    unittest.main()
