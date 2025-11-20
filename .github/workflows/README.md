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

1. **Configure Secrets** (`Settings → Secrets and variables → Actions`):
   - `QISKIT_API_KEY` - Your IBM Cloud API key
   - `QISKIT_API_BASE_URL` - API endpoint from IBM Quantum docs
   - `QISKIT_MODEL_NAME` - Model name from IBM Quantum docs

2. **Ensure Repository is Private** (recommended):
   - Go to `Settings → General`
   - Verify "Repository visibility" is "Private"

3. **Read the Setup Guide**:
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
2. Prompt type: `zeroshot`
3. Workers: `4`
4. Run analysis: ✓

### Run Both and Compare
1. Actions → "Qiskit Code Assistant Benchmark" → "Run workflow"
2. Prompt type: `both`
3. Workers: `4`
4. Run analysis: ✓
5. Download `comparison-results-XXX` artifact

### Schedule Weekly Runs
1. Edit `benchmark.yml`
2. Uncomment `schedule:` section
3. Commit changes
4. Runs automatically every Sunday

---

🔒 **Remember**: All results are private by default. Only share with authorized individuals.
