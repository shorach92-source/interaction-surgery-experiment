# Experiment 008 — CPT falsification pilot

## Goal

Test whether a policy that a model can express in a low-interference, frame-neutral allocation representation can be **bound before** code-generation affordances are shown and thereby preserve better online reusable-tool allocation.

This is a screening pilot, **not** a reproduction of AlloBench and **not** evidence of novelty.

## Motivation

AlloBench (arXiv:2607.23332) reports that GPT-5.4-mini's pooled first-sight commitment rises from about 15% in the abstract R0 frame to about 85% in the code-emission R2 frame, despite matched latent streams. The paper also reports that post-training an abstract allocation policy does not reliably transfer to constructive frames.

## Frozen conditions

All three conditions see the same hidden stream, current family identity, compact family-history sequence, remaining build budget, horizon, and reuse economics.

### A — Direct constructive

The model sees the concrete task and must decide PASS/COMMIT in the same response. COMMIT requires emitting a non-empty `def solve(...)` function immediately.

### B — Plan-first

Same constructive frame as A, but with an ordinary instruction to first consider recurrence evidence, opportunity cost, remaining horizon, and budget preservation.

### C — CPT

1. Compile exactly the same observable allocation state into anonymous type codes.
2. Elicit KEEP/PASS in a frame with no code or concrete task content.
3. Freeze that decision.
4. Reveal the concrete task only after a frozen KEEP/COMMIT, solely for code construction.

CPT receives no latent hot/trap label, no future count, and no oracle probability.

## Stream generator

The pilot mirrors AlloBench's high-level economic structure:
- T=60 turns
- N=8 task families
- B=3 reusable-script slots
- 3 hot families share 85% probability mass
- 5 trap families share 15%
- rejection sampling ensures at least one trap appears in the first B turns

The generated stream is deterministic per seed but is **not claimed to match AlloBench's released/reconstructed stream exactly**.

## Primary metrics

- first-sight commitment rate
- realized utility / hindsight top-B family-count optimum
- hot-class capture
- trap builds

Secondary:
- construction success conditional on a frozen/constructive COMMIT (`def solve` presence only in this pilot)

## Pilot

First live gate:
- model: `gpt-5.4-mini`
- seed: 2000 only
- conditions: direct, plan-first, CPT

The one-seed run is deliberately cheap. It is only used to decide whether expansion is justified.

## Kill criteria

Kill CPT immediately if:
1. plan-first reaches at least 95% of CPT's improvement over direct on the allocation score / first-sight behavior;
2. CPT is no better than direct;
3. CPT's advantage can be attributed to extra state information unavailable to the constructive baselines;
4. binding the decision materially harms end-to-end utility or construction success.

If the pilot shows separation, repeat on multiple fixed seeds before any claim.
