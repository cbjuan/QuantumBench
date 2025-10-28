# QuantumBench
<div align="center">
  <img src="images/papertitle.png" width="80%" alt="QuantumBench" />
</div>
<hr>

<p align="center">
  <a href="https://arxiv.org/abs/2501.16986"><b>arxiv Paper Link</b></a> |
</p>

<div align="center">
  <img src="images/fig_acc.svg" width="95%" alt="QuantumBench" />
</div>


## Overview
QuantumBench is an LLM benchmark built from 769 multiple-choice questions curated from open quantum science and engineering course materials. The dataset aggregates content from MIT OCW, TUD OCW, and LibreTexts. Each question includes seven distractors, the correct answer, source metadata, and human annotations for difficulty and required expertise. The repository ships both the dataset (as a password-protected archive) and a reference evaluation script that targets OpenAI-compatible APIs.

> ⚠️ **Important**: `quantumbench.zip` is password-protected. Unlock it with `Pass: do_not_use_quantumbench_for_training`—the password is also a reminder to keep the dataset for evaluation rather than model training.

## Dataset Layout
- `quantumbench.zip`: Password-protected archive that expands into the `quantumbench/` directory when unlocked.
- `quantumbench/quantumbench.csv`: English questions with seven incorrect answers, the correct answer, and provenance (769 rows).
- `quantumbench/quantumbench_jpn.csv`: Japanese translation of the same questions. Mathematical expressions remain in LaTeX.
- `quantumbench/category.csv`: Subdomain and question-type labels (`Algebraic Calculation`, `Numerical Calculation`, `Conceptual Understanding`) for each question.
- `quantumbench/human-evalation.csv`: Human ratings covering difficulty and required expertise.
- `code/100_run_benchmark.py`: Benchmark driver that calls OpenAI Responses API–compatible backends.
- `cache/`: Created on demand to store serialized prompts/responses when the benchmark runs.

## Question Counts by Domain and Type
Table 2 in `QuantumBench.pdf` summarizes the number of problems in each domain/type combination. The same information is reproduced here for convenience.

| Domain               | Algebraic Calculation | Numerical Calculation | Conceptual Understanding | Total |
|----------------------|----------------------:|----------------------:|-------------------------:|------:|
| Quantum Mechanics    | 177                   | 21                    | 14                       | 212   |
| Quantum Computation  | 54                    | 1                     | 5                        | 60    |
| Quantum Chemistry    | 16                    | 64                    | 6                        | 86    |
| Quantum Field Theory | 104                   | 1                     | 2                        | 107   |
| Photonics            | 54                    | 1                     | 2                        | 57    |
| Mathematics          | 37                    | 0                     | 0                        | 37    |
| Optics               | 101                   | 41                    | 15                       | 157   |
| Nuclear Physics      | 1                     | 15                    | 2                        | 18    |
| String Theory        | 31                    | 0                     | 2                        | 33    |
| **Total**            | **575**               | **144**               | **50**                   | **769** |


## Difficulty and Expertise Level
<div align="center">
  <img src="images/fig_level.svg" width="80%" alt="QuantumBench" />
</div>

- Average Difficulty Level: 2.68
- Average Expertise Level: 2.37

| Difficulty Level | Criteria |
|-------|----------|
| Level 1 | A problem whose correct answer can be obtained immediately |
| Level 2 | A problem with an obvious solution<br>that can be solved with simple calculations |
| Level 3 | A problem whose solution comes to mind quickly<br>but requires somewhat tedious steps |
| Level 4 | A problem that requires some thought to discover the solution,<br>or whose solution is obvious but involves considerably tedious steps |
| Level 5 | A problem whose solution cannot be easily identified |

| Expertise Level | Criteria |
|-------|----------|
| Level 1 | An elementary problem; non-specialists can understand the question |
| Level 2 | People who studied physics can understand the question |
| Level 3 | Understanding requires having read technical texts in the field |
| Level 4 | Only experts who conduct research in that field can understand the question |

## Setup
QuantumBench targets Python 3.12+. Extract the dataset, then use [uv](https://github.com/astral-sh/uv) to manage the virtual environment and dependencies.

```bash
# extract the dataset (creates quantumbench/ with CSV files)
unzip -P 'Pass: do_not_use_quantumbench_for_training' quantumbench.zip

# create and activate a uv-managed environment
uv venv
source .venv/bin/activate

# install project dependencies (uses pyproject.toml)
uv pip install -e .
```

Set `OPENAI_API_KEY` in your environment before invoking the OpenAI client. If you plan to route requests through OpenRouter, also export `OPENROUTER_API_KEY`.

## Running the Benchmark
Invoke `code/100_run_benchmark.py` from the command line. The script writes results to the directory specified by `--out-dir`.

```bash
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUT_DIR=$(pwd)/outputs/run_${TIMESTAMP}
mkdir -p "${OUT_DIR}"

python code/100_run_benchmark.py \
  --problem-name "quantumbench" \
  --model-name "gpt-4.1" \
  --model-type "openai" \
  --client-type "openai" \
  --effort "high" \
  --prompt-type "zeroshot" \
  --llm-server-url "None" \
  --out-dir "${OUT_DIR}" \
  --num-workers 4
```

### Key Arguments
- `--model-name`: Target model identifier. When using OpenAI Reasoning models, pair with `--effort minimal|low|medium|high`.
- `--model-type`: Controls API invocation path. Supported values include `openai`, `openaireasoning`, `deepseek`, `llama`, `qwen`.
- `--client-type`: Selects the API backend (`openai`, `openrouter`, `local`). For `local`, pass a base URL via `--llm-server-url`.
- `--prompt-type`: Currently `zeroshot` and `zeroshot-CoT` are available. The CoT mode issues a follow-up prompt that enforces answer formatting.
- `--num-workers`: ThreadPool parallelism. Increase cautiously to remain within provider rate limits.

The job name defaults to the final segment of `--out-dir`, and is reused for cache directories (`cache/<job_name>/`) and output filenames.

## Outputs and Caching
Each run produces `<out_dir>/<problem-name>_results_<model>_<seed>.csv` with columns such as:
- `Question id`, `Question`, `Correct answer`, `Correct index`: Ground-truth metadata.
- `Model answer index`, `Model answer`: Choice letter (A–H) and the resolved text. Missing parses fall back to `No response`.
- `Correct`: Boolean indicator of model accuracy.
- `Model response`: Last 100 characters of the raw response (kept short to control file size).
- `Subdomain`: Available subdomain label.
- `Prompt tokens`, `Cached tokens`, `Completion tokens`: Token usage as reported by the API.

The full prompt/response objects are serialized to `cache/<job_name>/<question_id>_response.pkl`. When rerunning the benchmark, existing CSV rows with valid answers are reused to minimize additional API calls.

## Limitations and Notes
- The evaluation script assumes the OpenAI Responses API schema. Extend `call_model` if you need to adapt to alternate providers.
- The dataset pulls from public educational resources. Confirm downstream licensing requirements before redistributing derived material.
- `category.csv` and `human-evalation.csv` can be joined with `quantumbench.csv` on `Question id` for enriched analysis.

## Contributing
Issues and pull requests are welcome. Contributions that improve evaluation workflows, prompt variants, or dataset documentation are especially helpful.

## Contributors
- Shunya Minami (AIST)

## Contributors
- Shunya Minami (AIST)

## Related projects
Coming soon.

## Acknowledgements
This work was performed for Council for Science, Technology and Innovation (CSTI), Cross-ministerial Strategic Innovation Promotion Program (SIP), “Promoting the application of advanced quantum technology platforms to social issues” (Funding agency : QST).

## Citaion
```
@misc{minami2025generative,
      title={QuantumBench: A Benchmark for Quantum Question Solving},
      author={Minami, Shunya and Ishigaki, Tatsuya and Hamamura, Ikko and Mikuriya, Taku and Ma, Youmi and Okazaki, Naoaki and Takakura, Hiroya and Suzuki, Yohichi and Kadowaki, Tadashi},
      year={2025},
      eprint={XXXX.XXXX},
      archivePrefix={arXiv},
      primaryClass={quant-ph},
      url={https://arxiv.org/abs/XXXX.XXXX},
}
```

## Contact
If you have any questions, please contact us.
