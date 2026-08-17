# Candidate 015 — Capability-Gradient Warning (CGW)

## Status

**Closed after negative frozen pilot.** Candidate gap only; no novelty claim was established.

## Observation motivating the candidate

Merrill, Lee & Karger (2026), *Is Capability a Liability? More Capable Language Models Make Worse Forecasts When It Matters Most* (arXiv:2605.22672), reports inverse scaling on distributional forecasting under superlinear growth / regime-change risk. Their per-quantile analysis localizes much of the degradation to the upper tail: more capable models push upper quantiles upward while lower quantiles move much less.

This candidate asked:

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

Normalize forecast differences by the scale of the observed series. For q90 define two ordered capability steps:

- `upper_step_1 = q90_mini - q90_nano`,
- `upper_step_2 = q90_full - q90_mini`.

The upper-tail signal is `ordered_upper = min(upper_step_1, upper_step_2)`, so a high score requires the upper tail to rise at **both** capability transitions rather than merely differing between endpoints.

For q10, compute the mean absolute movement over the same two transitions:

- `lower_motion = (abs(q10_mini-q10_nano) + abs(q10_full-q10_mini)) / 2`.

Then:

`CGW = ordered_upper - lower_motion`.

The intended signature is therefore a consistently rising upper tail with a comparatively stable lower tail. This definition was frozen before the first live result.

## Ex-post target

For each instance compute normalized q90 absolute error for all three models against the hidden true q90.

`inverse_scaling_event = full_q90_error > min(nano_q90_error, mini_q90_error) + 0.05`

Also retain the continuous harm margin:

`harm_margin = full_q90_error - min(nano_q90_error, mini_q90_error)`.

## Strong ordinary baselines

CGW had to beat, on the same instances:

- standard deviation of the three q90 forecasts,
- mean cross-model disagreement over q10/q50/q90,
- strongest-model interval width q90-q10,
- recent-history curvature.

## Kill criteria

Close the candidate if any of the following holds:

1. Fewer than 20% of valid instances exhibit the predeclared inverse-scaling event.
2. CGW AUROC is less than `best ordinary baseline AUROC + 0.05`.
3. A paired instance bootstrap does not put the 95% lower bound of `CGW AUROC - best baseline AUROC` above zero.
4. CGW Spearman correlation with continuous harm margin is less than `best ordinary baseline correlation + 0.05`.
5. The effect depends on parse failures or one scenario family only.

## Prior-art boundary

Nearby but not identical:

- ordinary ensemble spread/disagreement for uncertainty;
- multi-quantile post-hoc calibration such as MultiQT;
- inter-model disagreement / semantic divergence methods;
- the inverse-scaling forecasting paper itself, which documents the capability effect but does not, in the reviewed material, propose ordered per-instance capability movement as an ex-ante warning feature.

The frozen pilot failed the predeclared gates; see `RESULTS_015.md`.
