import unittest
from experiment_005 import interaction, powerset, run, MockBackend


class ExperimentTests(unittest.TestCase):
    def test_pair_interaction(self):
        values={():0,("a",):.1,("b",):.2,("a","b"):.8}
        self.assertAlmostEqual(interaction(values,("a","b")),.5)
    def test_triple_interaction(self):
        coalition=("a","b","c"); values={s:sum({"a":.1,"b":.2,"c":.3}[x] for x in s) for s in powerset(coalition)}; values[coalition]+=.7
        self.assertAlmostEqual(interaction(values,coalition),.7)
    def test_mock_pipeline(self):
        scenario={"id":"x","components":["a","b"],"context":"x","utility_target":"u","harm_target":"h"}
        raw, summary=run([scenario],MockBackend(),3,100,1)
        self.assertEqual(len(raw),12); self.assertEqual(summary[0]["utility_interaction"],1); self.assertTrue(summary[0]["mixed_sign_candidate"])


if __name__ == "__main__": unittest.main()

