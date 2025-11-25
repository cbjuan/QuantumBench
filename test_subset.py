#!/usr/bin/env python3
"""
Test script to run a small subset of the QuantumBench benchmark.
This runs only the first 5 questions to verify the setup works.
"""
import sys
import os
from datetime import datetime

# Add code directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'code'))

# Import the main benchmark module
from importlib import import_module
import importlib.util

spec = importlib.util.spec_from_file_location("run_benchmark", "code/100_run_benchmark.py")
benchmark = importlib.util.module_from_spec(spec)
sys.modules["run_benchmark"] = benchmark
spec.loader.exec_module(benchmark)

# Override load_examples to only load first 5 questions
original_load_examples = benchmark.load_examples

def load_subset_examples(seed: int, limit: int = 5):
    """Load only the first N examples"""
    all_examples = original_load_examples(seed)
    return all_examples[:limit]

# Apply the override
benchmark.load_examples = lambda seed: load_subset_examples(seed, limit=5)

if __name__ == "__main__":
    # Check if QISKIT_API_KEY is set
    if not os.environ.get("QISKIT_API_KEY"):
        print("❌ Error: QISKIT_API_KEY environment variable is not set.")
        print("   Please set it with: export QISKIT_API_KEY='your-api-key'")
        print("   Get your API key from: https://quantum.cloud.ibm.com/")
        sys.exit(1)
    
    # Get Qiskit base URL from environment or use default
    qiskit_base_url = os.environ.get(
        "QISKIT_BASE_URL", 
        "https://qiskit-code-assistant.quantum.ibm.com"
    )
    
    # Get model name from environment or use default
    qiskit_model = os.environ.get(
        "QISKIT_MODEL_NAME",
        "mistral-small-3.2-24b-qiskit"
    )
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = f"./outputs/test_subset_{timestamp}"
    os.makedirs(out_dir, exist_ok=True)
    
    print("=" * 80)
    print("RUNNING SUBSET TEST (5 questions only)")
    print("=" * 80)
    print(f"Output directory: {out_dir}")
    print(f"API Base URL: {qiskit_base_url}")
    print(f"Model: {qiskit_model}")
    print("=" * 80)
    print()
    
    # Create a simple args-like object
    args = type("Args", (), {
        "problem_name": "quantumbench",
        "model_name": qiskit_model,
        "model_type": "qiskit",
        "client_type": "local",
        "url": qiskit_base_url,
        "effort": "None",
        "prompt_type": "zeroshot",
        "out_dir": out_dir,
        "job_name": os.path.basename(out_dir.rstrip("/")),
        "num_workers": 1
    })()
    
    # Run the benchmark
    benchmark.main(
        problem_name=args.problem_name,
        model_name=args.model_name,
        out_dir=args.out_dir,
        prompt_type=args.prompt_type,
        model_type=args.model_type,
        client_type=args.client_type,
        url=args.url,
        effort=args.effort,
        job_name=args.job_name,
        seed=benchmark.SEED,
        num_workers=args.num_workers
    )
    
    print()
    print("=" * 80)
    print("TEST COMPLETED!")
    print("=" * 80)
    print(f"Results saved to: {out_dir}")
    print("=" * 80)
