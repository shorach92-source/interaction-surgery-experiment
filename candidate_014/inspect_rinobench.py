from __future__ import annotations

import json
import urllib.request
from pathlib import Path

URL = "https://raw.githubusercontent.com/TimSchopf/RINoBench/main/data/final_benchmark_dataset/test.json"
OUT = Path("candidate_014/schema_inspection")
OUT.mkdir(parents=True, exist_ok=True)

with urllib.request.urlopen(URL, timeout=120) as r:
    raw = r.read()

data = json.loads(raw)

report = {
    "top_type": type(data).__name__,
    "raw_bytes": len(raw),
}

if isinstance(data, list):
    report["count"] = len(data)
    sample = data[0] if data else None
elif isinstance(data, dict):
    report["top_keys"] = list(data.keys())
    # identify the first list-like split/container if present
    sample = None
    for k, v in data.items():
        if isinstance(v, list) and v:
            report["sample_container"] = k
            report["count"] = len(v)
            sample = v[0]
            break
else:
    sample = None

if isinstance(sample, dict):
    report["sample_keys"] = list(sample.keys())
    fields = {}
    for k, v in sample.items():
        entry = {"type": type(v).__name__}
        if isinstance(v, str):
            entry["chars"] = len(v)
            entry["preview"] = v[:240]
        elif isinstance(v, list):
            entry["length"] = len(v)
            if v:
                entry["item_type"] = type(v[0]).__name__
                entry["item_preview"] = str(v[0])[:240]
        elif isinstance(v, dict):
            entry["keys"] = list(v.keys())[:30]
        else:
            entry["preview"] = repr(v)[:240]
        fields[k] = entry
    report["sample_fields"] = fields

(OUT / "schema_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
