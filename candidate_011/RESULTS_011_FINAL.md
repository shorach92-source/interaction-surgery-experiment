# Candidate 011 — Final status

## Decision

**Closed. Do not tune the reconstruction further.**

Candidate 011 proposed Sentinel-Induced Deliberation (SID): inserting a semantically nearby but clearly disqualified sentinel tool might reduce capability-mirage selection beyond a matched neutral third-tool control.

The predeclared sensitivity gate required at least 15% baseline capability-mirage selection before the intervention could be evaluated.

## Runs

### Initial reconstruction — GPT-5.4-mini

- baseline correct: 1.000
- baseline mirage: 0.000
- neutral correct: 1.000
- sentinel correct: 1.000

### Same frozen reconstruction — GPT-4.1

- baseline correct: 1.000
- baseline mirage: 0.000
- neutral correct: 1.000
- sentinel correct: 1.000

### Canonical-aligned capability probe — GPT-4.1

The final probe changed the mirage only to align with the published Canary Tools Appendix-C recipe: it preserved the base semantics and schema and appended the published fixed capability lure, `ADVANCED: solves the hardest cases with research-grade accuracy`.

- baseline correct: 1.000
- baseline mirage: 0.000
- neutral correct: 1.000
- sentinel correct: 1.000
- diagnostic baseline: false
- vigilance gain: 0.000
- sentinel-specific gain: 0.000

## Interpretation

The Canary Tools paper reports a real GPT-4.1 trapped run on the exact unit-conversion task, so the phenomenon itself is not contradicted. Our reconstruction simply failed to reproduce the paper's susceptibility despite using the published fixed capability suffix in the last run. The paper states that its complete 72-canary pool, tasks and logs are released, but no direct artifact/code link was discoverable from the arXiv record or targeted public search during this investigation.

Because the baseline failure could not be reproduced, no experiment here measures whether SID helps. Further strengthening the mirage descriptions after observing perfect accuracy would amount to tuning the benchmark to manufacture the target failure.

Therefore Candidate 011 is closed under the project's falsification-first rule.

## Research-process lesson

Prefer future candidates with self-contained, deterministic ground truth and failure generators that we can reproduce completely. Do not base a new mechanism on a benchmark effect whose released artifact cannot be independently obtained.
