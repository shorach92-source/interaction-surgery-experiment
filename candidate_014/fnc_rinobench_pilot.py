from __future__ import annotations

import hashlib
import json
import math
import os
import statistics
import urllib.request
from pathlib import Path

from openai import OpenAI

TEST_URL = "https://raw.githubusercontent.com/TimSchopf/RINoBench/main/data/final_benchmark_dataset/test.json"
LABEL_URL = "https://raw.githubusercontent.com/TimSchopf/RINoBench/main/data/final_benchmark_dataset/label_descriptions.json"
OUT = Path("candidate_014/pilot_results")
OUT.mkdir(parents=True, exist_ok=True)
MODEL = os.environ.get("FNC_MODEL", "gpt-5.4-mini")
PER_SCORE = int(os.environ.get("FNC_PER_SCORE", "2"))


def load_json(url: str):
    with urllib.request.urlopen(url, timeout=120) as r:
        return json.loads(r.read())


def freeze_sample(rows):
    groups = {}
    for row in rows:
        score = int(row["novelty_score"])
        groups.setdefault(score, []).append(row)
    frozen = []
    for score in sorted(groups):
        ranked = sorted(
            groups[score],
            key=lambda r: hashlib.sha256(str(r.get("source", "")).encode()).hexdigest(),
        )
        frozen.extend(ranked[:PER_SCORE])
    return frozen


def compact_works(works):
    out = []
    preferred = ("title", "abstract", "summary", "year", "venue")
    for i, w in enumerate(works, 1):
        if isinstance(w, dict):
            c = {k: w[k] for k in preferred if k in w}
            if not c:
                c = w
        else:
            c = {"text": str(w)}
        c = {"work_id": i, **c}
        out.append(c)
    return out


def base_material(row, labels):
    return (
        "NOVELTY RUBRIC:\n" + json.dumps(labels, ensure_ascii=False) +
        "\n\nRESEARCH IDEA:\n" + json.dumps(row["research_idea"], ensure_ascii=False) +
        "\n\nRELATED WORKS (the complete evidence set for this experiment):\n" +
        json.dumps(compact_works(row["related_works"]), ensure_ascii=False)
    )


def prompt_direct(row, labels):
    return f"""You are judging the scientific novelty of a research idea using only the supplied related works.
Follow the supplied 1-5 novelty rubric. Judge the idea holistically and ground the judgment in the literature.
Return JSON only: {{"score": <integer 1-5>, "reason": "brief literature-grounded reason"}}.

{base_material(row, labels)}"""


def prompt_compare(row, labels):
    return f"""You are judging the scientific novelty of a research idea using only the supplied related works.
Before scoring, explicitly identify the closest prior works and compare the proposed idea against them. Do not reward wording differences; reward material methodological, problem, or capability differences.
Return JSON only with keys:
{{"closest_work_ids": [<up to 3 integers>], "material_differences": ["..."], "score": <integer 1-5>, "reason": "brief reason"}}.

{base_material(row, labels)}"""


def prompt_fnc(row, labels):
    return f"""You are a falsification-first novelty examiner. Do NOT start by assigning a novelty score.
Use only the supplied related works.

Procedure:
1. Decompose the proposed idea into at most 3 atomic claimed contributions.
2. For each contribution, identify the closest collision among the related works.
3. State what the closest work already covers.
4. State the MINIMAL DISTINGUISHING WITNESS that must be true, based on the proposed idea as written, for this contribution to be materially different. A witness must name a concrete method, capability, assumption, mechanism, or evaluation distinction; vague phrases such as 'more comprehensive', 'novel framework', 'better performance', or mere application to a new dataset do not count.
5. If no material witness can be stated from the idea, mark that contribution COLLAPSED. Otherwise mark it SURVIVES.
6. Only after all contributions are tested, derive a 1-5 novelty score using the supplied rubric. A high score requires material surviving witnesses, not persuasive prose.

Return JSON only:
{{
  "contributions": [
    {{"claim": "...", "closest_work_id": <integer>, "already_covered": "...", "witness": "...", "status": "COLLAPSED|SURVIVES"}}
  ],
  "score": <integer 1-5>,
  "reason": "brief final reason"
}}.

{base_material(row, labels)}"""


def parse_json(text: str):
    s, e = text.find("{"), text.rfind("}")
    if s < 0 or e < s:
        raise ValueError("no JSON object")
    return json.loads(text[s:e+1])


def call(client, prompt, max_tokens):
    r = client.responses.create(
        model=MODEL,
        input=prompt,
        reasoning={"effort": "none"},
        max_output_tokens=max_tokens,
    )
    return r.output_text


def ranks(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    r = [0.0] * len(vals)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def pearson(a, b):
    if len(a) < 2:
        return 0.0
    ma, mb = statistics.mean(a), statistics.mean(b)
    num = sum((x-ma)*(y-mb) for x, y in zip(a, b))
    da = math.sqrt(sum((x-ma)**2 for x in a))
    db = math.sqrt(sum((y-mb)**2 for y in b))
    return num/(da*db) if da and db else 0.0


def metrics(rows, arm):
    xs = [r for r in rows if r["arm"] == arm and r.get("pred_score") is not None]
    gold = [r["gold_score"] for r in xs]
    pred = [r["pred_score"] for r in xs]
    return {
        "n": len(xs),
        "mae": statistics.mean(abs(p-g) for p, g in zip(pred, gold)),
        "exact_accuracy": statistics.mean(p == g for p, g in zip(pred, gold)),
        "signed_error": statistics.mean(p-g for p, g in zip(pred, gold)),
        "spearman": pearson(ranks(pred), ranks(gold)),
        "high_false_positive_rate": (
            sum(1 for p, g in zip(pred, gold) if g <= 2 and p >= 4) /
            max(1, sum(1 for g in gold if g <= 2))
        ),
    }


def main():
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key.startswith("sk-"):
        raise RuntimeError("OPENAI_API_KEY missing")
    client = OpenAI(api_key=key)
    data = load_json(TEST_URL)
    labels = load_json(LABEL_URL)
    sample = freeze_sample(data)

    manifest = [
        {"source": r.get("source"), "venueid": r.get("venueid"), "gold_score": int(r["novelty_score"])}
        for r in sample
    ]
    (OUT / "frozen_sample_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    arms = [
        ("direct", prompt_direct, 500),
        ("compare", prompt_compare, 700),
        ("fnc", prompt_fnc, 1300),
    ]
    results = []
    for idx, row in enumerate(sample):
        for arm, fn, max_tokens in arms:
            raw = call(client, fn(row, labels), max_tokens)
            rec = {
                "sample_index": idx,
                "source": row.get("source"),
                "gold_score": int(row["novelty_score"]),
                "arm": arm,
                "raw": raw,
            }
            try:
                obj = parse_json(raw)
                score = int(obj.get("score"))
                if not 1 <= score <= 5:
                    raise ValueError("score out of range")
                rec["pred_score"] = score
                rec["parsed"] = obj
                if arm == "fnc":
                    contribs = obj.get("contributions", [])
                    rec["fnc_collapsed"] = sum(str(c.get("status", "")).upper() == "COLLAPSED" for c in contribs if isinstance(c, dict))
                    rec["fnc_survives"] = sum(str(c.get("status", "")).upper() == "SURVIVES" for c in contribs if isinstance(c, dict))
            except Exception as exc:
                rec["pred_score"] = None
                rec["parse_error"] = repr(exc)
            results.append(rec)
            print(json.dumps({k: rec.get(k) for k in ("sample_index", "gold_score", "arm", "pred_score")}), flush=True)

    (OUT / "rollouts.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in results) + "\n", encoding="utf-8")
    summary = {arm: metrics(results, arm) for arm, _, _ in arms}
    complete = all(summary[a]["n"] == len(sample) for a, _, _ in arms)
    if complete:
        best_baseline_mae = min(summary["direct"]["mae"], summary["compare"]["mae"])
        best_baseline_spearman = max(summary["direct"]["spearman"], summary["compare"]["spearman"])
        summary["phase_a_survives"] = (
            summary["fnc"]["mae"] < best_baseline_mae
            and summary["fnc"]["spearman"] >= best_baseline_spearman - 0.05
        )
    else:
        summary["phase_a_survives"] = False
    summary["model"] = MODEL
    summary["sample_size"] = len(sample)
    summary["per_gold_score"] = PER_SCORE
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "# Candidate 014 — RINoBench Phase-A pilot",
        "",
        f"Model: `{MODEL}`; frozen examples: {len(sample)} ({PER_SCORE} per observed gold-score bucket).",
        "",
        "| Arm | N | MAE | Exact | Signed error | Spearman | High-FP |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for arm in ("direct", "compare", "fnc"):
        m = summary[arm]
        lines.append(f'| {arm} | {m["n"]} | {m["mae"]:.3f} | {m["exact_accuracy"]:.3f} | {m["signed_error"]:.3f} | {m["spearman"]:.3f} | {m["high_false_positive_rate"]:.3f} |')
    lines += ["", f'Predeclared Phase-A survival flag: **{summary["phase_a_survives"]}**']
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
