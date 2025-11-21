# GitHub Actions Workflow Setup Guide

This guide explains how to configure and use the GitHub Actions workflow to run benchmarks privately and securely.

## Security Features

The workflow includes multiple layers of privacy:

1. **🔒 Private Artifacts**: Results are stored as GitHub artifacts, only visible to repo collaborators
2. **🔐 Secrets Management**: API keys and URLs never appear in logs
3. **🚫 Log Masking**: Sensitive data is automatically masked in workflow logs
4. **⏰ Retention Control**: Artifacts auto-delete after 90 days (configurable)
5. **👥 Access Control**: Only repo collaborators can view workflow runs and download artifacts

## Initial Setup

### Step 1: Configure Repository Secret

Navigate to your repository settings: `Settings → Secrets and variables → Actions`

Add the following secret:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `QISKIT_API_KEY` | Your IBM Cloud API key | `ibm_cloud_xxxxxxxx` |

**Important:**
- Never commit your API key to the repository
- Rotate API keys regularly for security

**Note:** The base URL and model name are **not** secrets - you'll provide them as workflow inputs when running the benchmark.

### Step 2: Ensure Repository is Private (Recommended)

For maximum security:
1. Go to `Settings → General`
2. Under "Danger Zone", ensure repository visibility is **Private**
3. This ensures:
   - Workflow runs are only visible to collaborators
   - Artifacts are only accessible to collaborators
   - Action logs are not publicly visible

### Step 3: Configure Artifact Retention (Optional)

Default: 90 days

To change:
1. Edit `.github/workflows/benchmark.yml`
2. Modify `retention-days:` values
3. Options: 1-90 days (or 1-400 days for GitHub Enterprise)

## Running the Benchmark

### Manual Trigger

1. Go to `Actions` tab in your repository
2. Select **"Qiskit Code Assistant Benchmark"** workflow
3. Click **"Run workflow"**
4. Configure options:

   | Option | Description | Required | Example |
   |--------|-------------|----------|---------|
   | **Qiskit API base URL** | API endpoint URL | Yes | Get from IBM Quantum docs |
   | **Model name** | Model identifier | Yes | Get from IBM Quantum docs |
   | **Prompt type** | `zeroshot`, `zeroshot-CoT`, or `both` | Yes | `zeroshot` |
   | **Number of workers** | Parallel workers (1-10) | No | `4` |
   | **Run analysis** | Generate analysis report | No | `true` |

   **Get base URL and model name from:**
   - https://qiskit-code-assistant.quantum.ibm.com/docs
   - https://quantum.cloud.ibm.com/docs/en/guides/qiskit-code-assistant-openai-api

5. Click **"Run workflow"**

### Workflow Options Explained

#### Prompt Type

- **`zeroshot`**: Fast, direct answering
  - Time: ~1-2 hours
  - Cost: 1x tokens
  - Best for: Quick baseline

- **`zeroshot-CoT`**: Chain-of-thought reasoning
  - Time: ~2-4 hours
  - Cost: 2x tokens (double API calls)
  - Best for: Maximum accuracy

- **`both`**: Run both and compare
  - Time: ~3-6 hours
  - Cost: 3x tokens
  - Best for: A/B testing
  - Generates comparison report automatically

#### Number of Workers

- **Lower (1-2)**: Safer for rate limits, slower
- **Medium (4)**: Balanced (recommended)
- **Higher (8+)**: Faster, but may hit rate limits

Start with 4, increase cautiously if no rate limit errors.

## Accessing Results

### Download from GitHub UI

1. Go to `Actions` tab
2. Click on the workflow run
3. Scroll to **"Artifacts"** section
4. Download:
   - `zeroshot-results-XXX` (if ran zeroshot)
   - `cot-results-XXX` (if ran CoT)
   - `comparison-results-XXX` (if ran both)
   - `run-summary-XXX` (always created)

**Note**: Only repo collaborators can see and download artifacts.

### Download via GitHub CLI

```bash
# List artifacts for a run
gh run view RUN_ID --repo OWNER/REPO

# Download specific artifact
gh run download RUN_ID --name zeroshot-results-123 --repo OWNER/REPO

# Download all artifacts from a run
gh run download RUN_ID --repo OWNER/REPO
```

### Download via API (Authenticated)

```bash
# Get artifacts list
curl -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/repos/OWNER/REPO/actions/artifacts

# Download artifact
curl -L -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -o results.zip \
  https://api.github.com/repos/OWNER/REPO/actions/artifacts/ARTIFACT_ID/zip
```

## Advanced: Upload to Private Cloud Storage

The workflow includes commented examples for uploading to private cloud storage.

### AWS S3 (Private Bucket)

1. Create a private S3 bucket
2. Add GitHub secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`
   - `S3_BUCKET_NAME`

3. Uncomment the "Upload to AWS S3" step in `benchmark.yml`

4. Ensure bucket policy restricts access:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::YOUR-BUCKET/*",
    "Condition": {
      "StringNotEquals": {
        "aws:PrincipalAccount": "YOUR-AWS-ACCOUNT-ID"
      }
    }
  }]
}
```

### Azure Blob Storage (Private Container)

1. Create a storage account with private container
2. Add GitHub secret:
   - `AZURE_STORAGE_CONNECTION_STRING`
   - `AZURE_CONTAINER_NAME`

3. Uncomment the "Upload to Azure" step in `benchmark.yml`

4. Ensure container access level is **Private**

### Google Cloud Storage (Private Bucket)

1. Create a private GCS bucket
2. Set up service account with minimal permissions
3. Add secret: `GCP_SERVICE_ACCOUNT_KEY`
4. Add custom step to workflow:

```yaml
- name: Upload to GCS
  env:
    GCP_SERVICE_ACCOUNT_KEY: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}
  run: |
    echo "$GCP_SERVICE_ACCOUNT_KEY" > key.json
    gcloud auth activate-service-account --key-file=key.json
    gsutil -m rsync -r ./outputs/ gs://${{ secrets.GCS_BUCKET_NAME }}/runs/${{ github.run_number }}/
    rm key.json
```

## Scheduled Runs (Optional)

To run benchmarks automatically on a schedule:

1. Edit `.github/workflows/benchmark.yml`
2. Uncomment the `schedule` section:

```yaml
on:
  workflow_dispatch:
    # ... existing config ...

  # Run every Sunday at midnight UTC
  schedule:
    - cron: '0 0 * * 0'
```

**Cron schedule examples:**
- `0 0 * * 0` - Every Sunday at midnight
- `0 0 * * 1` - Every Monday at midnight
- `0 0 1 * *` - First day of every month
- `0 */6 * * *` - Every 6 hours

**Note**: Scheduled runs use default parameters (zeroshot, 4 workers, with analysis).

## Security Best Practices

### 1. Protect Secrets

✅ **Do:**
- Use GitHub Secrets for all sensitive data
- Rotate API keys regularly
- Limit secret access to necessary workflows
- Use environment-specific secrets

❌ **Don't:**
- Hardcode credentials in workflow files
- Echo secret values in logs
- Commit secrets to repository
- Share secrets in public channels

### 2. Control Access

✅ **Do:**
- Keep repository private
- Limit collaborator access
- Use branch protection rules
- Enable required reviews for workflow changes

❌ **Don't:**
- Make repository public with sensitive workflows
- Share artifact download links publicly
- Allow untrusted contributors

### 3. Monitor Usage

✅ **Do:**
- Review workflow run logs regularly
- Monitor API usage and costs
- Set up billing alerts
- Track artifact storage usage

❌ **Don't:**
- Ignore failed runs
- Leave artifacts forever (use retention limits)
- Run excessive parallel jobs

### 4. Audit Artifacts

✅ **Do:**
- Regularly clean up old artifacts
- Download and archive important results locally
- Review artifact contents before sharing
- Delete artifacts with sensitive data when no longer needed

## Troubleshooting

### "Secret not found" error

**Cause**: API key secret not configured

**Solution**:
1. Go to `Settings → Secrets and variables → Actions`
2. Verify `QISKIT_API_KEY` secret exists
3. Secret name must be exactly `QISKIT_API_KEY` (case-sensitive)
4. Re-create secret if needed

**Note:** Base URL and model name are workflow inputs, not secrets

### Rate limit errors

**Cause**: Too many parallel workers

**Solution**:
1. Reduce `num_workers` to 2-4
2. Add delays between retries
3. Contact IBM about rate limits

### Artifacts not appearing

**Cause**: Workflow failed or path incorrect

**Solution**:
1. Check workflow logs for errors
2. Verify output directories exist
3. Check if files were created (`ls outputs/`)

### Workflow times out

**Cause**: Benchmark takes longer than 6 hours (GitHub limit)

**Solution**:
1. Split into multiple workflows
2. Request GitHub Actions extended timeout
3. Use self-hosted runners (no timeout)

### Can't download artifacts

**Cause**: Not a collaborator or artifact expired

**Solution**:
1. Verify you're a repo collaborator
2. Check artifact retention period
3. Use GitHub CLI with proper auth

## Viewing Results

After downloading artifacts:

```bash
# Unzip artifact
unzip zeroshot-results-123.zip

# View analysis report
cat outputs/*/quantumbench_results_*_analysis.txt

# View comparison (if ran both)
cat outputs/*/comparison_report.txt

# Check CSV results
head outputs/*/quantumbench_results_*.csv
```

## Cost Management

### Estimate Costs

| Prompt Type | API Calls | Tokens (est.) | Time (est.) |
|-------------|-----------|---------------|-------------|
| Zero-Shot | 769 | ~800K-1M | 1-2 hours |
| CoT | 1,538 | ~1.6M-2M | 2-4 hours |
| Both | 2,307 | ~2.4M-3M | 3-6 hours |

Actual costs depend on:
- Token pricing from IBM Quantum
- Question complexity
- Model selected
- Response lengths

### Monitor Costs

1. Check token usage in results:
```bash
grep "Total Tokens" outputs/*/quantumbench_results_*_analysis.txt
```

2. Set GitHub Actions spending limits:
   - Go to `Settings → Billing → Spending limits`
   - Set monthly limit for Actions

3. Use notification webhooks to alert on completion:
```yaml
- name: Notify on completion
  uses: actions/github-script@v7
  with:
    script: |
      // Send notification to your monitoring system
```

## Compliance & Data Handling

### Data Retention

- **GitHub Artifacts**: Auto-delete after 90 days (configurable)
- **Workflow Logs**: Retained per GitHub's data retention policy
- **Cloud Storage**: Configure lifecycle rules for auto-deletion

### GDPR Considerations

If subject to GDPR:
1. Document what data is collected
2. Ensure secure storage
3. Implement data deletion procedures
4. Maintain access logs

### Export Control

QuantumBench contains scientific/educational content. Ensure compliance with:
- Export control regulations
- Institutional policies
- Licensing requirements

## Support

### GitHub Actions Issues

- [GitHub Actions Documentation](https://docs.github.com/actions)
- [GitHub Support](https://support.github.com/)

### Workflow-Specific Issues

- Check workflow logs in Actions tab
- Review this documentation
- Open issue in repository

### Security Concerns

If you discover a security issue:
1. **Do not** create a public issue
2. Contact repository maintainers directly
3. Follow responsible disclosure practices

## Summary Checklist

Before running your first benchmark:

- [ ] Repository is private (recommended)
- [ ] `QISKIT_API_KEY` secret is configured
- [ ] You have base URL from IBM Quantum docs
- [ ] You have model name from IBM Quantum docs
- [ ] Artifact retention period is appropriate
- [ ] You understand cost implications
- [ ] You have access to download artifacts
- [ ] You've tested with a small run first

Then:
- [ ] Go to Actions tab
- [ ] Select workflow
- [ ] Click "Run workflow"
- [ ] Enter base URL and model name
- [ ] Configure other options
- [ ] Monitor progress
- [ ] Download results when complete

Your benchmark results will remain private and secure! 🔒
