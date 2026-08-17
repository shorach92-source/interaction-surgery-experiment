# Prior-art recheck — 2026-08-17

## Narrow question

After a harmful nonlinear interaction among otherwise useful agent components has been localized, is there an existing method that selectively suppresses the harmful interaction while preserving the beneficial joint effect of the same coalition?

## Closest verified prior art

- **More Is Not Always Better: Cross-Component Interference in LLM Agent Scaffolding** — arXiv:2605.05716. Full-factorial component subsets, Shapley analysis, submodularity violations, and exploratory three-body synergy. Strong evidence that higher-order agent-component interactions exist; response proposed is interaction-aware subset selection, not selective repair of one sign of a mixed interaction.
- **Workflow-Localized Mechanism Learning (WML)** — arXiv:2607.20999. Very close threat. Diagnoses single-mechanism vs multi-relation defects, patches L2 composition protocols for relational defects, uses successful trajectories as preservation constraints, and validates bounded patches. It does not explicitly decompose utility and harm interaction terms or demonstrate removal of a harmful higher-order term while preserving a beneficial higher-order term from the same coalition.
- **What Is a Skill Worth? / SkillSV** — arXiv:2608.04562. Structure-aware Shapley-style valuation recovers unit interactions and guides safe pruning/compression. Primarily valuation/pruning rather than mixed-sign interaction surgery.
- **SkillSmith: Co-Evolving Skills and Tools** — arXiv:2606.01314. Models pairwise complementarity/conflict and jointly modifies skills/tools. Pairwise ecological interaction model; not an explicit higher-order mixed-sign surgery result.
- **SkillReact** — arXiv:2606.00448, and **SCR-Bench** — arXiv:2606.15242. Show compositional risk from individually benign skills and motivate composition checks/isolation. They establish the risk phenomenon but do not show preservation of a beneficial higher-order interaction while selectively removing a harmful one.
- **HarnessFix** — arXiv:2606.06324. Trace-guided localization plus scoped harness repair and regression-aware validation. General scoped repair, not interaction-term-specific repair.
- **ASSAY: Not All Skills Help** — arXiv:2606.15390. Measures per-skill causal heterogeneity and performs per-task skill suppression. Individual-skill masking rather than higher-order same-coalition selective interaction repair.
- **FATE** — arXiv:2605.11882. Pareto-aware safety/utility repair through failure trajectories. Strong safety-utility preservation baseline, but not explicit higher-order component-interaction surgery.

## Current novelty posture

Do **not** claim novelty yet.

The candidate gap has narrowed to a stricter claim:

> Given an already-localized higher-order coalition that produces both useful and harmful joint behavior, can a repair suppress the harmful nonlinear contribution while preserving the useful joint contribution, outperforming simpler scoped composition patches, context guards, or coalition gating?

WML is the strongest direct threat because its multi-relation L2 composition repair plus preservation constraints may already solve practical instances without explicit interaction decomposition.

## Next kill test

Before designing an Interaction Surgery algorithm, test whether a simple generic calibration guard can repair the replicated D3-02 case while keeping full-coalition task utility. If it reaches approximately >=95% harm suppression and >=95% utility retention, this case does not justify a specialized surgery mechanism.
