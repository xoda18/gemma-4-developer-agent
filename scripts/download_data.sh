#!/usr/bin/env bash
# Downloads the lightweight parts of the competition dataset into ./data
# (tasks.jsonl, HARNESS_README.md, sample_submission, docker, sandbox setup).
#
# NOTE: the full dataset also includes snapshots/ (~20 GB), graphs/ and
# embeddings/ (~850 MB combined). Those are NOT downloaded by default since
# they are large and only needed for local evaluation runs. Pass --full to
# fetch everything via `kaggle competitions download`.
set -euo pipefail

COMPETITION="gemma-4-developer-agent"
DATA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/data"

if ! command -v kaggle >/dev/null 2>&1; then
  echo "error: kaggle CLI not found. Install it with: pip install kaggle" >&2
  exit 1
fi

mkdir -p "$DATA_DIR"

if [[ "${1:-}" == "--full" ]]; then
  echo "Downloading full competition dataset (~21 GB) into $DATA_DIR ..."
  kaggle competitions download -c "$COMPETITION" -p "$DATA_DIR"
  (cd "$DATA_DIR" && unzip -o "${COMPETITION}.zip" && rm -f "${COMPETITION}.zip")
  exit 0
fi

echo "Downloading lightweight reference files into $DATA_DIR ..."
FILES=(
  "HARNESS_README.md"
  "tasks.jsonl"
  "sample_submission/agent.yaml"
  "sample_submission/eval_config.yaml"
  "sample_submission/configs/sampling.yaml"
  "sample_submission/prompts/system.md"
  "sample_submission/prompts/analyzer.md"
  "sample_submission/sub_agents/code_analyzer.yaml"
  "docker/Dockerfile.public"
  "docker/Dockerfile.sandbox"
  "docker/imp.py"
  "docker/telnetlib.py"
  "sandbox/setup.py"
)

for f in "${FILES[@]}"; do
  echo "  - $f"
  kaggle competitions download -c "$COMPETITION" -f "$f" -p "$DATA_DIR/$(dirname "$f")" --force -q
done

echo "Done. For graphs/, embeddings/ and snapshots/ (needed for local evaluation), run:"
echo "  scripts/download_data.sh --full"
