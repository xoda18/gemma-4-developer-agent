# Конспект по соревнованию

Источник: официальный `HARNESS_README.md` из датасета соревнования (библиотеки `swegemma`, `adk-submission`, `adk-eval-core`).

## Суть задачи

Нужно собрать (через декларативный YAML-конфиг, без своего Python-кода) автономного
агента на базе Gemma 4, который чинит реальные issue в Python-репозиториях:
читает код, редактирует файлы, запускает тесты и отправляет патч.

Метрика — **Resolution Rate**: доля задач, для которых патч агента проходит
скрытые тесты (`pytest`, JUnit XML, `exit_code == 0`, без `FAIL`/`ERROR`).

## Формат сабмишена

Не предсказания, а **декларативный агент**: zip-архив с `agent.yaml` **в корне**
(не `submission/agent.yaml`!). Весь код агента выполняется YAML-конфигом,
который харнесс компилирует в дерево ADK-агентов — свой Python-код исполнять нельзя.

```
submission.zip
├── agent.yaml              # REQUIRED, единственный root-конфиг
├── eval_config.yaml        # опционально: лимиты на таск (time/tool_calls/turns)
├── configs/sampling.yaml   # температура, top_p, thinking_budget и т.д.
├── prompts/*.md            # системные промпты, подключаются через !include
├── sub_agents/*.yaml       # под-агенты (например, read-only code_analyzer)
├── adapters/<name>/        # опционально: LoRA (adapter_config.json + adapter_model.safetensors)
└── skills/                 # опционально: ADK skills (SKILL.md)
```

Разрешённые модели (ровно одна на весь сабмишен):
`gemma-4-31b-it-qat-w4a16-ct`, `gemma-4-12b-it-qat-w4a16-ct`,
`gemma-4-e4b-it-qat-w4a16-ct`, `gemma-4-e2b-it-qat-w4a16-ct`.

Лимит размера архива — **3 GiB** (вместе с адаптерами).

## Доступные инструменты агента (9 штук)

- `run_command`, `read_file`, `edit_file`, `write_file` — работа с кодом/шеллом в `/workspace`
- `get_status`, `submit_patch` — бюджет и финализация патча
- `get_code_neighbors`, `search_similar_code`, `get_code_subgraph` — поиск по графу кода (доступен не для всех репо)

Подробные сигнатуры и форматы ответов — см. раздел 6 `HARNESS_README.md`
(скачивается в `data/HARNESS_README.md` через `scripts/download_data.sh`).

## Как проходит оценка (кратко)

1. **Container A** (агент): снапшот репо на `base_commit`, агент работает до
   `submit_patch()` / таймаута / исчерпания бюджета → извлекается `agent_patch`.
2. **Container B** (проверка): чистый снапшот + `agent_patch` + `task.test_patch`
   → `pytest` → задача resolved, если exit code 0 и все нужные тесты прошли.

Изменения тестовых файлов (`test_*.py`, `conftest.py`, `pytest.ini` и т.д.)
из патча агента **вырезаются** перед верификацией — чинить нужно только
исходный код библиотеки.

## Данные соревнования (`data/`, не коммитятся)

- `tasks.jsonl` — 129 задач (репозитории: fastapi, rich, requests, httpx):
  `instance_id`, `repo`, `base_commit`, `patch`, `test_patch`,
  `problem_statement`, `hints_text`, `created_at`.
- `snapshots/` (~20 ГБ) — архивы репозиториев на нужных коммитах.
- `graphs/`, `embeddings/` (~850 МБ) — графы кода и эмбеддинги для
  `get_code_neighbors` / `search_similar_code` / `get_code_subgraph`.
- `wheels/` — офлайн-кэш Python-пакетов для песочницы (сеть отключена).
- `sample_submission/` — официальный baseline-сабмишен (на нём основан `submission/` в этом репо).

Полный датасет качается через `make download-data-full` (используется CLI `kaggle`).

## Локальная проверка (если нужно гонять харнесс)

Требует установленных пакетов `swegemma`, `adk-submission`, `adk-eval-core`
(ставятся из датасета соревнования, не из этого репо) и Docker:

```bash
swegemma eval \
  --tasks data/tasks.jsonl \
  --snapshots-dir data/snapshots \
  --submission-dir submission \
  --results-dir results/run_01 \
  --sandbox docker
```

В минимальном шаблоне этого репозитория такой раннер не настроен —
это задел на будущее.
