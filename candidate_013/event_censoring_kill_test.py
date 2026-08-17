from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np


def log_poisson_pmf(k: int, mu: float) -> float:
    return k * math.log(mu) - mu - math.lgamma(k + 1)


def poisson_sf_ge(k: int, mu: float) -> float:
    """P[X >= k] for Poisson(mu), using direct recurrence for this small benchmark."""
    if k <= 0:
        return 1.0
    p = math.exp(-mu)
    cdf = p
    for j in range(1, k):
        p *= mu / j
        cdf += p
    return max(1e-300, min(1.0, 1.0 - cdf))


def mle_multiplier(observations: list[dict], base_hat: dict[int, float], stores: set[int] | None = None) -> float:
    best_ll = -float("inf")
    best_m = None
    # Predeclared broad grid: no tuning to individual seeds.
    for m in np.linspace(0.5, 4.0, 701):
        ll = 0.0
        for o in observations:
            if stores is not None and o["store"] not in stores:
                continue
            mu = base_hat[o["store"]] * float(m)
            if o["censored"]:
                ll += math.log(poisson_sf_ge(o["cap"], mu))
            else:
                ll += log_poisson_pmf(o["sales"], mu)
        if ll > best_ll:
            best_ll = ll
            best_m = float(m)
    assert best_m is not None
    return best_m


def simulate(seed: int, nstores: int = 25, base_days: int = 120, event_occurrences: int = 4, m_true: float = 1.9) -> dict:
    rng = np.random.default_rng(seed)
    base_rates = rng.uniform(35.0, 70.0, nstores)

    # Ordinary non-event demand is fully observed and estimates each store's base rate.
    base_hat: dict[int, float] = {}
    for s, lam in enumerate(base_rates):
        base_hat[s] = float(rng.poisson(lam, base_days).mean())

    observations: list[dict] = []
    peer_cap_ratios = (0.9, 1.4, 2.6, 3.2)
    for s, lam in enumerate(base_rates):
        for e in range(event_occurrences):
            latent = int(rng.poisson(lam * m_true))
            if s == 0:
                # Target store: inventory is far below event demand on every event occurrence.
                # This makes local event magnitude effectively only lower-bounded by sales.
                cap = 10
            else:
                # Peer stores expose the same event under different inventory ceilings,
                # producing a mix of censored and uncensored observations.
                cap = max(1, int(round(lam * peer_cap_ratios[e])))
            censored = latent >= cap
            sales = min(latent, cap)
            observations.append({
                "store": s,
                "event_index": e,
                "latent": latent,
                "cap": cap,
                "sales": sales,
                "censored": bool(censored),
            })

    target = [o for o in observations if o["store"] == 0]
    # The benchmark requires all target event occurrences to be censored.
    if not all(o["censored"] for o in target):
        raise RuntimeError(f"seed {seed} violated predeclared all-target-censored condition")

    naive_local = (sum(o["sales"] for o in target) / len(target)) / base_hat[0]
    local_censored = mle_multiplier(target, base_hat, stores={0})
    pooled_censored = mle_multiplier(observations, base_hat)

    target_true_mean = float(base_rates[0] * m_true)
    target_pred_mean = float(base_hat[0] * pooled_censored)
    target_naive_mean = float(base_hat[0] * naive_local)

    peer = [o for o in observations if o["store"] != 0]
    return {
        "seed": seed,
        "true_multiplier": m_true,
        "naive_local_multiplier": naive_local,
        "local_censored_multiplier": local_censored,
        "pooled_censored_multiplier": pooled_censored,
        "pooled_multiplier_relative_error": abs(pooled_censored - m_true) / m_true,
        "target_true_event_mean": target_true_mean,
        "target_naive_event_mean": target_naive_mean,
        "target_pooled_event_mean": target_pred_mean,
        "target_pooled_relative_error": abs(target_pred_mean - target_true_mean) / target_true_mean,
        "target_censored_events": sum(o["censored"] for o in target),
        "peer_censored_events": sum(o["censored"] for o in peer),
        "peer_uncensored_events": sum(not o["censored"] for o in peer),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seeds", type=int, default=10)
    p.add_argument("--seed-start", type=int, default=1000)
    p.add_argument("--output", default="candidate_013/run")
    args = p.parse_args()

    rows = [simulate(args.seed_start + i) for i in range(args.seeds)]

    mean_mult_err = float(np.mean([r["pooled_multiplier_relative_error"] for r in rows]))
    max_mult_err = float(np.max([r["pooled_multiplier_relative_error"] for r in rows]))
    mean_target_err = float(np.mean([r["target_pooled_relative_error"] for r in rows]))
    max_target_err = float(np.max([r["target_pooled_relative_error"] for r in rows]))
    mean_naive_mult = float(np.mean([r["naive_local_multiplier"] for r in rows]))
    mean_local_censored = float(np.mean([r["local_censored_multiplier"] for r in rows]))
    mean_pooled = float(np.mean([r["pooled_censored_multiplier"] for r in rows]))

    killed = mean_mult_err <= 0.10 and mean_target_err <= 0.10
    summary = {
        "seeds": args.seeds,
        "true_multiplier": 1.9,
        "mean_naive_local_multiplier": mean_naive_mult,
        "mean_local_censored_multiplier": mean_local_censored,
        "mean_pooled_censored_multiplier": mean_pooled,
        "mean_pooled_multiplier_relative_error": mean_mult_err,
        "max_pooled_multiplier_relative_error": max_mult_err,
        "mean_target_pooled_relative_error": mean_target_err,
        "max_target_pooled_relative_error": max_target_err,
        "kill_threshold_relative_error": 0.10,
        "candidate_killed_by_predeclared_baseline": bool(killed),
        "total_peer_uncensored_events": int(sum(r["peer_uncensored_events"] for r in rows)),
        "total_peer_censored_events": int(sum(r["peer_censored_events"] for r in rows)),
    }

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "per_seed.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "# Candidate 013 — Event-censoring transfer kill test",
        "",
        f"Seeds: {args.seeds}",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f'| True event multiplier | {summary["true_multiplier"]:.3f} |',
        f'| Mean naive-local multiplier | {mean_naive_mult:.3f} |',
        f'| Mean local censored-MLE multiplier | {mean_local_censored:.3f} |',
        f'| Mean pooled censored-MLE multiplier | {mean_pooled:.3f} |',
        f'| Mean pooled multiplier relative error | {mean_mult_err:.3%} |',
        f'| Max pooled multiplier relative error | {max_mult_err:.3%} |',
        f'| Mean target event-mean relative error | {mean_target_err:.3%} |',
        f'| Max target event-mean relative error | {max_target_err:.3%} |',
        "",
        f'Predeclared kill criterion met: **{killed}**',
    ]
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
