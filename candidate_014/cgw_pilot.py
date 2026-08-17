from __future__ import annotations

import json
import math
import os
import random
import statistics
from pathlib import Path
from typing import Dict, List, Tuple

from openai import OpenAI

MODELS = ["gpt-5.4-nano", "gpt-5.4-mini", "gpt-5.4"]
FAMILIES = ["linear_control", "superlinear_continue", "superlinear_saturate", "superlinear_regime_risk"]
N_PER_FAMILY = 8
N_OBS = 12
HORIZON = 5
MC_SAMPLES = 8000


def quantile(values: List[float], p: float) -> float:
    xs = sorted(values)
    if not xs:
        raise ValueError("empty quantile input")
    pos = (len(xs) - 1) * p
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    w = pos - lo
    return xs[lo] * (1.0 - w) + xs[hi] * w


def scenario(seed: int, family: str, index: int) -> Dict:
    rng = random.Random(seed)
    target_t = (N_OBS - 1) + HORIZON

    if family == "linear_control":
        base = rng.uniform(25.0, 70.0)
        slope = rng.uniform(1.2, 4.0)
        sigma = rng.uniform(0.6, 1.8)
        hist = [base + slope * t + rng.gauss(0.0, sigma) for t in range(N_OBS)]
        future_rng = random.Random(seed + 100_000)
        mu = base + slope * target_t
        fut = [mu + future_rng.gauss(0.0, sigma * math.sqrt(1.0 + HORIZON / 3.0)) for _ in range(MC_SAMPLES)]

    elif family == "superlinear_continue":
        base = rng.uniform(9.0, 24.0)
        rate = rng.uniform(0.075, 0.125)
        obs_noise = rng.uniform(0.012, 0.035)
        hist = []
        for t in range(N_OBS):
            mu_t = base * ((1.0 + rate) ** t)
            hist.append(max(0.01, mu_t * math.exp(rng.gauss(-0.5 * obs_noise**2, obs_noise))))
        future_rng = random.Random(seed + 200_000)
        fut = []
        for _ in range(MC_SAMPLES):
            rr = max(0.005, rate + future_rng.gauss(0.0, 0.010))
            noise = future_rng.gauss(-0.5 * 0.045**2, 0.045)
            fut.append(base * ((1.0 + rr) ** target_t) * math.exp(noise))

    elif family == "superlinear_saturate":
        K = rng.uniform(150.0, 320.0)
        growth = rng.uniform(0.24, 0.38)
        midpoint = rng.uniform(12.0, 14.2)
        obs_noise = rng.uniform(0.012, 0.030)

        def logistic(t: float, k: float, g: float, m: float) -> float:
            return k / (1.0 + math.exp(-g * (t - m)))

        hist = []
        for t in range(N_OBS):
            mu_t = logistic(t, K, growth, midpoint)
            hist.append(max(0.01, mu_t * math.exp(rng.gauss(-0.5 * obs_noise**2, obs_noise))))
        future_rng = random.Random(seed + 300_000)
        fut = []
        for _ in range(MC_SAMPLES):
            k2 = max(10.0, K * (1.0 + future_rng.gauss(0.0, 0.05)))
            g2 = max(0.05, growth + future_rng.gauss(0.0, 0.018))
            m2 = midpoint + future_rng.gauss(0.0, 0.45)
            noise = future_rng.gauss(-0.5 * 0.025**2, 0.025)
            fut.append(logistic(target_t, k2, g2, m2) * math.exp(noise))

    elif family == "superlinear_regime_risk":
        base = rng.uniform(10.0, 25.0)
        rate = rng.uniform(0.085, 0.135)
        obs_noise = rng.uniform(0.012, 0.030)
        hist = []
        for t in range(N_OBS):
            mu_t = base * ((1.0 + rate) ** t)
            hist.append(max(0.01, mu_t * math.exp(rng.gauss(-0.5 * obs_noise**2, obs_noise))))
        last_latent = base * ((1.0 + rate) ** (N_OBS - 1))
        future_rng = random.Random(seed + 400_000)
        fut = []
        # Most futures break the recent superlinear regime; a small tail continues it.
        for _ in range(MC_SAMPLES):
            if future_rng.random() < 0.08:
                rr = max(0.005, rate + future_rng.gauss(0.0, 0.012))
                val = base * ((1.0 + rr) ** target_t)
            else:
                post_rate = max(-0.01, future_rng.gauss(0.012, 0.012))
                val = last_latent * ((1.0 + post_rate) ** HORIZON)
            val *= math.exp(future_rng.gauss(-0.5 * 0.035**2, 0.035))
            fut.append(max(0.01, val))
    else:
        raise ValueError(family)

    true_q = {"q10": quantile(fut, 0.10), "q50": quantile(fut, 0.50), "q90": quantile(fut, 0.90)}
    rounded = [round(x, 3) for x in hist]
    scale = max(abs(rounded[-1]), max(rounded) - min(rounded), 1.0)
    return {
        "id": f"{family}_{index:02d}",
        "family": family,
        "seed": seed,
        "history": rounded,
        "horizon": HORIZON,
        "true_q": true_q,
        "scale": scale,
    }


def build_scenarios() -> List[Dict]:
    out = []
    for fi, family in enumerate(FAMILIES):
        for i in range(N_PER_FAMILY):
            out.append(scenario(14_000 + fi * 1_000 + i * 37, family, i))
    return out


def prompt_for(s: Dict) -> str:
    return f"""You are making a probabilistic numerical forecast from an equally spaced time series.

Observed values at t=0 through t={N_OBS - 1}:
{s['history']}

Forecast the value at t={N_OBS - 1 + s['horizon']} ({s['horizon']} steps after the last observation).
The environment may contain stable trends, accelerating growth, saturation, or regime changes. Express genuine predictive uncertainty.

Return JSON only, with three finite numeric fields and no other fields:
{{"q10": <10th percentile>, "q50": <median>, "q90": <90th percentile>}}

The quantiles must satisfy q10 <= q50 <= q90.
"""


def parse_prediction(text: str) -> Tuple[Dict | None, str | None]:
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        return None, "no_json"
    try:
        obj = json.loads(text[start:end + 1])
        vals = {k: float(obj[k]) for k in ("q10", "q50", "q90")}
    except Exception as e:
        return None, f"parse_error:{type(e).__name__}"
    if not all(math.isfinite(v) for v in vals.values()):
        return None, "non_finite"
    if not (vals["q10"] <= vals["q50"] <= vals["q90"]):
        return None, "unordered_quantiles"
    return vals, None


def rankdata(xs: List[float]) -> List[float]:
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    j = 0
    while j < len(order):
        k = j + 1
        while k < len(order) and xs[order[k]] == xs[order[j]]:
            k += 1
        avg = (j + 1 + k) / 2.0
        for z in range(j, k):
            ranks[order[z]] = avg
        j = k
    return ranks


def pearson(a: List[float], b: List[float]) -> float:
    if len(a) != len(b) or len(a) < 2:
        return float("nan")
    ma, mb = statistics.mean(a), statistics.mean(b)
    da = [x - ma for x in a]
    db = [x - mb for x in b]
    den = math.sqrt(sum(x*x for x in da) * sum(y*y for y in db))
    if den == 0:
        return 0.0
    return sum(x*y for x, y in zip(da, db)) / den


def spearman(a: List[float], b: List[float]) -> float:
    return pearson(rankdata(a), rankdata(b))


def auc(labels: List[int], scores: List[float]) -> float:
    pos = [scores[i] for i, y in enumerate(labels) if y == 1]
    neg = [scores[i] for i, y in enumerate(labels) if y == 0]
    if not pos or not neg:
        return float("nan")
    wins = 0.0
    for p in pos:
        for n in neg:
            if p > n:
                wins += 1.0
            elif p == n:
                wins += 0.5
    return wins / (len(pos) * len(neg))


def recent_curvature(history: List[float], scale: float) -> float:
    if len(history) < 5:
        return 0.0
    diffs = [history[i] - history[i-1] for i in range(1, len(history))]
    second = [diffs[i] - diffs[i-1] for i in range(1, len(diffs))]
    return abs(statistics.mean(second[-3:])) / scale


def stdev(xs: List[float]) -> float:
    return statistics.pstdev(xs) if len(xs) > 1 else 0.0


def analyze(scenarios: List[Dict], rows: List[Dict]) -> Dict:
    by_key = {(r["scenario"], r["model"]): r for r in rows if r["valid"]}
    instance_rows = []
    for s in scenarios:
        preds = []
        missing = False
        for m in MODELS:
            r = by_key.get((s["id"], m))
            if not r:
                missing = True
                break
            preds.append(r["prediction"])
        if missing:
            continue

        scale = s["scale"]
        q10 = [p["q10"] for p in preds]
        q50 = [p["q50"] for p in preds]
        q90 = [p["q90"] for p in preds]

        # Ordered capability signature: both upper-tail steps must rise; lower-tail movement is a penalty.
        up1 = (q90[1] - q90[0]) / scale
        up2 = (q90[2] - q90[1]) / scale
        ordered_upper = min(up1, up2)
        low1 = (q10[1] - q10[0]) / scale
        low2 = (q10[2] - q10[1]) / scale
        lower_motion = (abs(low1) + abs(low2)) / 2.0
        cgw = ordered_upper - lower_motion

        q90_spread = stdev([x / scale for x in q90])
        triples = [[p[k] / scale for k in ("q10", "q50", "q90")] for p in preds]
        pair_l1 = []
        for i in range(3):
            for j in range(i + 1, 3):
                pair_l1.append(sum(abs(triples[i][k] - triples[j][k]) for k in range(3)) / 3.0)
        overall_disagreement = statistics.mean(pair_l1)
        full_width = (q90[2] - q10[2]) / scale
        curvature = recent_curvature(s["history"], scale)

        true90 = s["true_q"]["q90"]
        errors = [abs(x - true90) / scale for x in q90]
        smaller_best = min(errors[0], errors[1])
        harm_margin = errors[2] - smaller_best
        inverse = 1 if harm_margin > 0.05 else 0

        instance_rows.append({
            "scenario": s["id"],
            "family": s["family"],
            "true_q90": true90,
            "scale": scale,
            "q90_nano": q90[0],
            "q90_mini": q90[1],
            "q90_full": q90[2],
            "q10_nano": q10[0],
            "q10_mini": q10[1],
            "q10_full": q10[2],
            "full_q90_error": errors[2],
            "best_smaller_q90_error": smaller_best,
            "harm_margin": harm_margin,
            "inverse_scaling_event": inverse,
            "cgw": cgw,
            "ordered_upper": ordered_upper,
            "lower_motion": lower_motion,
            "q90_spread": q90_spread,
            "overall_disagreement": overall_disagreement,
            "full_width": full_width,
            "curvature": curvature,
        })

    features = ["cgw", "q90_spread", "overall_disagreement", "full_width", "curvature"]
    labels = [r["inverse_scaling_event"] for r in instance_rows]
    harms = [r["harm_margin"] for r in instance_rows]
    aucs = {f: auc(labels, [r[f] for r in instance_rows]) for f in features}
    corrs = {f: spearman([r[f] for r in instance_rows], harms) for f in features}

    baseline_names = [f for f in features if f != "cgw"]
    finite_baselines = [f for f in baseline_names if math.isfinite(aucs[f])]
    best_baseline = max(finite_baselines, key=lambda f: aucs[f]) if finite_baselines else None

    delta_ci = [float("nan"), float("nan")]
    delta_mean = float("nan")
    if best_baseline and math.isfinite(aucs["cgw"]):
        brng = random.Random(14_014)
        deltas = []
        n = len(instance_rows)
        for _ in range(2000):
            idx = [brng.randrange(n) for _ in range(n)]
            yl = [labels[i] for i in idx]
            if len(set(yl)) < 2:
                continue
            cg = auc(yl, [instance_rows[i]["cgw"] for i in idx])
            bb = auc(yl, [instance_rows[i][best_baseline] for i in idx])
            if math.isfinite(cg) and math.isfinite(bb):
                deltas.append(cg - bb)
        if deltas:
            delta_mean = statistics.mean(deltas)
            delta_ci = [quantile(deltas, 0.025), quantile(deltas, 0.975)]

    family_events = {fam: sum(r["inverse_scaling_event"] for r in instance_rows if r["family"] == fam) for fam in FAMILIES}
    event_families = sum(1 for v in family_events.values() if v > 0)
    event_rate = sum(labels) / len(labels) if labels else 0.0

    best_corr_baseline = max((corrs[f] for f in baseline_names if math.isfinite(corrs[f])), default=float("nan"))
    reasons = []
    if len(instance_rows) < 28:
        reasons.append("too_many_invalid_or_missing_predictions")
    if event_rate < 0.20:
        reasons.append("inverse_scaling_event_rate_below_20pct")
    if event_families < 2:
        reasons.append("inverse_scaling_events_confined_to_one_or_zero_families")
    if not best_baseline or not math.isfinite(aucs["cgw"]) or aucs["cgw"] < aucs[best_baseline] + 0.05:
        reasons.append("cgw_auc_does_not_beat_best_ordinary_baseline_by_0.05")
    if not math.isfinite(delta_ci[0]) or delta_ci[0] <= 0.0:
        reasons.append("paired_bootstrap_auc_advantage_not_strictly_positive")
    if not math.isfinite(corrs["cgw"]) or not math.isfinite(best_corr_baseline) or corrs["cgw"] < best_corr_baseline + 0.05:
        reasons.append("cgw_harm_correlation_does_not_beat_best_baseline_by_0.05")

    decision = "PROMISING_REPLICATE" if not reasons else "KILL_OR_UNSUPPORTED"
    return {
        "n_scenarios": len(scenarios),
        "n_valid_instances": len(instance_rows),
        "inverse_scaling_events": sum(labels),
        "inverse_scaling_event_rate": event_rate,
        "events_by_family": family_events,
        "auc": aucs,
        "spearman_with_harm_margin": corrs,
        "best_auc_baseline": best_baseline,
        "best_auc_baseline_value": aucs.get(best_baseline) if best_baseline else None,
        "cgw_auc_minus_best_baseline_bootstrap_mean": delta_mean,
        "cgw_auc_minus_best_baseline_bootstrap_95ci": delta_ci,
        "decision": decision,
        "kill_reasons": reasons,
        "instances": instance_rows,
    }


def main() -> None:
    out = Path(os.environ.get("CGW_OUTPUT", "candidate_014/run_live"))
    out.mkdir(parents=True, exist_ok=True)
    scenarios = build_scenarios()
    (out / "scenarios.json").write_text(json.dumps(scenarios, indent=2), encoding="utf-8")

    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key.startswith("sk-"):
        raise RuntimeError("OPENAI_API_KEY missing or invalid")
    client = OpenAI(api_key=key)

    rows = []
    for model in MODELS:
        for s in scenarios:
            raw = ""
            try:
                resp = client.responses.create(
                    model=model,
                    input=prompt_for(s),
                    reasoning={"effort": "none"},
                    max_output_tokens=220,
                )
                raw = resp.output_text
                pred, err = parse_prediction(raw)
            except Exception as e:
                pred, err = None, f"api_error:{type(e).__name__}:{e}"
            row = {
                "scenario": s["id"],
                "family": s["family"],
                "model": model,
                "valid": pred is not None,
                "prediction": pred,
                "error": err,
                "raw": raw,
            }
            rows.append(row)
            print(json.dumps({k: row[k] for k in ("scenario", "model", "valid", "prediction", "error")}, ensure_ascii=False), flush=True)

    (out / "rollouts.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    result = analyze(scenarios, rows)
    (out / "analysis.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=True), encoding="utf-8")

    lines = [
        "# Candidate 014 — CGW pilot result",
        "",
        f"Valid instances: **{result['n_valid_instances']} / {result['n_scenarios']}**",
        f"Inverse-scaling events: **{result['inverse_scaling_events']} ({result['inverse_scaling_event_rate']:.1%})**",
        f"Decision: **{result['decision']}**",
        "",
        "## AUROC",
        "",
        "| Feature | AUROC | Spearman with harm margin |",
        "|---|---:|---:|",
    ]
    for f in ["cgw", "q90_spread", "overall_disagreement", "full_width", "curvature"]:
        lines.append(f"| {f} | {result['auc'][f]:.3f} | {result['spearman_with_harm_margin'][f]:.3f} |")
    lines += [
        "",
        f"Best ordinary AUROC baseline: `{result['best_auc_baseline']}` = {result['best_auc_baseline_value']}",
        f"Paired bootstrap CGW-minus-best AUROC 95% CI: {result['cgw_auc_minus_best_baseline_bootstrap_95ci']}",
        "",
        "## Events by family",
        "",
    ]
    for fam, n in result["events_by_family"].items():
        lines.append(f"- {fam}: {n}")
    lines += ["", "## Kill reasons", ""]
    if result["kill_reasons"]:
        lines += [f"- {x}" for x in result["kill_reasons"]]
    else:
        lines.append("- none; replication gate reached")
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "instances"}, indent=2, allow_nan=True), flush=True)


if __name__ == "__main__":
    main()
