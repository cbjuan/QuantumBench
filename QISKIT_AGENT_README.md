# Qiskit Code Assistant Benchmark Agent

This agent runs the QuantumBench benchmark against the Qiskit Code Assistant OpenAI API-compatible endpoints and provides detailed analysis of results based on difficulty and expertise levels.

## Features

- **Automated Benchmarking**: Run QuantumBench against Qiskit Code Assistant API
- **Detailed Analysis**: Analyze results by:
  - Difficulty levels (1-5)
  - Expertise levels (1-4)
  - Subdomain (Quantum Mechanics, Quantum Computation, etc.)
  - Question type (Algebraic, Numerical, Conceptual)
  - Difficulty × Expertise matrix
- **Flexible Configuration**: Support for custom API endpoints and models
- **Parallel Execution**: Multi-threaded benchmark execution for faster results

## Prerequisites

1. **IBM Cloud API Key**: You need an API key with access to Qiskit Code Assistant
2. **Python 3.12+**: Ensure Python is installed
3. **Dependencies**: Install required packages:

```bash
# Using uv for environment and dependency management
uv venv
source .venv/bin/activate
uv pip install openai pandas tqdm
```

## Quick Start

### 1. Set up your API key

```bash
export OPENAI_API_KEY="your_ibm_cloud_api_key_here"
```

### 2. Run the benchmark

```bash
python code/qiskit_benchmark_agent.py \
    --base-url YOUR_QISKIT_API_BASE_URL \
    --model-name YOUR_MODEL_NAME \
    --num-workers 4 \
    --analyze
```

Replace `YOUR_QISKIT_API_BASE_URL` with the actual endpoint from IBM Quantum documentation.
Replace `YOUR_MODEL_NAME` with the model identifier from IBM Quantum.

This will:
1. Run the benchmark against Qiskit Code Assistant
2. Save results to `./outputs/qiskit_run_TIMESTAMP/`
3. Generate a detailed analysis report

## Usage Guide

### Basic Usage

```bash
# Run with automatic analysis
python code/qiskit_benchmark_agent.py \
    --api-key YOUR_IBM_CLOUD_API_KEY \
    --base-url YOUR_QISKIT_API_BASE_URL \
    --model-name YOUR_MODEL_NAME \
    --analyze
```

### Advanced Options

```bash
python code/qiskit_benchmark_agent.py \
    --api-key YOUR_API_KEY \
    --base-url YOUR_QISKIT_API_BASE_URL \
    --model-name YOUR_MODEL_NAME \
    --prompt-type zeroshot-CoT \
    --out-dir ./outputs/my_custom_run \
    --num-workers 8 \
    --analyze
```

### Command-Line Arguments

#### API Configuration
- `--api-key`: IBM Cloud API key (or set `OPENAI_API_KEY` environment variable)
- `--base-url`: Base URL for Qiskit Code Assistant API (obtain from IBM Quantum documentation)
- `--model-name`: Model name to use (obtain from IBM Quantum documentation)

#### Benchmark Configuration
- `--problem-name`: Problem name for output files (default: `quantumbench`)
- `--prompt-type`: Prompt type - `zeroshot` or `zeroshot-CoT` (default: `zeroshot`)
- `--out-dir`: Output directory for results (default: auto-generated with timestamp)
- `--num-workers`: Number of parallel workers (default: 4)

#### Analysis Options
- `--analyze`: Run analysis after benchmark completes
- `--analyze-only RESULTS_FILE`: Skip benchmark and only analyze existing results

## Analysis Only Mode

If you already have results and want to re-run the analysis:

```bash
python code/analyze_results.py \
    --results-file outputs/qiskit_run_20250120_143022/quantumbench_results_qiskit-code-assistant_0.csv
```

### Analysis Output

The analysis generates a comprehensive report including:

#### 1. Overall Statistics
- Total questions and correct answers
- Overall pass rate
- Average difficulty and expertise levels
- Token usage statistics

#### 2. Analysis by Difficulty Level
Shows pass rates for each difficulty level (1-5):
- **Level 1**: Immediate answer problems
- **Level 2**: Simple calculation problems
- **Level 3**: Quick but tedious solutions
- **Level 4**: Requires thought or complex steps
- **Level 5**: Solution not easily identified

#### 3. Analysis by Expertise Level
Shows pass rates for each expertise level (1-4):
- **Level 1**: Elementary, non-specialists can understand
- **Level 2**: Physics background required
- **Level 3**: Technical texts knowledge needed
- **Level 4**: Expert-level research knowledge required

#### 4. Analysis by Subdomain
Pass rates broken down by quantum science domains:
- Quantum Mechanics
- Quantum Computation
- Quantum Chemistry
- Quantum Field Theory
- Photonics
- Optics
- Nuclear Physics
- String Theory
- Mathematics

#### 5. Analysis by Question Type
Performance on different problem types:
- Algebraic Calculation
- Numerical Calculation
- Conceptual Understanding

#### 6. Difficulty × Expertise Matrix
Cross-tabulation showing pass rates for each combination of difficulty and expertise level.

## Example Output

```
==================================================================================================
QUANTUMBENCH RESULTS ANALYSIS - QISKIT CODE ASSISTANT
==================================================================================================

OVERALL STATISTICS
--------------------------------------------------------------------------------------------------
Total Questions:           769
Correct Answers:           432
Overall Pass Rate:         56.17%
Average Difficulty Level:  2.68
Average Expertise Level:   2.37
Total Tokens Used:         1,234,567 (Prompt: 987,654, Completion: 246,913)

ANALYSIS BY DIFFICULTY LEVEL
--------------------------------------------------------------------------------------------------

Difficulty Level Criteria:
  Level 1: A problem whose correct answer can be obtained immediately
  Level 2: A problem with an obvious solution that can be solved with simple calculations
  Level 3: A problem whose solution comes to mind quickly but requires somewhat tedious steps
  Level 4: A problem that requires some thought to discover the solution
  Level 5: A problem whose solution cannot be easily identified

                 Total_Questions  Correct_Answers  Pass_Rate  Avg_Difficulty
Difficulty_Level
Level 1                       45               38      84.44            1.33
Level 2                      312              205      65.71            2.12
Level 3                      285              149      52.28            3.08
Level 4                      102               35      34.31            4.15
Level 5                       25                5      20.00            4.88

ANALYSIS BY EXPERTISE LEVEL
--------------------------------------------------------------------------------------------------

Expertise Level Criteria:
  Level 1: An elementary problem; non-specialists can understand the question
  Level 2: People who studied physics can understand the question
  Level 3: Understanding requires having read technical texts in the field
  Level 4: Only experts who conduct research in that field can understand the question

                Total_Questions  Correct_Answers  Pass_Rate  Avg_Expertise
Expertise_Level
Level 1                      52               42      80.77           1.15
Level 2                     548              345      62.96           2.28
Level 3                     158               44      27.85           3.12
Level 4                      11                1       9.09           3.85
```

## Comparing Prompt Types

Want to know if Chain-of-Thought (CoT) prompting performs better than standard zero-shot? You can compare both approaches:

### Automated Comparison

Run both prompt types and generate a comparison report:

```bash
# Edit the script first to add your API credentials
bash examples/compare_prompt_types.sh
```

This will:
1. Run the benchmark with `zeroshot` prompting
2. Run the benchmark with `zeroshot-CoT` prompting
3. Generate a detailed comparison report showing:
   - Overall pass rate differences
   - Performance by difficulty and expertise levels
   - Token usage comparison (CoT uses ~2x tokens)
   - Which questions each approach answers correctly
   - Cost-benefit recommendations

### Manual Comparison

If you already have results from different runs:

```bash
python code/compare_prompts.py \
    --results1 outputs/zeroshot_run/quantumbench_results_model_0.csv \
    --results2 outputs/cot_run/quantumbench_results_model_0.csv \
    --label1 "Zero-Shot" \
    --label2 "Zero-Shot CoT"
```

### Understanding the Comparison

The comparison report helps you decide which prompt type is worth using:

```
OVERALL STATISTICS
Metric               Zero-Shot  Zero-Shot CoT  Difference
Pass Rate (%)           56.17          60.86       +4.69
Total Tokens           850000        1700000     +850000

RECOMMENDATIONS
  ✓ Zero-Shot CoT shows significant improvement (+4.69%)
  ⚠ Consider whether the performance gain justifies 100% more tokens
```

**See [COMPARISON_GUIDE.md](COMPARISON_GUIDE.md) for detailed guidance on interpreting results and making decisions.**

## API Endpoint Configuration

You need to provide the correct base URL for your Qiskit Code Assistant API endpoint. Please refer to the official IBM Quantum documentation:
- https://qiskit-code-assistant.quantum.ibm.com/docs
- https://quantum.cloud.ibm.com/docs/en/guides/qiskit-code-assistant-openai-api

Example usage:
```bash
--base-url YOUR_QISKIT_API_BASE_URL
```

The base URL should be the OpenAI-compatible endpoint provided by IBM Quantum for the Qiskit Code Assistant service.

## Prompt Types

### Zero-Shot (`zeroshot`)
Direct question answering without intermediate reasoning steps. Faster but may be less accurate on complex problems.

```
What is the correct answer to this question: [question]

Choices:
(A) [choice 1]
(B) [choice 2]
...

Format your response as follows: "The correct answer is (<insert answer id here>)."
```

### Zero-Shot Chain-of-Thought (`zeroshot-CoT`)
Encourages step-by-step reasoning before answering. Slower but potentially more accurate.

```
What is the correct answer to this question: [question]

Choices:
(A) [choice 1]
(B) [choice 2]
...

Let's think step by step:
```

## Performance Tips

1. **Parallel Workers**: Adjust `--num-workers` based on API rate limits
   - Start with 4 workers
   - Increase cautiously to avoid rate limiting

2. **Prompt Type Selection**:
   - Use `zeroshot` for faster results
   - Use `zeroshot-CoT` for potentially better accuracy on difficult problems

3. **Caching**: The benchmark automatically caches responses in `./cache/`
   - Rerunning will reuse valid cached answers
   - Reduces cost and time for partial reruns

## Troubleshooting

### API Authentication Errors
```
Error: API key is required. Set --api-key or OPENAI_API_KEY environment variable
```
**Solution**: Set your API key via environment variable or command-line argument

### Rate Limiting
```
Error 429: Too Many Requests
```
**Solution**: Reduce `--num-workers` to slow down request rate

### Connection Errors
```
Error: Connection failed to https://...
```
**Solution**: Verify the `--base-url` is correct and accessible

## File Structure

```
QuantumBench/
├── code/
│   ├── qiskit_benchmark_agent.py  # Main agent script
│   ├── analyze_results.py         # Analysis script
│   └── 100_run_benchmark.py       # Core benchmark runner
├── quantumbench/
│   ├── quantumbench.csv           # Questions and answers
│   ├── human-evaluation.csv       # Difficulty and expertise ratings
│   └── category.csv               # Domain and type classifications
├── outputs/
│   └── qiskit_run_TIMESTAMP/      # Results directory
│       ├── quantumbench_results_*.csv
│       └── quantumbench_results_*_analysis.txt
└── cache/
    └── job_name/                  # Cached API responses
        └── *_response.pkl
```

## Citation

If you use this benchmark in your research, please cite the original QuantumBench paper:

```bibtex
@misc{minami2025quantumbench,
      title={QuantumBench: A Benchmark for Quantum Question Solving},
      author={Minami, Shunya and Ishigaki, Tatsuya and Hamamura, Ikko and Mikuriya, Taku and Ma, Youmi and Okazaki, Naoaki and Takakura, Hiroya and Suzuki, Yohichi and Kadowaki, Tadashi},
      year={2025},
      eprint={2511.00092},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2511.00092},
}
```

## Related Resources

- [QuantumBench Paper](https://arxiv.org/abs/2511.00092)
- [Qiskit Code Assistant Documentation](https://quantum.cloud.ibm.com/docs/en/guides/qiskit-code-assistant-openai-api)
- [IBM Quantum Cloud](https://quantum.cloud.ibm.com/)

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests for:
- Additional analysis features
- Support for other quantum AI models
- Visualization tools
- Performance improvements

## License

This project follows the same license as the original QuantumBench repository.
