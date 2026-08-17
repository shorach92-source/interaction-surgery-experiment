# Diagnostic 009 — Same-frame prospective allocation scaffold

## Status

Diagnostic extension only. **Not a novelty claim and not an exact AllocBench reproduction.**

## Question

AllocBench reports that GPT-5.4-mini is selective in the abstract allocation frame but becomes strongly first-sight-eager once COMMIT requires code emission. Our earlier one-seed reconstructed pilot unexpectedly found that an ordinary plan-first prompt greatly improved allocation while CPT did not.

This diagnostic asks whether that improvement is:

1. merely a generic instruction-to-think effect, or
2. specifically associated with making prospective recurrence/opportunity-cost reasoning explicit inside the same constructive R2-like frame.

## Fixed setup

- model: `gpt-5.4-mini`
- Responses API reasoning effort: `none`
- reconstructed T=60, N=8, B=3 stream generator from Candidate 008
- five deterministic streams: 2000–2004
- same stream, history, current family, problem, budget, horizon, and scoring across conditions
- COMMIT requires immediate non-empty Python `def solve(...)` code in every condition

These streams are reconstructed from the paper's published high-level generator, not the authors' canonical artifacts.

## Conditions

### Direct

No extra deliberation scaffold.

### Generic-think

One generic same-frame instruction to think carefully about the whole session rather than react only to the current task. It does not name recurrence, opportunity cost, or waiting-for-evidence logic.

### Prospective

A four-part checklist explicitly asks the model to evaluate:
- evidence of recurrence,
- opportunity cost of spending a scarce build slot,
- remaining horizon,
- value of waiting for another occurrence.

No future class frequencies or hot/trap labels are exposed.

## Primary metrics

- competitive score vs hindsight top-B optimum
- first-sight commitment rate
- hot-class capture
- trap builds

Secondary:
- simple construction-presence check for committed responses

## Interpretation / kill rules

- If `generic_think` is approximately as good as `prospective`, reject any special mechanism claim; the effect is ordinary deliberation prompting.
- If neither robustly improves over `direct`, reject the one-seed effect as unstable.
- If `prospective` is materially and consistently better across reconstructed streams, treat that only as motivation for an exact/canonical AllocBench extension and renewed prior-art review.
- Existing budget-aware planning methods already make generic budget-aware prompting non-novel; only a reproducible *specific framing-gap result* could remain interesting.
