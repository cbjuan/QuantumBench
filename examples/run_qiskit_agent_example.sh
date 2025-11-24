#!/bin/bash
# Example script for running the Qiskit Code Assistant Benchmark Agent
#
# This script uses the default Qiskit Code Assistant configuration.
# To use custom values, set these environment variables before running:
#   export QISKIT_API_BASE_URL="https://your-custom-endpoint.com/"
#   export QISKIT_MODEL_NAME="your-model-name"
#
# Usage:
#   1. Set your API key: export OPENAI_API_KEY="your_ibm_cloud_api_key"
#   2. Run this script: bash examples/run_qiskit_agent_example.sh

set -e

echo "=========================================="
echo "Qiskit Code Assistant Benchmark Agent"
echo "=========================================="
echo ""

# Check if API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY environment variable is not set"
    echo "Please set it with: export OPENAI_API_KEY='your_ibm_cloud_api_key'"
    exit 1
fi

# Configuration - EDIT IF NEEDED (defaults are set for Qiskit Code Assistant)
BASE_URL="${QISKIT_API_BASE_URL:-https://qiskit-code-assistant.quantum.ibm.com/}"
MODEL_NAME="${QISKIT_MODEL_NAME:-mistral-small-3.2-24b-qiskit}"
PROMPT_TYPE="zeroshot"
NUM_WORKERS=4

echo "Note: Using default Qiskit Code Assistant configuration"
echo "  To use custom values, set QISKIT_API_BASE_URL and QISKIT_MODEL_NAME environment variables"

# Generate timestamp for output directory
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUT_DIR="./outputs/qiskit_run_${TIMESTAMP}"

echo "Configuration:"
echo "  Base URL:    ${BASE_URL}"
echo "  Model:       ${MODEL_NAME}"
echo "  Prompt Type: ${PROMPT_TYPE}"
echo "  Workers:     ${NUM_WORKERS}"
echo "  Output Dir:  ${OUT_DIR}"
echo ""
echo "Starting benchmark..."
echo ""

# Run the benchmark agent
python code/qiskit_benchmark_agent.py \
    --base-url "${BASE_URL}" \
    --model-name "${MODEL_NAME}" \
    --prompt-type "${PROMPT_TYPE}" \
    --out-dir "${OUT_DIR}" \
    --num-workers ${NUM_WORKERS} \
    --analyze

echo ""
echo "=========================================="
echo "Benchmark Complete!"
echo "=========================================="
echo ""
echo "Results saved to: ${OUT_DIR}"
echo ""
echo "To view the analysis report:"
echo "  cat ${OUT_DIR}/*_analysis.txt"
echo ""
