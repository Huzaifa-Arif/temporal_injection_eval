"""
ASR aggregation and analysis for Paper 1.

Reads the JSONL output from eval.py and produces:
  - summarize_asr():           ASR(k) per condition and model
  - summarize_by_category():   per-category breakdown (for flat-curve diagnosis)
  - summarize_secondary():     expressed_concern and blind_integration rates by k
  - print_pilot_verdict():     go/no-go text summary
"""
from __future__ import annotations

import json
from pathlib import Path


def _load(path: str | Path) -> list[dict]:
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records


def summarize_asr(path: str | Path) -> "pd.DataFrame":
    """
    Returns a DataFrame with columns:
    [model_id, condition, template, conversation_length, injection_turn, n, asr, injection_relative_pos]
    """
    import pandas as pd

    df = pd.DataFrame(_load(path))
    summary = (
        df.groupby(["model_id", "condition", "template", "conversation_length", "injection_turn"])
        .agg(n=("judge_success", "size"), asr=("judge_success", "mean"))
        .reset_index()
    )
    summary["injection_relative_pos"] = (
        summary["injection_turn"] / summary["conversation_length"]
    )
    return summary


def summarize_by_category(path: str | Path) -> "pd.DataFrame":
    import pandas as pd

    df = pd.DataFrame(_load(path))
    return (
        df.groupby(["model_id", "condition", "injection_turn", "category"])
        .agg(n=("judge_success", "size"), asr=("judge_success", "mean"))
        .reset_index()
    )


def summarize_secondary(path: str | Path) -> "pd.DataFrame":
    """
    Rates of expressed_concern and blind_integration by injection_turn.
    Used to operationalize H2 (anchoring vs. detection).
    """
    import pandas as pd

    df = pd.DataFrame(_load(path))
    return (
        df.groupby(["model_id", "condition", "injection_turn"])
        .agg(
            n=("judge_success", "size"),
            asr=("judge_success", "mean"),
            concern_rate=("expressed_concern", "mean"),
            blind_integration_rate=("blind_integration", "mean"),
        )
        .reset_index()
    )


def print_asr_table(path: str | Path, condition: str = "C1") -> None:
    summary = summarize_asr(path)
    try:
        import pandas as pd
        sub = summary[summary["condition"] == condition]
        pivot = sub.pivot_table(
            index=["model_id", "template"],
            columns="injection_turn",
            values="asr",
        )
        print(f"\n=== ASR by injection_turn (Condition {condition}) ===")
        print(pivot.to_string())
    except Exception as e:
        print(f"Could not render table: {e}")


def compute_asr(path: str | Path) -> float:
    records = _load(path)
    if not records:
        return 0.0
    successes = sum(r["judge_success"] for r in records)
    return successes / len(records)
