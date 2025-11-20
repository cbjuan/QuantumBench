#!/bin/bash
# Run benchmark with both zeroshot and zeroshot-CoT prompt types and compare results
#
# IMPORTANT: Edit the BASE_URL and MODEL_NAME variables below with your actual values
#            from IBM Quantum documentation:
#            - https://qiskit-code-assistant.quantum.ibm.com/docs
#            - https://quantum.cloud.ibm.com/docs/en/guides/qiskit-code-assistant-openai-api
#
# Usage:
#   1. Edit BASE_URL and MODEL_NAME below
#   2. Set your API key: export OPENAI_API_KEY="your_ibm_cloud_api_key"
#   3. Run this script: bash examples/compare_prompt_types.sh

set -e

echo "=========================================="
echo "Qiskit Prompt Type Comparison"
echo "=========================================="
echo ""

# Check if API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY environment variable is not set"
    echo "Please set it with: export OPENAI_API_KEY='your_ibm_cloud_api_key'"
    exit 1
fi

# Configuration - EDIT THESE VALUES
# Get the correct BASE_URL and MODEL_NAME from IBM Quantum documentation
BASE_URL="YOUR_QISKIT_API_BASE_URL"  # e.g., "https://example.com/v1"
MODEL_NAME="YOUR_MODEL_NAME"          # e.g., "granite-qiskit-3.0"
NUM_WORKERS=4  # Reduce to 2 for CoT if you hit rate limits

# Validate configuration
if [ "$BASE_URL" = "YOUR_QISKIT_API_BASE_URL" ] || [ "$MODEL_NAME" = "YOUR_MODEL_NAME" ]; then
    echo "Error: Please edit this script and set BASE_URL and MODEL_NAME"
    echo "Get these values from IBM Quantum documentation:"
    echo "  - https://qiskit-code-assistant.quantum.ibm.com/docs"
    echo "  - https://quantum.cloud.ibm.com/docs/en/guides/qiskit-code-assistant-openai-api"
    exit 1
fi

# Generate timestamp for output directories
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUT_DIR_BASE="./outputs/comparison_${TIMESTAMP}"
OUT_DIR_ZEROSHOT="${OUT_DIR_BASE}/zeroshot"
OUT_DIR_COT="${OUT_DIR_BASE}/zeroshot_cot"

mkdir -p "${OUT_DIR_ZEROSHOT}"
mkdir -p "${OUT_DIR_COT}"

echo "Configuration:"
echo "  Base URL:    ${BASE_URL}"
echo "  Model:       ${MODEL_NAME}"
echo "  Workers:     ${NUM_WORKERS}"
echo "  Output Base: ${OUT_DIR_BASE}"
echo ""
echo "This will run TWO benchmarks:"
echo "  1. Zero-Shot (direct answering)"
echo "  2. Zero-Shot CoT (chain-of-thought)"
echo ""
echo "Note: CoT will take approximately 2x longer and use 2x tokens"
echo ""

# Ask for confirmation
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "=========================================="
echo "Step 1/3: Running Zero-Shot Benchmark"
echo "=========================================="
echo ""

python code/qiskit_benchmark_agent.py \
    --base-url "${BASE_URL}" \
    --model-name "${MODEL_NAME}" \
    --prompt-type zeroshot \
    --out-dir "${OUT_DIR_ZEROSHOT}" \
    --num-workers ${NUM_WORKERS} \
    --analyze

echo ""
echo "=========================================="
echo "Step 2/3: Running Zero-Shot CoT Benchmark"
echo "=========================================="
echo ""

python code/qiskit_benchmark_agent.py \
    --base-url "${BASE_URL}" \
    --model-name "${MODEL_NAME}" \
    --prompt-type zeroshot-CoT \
    --out-dir "${OUT_DIR_COT}" \
    --num-workers ${NUM_WORKERS} \
    --analyze

echo ""
echo "=========================================="
echo "Step 3/3: Comparing Results"
echo "=========================================="
echo ""

# Find the results files
RESULTS_ZEROSHOT=$(find "${OUT_DIR_ZEROSHOT}" -name "quantumbench_results_*.csv" | head -1)
RESULTS_COT=$(find "${OUT_DIR_COT}" -name "quantumbench_results_*.csv" | head -1)

if [ -z "$RESULTS_ZEROSHOT" ] || [ -z "$RESULTS_COT" ]; then
    echo "Error: Could not find results files"
    exit 1
fi

python code/compare_prompts.py \
    --results1 "${RESULTS_ZEROSHOT}" \
    --results2 "${RESULTS_COT}" \
    --label1 "Zero-Shot" \
    --label2 "Zero-Shot CoT" \
    --output-file "${OUT_DIR_BASE}/comparison_report.txt"

echo ""
echo "=========================================="
echo "Comparison Complete!"
echo "=========================================="
echo ""
echo "Results saved to: ${OUT_DIR_BASE}"
echo ""
echo "Files:"
echo "  Zero-Shot results:  ${OUT_DIR_ZEROSHOT}"
echo "  CoT results:        ${OUT_DIR_COT}"
echo "  Comparison report:  ${OUT_DIR_BASE}/comparison_report.txt"
echo ""
echo "To view the comparison report:"
echo "  cat ${OUT_DIR_BASE}/comparison_report.txt"
echo ""
