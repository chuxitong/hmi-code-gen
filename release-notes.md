# Release notes. Замороженный снимок прототипа

Дата снимка: 2026-04-17.

К девятой неделе прототип считается feature-complete: на десятой я уже не добавляю функциональность, а пишу текст ВКР. Этот файл фиксирует состав того, что считается «релизной версией». В git создан тег `v2026.04.17-prototype-freeze` на этом снимке; при необходимости можно откатиться командой `git checkout v2026.04.17-prototype-freeze`.

В репозитории на этом снимке есть плагин Figma с готовым UI и тремя действиями (Generate Code, Make It Closer to the Mockup, Edit by Request), двумя опциональными галками контекста и собранным `dist/code.js`. Локальный сервис FastAPI с эндпоинтами `/generate`, `/refine`, `/edit`, `/render`. Модуль рендера HTML в PNG через Playwright. Настоящая визуально-языковая модель UI2Code^N, обёрнутая в `local-service/model_wrapper.py`. Детерминированный заместитель с тем же интерфейсом `local-service/rule_based_model.py`, нужен для быстрой отладки пайплайна. Пост-процессор HTML в `local-service/postprocess.py` для финального «причёсывания» кода. Экспериментальные скрипты: `baseline-tests/run_baseline_tests.py`, `run_full_evaluation.py`, `run_edit_and_context.py`, `run_week9_comparison.py`. Один общий прогон подряд: `baseline-tests/run_all_experiments.py`. Проверка, что все файлы из плана на месте: `baseline-tests/verify_deliverables.py`. Скриншоты и GIF для отчётов: `baseline-tests/build_report_screenshots.py` (результат в `reports/screenshots/`).

Чтобы всё поднять у себя, нужно активировать `local-service/.venv`, запустить сервис через `uvicorn app:app --port 8000`, и параллельно последовательно выполнить нужные экспериментальные скрипты. Если UI2Code^N не хочется качать или не помещается в железо, можно не выставлять `USE_REAL_MODEL`; сервис тогда падёт на `RuleBasedModel`, и весь пайплайн отработает без изменений.

Чтобы переключиться на настоящую модель, нужно скачать её веса (`huggingface_hub snapshot_download zai-org/UI2Code_N → d:/hf_models/UI2Code_N`, при слабом канале через зеркало `HF_ENDPOINT=https://hf-mirror.com`) и перед стартом сервиса выставить `USE_REAL_MODEL=1`. Всё остальное не меняется.
