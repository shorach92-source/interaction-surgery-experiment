# Candidate 008 — CPT pilot result

## Decision

**KILL as a distinct research direction.**

The one-seed falsification pilot on `gpt-5.4-mini` passed compile/mock sanity and completed successfully on seed 2000. The direct constructive condition reproduced strong eager commitment, but a simple plan-first instruction outperformed CPT by a wide margin.

## Results

| Condition | Competitive score | First-sight commitment | Hot capture | Trap builds | Construction success |
|---|---:|---:|---:|---:|---:|
| Direct constructive | 0.420 | 1.000 | 0.333 | 2 | 1.000 |
| Plan-first | 0.900 | 0.333 | 1.000 | 0 | 0.667 |
| CPT | 0.520 | 0.667 | 0.333 | 2 | 1.000 |

Hindsight top-B utility was 50. Direct realized 21, plan-first 45, CPT 26.

## Why this kills CPT

The preregistered-style kill criterion stated that CPT should be rejected if an ordinary plan-first prompt recovered at least 95% of CPT's allocation improvement over direct.

- CPT improvement over direct: +0.10 competitive-score points.
- Plan-first improvement over direct: +0.48 points.

Plan-first therefore exceeds the CPT improvement rather than merely recovering 95% of it. It also has lower first-sight commitment and zero trap builds versus two for CPT.

The main CPT-specific hypothesis — that cross-frame policy elicitation plus a binding decision is needed to recover the suppressed allocation capability — is not supported by this pilot. A much simpler same-frame planning instruction performs substantially better.

## Instrument note

One plan-first COMMIT response contained JSON formatting that caused the benchmark's simple construction checker to miss `def solve`, yielding construction success 2/3. The allocation decision itself was still recovered by the fallback parser. Allocation is the primary endpoint in this R2-like pilot, so this does not rescue CPT; if anything, plan-first achieved the best allocation score despite that formatting issue.

## Scope

This is one deterministic stream and not an AlloBench reproduction. It does **not** establish that plan-first solves online tool allocation generally. It is sufficient only to reject CPT as a distinct mechanism under the experiment's own kill rule.

Do not tune CPT further on this seed. Move to a new research gap.
