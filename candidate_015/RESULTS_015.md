# Candidate 015 — Capability-Gradient Warning result

## Decision

**Negative. Close Candidate 015. Do not tune CGW on these scenarios.**

The frozen pilot evaluated 32 synthetic forecasting instances with deterministic hidden future distributions: eight stable-linear controls, eight continued-superlinear cases, eight superlinear-looking saturation cases, and eight superlinear-history cases with future regime-change risk.

Each instance was forecast independently by the predeclared capability ordering:

1. `gpt-5.4-nano`
2. `gpt-5.4-mini`
3. `gpt-5.4`

All calls used `reasoning.effort = none`. All 32 instances had valid q10/q50/q90 output from all three models.

## Main result

Inverse scaling itself was reproduced in this synthetic pilot: the strongest model's normalized q90 error exceeded the best smaller-model q90 error by more than 0.05 on **15/32 = 46.9%** of instances.

However, the proposed ordered capability-gradient warning signal failed badly.

| Feature | AUROC | Spearman with continuous harm margin |
|---|---:|---:|
| CGW | 0.235 | -0.559 |
| q90 spread | 0.816 | 0.564 |
| overall cross-model disagreement | 0.784 | 0.519 |
| strongest-model interval width | 0.820 | 0.507 |
| recent-history curvature | **0.878** | **0.700** |

The best ordinary baseline was recent-history curvature with AUROC 0.878. The paired bootstrap for `CGW AUROC - curvature AUROC` was entirely negative:

- mean delta ≈ -0.649
- 95% CI ≈ **[-0.879, -0.368]**

This violates every performance-based continuation criterion for CGW.

## Events by family

- linear control: 0 / 8
- superlinear continuation: 1 / 8
- superlinear saturation: 6 / 8
- superlinear regime risk: 8 / 8

The inverse-scaling phenomenon therefore generalized beyond a single family, but the proposed warning mechanism did not.

## Mechanistic readout

The failure was informative. Harmful cases did **not** usually exhibit a smooth monotonic `nano -> mini -> full` upward progression. The strongest model often made a late capability cliff / outlier move, especially in saturation cases. As a result, the predeclared monotonic CGW score was lower on harmful cases rather than higher.

That observation does not justify a CGW v2. Ordinary q90 spread already detects this kind of outlier behavior well, and recent-history curvature performs even better in this pilot. Redefining CGW after observing this result would move the goalposts.

## Reproducibility note

The original live run was GitHub Actions run `32075102291`, created under an accidental Candidate-014 numbering collision. The run artifact was `candidate-014-cgw-32075102291`; the protocol/result have been renumbered to Candidate 015 without changing the experiment or metrics.

## Conclusion

The motivating inverse-scaling failure is real enough to reproduce, but **ordered capability gradient is not a useful special warning mechanism under this test**. Simple observable baselines dominate it by a wide margin.

Candidate 015 is closed under the project's falsification-first rule.
