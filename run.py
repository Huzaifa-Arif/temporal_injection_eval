"""
CLI entry point for Temporal Prompt Injection evaluation.

Usage:
  python run.py pilot --config configs/pilot_llama3_8b.yaml
  python run.py sweep --config configs/full_sweep_llama3_8b.yaml
  python run.py analyze --results outputs/runs/pilot_llama3_8b.jsonl
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import yaml


def _load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _build_victim(cfg: dict):
    from src.backends import build_backend
    vcfg = cfg["victim"]
    return build_backend(vcfg["backend"], vcfg["model"], vcfg.get("base_url", "http://localhost:8000/v1"))


def _build_judge(cfg: dict):
    from src.backends import build_backend
    from src.judges import LLMJudge
    jcfg = cfg["judge"]
    backend = build_backend(jcfg["backend"], jcfg["model"], jcfg.get("base_url", "http://localhost:8001/v1"))
    return LLMJudge(backend, temperature=jcfg.get("temperature", 0.0), max_tokens=jcfg.get("max_tokens", 8))


def _load_behaviors(cfg: dict):
    from src.datasets import load_dataset
    dcfg = cfg["data"]
    return load_dataset(dcfg["source"], dcfg["data_dir"], limit=dcfg.get("limit"))


def cmd_pilot(args):
    cfg = _load_config(args.config)
    victim = _build_victim(cfg)
    judge = _build_judge(cfg)
    behaviors = _load_behaviors(cfg)
    model_id = cfg["victim"]["model"]
    output = cfg["output"]["path"]
    seeds = cfg["experiment"].get("seeds", [0])
    n = cfg["data"].get("limit", 50)

    from src.eval import run_pilot
    run_pilot(model_id=model_id, victim=victim, judge=judge,
              behaviors=behaviors, output_path=output, n_behaviors=n, seeds=seeds)


def cmd_sweep(args):
    cfg = _load_config(args.config)
    victim = _build_victim(cfg)
    judge = _build_judge(cfg)
    behaviors = _load_behaviors(cfg)
    model_id = cfg["victim"]["model"]
    exp = cfg["experiment"]
    output = cfg["output"]["path"]

    from src.eval import run_position_sweep
    run_position_sweep(
        model_id=model_id,
        victim=victim,
        judge=judge,
        behaviors=behaviors,
        conditions=exp.get("conditions", ["C1", "C2"]),
        templates=exp.get("templates", ["chemistry_lab", "legal_drafting", "medical_consultation"]),
        injection_turns=exp.get("injection_turns", list(range(1, 7))),
        conversation_length=exp.get("conversation_length", 6),
        seeds=exp.get("seeds", [0, 1]),
        output_path=output,
        temperature=cfg["victim"].get("temperature", 0.7),
        max_tokens=cfg["victim"].get("max_tokens", 512),
    )


def cmd_analyze(args):
    from src.analysis import print_asr_table, summarize_secondary
    path = args.results
    condition = args.condition

    print_asr_table(path, condition=condition)

    secondary = summarize_secondary(path)
    print(f"\n=== Secondary metrics (concern / blind integration) ===")
    try:
        print(secondary.to_string(index=False))
    except Exception:
        print(secondary)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Temporal Injection Eval")
    sub = parser.add_subparsers(dest="command")

    p_pilot = sub.add_parser("pilot", help="Run Week 1 pilot (50 instances, k={1,5})")
    p_pilot.add_argument("--config", required=True)

    p_sweep = sub.add_parser("sweep", help="Run full position sweep")
    p_sweep.add_argument("--config", required=True)

    p_analyze = sub.add_parser("analyze", help="Print ASR tables from JSONL results")
    p_analyze.add_argument("--results", required=True)
    p_analyze.add_argument("--condition", default="C1", choices=["C1", "C2", "C3", "C4"])

    args = parser.parse_args()
    if args.command == "pilot":
        cmd_pilot(args)
    elif args.command == "sweep":
        cmd_sweep(args)
    elif args.command == "analyze":
        cmd_analyze(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
