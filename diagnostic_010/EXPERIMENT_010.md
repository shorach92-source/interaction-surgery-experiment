# Diagnostic 010 — Skill-induced procedural modal collapse

## Status

Empirical diagnostic only. **Novelty is not established.**

## Narrow question

Does packaging identical procedural guidance as a reusable agent skill increase the tendency to flatten normative modality — especially treating conditional or optional steps as mandatory work — compared with presenting the same rule as ordinary task guidance?

This is motivated by Dong et al. (2026), who report that relevant skills frequently induce excessive procedure and can turn validation checklists/construction recipes into mandatory work. Their published taxonomy does not isolate modality by changing only the normative force of an otherwise identical step.

## Factorial design

Six task domains:
- customer support
- data import
- deployment
- research
- scheduling
- file cleanup

For each domain, the same extra costly action appears under four modal conditions:
1. MUST — extra action is required.
2. SHOULD-TRUE — conditional recommendation and the condition is true.
3. SHOULD-FALSE — same conditional recommendation but condition is false.
4. MAY — explicitly optional assurance step; task objective says minimize unnecessary actions.

Each condition is presented in two forms:
- `inline`: ordinary task guidance;
- `skill`: the same rule inside a loaded reusable skill that is declared relevant.

The semantic rule text is held constant across presentation forms; only the wrapper changes.

## Metrics

- Required-extra rate: execution of the extra step for MUST and SHOULD-TRUE.
- Unnecessary-extra rate: execution for SHOULD-FALSE and MAY.
- Core completion rate.
- Modal accuracy.
- Modal Collapse Index (MCI): `skill unnecessary-extra rate - inline unnecessary-extra rate`.

## One-repetition pilot

6 domains x 4 modal conditions x 2 presentation forms = 48 live calls on `gpt-5.4-mini`, `reasoning.effort=none`.

## Falsification criteria

Reject the skill-specific modal-collapse hypothesis if any of the following holds:
- MCI <= 0.10 in the pilot and no coherent domain-level pattern appears;
- skill presentation does not selectively increase optional/conditional over-execution;
- any observed difference is explained by loss of required-step compliance or core task completion rather than modality;
- stronger prior art is found that already measures this exact skill-vs-inline modality interaction.

If a strong positive signal appears, freeze the six scenarios and replicate before testing any mitigation.

## Prior-art boundary

This diagnostic does NOT claim novelty for typed hard/soft/deontic constraints. U-Define already distinguishes hard and soft constraints with different verification; PolicyKG classifies obligations, permissions and prohibitions into formal constraints; Skill-Use measures skill trigger/compliance/boundary. The candidate phenomenon is narrower: whether the *skill packaging itself* changes behavioral fidelity to normative force.
