#!/bin/bash
# Example script for analyzing existing benchmark results
#
# Usage:
#   bash examples/analyze_existing_results.sh path/to/results.csv

set -e

if [ $# -eq 0 ]; then
    echo "Error: No results file specified"
    echo "Usage: bash examples/analyze_existing_results.sh path/to/results.csv"
    echo ""
    echo "Example:"
    echo "  bash examples/analyze_existing_results.sh outputs/qiskit_run_20250120_143022/quantumbench_results_qiskit-code-assistant_0.csv"
    exit 1
fi

RESULTS_FILE="$1"

if [ ! -f "$RESULTS_FILE" ]; then
    echo "Error: Results file not found: $RESULTS_FILE"
    exit 1
fi

echo "=========================================="
echo "Analyzing Results"
echo "=========================================="
echo ""
echo "Results file: $RESULTS_FILE"
echo ""

python code/analyze_results.py --results-file "$RESULTS_FILE"

echo ""
echo "Analysis complete!"
echo ""
