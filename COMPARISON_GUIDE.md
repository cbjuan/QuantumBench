# Prompt Type Comparison Guide

This guide explains how to compare different prompt types (zeroshot vs zeroshot-CoT) to determine which approach works best for your use case.

## Why Compare Prompt Types?

Different prompt types have different trade-offs:

| Approach | Speed | Cost | Potential Accuracy |
|----------|-------|------|-------------------|
| **Zero-Shot** | Fast | Lower (1x tokens) | Good for straightforward questions |
| **Zero-Shot CoT** | Slow (2x API calls) | Higher (2x tokens) | Better for complex reasoning |

**Chain-of-Thought (CoT)** encourages the model to reason step-by-step before answering, which can improve accuracy on complex problems but doubles the API usage.

## Quick Start: Compare Both Approaches

### Option 1: Automated Comparison (Easiest)

Run both approaches and generate a comparison report automatically:

```bash
# 1. Edit the script to add your API credentials
vim examples/compare_prompt_types.sh
# Set BASE_URL and MODEL_NAME

# 2. Set your API key
export OPENAI_API_KEY="your_ibm_cloud_api_key"

# 3. Run the comparison
bash examples/compare_prompt_types.sh
```

This will:
1. Run the full benchmark with zero-shot prompting
2. Run the full benchmark with zero-shot CoT prompting
3. Generate a detailed comparison report

**Time estimate**: 2-4 hours depending on API speed and rate limits

### Option 2: Manual Comparison

If you already have results from different runs:

```bash
python code/compare_prompts.py \
    --results1 outputs/run1/quantumbench_results_model_0.csv \
    --results2 outputs/run2/quantumbench_results_model_0.csv \
    --label1 "Zero-Shot" \
    --label2 "Zero-Shot CoT"
```

## Understanding the Comparison Report

The comparison report includes several sections:

### 1. Overall Statistics

```
OVERALL STATISTICS
----------------------------------------------------------------------------------
              Metric  Zero-Shot  Zero-Shot CoT  Difference
       Total Questions      769            769          +0
      Correct Answers      432            468         +36
        Pass Rate (%)    56.17          60.86       +4.69
       Avg Difficulty     2.68           2.68       +0.00
       Avg Expertise      2.37           2.37       +0.00
        Total Tokens   850000        1700000     +850000
       Prompt Tokens   680000        1360000     +680000
   Completion Tokens   170000         340000     +170000
```

**Key metrics:**
- **Pass Rate difference**: How much better (or worse) CoT performs
- **Total Tokens difference**: Cost increase (CoT typically uses 2x tokens)

### 2. Question-Level Comparison

```
QUESTION-LEVEL COMPARISON
----------------------------------------------------------------------------------
Both Correct:          385 (50.1%)
Both Incorrect:        289 (37.6%)
Only Zero-Shot Correct: 47 (6.1%)
Only Zero-Shot CoT Correct: 83 (10.8%)
```

**Interpretation:**
- **Both Correct**: Questions both approaches get right (baseline difficulty)
- **Both Incorrect**: Very difficult questions neither approach solves
- **Only CoT Correct**: Questions where reasoning helps (CoT advantage)
- **Only Zero-Shot Correct**: Questions where CoT overthinks (Zero-Shot advantage)

### 3. Comparison by Difficulty Level

```
COMPARISON BY DIFFICULTY LEVEL
----------------------------------------------------------------------------------
  Difficulty  Zero-Shot_Pass_Rate  Zero-Shot CoT_Pass_Rate  Questions  Difference
    Level 1                 84.44                    91.11         45       +6.67
    Level 2                 65.71                    68.27        312       +2.56
    Level 3                 52.28                    57.89        285       +5.61
    Level 4                 34.31                    40.20        102       +5.89
    Level 5                 20.00                    28.00         25       +8.00
```

**Interpretation:**
- Positive differences: CoT performs better
- Shows where CoT has the biggest impact (often harder questions)

### 4. Comparison by Expertise Level

Shows performance differences across questions requiring different levels of expertise (elementary to expert-only).

### 5. Recommendations

The report provides actionable recommendations:

```
RECOMMENDATIONS
----------------------------------------------------------------------------------
  ✓ Zero-Shot CoT shows significant improvement (+4.69%)
  ⚠ Consider whether the performance gain justifies 100.0% more tokens
```

## Decision Framework

### Choose **Zero-Shot** if:
- ✓ Cost is a primary concern
- ✓ Performance difference is < 2-3%
- ✓ Questions are straightforward
- ✓ Speed is important
- ✓ API rate limits are restrictive

### Choose **Zero-Shot CoT** if:
- ✓ Performance difference is > 5%
- ✓ Accuracy is more important than cost
- ✓ Working with complex problems (difficulty level 4-5)
- ✓ Budget allows for 2x token usage
- ✓ CoT shows consistent improvements across categories

### Run A/B Tests if:
- Performance difference is 2-5%
- Different subdomains show mixed results
- Cost-benefit ratio is unclear

## Advanced: Comparing Other Configurations

The comparison tool can compare any two benchmark runs:

```bash
# Compare different models
python code/compare_prompts.py \
    --results1 outputs/model_a/results.csv \
    --results2 outputs/model_b/results.csv \
    --label1 "Model A" \
    --label2 "Model B"

# Compare different versions
python code/compare_prompts.py \
    --results1 outputs/v1/results.csv \
    --results2 outputs/v2/results.csv \
    --label1 "Version 1.0" \
    --label2 "Version 2.0"
```

## Tips for Effective Comparison

### 1. Control for Randomness
- Use the same random seed (default: 0)
- Run on the same dataset version
- Use same infrastructure/network conditions if possible

### 2. Watch Rate Limits
- CoT uses 2x API calls
- Reduce `--num-workers` for CoT runs
- Consider spreading runs over time

### 3. Cost Analysis
Track token usage:
```bash
# Extract token counts from results
grep "Total Tokens" outputs/*/comparison_report.txt
```

### 4. Statistical Significance
With 769 questions, differences > 2-3% are generally meaningful, but consider:
- Consistency across difficulty levels
- Performance on your specific subdomains of interest
- Error patterns (systematic vs random)

## Example: Real-World Comparison

Let's say you run a comparison and get:

```
Pass Rate: Zero-Shot 56.2%, CoT 58.7% (+2.5%)
Total Tokens: Zero-Shot 850K, CoT 1.7M (+100%)
```

**Analysis:**
- 2.5% improvement = ~19 more questions correct
- 100% more tokens = 2x cost
- Cost per additional correct answer = 2x baseline cost / 19 = ~0.105x baseline per question

**Decision factors:**
1. Is 2.5% improvement worth 2x cost?
2. Check where improvement comes from (difficulty/subdomain breakdown)
3. If improvement is concentrated in important areas (e.g., Quantum Computation), might be worth it
4. If improvement is uniform but marginal, stick with zero-shot

## Troubleshooting

### "Results files not found"
- Ensure benchmark completed successfully
- Check the output directories specified
- Verify CSV files exist in the directories

### "Different number of questions"
- Both runs must use the same dataset
- Check if either run was interrupted
- Verify both ran to completion

### Very Large Token Differences
- Expected: CoT typically uses 2x tokens
- If much larger: Check if model is generating very long reasoning chains
- Consider if longer reasoning is actually helping (check per-question analysis)

## Next Steps

After comparing:

1. **Document your findings**: Save comparison reports for future reference
2. **Choose your approach**: Select the prompt type for production use
3. **Monitor over time**: Re-compare when model versions update
4. **Optimize further**: Consider custom prompts or hybrid approaches

## Related Documentation

- [QISKIT_AGENT_README.md](QISKIT_AGENT_README.md) - Full agent documentation
- [QUICKSTART_QISKIT.md](QUICKSTART_QISKIT.md) - Getting started guide
- [README.md](README.md) - QuantumBench overview

## Support

For issues or questions about prompt comparison:
1. Check the comparison report carefully
2. Review token usage and costs
3. Consider your specific use case requirements
4. Open an issue if you encounter bugs
