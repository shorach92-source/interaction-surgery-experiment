import os, unittest
from unittest.mock import patch
from experiment_005 import interaction, normalized_api_key, powerset, run, MockBackend


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
    def test_api_key_is_trimmed(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY":"  sk-test-value\r\n"}):
            self.assertEqual(normalized_api_key(), "sk-test-value")


if __name__ == "__main__": unittest.main()

