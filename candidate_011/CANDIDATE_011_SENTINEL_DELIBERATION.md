# Candidate 011 — Sentinel-Induced Deliberation (SID)

## Status

Candidate gap only. Novelty is **not established**.

## Motivation

Canary Tools (arXiv:2608.04719) reports a counter-intuitive density effect: for hosted models, adding all six canary types often *reduced* overall canary susceptibility and reduced the dominant capability-mirage trap rate. The authors suggest that extra competing tool descriptions may cause capable models to inspect tool contracts more carefully.

Existing work uses fake/canary tools mainly as **diagnostic probes** or **deception-based compromise detectors** (e.g. AgentShield, arXiv:2605.11026). In the prior-art sweep reviewed before this experiment, we did not find a system that intentionally inserts a benign, known-invalid sentinel tool as a runtime intervention whose purpose is to improve ordinary non-adversarial tool-selection reasoning.

## Narrow hypothesis

A deliberately designed, semantically nearby but clearly disqualified **sentinel tool** can induce broader contract scrutiny and reduce selection of a capability-mirage tool more than merely adding one unrelated neutral tool.

The claim is not that larger tool lists help. The candidate mechanism requires a **sentinel-specific gain beyond list-length control**.

## Phase A falsification pilot

For each matched task, compare three byte-stable tool-set conditions:

1. `baseline`: correct tool + capability-mirage tool.
2. `neutral`: baseline + one unrelated benign tool (controls list length / option count).
3. `sentinel`: baseline + one semantically nearby but visibly disqualified tool along a different contract axis (e.g. stale, wrong scope, missing prerequisite).

The model must select exactly one real function tool through the Responses API (`tool_choice="required"`). No tool output is executed; this isolates first-step selection.

### Primary metrics

- correct-tool selection rate,
- capability-mirage selection rate,
- sentinel selection rate,
- neutral-distractor selection rate,
- sentinel vigilance gain = baseline mirage rate - sentinel mirage rate,
- neutral count-control gain = baseline mirage rate - neutral mirage rate,
- sentinel-specific gain = vigilance gain - count-control gain.

## Kill criteria

Reject SID as a distinct mechanism if any of the following holds:

1. The baseline capability-mirage rate is too low to measure (pilot < 15% on the chosen model); this pilot is then non-diagnostic for this model.
2. Sentinel mirage reduction is < 15 percentage points.
3. A neutral third tool produces at least 80% of the sentinel's mirage reduction.
4. Sentinel injection reduces correct-tool selection or introduces comparable sentinel-tool errors, so apparent gain is only redistribution among wrong choices.
5. Prior art is found that already uses benign canary/decoy tool injection specifically to improve normal tool-selection reasoning rather than detect attacks or measure susceptibility.

## Positive bar

Continue only if baseline mirage susceptibility is measurable and the sentinel produces a reproducible reduction beyond a matched neutral-tool count control without lowering correct selection.

A positive result would establish an empirical runtime effect worth further study, **not broad scientific novelty or patent novelty**. A renewed literature search is mandatory before any stronger claim.
