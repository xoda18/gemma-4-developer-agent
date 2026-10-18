# Gemma 4 Developer Agent — стартовый шаблон

Минимальный шаблон сабмишена для соревнования [Google — The Gemma 4 Developer Agent Competition](https://www.kaggle.com/competitions/gemma-4-developer-agent) на Kaggle.

## О соревновании

Нужно собрать автономного SWE-агента на базе **Gemma 4**, который чинит
реальные issue в Python-репозиториях: исследует код, вносит минимальные
правки и отправляет патч. Метрика — **Resolution Rate**: доля задач, патч
которых проходит скрытые тесты (в духе SWE-bench).

Сабмишен — не предсказания, а **декларативный YAML-конфиг агента**
(`agent.yaml` + промпты + опциональные LoRA-адаптеры), который харнесс
компилирует в дерево ADK-агентов. Свой Python-код исполнять нельзя.

Подробный разбор формата — в [docs/NOTES.md](docs/NOTES.md).

## Структура репозитория

```
submission/              # содержимое будущего submission.zip
├── agent.yaml           # корневой конфиг агента (REQUIRED)
├── eval_config.yaml     # опционально: лимиты по времени/вызовам инструментов
├── configs/sampling.yaml
├── prompts/             # system.md, analyzer.md — !include из YAML
├── sub_agents/          # code_analyzer.yaml — read-only под-агент
└── adapters/            # сюда кладутся LoRA-адаптеры (пока пусто)
scripts/
├── download_data.sh     # скачивает данные соревнования через Kaggle API
├── pack_submission.py   # собирает submission/ -> submission.zip
└── validate_submission.py
docs/NOTES.md            # конспект по формату соревнования и харнессу
```

## Быстрый старт

1. Настрой Kaggle API (один раз):
   ```bash
   mkdir -p ~/.kaggle
   echo "<ТВОЙ_KAGGLE_API_TOKEN>" > ~/.kaggle/access_token
   chmod 600 ~/.kaggle/access_token
   pip install kaggle
   ```
2. Скачай лёгкие справочные файлы соревнования (`tasks.jsonl`, `HARNESS_README.md`, baseline-сабмишен):
   ```bash
   make download-data
   ```
   Полный датасет (графы кода, эмбеддинги, снапшоты репозиториев, ~21 ГБ):
   ```bash
   make download-data-full
   ```
3. Проверь и собери сабмишен:
   ```bash
   make pack
   ```
   Получится `submission.zip` с `agent.yaml` в корне архива.
4. Загрузи `submission.zip` на странице соревнования (**Submit Predictions**).

## Данные

Данные соревнования не хранятся в репозитории (`data/` в `.gitignore`) —
они объёмные (до ~21 ГБ) и скачиваются индивидуально через Kaggle API
каждым участником.

## Статус

Это пустой стартовый шаблон на основе официального `sample_submission` из
датасета соревнования: baseline-промпт и набор инструментов без
дообучения (LoRA) и без локального eval-раннера. Следующие шаги —
улучшение промпта, и (опционально) LoRA-файнтюнинг под `submission/adapters/`.
