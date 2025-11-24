# Troubleshooting Guide

This guide helps you resolve common issues when running the Qiskit Code Assistant benchmark.

## Table of Contents

- [API 404 Errors](#api-404-errors)
- [Analysis Errors](#analysis-errors)
- [Authentication Issues](#authentication-issues)
- [Rate Limiting](#rate-limiting)
- [Data Loading Errors](#data-loading-errors)
- [Getting Help](#getting-help)

---

## API 404 Errors

### Symptom
```
❌ Question X - API endpoint not found (404)
Error: Error code: 404 - {'detail': 'Not Found'}
```

### Cause
The API base URL or endpoint path is incorrect.

### Solution

#### 1. Verify Your Base URL

The default base URL is `https://qiskit-code-assistant.quantum.ibm.com/` but this may not be the correct endpoint for your account.

**Check IBM Quantum Documentation:**
- Visit: https://quantum.cloud.ibm.com/docs
- Look for "Qiskit Code Assistant" API documentation
- Find the correct base URL for your region/account

**Test Your Endpoint:**
```bash
# Test if the endpoint is accessible
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://your-endpoint.quantum.ibm.com/v1/models
```

If you get a 404, the endpoint URL is incorrect.

#### 2. Verify Your Model Name

The default model is `mistral-small-3.2-24b-qiskit` but this may not be available in your account.

**List Available Models:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://your-endpoint.quantum.ibm.com/v1/models
```

This will show you the available model names. Use the exact model ID from this list.

#### 3. Update Your Configuration

Once you have the correct values:

**Option A: Environment Variables**
```bash
export OPENAI_API_KEY="your_api_key"
export QISKIT_API_BASE_URL="https://correct-endpoint.quantum.ibm.com/"
export QISKIT_MODEL_NAME="correct-model-name"

python code/qiskit_benchmark_agent.py --analyze
```

**Option B: Command-Line Arguments**
```bash
python code/qiskit_benchmark_agent.py \
    --api-key YOUR_API_KEY \
    --base-url https://correct-endpoint.quantum.ibm.com/ \
    --model-name correct-model-name \
    --analyze
```

**Option C: GitHub Actions**

Update workflow inputs when triggering the action:
- Base URL: `https://correct-endpoint.quantum.ibm.com/`
- Model Name: `correct-model-name`

#### 4. Contact IBM Support

If you still get 404 errors after verifying the endpoint and model:
- Check your account has access to Qiskit Code Assistant
- Verify your API key has the correct permissions
- Contact IBM Quantum support for assistance

---

## Analysis Errors

### Symptom 1: TypeError with String/Float Concatenation
```
TypeError: can only concatenate str (not "float") to str
```

### Solution
This has been fixed in commit `88b4023`. Update your code:
```bash
git pull origin claude/qiskit-benchmark-agent-01PmNocvTBdRULRzbykrcDxR
```

The fix converts difficulty and expertise columns to numeric before calculating means.

### Symptom 2: KeyError for Missing Columns
```
KeyError: 'Subdomain'
```

### Solution
This has been fixed in commit `8c5a322`. The code now correctly merges category data and uses the right column name.

### Symptom 3: NaN Handling Issues
```
ValueError: cannot convert NaN to integer
```

### Solution
This has been fixed in commit `571783d`. The code now properly filters out NaN values before analysis.

---

## Authentication Issues

### Symptom
```
Error 401: Unauthorized
Error 403: Forbidden
```

### Cause
Invalid API key or insufficient permissions.

### Solution

#### 1. Verify Your API Key

**Check the key is set:**
```bash
echo $OPENAI_API_KEY
# Should output your API key (not empty)
```

**Test authentication:**
```bash
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://your-endpoint.quantum.ibm.com/v1/models
```

#### 2. Generate a New API Key

If your key is invalid:
1. Log in to https://quantum.cloud.ibm.com/
2. Go to API Keys section
3. Generate a new API key
4. Update your environment variable or GitHub secret

#### 3. Check Permissions

Ensure your account has:
- Access to Qiskit Code Assistant service
- Sufficient quota/credits
- Correct permissions for the model you're trying to use

---

## Rate Limiting

### Symptom
```
Error 429: Too Many Requests
Retry 1/3 after error: Rate limit exceeded... Waiting 2.0s
```

### Cause
Sending requests too quickly to the API.

### Solution

#### 1. Reduce Worker Count

Lower the number of parallel workers:
```bash
python code/qiskit_benchmark_agent.py \
    --num-workers 2 \  # Default is 4, try 2 or 1
    --analyze
```

#### 2. The Benchmark Auto-Retries

The benchmark includes exponential backoff retry logic (commit `602d052`):
- Automatically retries on rate limit errors
- Waits increasingly longer between retries (2s, 4s, 8s)
- Up to 3 retries per request

Just let it run - it will handle rate limits automatically.

#### 3. Check Your Quota

If rate limits persist:
- Check your IBM Quantum account quota
- Verify you haven't exceeded monthly limits
- Consider upgrading your account tier

---

## Data Loading Errors

### Symptom
```
FileNotFoundError: [Errno 2] No such file or directory: './quantumbench/quantumbench.csv'
```

### Cause
Dataset not extracted.

### Solution

#### Extract the Dataset
```bash
unzip -P 'do_not_use_quantumbench_for_training' quantumbench.zip
```

This will create:
- `quantumbench/quantumbench.csv` - Questions and answers
- `quantumbench/category.csv` - Subdomain and question type
- `quantumbench/human-evaluation.csv` - Difficulty and expertise ratings

#### Verify Files Exist
```bash
ls -la quantumbench/
# Should show all three CSV files
```

---

## Getting Help

### Before Opening an Issue

1. **Check this troubleshooting guide** - Common issues are documented here
2. **Review recent commits** - Your issue may already be fixed
3. **Check the error summary** - The benchmark now shows error counts and types
4. **Enable debug logging** - Add `--verbose` flag (if available)

### Information to Include

When reporting an issue, include:

1. **Full error message** - Copy the entire error output
2. **Configuration used**:
   ```
   Base URL: [your endpoint]
   Model Name: [your model]
   Prompt Type: [zeroshot or zeroshot-CoT]
   Workers: [number]
   ```
3. **Error frequency**: How many questions failed vs succeeded
4. **Environment**:
   ```bash
   python --version
   pip list | grep openai
   pip list | grep pandas
   ```
5. **Recent commits**: Run `git log -1 --oneline`

### Diagnostic Commands

**Check benchmark configuration:**
```bash
python code/qiskit_benchmark_agent.py --help
```

**Test API connectivity:**
```bash
curl -v -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://your-endpoint.quantum.ibm.com/v1/models
```

**Verify dataset integrity:**
```bash
wc -l quantumbench/*.csv
# quantumbench.csv should have 770 lines (769 questions + header)
# category.csv should have 770 lines
# human-evaluation.csv should have 770 lines
```

**Check Python dependencies:**
```bash
uv pip list
# Verify: openai, pandas, tqdm are installed
```

### Where to Get Help

1. **Documentation**:
   - [Quick Start Guide](QUICKSTART_QISKIT.md)
   - [Full README](QISKIT_AGENT_README.md)
   - [Implementation Review](IMPLEMENTATION_REVIEW.md)

2. **IBM Quantum**:
   - Documentation: https://quantum.cloud.ibm.com/docs
   - Support: Contact IBM Quantum support team
   - Community: IBM Quantum Slack/Discord

3. **GitHub Issues**:
   - Open an issue on this repository
   - Use the bug report template
   - Include diagnostic information listed above

---

## Recent Fixes

These issues have been fixed in recent commits:

| Issue | Commit | Date | Fix |
|-------|--------|------|-----|
| Analysis TypeError | `88b4023` | 2024 | Convert columns to numeric before mean calculation |
| 404 Error Diagnostics | `ffe19fa` | 2024 | Add detailed error messages and troubleshooting |
| Subdomain KeyError | `8c5a322` | 2024 | Use correct column name from category.csv |
| Missing Subdomain Data | `d9b3763` | 2024 | Merge category data properly |
| CSV Column Mismatch | `571783d` | 2024 | Remove unused Source File column |
| NaN Handling | `571783d` | 2024 | Filter NaN values before binning |
| URL Normalization | `571783d` | 2024 | Robust API URL handling |
| Division by Zero | `571783d` | 2024 | Add zero checks in comparisons |

Update your code to get these fixes:
```bash
git pull origin claude/qiskit-benchmark-agent-01PmNocvTBdRULRzbykrcDxR
```

---

## Quick Reference

### Common Commands

```bash
# Run benchmark with defaults
python code/qiskit_benchmark_agent.py --analyze

# Run with custom endpoint
python code/qiskit_benchmark_agent.py \
    --base-url https://custom-endpoint.com/ \
    --model-name custom-model \
    --analyze

# Re-analyze existing results
python code/analyze_results.py \
    --results-file outputs/qiskit_run_DATE/quantumbench_results_*.csv

# Compare prompt types
python code/compare_prompts.py \
    --results1 outputs/zeroshot_run/*.csv \
    --results2 outputs/cot_run/*.csv

# Clear cache and rerun
python code/qiskit_benchmark_agent.py --clear-cache --analyze
```

### Environment Variables

```bash
# Required
export OPENAI_API_KEY="your_api_key"

# Optional (override defaults)
export QISKIT_API_BASE_URL="https://custom-endpoint.com/"
export QISKIT_MODEL_NAME="custom-model-name"
```

### File Locations

```
QuantumBench/
├── quantumbench/           # Dataset files
│   ├── quantumbench.csv
│   ├── category.csv
│   └── human-evaluation.csv
├── outputs/                # Results
│   └── qiskit_run_*/
│       ├── *_results_*.csv
│       └── *_analysis.txt
├── cache/                  # API response cache
│   └── job_name/
│       └── *_response.pkl
└── code/                   # Scripts
    ├── qiskit_benchmark_agent.py
    ├── analyze_results.py
    └── compare_prompts.py
```

---

**Last Updated**: 2024-11-24
**Applies to**: Commits `88b4023` and later
