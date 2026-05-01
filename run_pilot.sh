#!/usr/bin/env bash
# Week 1 pilot script.
# Prerequisites: two vLLM servers running (victim on :8000, judge on :8001).
#
# Start victim:
#   vllm serve meta-llama/Meta-Llama-3.1-8B-Instruct --port 8000 --api-key EMPTY
#
# Start judge:
#   vllm serve meta-llama/Meta-Llama-3.1-70B-Instruct --port 8001 --api-key EMPTY \
#        --tensor-parallel-size 4
#
# Then run this script:
#   bash run_pilot.sh

set -e
cd "$(dirname "$0")"

echo "=== Temporal Injection Eval — Pilot Run ==="
echo "Config: configs/pilot_llama3_8b.yaml"
echo "Output: outputs/runs/pilot_llama3_8b.jsonl"
echo ""

python run.py pilot --config configs/pilot_llama3_8b.yaml

echo ""
echo "=== Analyzing pilot results ==="
python run.py analyze --results outputs/runs/pilot_llama3_8b.jsonl --condition C1
