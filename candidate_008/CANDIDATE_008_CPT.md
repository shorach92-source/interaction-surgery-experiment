# Candidate 008 — Counterfactual Policy Transplantation (CPT)

## Status

Candidate gap only. Novelty is **not established**.

## Observed capability boundary

AlloBench (arXiv:2607.23332) reports a paired framing gap in online reusable-tool allocation. Frontier models behave near-optimally when the allocation problem is presented abstractly, but become strongly eager to commit budget when the same latent stream requires code emission or real script construction. GPT-5.4-mini rises from roughly 15% first-sight commitment in the abstract frame to roughly 85% when code emission is required; GPT-5.6 Sol preserves more selectivity under code emission but collapses under full script-tool execution.

The paper localizes the failure to framing/execution rather than lack of abstract allocation competence and reports that policy training in the abstract frame fails to transfer reliably to constructive frames.

## Narrow hypothesis

A demonstrated policy can be recovered from a lower-interference, behaviorally isomorphic representation of the same decision state and then **transplanted as a binding decision contract** into the concrete execution frame.

Working formulation:

1. **Compile state**: map the concrete task/history/budget into a minimal frame-neutral allocation state.
2. **Elicit policy**: ask the same model (or fixed policy module) to make only the investment decision in the abstract state, without seeing code-generation affordances.
3. **Commit decision**: freeze COMMIT/PASS before any code/tool-construction prompt is shown.
4. **Execute conditionally**: only if COMMIT is frozen, expose the concrete construction task to the executor.

The key claim is not ordinary planner/executor separation. It is **cross-frame transplantation of a policy that the model demonstrably has in an isomorphic representation but loses under an action affordance**.

## Closest prior art / threats

- **AlloBench** (arXiv:2607.23332): establishes the abstract-to-construction allocation gap and explicitly notes that existing budget-awareness methods have not addressed tool-investment transfer. Strongest motivation and benchmark threat.
- **MetaForge** (arXiv:2606.01801): unified Decide/Retrieve/Adapt/Forge orchestration, RL-optimized invocation necessity and forged-skill reusability with invocation-cost penalty. Strong threat to any generic 'learn when to create tools' claim; does not, from reviewed material, use an isomorphic abstract twin to recover and freeze a suppressed policy.
- **INTENT** (arXiv:2602.11541): budget-constrained planning for costly tool use using an intention-aware world model. Strong threat to generic budget-aware orchestration; not specifically reusable-tool investment under abstract/concrete framing.
- **CREATOR** (arXiv:2305.14318): disentangles abstract tool creation from concrete decision execution. Strong threat to generic reasoning/execution separation; not the same as extracting an allocation policy from an isomorphic frame and enforcing it before construction.
- **Plan-then-Execute architectures**: known general pattern. CPT must outperform a normal one-pass 'plan first' prompt to justify a distinct mechanism.

## Phase A falsification experiment

Use a reconstruction of AlloBench's paired allocation setting with matched hidden task streams and a fixed tool budget.

Compare, on the **same streams**:

A. Direct constructive allocation (R2-like): model chooses PASS or COMMIT; COMMIT requires code emission.
B. Plan-first baseline: model is told to reason about budget before making the same constructive decision in one context.
C. CPT: concrete history is compiled to a frame-neutral state; COMMIT/PASS is elicited separately and frozen; code is exposed only after a frozen COMMIT.
D. Oracle recurrence policy: a non-LLM upper/reference policy using the known benchmark rule for analysis only.

Primary metrics:
- first-sight commitment rate (lower is better under AlloBench's streams),
- competitive allocation score / realized utility,
- hot-class capture,
- trap-class budget waste,
- policy disagreement between abstract decision and concrete executor attempt.

Secondary metric:
- construction success conditional on a frozen COMMIT, to separate allocation from coding ability.

## Kill criteria

Kill CPT as a distinct research direction if **any** of the following holds:

1. A simple plan-first prompt recovers at least 95% of CPT's allocation improvement.
2. An existing budget-aware method (e.g. INTENT-style expected-utility controller) reaches the same result without cross-frame policy transplantation.
3. CPT only works because the abstract representation leaks the latent class distribution or removes information/effort that the direct condition genuinely needs.
4. The frozen decision degrades end-to-end utility because allocation and construction cannot be cleanly separated.
5. Prior art is found that already performs abstract-isomorphic policy elicitation followed by binding concrete execution in this setting.

## Positive bar

Continue only if CPT shows a reproducible frame-transfer advantage over direct constructive and ordinary plan-first baselines on matched streams, with no oracle information and with construction quality held separate from allocation quality.

Even a positive result would establish a useful mechanism/phenomenon, **not patent novelty or broad scientific novelty**. A renewed literature search is mandatory before any stronger claim.
