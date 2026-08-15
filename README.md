# Interaction Surgery — Experiment 005

Experiment 005 measures whether the same coalition of otherwise useful agent
components exhibits both a positive utility interaction and a positive harm
interaction. It evaluates every subset of each coalition and computes exact
Möbius/Harsanyi interaction terms.

The locked pilot contains four order-2 and four order-3 scenarios. With the
default five repetitions this is exactly 240 live model calls.

## Local sanity check

```bash
python -m unittest discover -s tests -v
python experiment_005.py --backend mock --repetitions 20
```

## Remote run

1. Add an Actions repository secret named `OPENAI_API_KEY`.
2. Open **Actions → Experiment 005 benchmark → Run workflow**.
3. Keep the default 5 repetitions for the 240-call pilot, or use 1 first for a
   48-call connectivity check.
4. Download the `experiment-005-results-*` artifact after the run.

No API key is stored or printed by this repository. The live backend uses the
OpenAI Responses API and reads credentials from the runner environment.

Outputs are written to `results/`: raw JSONL rollouts, interaction estimates,
and a compact Markdown report. Mock output is infrastructure validation only,
not evidence about a real model.

