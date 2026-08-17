# Candidate 012 — Fallback Guarantee Laundering result

## Decision

**Negative. Close the simple FGL hypothesis.**

Candidate 012 tested whether a visible semantic downgrade from a successful fallback becomes laundered after one or two successful downstream transformations.

Six deterministic guarantee dimensions were tested:

- freshness,
- authority,
- precision,
- completeness,
- scope fidelity,
- calibration.

Each dimension had clean and degraded arms at depths D0, D1 and D2. The clean source and degraded fallback used the same decision-driving value; only the semantic guarantee differed. Therefore the oracle is fully synthetic and deterministic: clean arms should EXECUTE and degraded arms should DEGRADE at every depth.

## Guarded Phase A

The first 36-call run included one generic reminder that successful downstream computations do not change the properties of their input evidence.

| Depth | Degraded laundering | Clean execution |
|---:|---:|---:|
| D0 | 0.000 | 1.000 |
| D1 | 0.000 | 1.000 |
| D2 | 0.000 | 1.000 |

Overall degraded laundering = 0.000. Depth slope = 0.000. Preservation score = 1.000.

## Unguarded Phase A

Because the reminder could itself act as a mitigation, a second frozen 36-call run removed only that one sentence. The six scenarios, all trace contents, clean/degraded values, depth transformations, decision format, model (`gpt-5.4-mini`), reasoning setting and scoring remained unchanged.

| Depth | Degraded laundering | Clean execution |
|---:|---:|---:|
| D0 | 0.000 | 1.000 |
| D1 | 0.000 | 1.000 |
| D2 | 0.000 | 1.000 |

Every degraded case was rejected and every clean case was executed. All six guarantee dimensions had zero laundering across all three depths.

## Interpretation

Under this explicit-evidence synthetic setup, downstream computational success does **not** cause GPT-5.4-mini to forget a visible user-level semantic requirement. The effect therefore fails the predeclared first kill criterion and does not justify a new guarantee-propagation mechanism.

This negative result does not contradict SARC-DQ's finding that metadata-borne defects can silently convert into bad actions when the relevant quality signal is absent from the agent's payload context. Our experiment deliberately made the downgrade visible. That distinction is exactly why no further prompt tuning is warranted: hiding the downgrade would reduce the problem to an already-covered metadata-visibility/data-quality gate problem.

Do not complicate the scenario to manufacture laundering. Candidate 012 is closed.
