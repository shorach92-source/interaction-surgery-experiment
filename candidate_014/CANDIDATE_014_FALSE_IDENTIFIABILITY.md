# Candidate 014 — False Identifiability in AI Scientists

## Status
Candidate gap only. No novelty claim. Phase A deterministic kill test launched.

## Research question
Can an LLM scientific agent correctly recognize when **no experiment in the allowed intervention set can distinguish two competing hypotheses**, or does it invent/select a supposedly decisive test even when the hypotheses are observationally equivalent under all allowed experiments?

This is an identifiability-awareness question, not ordinary experiment ranking.

## Why this is narrower than adjacent work
- BoxingGym evaluates informativeness / expected information gain of experiments and model discovery.
- SCOPE evaluates scientific experiment planning quality and configuration.
- HEP makes hypothesis-test-evidence-belief cycles explicit and auditable.
- Classical optimal experimental design already studies parameter identifiability and model discrimination.

The candidate gap is narrower: explicit recognition of **zero discriminability under the entire allowed experiment set** by an LLM scientific agent.

## Phase A — deterministic finite-world sanity/kill test
Each case contains:
1. two hypotheses H1 and H2,
2. a finite set of allowed experiments,
3. deterministic predicted outcomes for every hypothesis-experiment pair.

Oracle:
- IDENTIFIABLE iff at least one allowed experiment has different predictions under H1 and H2;
- otherwise NOT_IDENTIFIABLE.

The LLM must return either one actually discriminative experiment or `NOT_IDENTIFIABLE`.

### Predeclared kill criteria
Close the simple candidate if a direct `gpt-5.4-mini` baseline with reasoning effort `none` achieves:
- overall decision accuracy >= 0.95, and
- non-identifiable recognition >= 0.90, and
- invented / outside-set experiment rate = 0.

Do not make cases harder after seeing a perfect/near-perfect result merely to manufacture a failure.

### Positive signal
Only if the direct baseline fails the predeclared gate should we consider a second phase with richer but still fully deterministic mechanistic descriptions.

## Competition rule
Before any novelty claim, re-run a targeted prior-art search for LLM scientific agents, identifiability, model discrimination, expected information gain, and autonomous experimental design.
