#!/bin/bash
# Example script for running the Qiskit Code Assistant Benchmark Agent
#
# IMPORTANT: Edit the BASE_URL and MODEL_NAME variables below with your actual values
#            from IBM Quantum documentation:
#            - https://qiskit-code-assistant.quantum.ibm.com/docs
#            - https://quantum.cloud.ibm.com/docs/en/guides/qiskit-code-assistant-openai-api
#
# Usage:
#   1. Edit BASE_URL and MODEL_NAME below
#   2. Set your API key: export OPENAI_API_KEY="your_ibm_cloud_api_key"
#   3. Run this script: bash examples/run_qiskit_agent_example.sh

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

# Configuration - EDIT THESE VALUES
# Get the correct BASE_URL and MODEL_NAME from IBM Quantum documentation
BASE_URL="YOUR_QISKIT_API_BASE_URL"  # e.g., "https://example.com/v1"
MODEL_NAME="YOUR_MODEL_NAME"          # e.g., "granite-qiskit-3.0"
PROMPT_TYPE="zeroshot"
NUM_WORKERS=4

# Validate configuration
if [ "$BASE_URL" = "YOUR_QISKIT_API_BASE_URL" ] || [ "$MODEL_NAME" = "YOUR_MODEL_NAME" ]; then
    echo "Error: Please edit this script and set BASE_URL and MODEL_NAME"
    echo "Get these values from IBM Quantum documentation:"
    echo "  - https://qiskit-code-assistant.quantum.ibm.com/docs"
    echo "  - https://quantum.cloud.ibm.com/docs/en/guides/qiskit-code-assistant-openai-api"
    exit 1
fi

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
