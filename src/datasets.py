"""
Loaders for HarmBench, JailbreakBench, and AdvBench harmful behavior datasets.
Data files are copied from the FITD repo (data/).
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class HarmfulBehavior:
    behavior_id: str
    category: str
    instruction: str


def load_harmbench(path: str | Path, limit: int | None = None) -> list[HarmfulBehavior]:
    """
    HarmBench CSV columns: Goal, FunctionalCategory, SemanticCategory, Tags, ContextString, BehaviorID
    """
    rows: list[HarmfulBehavior] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            instruction = row.get("Goal", "").strip()
            if not instruction:
                continue
            behavior_id = row.get("BehaviorID") or f"harmbench_{i}"
            category = row.get("SemanticCategory") or row.get("FunctionalCategory") or "unknown"
            rows.append(HarmfulBehavior(behavior_id=behavior_id, category=category, instruction=instruction))
            if limit is not None and len(rows) >= limit:
                break
    return rows


def load_jailbreakbench(path: str | Path, limit: int | None = None) -> list[HarmfulBehavior]:
    """
    JailbreakBench CSV columns: Index, Goal, Target, Behavior, Category, Source
    """
    rows: list[HarmfulBehavior] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            instruction = row.get("Goal", "").strip()
            if not instruction:
                continue
            behavior_id = f"jbb_{row.get('Index', i)}"
            category = row.get("Category") or "unknown"
            rows.append(HarmfulBehavior(behavior_id=behavior_id, category=category, instruction=instruction))
            if limit is not None and len(rows) >= limit:
                break
    return rows


def load_dataset(source: str, data_dir: str | Path, limit: int | None = None) -> list[HarmfulBehavior]:
    data_dir = Path(data_dir)
    if source == "harmbench":
        return load_harmbench(data_dir / "harmbench.csv", limit=limit)
    elif source == "jailbreakbench":
        return load_jailbreakbench(data_dir / "jailbreakbench.csv", limit=limit)
    else:
        raise ValueError(f"Unknown source '{source}'. Choose 'harmbench' or 'jailbreakbench'.")
