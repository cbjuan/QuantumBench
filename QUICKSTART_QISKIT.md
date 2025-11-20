# Quick Start Guide: Qiskit Code Assistant Benchmark

This guide will help you get started with running the QuantumBench against Qiskit Code Assistant in just a few steps.

## Prerequisites

- Python 3.12+
- IBM Cloud API key with access to Qiskit Code Assistant
- Required packages installed (see Setup below)

## Setup (One-time)

```bash
# 1. Clone/navigate to the repository
cd QuantumBench

# 2. Extract the dataset (if not already done)
unzip -P 'do_not_use_quantumbench_for_training' quantumbench.zip

# 3. Install dependencies (using uv - recommended)
uv venv
source .venv/bin/activate
uv pip install openai pandas tqdm

# OR using regular pip
pip install openai pandas tqdm
```

## Running the Benchmark

### Option 1: Using the Example Script (Easiest)

**Note:** You need to edit `examples/run_qiskit_agent_example.sh` first to add your actual API base URL and model name from IBM Quantum documentation.

```bash
# Set your API key
export OPENAI_API_KEY="your_ibm_cloud_api_key_here"

# Edit the example script first to add your base URL and model name
# Then run:
bash examples/run_qiskit_agent_example.sh
```

That's it! The script will:
1. Run the full benchmark (769 questions)
2. Save results to `outputs/qiskit_run_TIMESTAMP/`
3. Generate a detailed analysis report

### Option 2: Using Python Directly

```bash
export OPENAI_API_KEY="your_ibm_cloud_api_key_here"

python code/qiskit_benchmark_agent.py \
    --base-url YOUR_QISKIT_API_BASE_URL \
    --model-name YOUR_MODEL_NAME \
    --num-workers 4 \
    --analyze
```

Replace `YOUR_QISKIT_API_BASE_URL` and `YOUR_MODEL_NAME` with values from IBM Quantum documentation:
- https://qiskit-code-assistant.quantum.ibm.com/docs
- https://quantum.cloud.ibm.com/docs/en/guides/qiskit-code-assistant-openai-api

### Option 3: Custom Configuration

```bash
python code/qiskit_benchmark_agent.py \
    --api-key "your_key" \
    --base-url "https://your-endpoint.com/v1" \
    --model-name "your-model" \
    --prompt-type zeroshot-CoT \
    --num-workers 8 \
    --out-dir ./outputs/my_run \
    --analyze
```

## Understanding the Results

After the benchmark completes, you'll find:

### 1. Results CSV
Located at: `outputs/qiskit_run_TIMESTAMP/quantumbench_results_*.csv`

Contains:
- Each question and its correct answer
- Model's answer and whether it was correct
- Token usage statistics
- Subdomain and question type

### 2. Analysis Report
Located at: `outputs/qiskit_run_TIMESTAMP/quantumbench_results_*_analysis.txt`

Shows detailed breakdown by:
- **Overall Statistics**: Total pass rate, average difficulty/expertise
- **Difficulty Level**: Pass rates for problems rated 1-5 in difficulty
- **Expertise Level**: Pass rates for problems requiring expertise levels 1-4
- **Subdomain**: Performance on Quantum Mechanics, Quantum Computation, etc.
- **Question Type**: Performance on Algebraic, Numerical, and Conceptual problems
- **Matrix View**: Combined difficulty × expertise analysis

## Example Output Interpretation

```
OVERALL STATISTICS
Total Questions:           769
Correct Answers:           432
Overall Pass Rate:         56.17%
Average Difficulty Level:  2.68
Average Expertise Level:   2.37
```

This shows the model answered 432 out of 769 questions correctly (56.17% pass rate) on a dataset with average difficulty of 2.68 and average expertise requirement of 2.37.

```
ANALYSIS BY DIFFICULTY LEVEL
                 Total_Questions  Correct_Answers  Pass_Rate  Avg_Difficulty
Difficulty_Level
Level 1                       45               38      84.44            1.33
Level 2                      312              205      65.71            2.12
Level 3                      285              149      52.28            3.08
Level 4                      102               35      34.31            4.15
Level 5                       25                5      20.00            4.88
```

This shows the model performs better on easier questions:
- 84% pass rate on Level 1 (easiest)
- Only 20% on Level 5 (hardest)

## Comparing Prompt Types (Zero-Shot vs CoT)

Want to know if Chain-of-Thought reasoning improves performance? Run both and compare:

```bash
# Edit the script to add your API credentials first
bash examples/compare_prompt_types.sh
```

This automatically:
1. Runs benchmark with zero-shot prompting
2. Runs benchmark with chain-of-thought prompting
3. Generates a comparison report

**Note**: CoT takes ~2x longer and uses ~2x tokens, but may improve accuracy on complex problems.

See [COMPARISON_GUIDE.md](COMPARISON_GUIDE.md) for detailed guidance on interpreting results.

## Re-analyzing Existing Results

If you want to re-run the analysis on existing results:

```bash
python code/analyze_results.py \
    --results-file outputs/qiskit_run_20250120/quantumbench_results_qiskit-code-assistant_0.csv
```

Or use the helper script:

```bash
bash examples/analyze_existing_results.sh outputs/qiskit_run_20250120/quantumbench_results_*.csv
```

## Configuration Options

### API Endpoints

You need to obtain the correct base URL from IBM Quantum documentation:
- https://qiskit-code-assistant.quantum.ibm.com/docs
- https://quantum.cloud.ibm.com/docs/en/guides/qiskit-code-assistant-openai-api

The endpoint should be an OpenAI-compatible API URL provided by IBM Quantum.

### Prompt Types

**`zeroshot` (default)**: Direct question answering
- Faster execution
- Good for straightforward questions

**`zeroshot-CoT`**: Chain-of-thought reasoning
- Slower execution (2x API calls per question)
- Better for complex problems
- More expensive (higher token usage)

### Worker Configuration

```bash
--num-workers 4   # Default, good for most cases
--num-workers 8   # Faster, but watch for rate limits
--num-workers 2   # Slower, more conservative
```

## Troubleshooting

### "API key is required"
Set your API key:
```bash
export OPENAI_API_KEY="your_key"
```

### "Connection failed"
Check your base URL and internet connection:
```bash
curl https://qiskit-code-assistant.quantum.ibm.com/v1/models
```

### "Rate limit exceeded"
Reduce the number of workers:
```bash
--num-workers 2
```

### "Dataset not found"
Extract the dataset:
```bash
unzip -P 'do_not_use_quantumbench_for_training' quantumbench.zip
```

## Next Steps

- Review the full documentation: [QISKIT_AGENT_README.md](QISKIT_AGENT_README.md)
- Experiment with different prompt types
- Compare results across different model versions
- Analyze specific subdomains or question types

## Getting Help

- Check the main README: [README.md](README.md)
- Review the code: `code/qiskit_benchmark_agent.py`
- Open an issue on the repository

## Summary Commands

```bash
# Complete workflow in one go
export OPENAI_API_KEY="your_key"
unzip -P 'do_not_use_quantumbench_for_training' quantumbench.zip
uv pip install openai pandas tqdm
bash examples/run_qiskit_agent_example.sh
```

That's it! You're ready to benchmark Qiskit Code Assistant on quantum science questions.
