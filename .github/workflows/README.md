# GitHub Actions Workflows

This directory contains automated workflows for running benchmarks securely.

## Available Workflows

### `benchmark.yml` - Qiskit Code Assistant Benchmark

Runs the QuantumBench benchmark against Qiskit Code Assistant with full privacy controls.

**Features:**
- 🔒 Private results (artifacts only visible to repo collaborators)
- 🔐 Secure secrets management
- 🚫 Automatic log masking for sensitive data
- ⚙️ Configurable prompt types (zeroshot, CoT, or both)
- 📊 Optional automatic comparison
- ☁️ Optional cloud storage upload

**Quick Start:**
1. See [WORKFLOW_SETUP.md](WORKFLOW_SETUP.md) for configuration
2. Go to Actions tab → "Qiskit Code Assistant Benchmark" → "Run workflow"
3. Download results from artifacts section

## Security & Privacy

All workflows are designed with privacy in mind:

- **Results stored as private artifacts**: Only repo collaborators can access
- **Secrets management**: API keys never appear in logs
- **Log masking**: Sensitive data automatically redacted
- **Retention control**: Artifacts auto-delete after 90 days
- **Access control**: Workflow runs restricted to collaborators

## Setup Required

Before running workflows:

1. **Configure API Key Secret** (`Settings → Secrets and variables → Actions`):
   - `QISKIT_API_KEY` - Your IBM Cloud API key (the only secret needed)

2. **Get Configuration Parameters** (from IBM Quantum documentation):
   - Base URL - API endpoint (https://qiskit-code-assistant.quantum.ibm.com/docs)
   - Model name - Model identifier (https://quantum.cloud.ibm.com/docs/en/guides/qiskit-code-assistant-openai-api)

   You'll provide these as workflow inputs (they're not secrets)

3. **Ensure Repository is Private** (recommended):
   - Go to `Settings → General`
   - Verify "Repository visibility" is "Private"

4. **Read the Setup Guide**:
   - See [WORKFLOW_SETUP.md](WORKFLOW_SETUP.md) for detailed instructions

## Documentation

- **[WORKFLOW_SETUP.md](WORKFLOW_SETUP.md)** - Complete setup and usage guide
- **[../QISKIT_AGENT_README.md](../QISKIT_AGENT_README.md)** - Agent documentation
- **[../COMPARISON_GUIDE.md](../COMPARISON_GUIDE.md)** - Prompt comparison guide

## Cost Considerations

Running benchmarks consumes API tokens:

| Prompt Type | API Calls | Est. Time | Relative Cost |
|-------------|-----------|-----------|---------------|
| Zero-Shot | 769 | 1-2 hours | 1x |
| Zero-Shot CoT | 1,538 | 2-4 hours | 2x |
| Both | 2,307 | 3-6 hours | 3x |

Start with `zeroshot` and 4 workers to establish a baseline.

## Support

- **Setup Issues**: See [WORKFLOW_SETUP.md](WORKFLOW_SETUP.md) troubleshooting section
- **GitHub Actions Help**: https://docs.github.com/actions
- **Security Concerns**: Contact maintainers directly (not via public issues)

## Examples

### Run Zero-Shot Benchmark
1. Actions → "Qiskit Code Assistant Benchmark" → "Run workflow"
2. Enter your base URL and model name
3. Prompt type: `zeroshot`
4. Workers: `4`
5. Run analysis: ✓

### Run Both and Compare
1. Actions → "Qiskit Code Assistant Benchmark" → "Run workflow"
2. Enter your base URL and model name
3. Prompt type: `both`
4. Workers: `4`
5. Run analysis: ✓
6. Download `comparison-results-XXX` artifact

### Schedule Weekly Runs
1. Edit `benchmark.yml`
2. Uncomment `schedule:` section
3. Commit changes
4. Runs automatically every Sunday

---

🔒 **Remember**: All results are private by default. Only share with authorized individuals.
