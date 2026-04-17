# Список литературы

Окончательное оформление делается по требованиям кафедры. Ниже — состав источников, на которых строится работа, с короткими пометками о роли каждого.

## Основные источники по screenshot/UI-to-code

1. Ян и соавторы. UI2Code^N: A Visual Language Model for Test-Time Scalable Interactive UI-to-Code Generation. arXiv:2511.08195, 2025. Репозиторий кода: `https://github.com/zai-org/UI2Code_N`. Веса: `https://huggingface.co/zai-org/UI2Code_N`. Основной baseline моей работы: открытая VLM с режимами UI-to-code, UI-editing, UI-polishing. Базовая модель — GLM-4.1V-9B-Base.

2. Си и соавторы. Design2Code: How Far Are We From Automating Front-End Engineering? 2024. Методика и бенчмарк для оценки систем screenshot-to-code. Использовалась как ориентир при построении собственного протокола оценки.

3. Laurençon и соавторы. WebSight: A Large-Scale Dataset of Synthetic UI Screenshots and Their HTML/CSS Code. 2024. Большой веб-датасет, в моей работе упоминается как методологический контекст: задаёт масштаб данных, на котором работают современные подходы.

4. Yue и соавторы. Web2Code: A Large-Scale Webpage-to-Code Dataset and Benchmark. 2024. Датасет и базовые методы для генерации кода по веб-скриншотам. Роль в работе — контекст, не прямое использование.

## Инженерный контекст Figma

5. Figma Plugin API — официальная документация. `https://www.figma.com/plugin-docs/`. Ключевые разделы: `exportAsync`, `figma.variables`, `getCSSAsync`, `figma.ui.postMessage`/`parent.postMessage`. На эту документацию опирается вся часть по извлечению данных из макета.

## Промышленные HMI / SCADA — визуальные референсы

6. Siemens. HMI Template Suite. Публичные промышленные шаблоны операторских панелей.

7. Inductive Automation. Ignition SCADA Public Demonstration. Открытое демо реальной SCADA-платформы.

8. FUXA — открытая web-based SCADA. SVG-ориентированные синоптические экраны.

9. JointJS. SCADA/HMI Demo. Интерактивные демо с диаграммами трубопроводов и танков.

10. ISA. ISA-101 Human-Machine Interfaces for Process Automation Systems. 2015. Стандарт по эргономике HMI, из которого взяты соглашения по цвету, контрасту и иерархии в собственных мокапах.

## Инструменты реализации

11. FastAPI. Web framework. `https://fastapi.tiangolo.com/`. Основа локального сервиса.

12. Playwright. `https://playwright.dev/`. Headless-браузер для рендера HTML в PNG.

13. Hugging Face `transformers`, `accelerate`, `bitsandbytes`. Стек загрузки и инференса VLM, с квантизацией в 4-bit при необходимости.

## Дополнительное чтение

14. Обзорные работы по визуально-языковым моделям и мультимодальному обучению (добавляются по рекомендации руководителя на этапе правок).

15. Источники по эргономике операторских интерфейсов и стандартам визуализации в АСУ ТП (ISO 11064 и смежные).

Даты обращения ко всем электронным ресурсам указываются на финальной стадии оформления списка.
