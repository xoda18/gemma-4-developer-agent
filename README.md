# Gemma 4 Developer Agent — starter template

Minimal submission template for the [Google — The Gemma 4 Developer Agent Competition](https://www.kaggle.com/competitions/gemma-4-developer-agent) on Kaggle.

## About the competition

The goal is to build an autonomous SWE agent powered by **Gemma 4** that
fixes real issues in Python repositories: it explores the code, makes a
minimal patch, and submits it. The metric is **Resolution Rate**: the
fraction of tasks whose patch passes the hidden tests (SWE-bench style).

A submission is not a set of predictions but a **declarative YAML agent
config** (`agent.yaml` + prompts + optional LoRA adapters), which the
harness compiles into a tree of ADK agents. You cannot execute your own
Python code.

A detailed breakdown of the format is in [docs/NOTES.md](docs/NOTES.md).

## Repository structure

```
submission/              # contents of the future submission.zip
├── agent.yaml           # root agent config (REQUIRED)
├── eval_config.yaml     # optional: time / tool-call budget overrides
├── configs/sampling.yaml
├── prompts/             # system.md, analyzer.md — included via !include
├── sub_agents/          # code_analyzer.yaml — read-only sub-agent
└── adapters/            # LoRA adapters go here (currently empty)
scripts/
├── download_data.sh     # downloads competition data via the Kaggle API
├── pack_submission.py   # packs submission/ -> submission.zip
└── validate_submission.py
docs/NOTES.md            # notes on the competition format and harness
```

## Quick start

1. Set up the Kaggle API (one-time):
   ```bash
   mkdir -p ~/.kaggle
   echo "<YOUR_KAGGLE_API_TOKEN>" > ~/.kaggle/access_token
   chmod 600 ~/.kaggle/access_token
   pip install kaggle
   ```
2. Download the lightweight reference files (`tasks.jsonl`, `HARNESS_README.md`, baseline submission):
   ```bash
   make download-data
   ```
   Full dataset (code graphs, embeddings, repository snapshots, ~21 GB):
   ```bash
   make download-data-full
   ```
3. Validate and pack the submission:
   ```bash
   make pack
   ```
   This produces `submission.zip` with `agent.yaml` at the archive root.
4. Upload `submission.zip` on the competition page (**Submit Predictions**).

## Data

Competition data is not stored in this repository (`data/` is gitignored) —
it is large (up to ~21 GB) and each participant downloads it individually
via the Kaggle API.

## Status

This is an empty starter template based on the competition's official
`sample_submission`: a baseline prompt and tool set, without fine-tuning
(LoRA) and without a local eval runner. Next steps: improve the prompt and,
optionally, LoRA fine-tuning under `submission/adapters/`.
