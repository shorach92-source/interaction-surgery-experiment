# Candidate 014 — Falsifiable Novelty Certificate (FNC)

## Status

**Candidate gap only. No novelty claim.**

## Problem

Automated scientific-idea novelty judges can produce convincing literature-grounded rationales while still disagreeing substantially with human novelty judgments. Existing systems commonly output a scalar/rubric novelty score plus explanation.

FNC tests a different decision object: a novelty claim must survive explicit attempted falsification.

For each proposed contribution, the system must:

1. state the atomic contribution;
2. identify the closest collision in the supplied related work;
3. state what that prior work already covers;
4. state the minimal distinguishing witness that would have to be true for the contribution to remain novel;
5. mark the contribution `COLLAPSED` when no material witness can be stated from the idea;
6. derive the final novelty judgment from the surviving witnesses rather than from an unconstrained holistic impression.

The intended difference is not claim decomposition by itself. Patent claim charts, literature-grounded novelty checkers and scientific novelty benchmarks already exist. The candidate is the use of **falsifiable distinguishing witnesses as mandatory proof obligations before a novelty score may be emitted**.

## Closest prior art found before experimentation

- Idea Novelty Checker: retrieve/rerank literature-grounded novelty assessment.
- RINoBench: human-labeled benchmark for idea novelty judgments and justifications.
- RQ-Bench / novelty-mirage work: LLM judges can overrate model-generated research questions.
- Patent claim↔prior-art correspondence and automated claim-chart systems.
- Intra-paper novelty-claim verification: checks whether methods substantiate stated novelty claims.
- Popper: agentic sequential falsification of scientific hypotheses, but not prior-art novelty claims.

Therefore FNC is **not** claimed to be a new general novelty-assessment system. It survives only if the witness constraint produces a measurable advantage over direct novelty judging on a public benchmark.

## Public benchmark

Use the untouched RINoBench test split, which includes research ideas, human gold novelty judgments, related works and human justifications.

## Phase A — cheap kill test

Freeze a small deterministic test subset before seeing model outputs.

Compare the same model under:

- `DIRECT`: standard rubric-style novelty judgment from idea + supplied related works.
- `FNC`: atomic contribution → closest collision → distinguishing witness → collapse/survive → score.

No external literature retrieval is added in Phase A; both arms receive exactly the same RINoBench evidence.

Primary metric: agreement/error against the human gold novelty score on the frozen sample.

Secondary diagnostics:

- direction of scoring bias;
- exact-score accuracy;
- mean absolute error;
- whether FNC reduces high-novelty false positives;
- number of collapsed vs surviving contribution witnesses.

## Predeclared kill criterion

Close Candidate 014 immediately if any of the following occurs:

1. FNC does not improve mean absolute error over DIRECT on the frozen pilot sample; or
2. any apparent improvement comes only from globally lowering all scores rather than better ranking/calibration; or
3. a simpler prompt baseline that asks for explicit nearest-work comparison matches FNC; or
4. renewed prior-art search finds an existing scientific-novelty system that already requires equivalent claim-level distinguishing proof obligations and demonstrates the same function.

A positive pilot is not a novelty result. It only earns replication on a larger untouched RINoBench sample and another prior-art search.
