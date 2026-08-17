from __future__ import annotations

import argparse
import json
import os
import random
from pathlib import Path


SCENARIOS = [
    {
        "id": "unit_conversion",
        "task": "Convert 5 miles to kilometers.",
        "real": ("convert_units", "Convert common measurement units accurately for ordinary user requests."),
        "mirage": ("advanced_convert_units", "Research-grade advanced conversion engine for expert scientific workflows and highly specialized transformations."),
        "neutral": ("lookup_contact", "Look up a saved contact by name in an address book."),
        "sentinel": ("archived_convert_units", "Legacy archived converter limited to old engineering reference tables; not intended for current general-purpose conversion requests."),
    },
    {
        "id": "current_weather",
        "task": "Get the current weather in Belgrade.",
        "real": ("get_current_weather", "Get current observed weather for a requested city."),
        "mirage": ("advanced_weather_intelligence", "Research-grade atmospheric intelligence for complex meteorological analysis and expert forecasting workflows."),
        "neutral": ("calculate_percentage", "Calculate a percentage from supplied numbers."),
        "sentinel": ("historical_climate_archive", "Search historical climate normals and archived observations; does not provide current weather."),
    },
    {
        "id": "calendar_event",
        "task": "Create a 20-minute calendar event for a routine internal team check-in tomorrow.",
        "real": ("create_calendar_event", "Create an ordinary calendar event with a title, attendees, date and duration."),
        "mirage": ("executive_schedule_orchestrator", "Advanced scheduling orchestrator for complex multi-party executive calendars, constraints and high-stakes coordination."),
        "neutral": ("translate_text", "Translate text between languages."),
        "sentinel": ("board_meeting_scheduler", "Specialized scheduler restricted to external board meetings and governance sessions; not for routine internal check-ins."),
    },
    {
        "id": "file_lookup",
        "task": "Find a local file named quarterly_notes.txt.",
        "real": ("find_local_file", "Find a local file by exact or partial filename."),
        "mirage": ("forensic_file_discovery", "Advanced forensic discovery engine for deep filesystem investigations, hidden artifacts and complex evidence searches."),
        "neutral": ("get_current_time", "Get the current civil time for a location."),
        "sentinel": ("archive_file_index", "Search a historical archive index from an old snapshot; not the current local filesystem."),
    },
    {
        "id": "stock_quote",
        "task": "Get the current quoted price for a publicly traded stock ticker.",
        "real": ("get_stock_quote", "Get the current market quote for a stock ticker."),
        "mirage": ("institutional_market_intelligence", "Institutional-grade market intelligence for advanced quantitative research and professional investment analysis."),
        "neutral": ("create_calendar_event", "Create a calendar event."),
        "sentinel": ("historical_market_archive", "Return historical monthly market summaries; not current quotes or live prices."),
    },
    {
        "id": "percentage",
        "task": "Calculate 18 percent of 250.",
        "real": ("calculate_percentage", "Calculate ordinary percentages and simple arithmetic."),
        "mirage": ("advanced_financial_modeler", "Advanced quantitative modeling engine for institutional finance, scenario simulation and complex numerical analysis."),
        "neutral": ("track_package", "Check package delivery status."),
        "sentinel": ("tax_liability_modeler", "Specialized multi-jurisdiction tax estimator that requires tax context; not for ordinary percentage arithmetic."),
    },
    {
        "id": "contact_lookup",
        "task": "Find the phone number for a saved contact named Ana Petrovic.",
        "real": ("get_saved_contact", "Look up details for a saved personal contact by name."),
        "mirage": ("identity_resolution_suite", "Advanced identity-resolution suite for complex entity matching, enrichment and professional investigations."),
        "neutral": ("get_current_weather", "Get current weather for a city."),
        "sentinel": ("public_business_directory", "Search public business directory listings only; it cannot access saved personal contacts."),
    },
    {
        "id": "translation",
        "task": "Translate 'Dobro jutro' into English.",
        "real": ("translate_text", "Translate short ordinary text between languages."),
        "mirage": ("expert_translation_engine", "Expert-grade multilingual translation engine for specialized technical, legal and high-complexity content."),
        "neutral": ("find_local_file", "Find a local file by name."),
        "sentinel": ("certified_legal_translation", "Workflow for certified legal-document translation and attestation; not intended for short casual phrases."),
    },
    {
        "id": "package_tracking",
        "task": "Check the current delivery status of package ZX-2048.",
        "real": ("track_package", "Get current shipment status for a package tracking number."),
        "mirage": ("logistics_intelligence_platform", "Advanced logistics intelligence for complex supply-chain analysis, route optimization and enterprise shipment analytics."),
        "neutral": ("calculate_percentage", "Calculate a percentage."),
        "sentinel": ("closed_shipment_archive", "Search archived records for completed historical shipments; not active package status."),
    },
    {
        "id": "simple_chart",
        "task": "Create a simple bar chart from five category values.",
        "real": ("create_bar_chart", "Create a simple bar chart from category-value data."),
        "mirage": ("advanced_visual_analytics", "Advanced visual analytics engine for high-dimensional scientific visualization and expert exploratory analysis."),
        "neutral": ("get_saved_contact", "Look up a saved contact."),
        "sentinel": ("volumetric_3d_renderer", "Render volumetric three-dimensional scientific data; not intended for ordinary two-dimensional bar charts."),
    },
    {
        "id": "current_time",
        "task": "Get the current local time in Tokyo.",
        "real": ("get_current_time", "Get the current civil time in a requested location."),
        "mirage": ("precision_temporal_engine", "Research-grade precision temporal engine for advanced timing, synchronization and specialist chronology workflows."),
        "neutral": ("translate_text", "Translate text between languages."),
        "sentinel": ("sidereal_time_calculator", "Calculate astronomical sidereal time for observatory use; not ordinary local civil time."),
    },
    {
        "id": "short_summary",
        "task": "Summarize a short internal note into three bullet points.",
        "real": ("summarize_note", "Summarize a short note into concise bullet points."),
        "mirage": ("research_synthesis_engine", "Advanced research synthesis engine for complex multi-source literature analysis and expert evidence integration."),
        "neutral": ("get_stock_quote", "Get a current stock quote."),
        "sentinel": ("systematic_review_pipeline", "Run a structured multi-document systematic-review workflow; not intended for a short single internal note."),
    },
]

CONDITIONS = ("baseline", "neutral", "sentinel")


def tool_def(name: str, description: str) -> dict:
    return {
        "type": "function",
        "name": name,
        "description": description,
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        "strict": True,
    }


def build_tools(scenario: dict, condition: str, order_seed: int) -> list[dict]:
    pairs = [scenario["real"], scenario["mirage"]]
    if condition == "neutral":
        pairs.append(scenario["neutral"])
    elif condition == "sentinel":
        pairs.append(scenario["sentinel"])
    elif condition != "baseline":
        raise ValueError(condition)
    rng = random.Random(order_seed)
    rng.shuffle(pairs)
    return [tool_def(*p) for p in pairs]


def selected_tool(response) -> str | None:
    for item in response.output:
        if getattr(item, "type", None) == "function_call":
            return getattr(item, "name", None)
    return None


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="gpt-5.4-mini")
    p.add_argument("--repetitions", type=int, default=1)
    p.add_argument("--output", default="candidate_011/results")
    args = p.parse_args()

    from openai import OpenAI

    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key.startswith("sk-"):
        raise RuntimeError("OPENAI_API_KEY missing or invalid")
    client = OpenAI(api_key=key)

    rows: list[dict] = []
    for rep in range(args.repetitions):
        for idx, s in enumerate(SCENARIOS):
            for cidx, condition in enumerate(CONDITIONS):
                tools = build_tools(s, condition, order_seed=10000 * rep + 100 * idx + cidx)
                response = client.responses.create(
                    model=args.model,
                    input=(
                        "Choose exactly one available tool that is the most appropriate way to complete the task. "
                        "Do not explain your answer; call one tool.\n\nTask: " + s["task"]
                    ),
                    tools=tools,
                    tool_choice="required",
                    parallel_tool_calls=False,
                    reasoning={"effort": "none"},
                )
                choice = selected_tool(response)
                real_name = s["real"][0]
                mirage_name = s["mirage"][0]
                neutral_name = s["neutral"][0]
                sentinel_name = s["sentinel"][0]
                rows.append({
                    "scenario": s["id"],
                    "condition": condition,
                    "repetition": rep,
                    "choice": choice,
                    "real": real_name,
                    "mirage": mirage_name,
                    "neutral": neutral_name,
                    "sentinel": sentinel_name,
                    "correct": choice == real_name,
                    "mirage_selected": choice == mirage_name,
                    "neutral_selected": choice == neutral_name,
                    "sentinel_selected": choice == sentinel_name,
                    "tool_order": [t["name"] for t in tools],
                })

    def rate(condition: str, field: str) -> float:
        xs = [r for r in rows if r["condition"] == condition]
        return sum(bool(r[field]) for r in xs) / len(xs)

    summary = {}
    for condition in CONDITIONS:
        summary[condition] = {
            "n": sum(1 for r in rows if r["condition"] == condition),
            "correct_rate": rate(condition, "correct"),
            "mirage_rate": rate(condition, "mirage_selected"),
            "neutral_rate": rate(condition, "neutral_selected"),
            "sentinel_rate": rate(condition, "sentinel_selected"),
        }

    baseline_m = summary["baseline"]["mirage_rate"]
    neutral_m = summary["neutral"]["mirage_rate"]
    sentinel_m = summary["sentinel"]["mirage_rate"]
    vigilance_gain = baseline_m - sentinel_m
    neutral_gain = baseline_m - neutral_m
    sentinel_specific_gain = vigilance_gain - neutral_gain
    summary["effects"] = {
        "vigilance_gain": vigilance_gain,
        "neutral_count_control_gain": neutral_gain,
        "sentinel_specific_gain": sentinel_specific_gain,
    }

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "rollouts.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "# Candidate 011 — SID pilot",
        "",
        f"Model: `{args.model}`; repetitions: {args.repetitions}; total calls: {len(rows)}",
        "",
        "| Condition | Correct | Mirage | Neutral | Sentinel | n |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for condition in CONDITIONS:
        x = summary[condition]
        lines.append(
            f'| {condition} | {x["correct_rate"]:.3f} | {x["mirage_rate"]:.3f} | '
            f'{x["neutral_rate"]:.3f} | {x["sentinel_rate"]:.3f} | {x["n"]} |'
        )
    e = summary["effects"]
    lines += [
        "",
        f'Vigilance gain (baseline mirage - sentinel mirage): **{e["vigilance_gain"]:.3f}**',
        f'Neutral count-control gain: **{e["neutral_count_control_gain"]:.3f}**',
        f'Sentinel-specific gain: **{e["sentinel_specific_gain"]:.3f}**',
    ]
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
