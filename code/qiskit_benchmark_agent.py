#!/usr/bin/env python3
"""
Qiskit Code Assistant Benchmark Agent

This script runs the QuantumBench benchmark against the Qiskit Code Assistant OpenAI API-compatible endpoints
and analyzes the results based on difficulty and expertise levels.

Usage:
    python code/qiskit_benchmark_agent.py \
        --api-key YOUR_IBM_CLOUD_API_KEY \
        --base-url https://qiskit-code-assistant.quantum.ibm.com/v1 \
        --model-name qiskit-code-assistant \
        --out-dir ./outputs/qiskit_run_$(date +"%Y%m%d_%H%M%S") \
        --num-workers 4 \
        --analyze
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description='Qiskit Code Assistant Benchmark Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run benchmark with Qiskit Code Assistant
  python code/qiskit_benchmark_agent.py \\
      --api-key YOUR_IBM_CLOUD_API_KEY \\
      --base-url https://qiskit-code-assistant.quantum.ibm.com/v1 \\
      --model-name qiskit-code-assistant \\
      --num-workers 4

  # Run with custom configuration
  python code/qiskit_benchmark_agent.py \\
      --api-key YOUR_API_KEY \\
      --base-url https://custom-endpoint.com/v1 \\
      --model-name granite-qiskit \\
      --prompt-type zeroshot-CoT \\
      --analyze
        """
    )

    # API Configuration
    api_group = parser.add_argument_group('API Configuration')
    api_group.add_argument(
        '--api-key',
        type=str,
        help='IBM Cloud API key for Qiskit Code Assistant (or set OPENAI_API_KEY env var)',
        default=os.environ.get('OPENAI_API_KEY', '')
    )
    api_group.add_argument(
        '--base-url',
        type=str,
        help='Base URL for Qiskit Code Assistant API',
        default='https://qiskit-code-assistant.quantum.ibm.com/v1'
    )
    api_group.add_argument(
        '--model-name',
        type=str,
        help='Model name to use (e.g., qiskit-code-assistant, granite-qiskit)',
        default='qiskit-code-assistant'
    )

    # Benchmark Configuration
    bench_group = parser.add_argument_group('Benchmark Configuration')
    bench_group.add_argument(
        '--problem-name',
        type=str,
        help='Problem name for output files',
        default='quantumbench'
    )
    bench_group.add_argument(
        '--prompt-type',
        type=str,
        choices=['zeroshot', 'zeroshot-CoT'],
        help='Prompt type to use',
        default='zeroshot'
    )
    bench_group.add_argument(
        '--out-dir',
        type=str,
        help='Output directory for results',
        default=None
    )
    bench_group.add_argument(
        '--num-workers',
        type=int,
        help='Number of parallel workers',
        default=4
    )

    # Analysis Configuration
    analysis_group = parser.add_argument_group('Analysis Configuration')
    analysis_group.add_argument(
        '--analyze',
        action='store_true',
        help='Run analysis after benchmark completes'
    )
    analysis_group.add_argument(
        '--analyze-only',
        type=str,
        help='Skip benchmark and only analyze existing results file',
        default=None
    )

    args = parser.parse_args()

    # Generate output directory if not provided
    if args.out_dir is None and args.analyze_only is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.out_dir = f"./outputs/qiskit_run_{timestamp}"

    return args


def run_benchmark(args):
    """
    Run the QuantumBench benchmark using the existing benchmark script
    """
    print("=" * 80)
    print("Running Qiskit Code Assistant Benchmark")
    print("=" * 80)
    print(f"Model: {args.model_name}")
    print(f"Base URL: {args.base_url}")
    print(f"Prompt Type: {args.prompt_type}")
    print(f"Output Directory: {args.out_dir}")
    print(f"Workers: {args.num_workers}")
    print("=" * 80)
    print()

    # Create output directory
    os.makedirs(args.out_dir, exist_ok=True)

    # Set environment variable for API key
    env = os.environ.copy()
    if args.api_key:
        env['OPENAI_API_KEY'] = args.api_key

    # Build command for the existing benchmark script
    cmd = [
        sys.executable,
        'code/100_run_benchmark.py',
        '--problem-name', args.problem_name,
        '--model-name', args.model_name,
        '--model-type', 'openai',  # Use openai type since Qiskit API is OpenAI-compatible
        '--client-type', 'local',  # Use local client type to specify custom base URL
        '--effort', 'None',
        '--prompt-type', args.prompt_type,
        '--llm-server-url', args.base_url.rstrip('/v1'),  # Remove /v1 suffix if present
        '--out-dir', args.out_dir,
        '--num-workers', str(args.num_workers)
    ]

    print("Executing benchmark command:")
    print(" ".join(cmd))
    print()

    # Run the benchmark
    try:
        result = subprocess.run(cmd, env=env, check=True)
        print("\n✓ Benchmark completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Benchmark failed with error code {e.returncode}")
        return False
    except KeyboardInterrupt:
        print("\n✗ Benchmark interrupted by user")
        return False


def main():
    args = parse_args()

    # Validate API key
    if not args.analyze_only and not args.api_key:
        print("Error: API key is required. Set --api-key or OPENAI_API_KEY environment variable")
        sys.exit(1)

    # Run benchmark if not analyze-only mode
    if not args.analyze_only:
        success = run_benchmark(args)
        if not success:
            print("\nBenchmark failed. Exiting.")
            sys.exit(1)

    # Run analysis if requested
    if args.analyze or args.analyze_only:
        print("\n" + "=" * 80)
        print("Running Analysis")
        print("=" * 80)

        # Find the results file
        if args.analyze_only:
            results_file = args.analyze_only
        else:
            # Find the most recent results file in the output directory
            results_files = list(Path(args.out_dir).glob(f"{args.problem_name}_results_*.csv"))
            if not results_files:
                print(f"Error: No results files found in {args.out_dir}")
                sys.exit(1)
            results_file = str(sorted(results_files, key=lambda x: x.stat().st_mtime)[-1])

        # Run the analysis script
        analysis_cmd = [
            sys.executable,
            'code/analyze_results.py',
            '--results-file', results_file
        ]

        try:
            subprocess.run(analysis_cmd, check=True)
            print("\n✓ Analysis completed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"\n✗ Analysis failed with error code {e.returncode}")
            sys.exit(1)
        except FileNotFoundError:
            print("\n✗ Analysis script not found. Creating it now...")
            # The analysis script will be created separately
            print("Please run the analysis manually using: python code/analyze_results.py --results-file", results_file)


if __name__ == "__main__":
    main()
