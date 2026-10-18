#!/usr/bin/env python3
"""Lightweight local validation of submission/ against the rules documented
in data/HARNESS_README.md (section 2-3). This is NOT the official validator,
just a sanity check before packaging. Requires PyYAML (pip install pyyaml)."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("error: PyYAML is required (pip install pyyaml)", file=sys.stderr)
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parent.parent
SUBMISSION_DIR = ROOT / "submission"

ALLOWED_MODELS = {
    "gemma-4-31b-it-qat-w4a16-ct",
    "gemma-4-12b-it-qat-w4a16-ct",
    "gemma-4-e4b-it-qat-w4a16-ct",
    "gemma-4-e2b-it-qat-w4a16-ct",
}
ALLOWED_EXTENSIONS = {".yaml", ".yml", ".md", ".txt", ".py", ".json", ".safetensors"}
MAX_TOTAL_SIZE_BYTES = 3 * 1024 * 1024 * 1024  # 3 GiB


class IncludeLoader(yaml.SafeLoader):
    pass


def _include_constructor(loader: IncludeLoader, node: yaml.Node):
    base_dir = Path(loader.name).parent if hasattr(loader, "name") else SUBMISSION_DIR
    filename = loader.construct_scalar(node)
    filepath = (base_dir / filename).resolve()
    if not str(filepath).startswith(str(SUBMISSION_DIR.resolve())):
        raise ValueError(f"!include path escapes submission root: {filename}")
    if not filepath.exists():
        raise FileNotFoundError(f"!include target does not exist: {filepath}")
    if filepath.suffix in (".yaml", ".yml"):
        with open(filepath, "r", encoding="utf-8") as fh:
            sub_loader = IncludeLoader(fh)
            sub_loader.name = str(filepath)
            return sub_loader.get_single_data()
    with open(filepath, "r", encoding="utf-8") as fh:
        return fh.read()


IncludeLoader.add_constructor("!include", _include_constructor)


def load_yaml(path: Path):
    with open(path, "r", encoding="utf-8") as fh:
        loader = IncludeLoader(fh)
        loader.name = str(path)
        return loader.get_single_data()


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    agent_yaml = SUBMISSION_DIR / "agent.yaml"
    if not agent_yaml.exists():
        errors.append(f"missing required file: {agent_yaml}")
        print_results(errors, warnings)
        return 1

    try:
        config = load_yaml(agent_yaml)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"failed to parse/resolve agent.yaml: {exc}")
        print_results(errors, warnings)
        return 1

    models_found: set[str] = set()

    def collect_models(cfg: dict) -> None:
        if isinstance(cfg, dict):
            model = cfg.get("model")
            if isinstance(model, str):
                models_found.add(model)

    collect_models(config)

    if not models_found:
        errors.append("no 'model' field found in agent.yaml")
    elif len(models_found) > 1:
        errors.append(f"multiple models declared (must be exactly one): {models_found}")
    else:
        model = next(iter(models_found))
        if model not in ALLOWED_MODELS:
            errors.append(f"model '{model}' is not in the allowed set: {sorted(ALLOWED_MODELS)}")

    if not config.get("instruction"):
        errors.append("missing 'instruction' field in agent.yaml")

    if not config.get("tools"):
        warnings.append("no 'tools' declared in agent.yaml")

    total_size = 0
    for path in SUBMISSION_DIR.rglob("*"):
        if path.is_dir() or path.name == ".gitkeep":
            continue
        total_size += path.stat().st_size
        if path.suffix not in ALLOWED_EXTENSIONS:
            warnings.append(f"file extension '{path.suffix}' not in allowed set: {path}")

    if total_size > MAX_TOTAL_SIZE_BYTES:
        errors.append(
            f"submission size {total_size / (1024**3):.2f} GiB exceeds the 3 GiB limit"
        )

    print_results(errors, warnings)
    return 1 if errors else 0


def print_results(errors: list[str], warnings: list[str]) -> None:
    for w in warnings:
        print(f"WARNING: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if not errors and not warnings:
        print("OK: submission/ looks valid.")
    elif not errors:
        print("OK: no blocking errors found.")


if __name__ == "__main__":
    raise SystemExit(main())
