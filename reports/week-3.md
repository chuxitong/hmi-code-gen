# Еженедельный отчёт — Неделя 3

**Тема:** Запуск и проверка базовой модели UI2Code^N  
**Дата:** Неделя 3  
**Автор:** Чжан Сычэн

---

## Выполненные задачи

### 1. Установка и настройка окружения

**Аппаратное обеспечение:**
- GPU: NVIDIA RTX 4090 (24 ГБ VRAM)
- RAM: 32 ГБ
- Диск: ~30 ГБ для весов модели

**Программное обеспечение:**
- Python 3.10 (conda)
- PyTorch 2.1 + CUDA 12.1
- Transformers (HuggingFace), Gradio

**Процесс установки:**
```bash
git clone https://github.com/aspect-ux/UI2CodeN.git
conda create -n ui2code python=3.10 -y && conda activate ui2code
pip install -r requirements.txt
python download_model.py
```

- Загрузка модели: ~45 сек
- Потребление VRAM: ~18 ГБ при инференсе

### 2. Тестовые примеры (3 теста)

#### Тест 1: Equipment Status Dashboard (Простой)
- **Верно:** структура сетки 3×2, цвета фона карточек, цвета индикаторов статуса
- **Ошибки:** отступы на ~30% больше референса, единый размер шрифта 14px вместо иерархии 12/16/20px, иконки заменены текстом
- **Визуальное сходство:** ~65%
- **Скриншоты:** см. `baseline-tests/outputs/test1-generated.png` и `baseline-tests/outputs/test1-comparison.png`

#### Тест 2: Alarm & Event Screen (Простой)
- **Верно:** структура таблицы, тёмный заголовок, кнопки «Acknowledge»
- **Ошибки:** неточные цвета бейджей серьёзности, непоследовательная высота строк, потеря моноширинного шрифта для временных меток
- **Визуальное сходство:** ~60%
- **Скриншоты:** см. `baseline-tests/outputs/test2-generated.png` и `baseline-tests/outputs/test2-comparison.png`

#### Тест 3: Operator Control Panel (Средний)
- **Верно:** двухколоночная компоновка, текст кнопок «START»/«STOP»/«RESET», тёмные блоки для числовых значений
- **Ошибки:** выпадающий список стал текстовым списком, неконсистентные размеры кнопок, поля уставок отсутствуют
- **Визуальное сходство:** ~50%
- **Скриншоты:** см. `baseline-tests/outputs/test3-generated.png` и `baseline-tests/outputs/test3-comparison.png`

### 3. Итеративное улучшение (режим Polishing)

Проверено на Тесте 1 с 1–3 итерациями:

| Итерация | Визуальное сходство | Изменение |
|:--------:|:-------------------:|-----------|
| 0 (исходное) | ~65% | Базовая генерация |
| 1 | ~72% | Уменьшены отступы карточек, скорректирован размер заголовка |
| 2 | ~75% | Улучшено позиционирование индикаторов статуса |
| 3 | ~76% | Минимальные изменения, риск регрессий |

Скриншот после 2-й итерации: см. `baseline-tests/outputs/test1-refined-iter2.png`

---

## Основные выводы

### Сильные стороны модели
1. Корректное определение общей структуры макета (сетки, колонки, карточки)
2. Точное извлечение текстового содержимого (надписи, заголовки, текст кнопок)
3. Приближённое воспроизведение цветовой палитры (±10%)
4. Самодостаточный HTML+CSS вывод, сразу рендерится в браузере
5. Режим редактирования работает: инструкции типа «сделай кнопку красной» применяются корректно

### Типичные ошибки
1. **Некорректные отступы** (очень часто) — отклонение 20–50%
2. **Единообразие шрифтов** (часто) — модель игнорирует типографическую иерархию
3. **Плохое выравнивание** (часто) — правое/центральное выравнивание становится левым
4. **Пропуск элементов** (средне) — мелкие элементы (иконки, бейджи, тоглы) опускаются
5. **Области графиков** (часто) — графики заменяются цветным прямоугольником

---

## Текущие проблемы

- Режим CPU-инференса непрактично медленный (~5 мин на генерацию).
- Графики и диаграммы не воспроизводятся — потребуется специальная обработка.

## Следующие шаги

- Обернуть модель в локальный HTTP-сервис (Неделя 4).
- Определить API-эндпоинты для всех трёх режимов работы.

---

## Воспроизводимость

### Скрипт запуска тестов

Все тесты можно воспроизвести одной командой:

```bash
python baseline-tests/run_baseline_tests.py
```

Скрипт последовательно выполняет:
1. **Generation** — генерация кода из 3 скриншотов (Equipment Status, Alarm Screen, Operator Panel)
2. **Refinement** — 2 итерации улучшения на Тесте 1
3. **Editing** — редактирование по текстовой инструкции на Тесте 1

Результаты (HTML, PNG, лог) сохраняются в `baseline-tests/outputs/`.

### Использованные промпты

**Тест 1 (Generation):**
> Generate a complete single-file HTML page with inline CSS that reproduces this industrial equipment status dashboard. Use a dark background, colored status indicator dots, and card-based layout.

**Тест 2 (Generation):**
> Generate a complete single-file HTML page with inline CSS that reproduces this alarm and event monitoring screen. Include a summary bar with severity counts, tab navigation, and a data table with severity badges, timestamps, descriptions, and acknowledge buttons.

**Тест 3 (Generation):**
> Generate a complete single-file HTML page with inline CSS that reproduces this operator control panel. Include start/stop/reset buttons, operating mode selector (Auto/Manual/Service), setpoint input fields, and live readout displays.

**Refinement:**
> Compare the rendered code screenshot with the original reference image. Improve spacing, font size hierarchy, status indicator styling, and card proportions to make the output closer to the reference mockup.

**Editing:**
> Make the warning card border thicker and add a pulsing animation to the fault status indicator.

Все промпты также сохранены в файле `baseline-tests/outputs/prompts.json`.

---

## Приложение: файлы交付物

| # | 交付物 | Расположение в репозитории |
|---|--------|---------------------------|
| 1 | Полный отчёт по оценке базовой модели | `baseline-tests/baseline-report.md` |
| 2 | **Скрипт запуска тестов** | `baseline-tests/run_baseline_tests.py` |
| 3 | **Промпты (JSON)** | `baseline-tests/outputs/prompts.json` |
| 4 | **Лог выполнения** | `baseline-tests/outputs/test-run.log` |
| 5 | **Сводка результатов** | `baseline-tests/outputs/results-summary.json` |
| 6 | Тест 1 — сгенерированный HTML | `baseline-tests/outputs/test1-generated.html` |
| 7 | Тест 2 — сгенерированный HTML | `baseline-tests/outputs/test2-generated.html` |
| 8 | Тест 3 — сгенерированный HTML | `baseline-tests/outputs/test3-generated.html` |
| 9 | Тест 1 — скриншот вывода модели | `baseline-tests/outputs/test1-generated.png` |
| 10 | Тест 2 — скриншот вывода модели | `baseline-tests/outputs/test2-generated.png` |
| 11 | Тест 3 — скриншот вывода модели | `baseline-tests/outputs/test3-generated.png` |
| 12 | Тест 1 — HTML после итерации 1 | `baseline-tests/outputs/test1-refined-iter1.html` |
| 13 | Тест 1 — HTML после итерации 2 | `baseline-tests/outputs/test1-refined-iter2.html` |
| 14 | Тест 1 — скриншот после итерации 2 | `baseline-tests/outputs/test1-refined-iter2.png` |
| 15 | Тест 1 — HTML после редактирования | `baseline-tests/outputs/test1-edited.html` |
| 16 | Тест 1 — скриншот после редактирования | `baseline-tests/outputs/test1-edited.png` |
| 17 | Тест 1 — сравнение: референс / вывод / улучшение | `baseline-tests/outputs/test1-comparison.png` |
| 18 | Тест 2 — сравнение: референс / вывод | `baseline-tests/outputs/test2-comparison.png` |
| 19 | Тест 3 — сравнение: референс / вывод | `baseline-tests/outputs/test3-comparison.png` |
