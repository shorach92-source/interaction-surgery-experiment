# Candidate 014 — Capability-Gradient Warning (CGW)

## Status

Candidate gap only. No novelty claim.

## Observation motivating the candidate

Merrill, Lee & Karger (2026), *Is Capability a Liability? More Capable Language Models Make Worse Forecasts When It Matters Most* (arXiv:2605.22672), reports inverse scaling on distributional forecasting under superlinear growth / regime-change risk. Their per-quantile analysis localizes much of the degradation to the upper tail: more capable models push upper quantiles upward while lower quantiles move much less.

This candidate asks a different question from the paper:

> Can the **ordered direction of forecast change across capability levels on one instance** warn us, before the future is observed, that the strongest model's upper-tail forecast is brittle?

This is not ordinary ensemble disagreement. CGW uses an externally fixed ordering of model capability and measures directional/asymmetric movement through that ordering.

## Predeclared live pilot

Use one current model family with fixed order:

1. `gpt-5.4-nano`
2. `gpt-5.4-mini`
3. `gpt-5.4`

All use `reasoning.effort = none` and the same forecast prompt.

Generate 32 deterministic synthetic forecasting instances, eight each from four families:

- stable linear control,
- continued superlinear growth,
- superlinear-looking saturation,
- superlinear history with future regime-change risk.

The model sees only the observed numerical history and forecast horizon. The generator retains the hidden future distribution and computes the oracle q10/q50/q90 independently by seeded Monte Carlo.

Each model returns q10/q50/q90 for the same target horizon. No model sees another model's forecast or its place in the capability ordering.

## Candidate feature

For normalized forecasts across capability ranks 0,1,2:

- `upper_slope` = least-squares slope of q90 vs capability rank,
- `lower_slope` = least-squares slope of q10 vs capability rank,
- `CGW = upper_slope - lower_slope`.

The intended signature is a rising upper tail with a comparatively stable lower tail.

## Ex-post target

For each instance compute normalized q90 absolute error for all three models against the hidden true q90.

`inverse_scaling_event = full_q90_error > min(nano_q90_error, mini_q90_error) + 0.05`

Also retain the continuous harm margin:

`harm_margin = full_q90_error - min(nano_q90_error, mini_q90_error)`.

## Strong ordinary baselines

CGW must beat, on the same instances:

- standard deviation of the three q90 forecasts,
- mean cross-model disagreement over q10/q50/q90,
- strongest-model interval width q90-q10,
- recent-history curvature.

This deliberately makes the candidate hard to save: with only three ordered models, ordinary spread may contain nearly all useful information in the slope.

## Kill criteria

Close Candidate 014 if any of the following holds:

1. Fewer than 20% of valid instances exhibit the predeclared inverse-scaling event.
2. CGW AUROC is less than `best ordinary baseline AUROC + 0.05`.
3. A paired instance bootstrap does not put the 95% lower bound of `CGW AUROC - best baseline AUROC` above zero.
4. CGW Spearman correlation with continuous harm margin is less than `best ordinary baseline correlation + 0.05`.
5. The effect depends on parse failures or one scenario family only.

A positive pilot is not evidence of novelty. It would only justify replication on additional model families / real data and a renewed prior-art search.

## Prior-art boundary

Nearby but not identical:

- ordinary ensemble spread/disagreement for uncertainty;
- multi-quantile post-hoc calibration such as MultiQT;
- inter-model disagreement / semantic divergence methods;
- the inverse-scaling forecasting paper itself, which documents the capability effect but does not, in the reviewed material, propose ordered per-instance capability slope as an ex-ante warning feature.

If a direct ordered-capability warning method is found later, close this candidate regardless of pilot performance.
