# Competition notes

Source: the official `HARNESS_README.md` from the competition dataset
(`swegemma`, `adk-submission`, `adk-eval-core` libraries).

## The task

Build (via a declarative YAML config, no custom Python code) an autonomous
agent based on Gemma 4 that fixes real issues in Python repositories: reads
code, edits files, runs tests, and submits a patch.

Metric: **Resolution Rate** — the fraction of tasks whose agent patch
passes the hidden tests (`pytest`, JUnit XML, `exit_code == 0`, no
`FAIL`/`ERROR`).

## Submission format

Not predictions — a **declarative agent**: a zip archive with `agent.yaml`
**at the root** (not `submission/agent.yaml`!). All agent behavior is
defined by the YAML config, which the harness compiles into a tree of ADK
agents — you cannot run your own Python code.

```
submission.zip
├── agent.yaml              # REQUIRED, the single root config
├── eval_config.yaml        # optional: per-task limits (time/tool_calls/turns)
├── configs/sampling.yaml   # temperature, top_p, thinking_budget, etc.
├── prompts/*.md            # system prompts, included via !include
├── sub_agents/*.yaml       # sub-agents (e.g. read-only code_analyzer)
├── adapters/<name>/        # optional: LoRA (adapter_config.json + adapter_model.safetensors)
└── skills/                 # optional: ADK skills (SKILL.md)
```

Allowed models (exactly one per submission):
`gemma-4-31b-it-qat-w4a16-ct`, `gemma-4-12b-it-qat-w4a16-ct`,
`gemma-4-e4b-it-qat-w4a16-ct`, `gemma-4-e2b-it-qat-w4a16-ct`.

Archive size limit: **3 GiB** (including adapters).

## Available agent tools (9 total)

- `run_command`, `read_file`, `edit_file`, `write_file` — code/shell access inside `/workspace`
- `get_status`, `submit_patch` — budget tracking and patch finalization
- `get_code_neighbors`, `search_similar_code`, `get_code_subgraph` — code graph search (not available for every repo)

Full signatures and response formats are in section 6 of `HARNESS_README.md`
(downloaded to `data/HARNESS_README.md` via `scripts/download_data.sh`).

## How evaluation works (summary)

1. **Container A** (agent): snapshot of the repo at `base_commit`, the agent
   works until `submit_patch()` / timeout / budget exhaustion → `agent_patch`
   is extracted.
2. **Container B** (verification): clean snapshot + `agent_patch` +
   `task.test_patch` → `pytest` → task is resolved if the exit code is 0 and
   all required tests pass.

Any changes to test files (`test_*.py`, `conftest.py`, `pytest.ini`, etc.)
in the agent's patch are **stripped out** before verification — only the
library's source code should be fixed.

## Competition data (`data/`, not committed)

- `tasks.jsonl` — 129 tasks (repos: fastapi, rich, requests, httpx):
  `instance_id`, `repo`, `base_commit`, `patch`, `test_patch`,
  `problem_statement`, `hints_text`, `created_at`.
- `snapshots/` (~20 GB) — repository archives at the relevant commits.
- `graphs/`, `embeddings/` (~850 MB combined) — code graphs and embeddings
  for `get_code_neighbors` / `search_similar_code` / `get_code_subgraph`.
- `wheels/` — offline cache of Python packages for the sandbox (no network access).
- `sample_submission/` — the official baseline submission (`submission/` in this repo is based on it).

The full dataset can be downloaded with `make download-data-full` (uses the `kaggle` CLI).

## Local evaluation (if you need to run the harness)

Requires the `swegemma`, `adk-submission`, `adk-eval-core` packages
(installed from the competition dataset, not from this repo) and Docker:

```bash
swegemma eval \
  --tasks data/tasks.jsonl \
  --snapshots-dir data/snapshots \
  --submission-dir submission \
  --results-dir results/run_01 \
  --sandbox docker
```

This minimal template does not set up such a runner — that's a future step.
