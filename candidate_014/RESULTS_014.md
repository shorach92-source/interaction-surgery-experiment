# Candidate 014 — Falsifiable Novelty Certificate result

## Decision

**Negative. Close Candidate 014 under the predeclared Phase-A kill criterion.**

Candidate 014 tested whether forcing a scientific novelty judge to produce claim-level prior-art collisions and falsifiable distinguishing witnesses before scoring would improve agreement with human novelty judgments.

The public RINoBench test split was used. It contains 277 examples with structured research ideas, human novelty scores, human justifications and related works. Before any model output was observed, the pilot deterministically selected two examples from each gold score bucket (10 examples total) using a SHA-256 ordering over source identifiers.

All three arms used the same `gpt-5.4-mini` model, the same supplied RINoBench evidence and the same novelty rubric:

- `DIRECT`: holistic rubric judgment;
- `COMPARE`: explicit closest-related-work comparison before scoring;
- `FNC`: atomic contribution → closest collision → distinguishing witness → COLLAPSED/SURVIVES → score.

## Results

| Arm | N | MAE | Exact accuracy | Signed error | Spearman | High-novelty false-positive rate |
|---|---:|---:|---:|---:|---:|---:|
| DIRECT | 10 | 0.900 | 0.300 | +0.300 | 0.653 | 0.250 |
| COMPARE | 10 | 1.000 | 0.300 | -0.200 | 0.530 | 0.000 |
| FNC | 10 | 1.200 | 0.200 | 0.000 | 0.000 | 0.000 |

The predeclared Phase-A survival flag was `False`.

## Failure pattern

FNC did not merely miss a few examples. It collapsed all ten predictions to score `3`, including examples whose human gold scores spanned 1 through 5. In eight of ten examples it still marked all generated contribution witnesses as `SURVIVES`; therefore the witness procedure did not create useful ordinal separation.

Per frozen sample, FNC scores were:

- gold 1 → 3, 3
- gold 2 → 3, 3
- gold 3 → 3, 3
- gold 4 → 3, 3
- gold 5 → 3, 3

This produced zero rank correlation with the human labels.

## Interpretation

The structured falsification language reduced extreme high-novelty false positives, but it did so by inducing middle-score conservatism rather than by improving novelty discrimination. The simpler DIRECT arm had both lower MAE and substantially better rank correlation.

This is exactly the failure mode covered by the predeclared kill criterion: an apparent calibration benefit that comes from globally shrinking scores rather than better distinguishing novelty levels.

Do not tune witness definitions, score mapping, contribution counts or prompt wording on these ten observed examples. Any future work on scientific novelty assessment must start as a new candidate with a fresh prior-art search and an untouched evaluation design.
