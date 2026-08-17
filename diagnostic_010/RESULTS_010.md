# Diagnostic 010 — Skill modal-collapse result

## Decision

**Negative. Reject the simple skill-wrapper modal-collapse hypothesis.**

The diagnostic compared identical procedural rules presented as ordinary task guidance versus inside a loaded relevant reusable skill, across six domains and four normative modes (MUST, SHOULD-condition-true, SHOULD-condition-false, MAY).

## Guarded pilot

The first 48-call pilot included an explicit generic instruction not to reinterpret optional guidance as mandatory.

| Presentation | Required-extra rate | Unnecessary-extra rate | Core completion | Modal accuracy |
|---|---:|---:|---:|---:|
| inline | 0.917 | 0.000 | 1.000 | 0.958 |
| skill | 0.917 | 0.000 | 1.000 | 0.958 |

MCI = 0.000.

Because that prompt contained an anti-collapse reminder, a negative result could not by itself falsify the phenomenon.

## Unguarded pilot

A second frozen 48-call run removed only the anti-collapse sentence. Scenarios, model, modality rules, cost objective, action set, scoring and `reasoning.effort=none` remained unchanged.

| Presentation | Required-extra rate | Unnecessary-extra rate | Core completion | Modal accuracy |
|---|---:|---:|---:|---:|
| inline | 1.000 | 0.000 | 1.000 | 1.000 |
| skill | 1.000 | 0.000 | 1.000 | 1.000 |

MCI = 0.000.

## Interpretation

In this controlled planning-only setting, packaging a relevant procedural rule as a reusable skill did not flatten MUST/SHOULD/MAY distinctions. The model correctly executed required/condition-satisfied extra actions and omitted condition-false/optional costly actions in both presentation formats.

Therefore, the harmful-skill observation reported by Dong et al. (2026) cannot be explained by a simple `skill wrapper -> stronger normative force` mechanism under this setup. The failures likely require richer mechanisms such as long-horizon execution, procedural interactions, defaults/templates, tool feedback, or verification loops.

Do not tune this diagnostic to force a positive effect. The current candidate is closed.
