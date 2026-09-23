# Кейсы: что реально делали AI-агенты в Blender

Ссылки и полные оговорки находятся в `SOURCE_AUDIT.csv/json`. Идентификатор `Sxx` — запись аудита. «Показано» означает только то, что подтверждается кодом, статьёй, логами или демонстрацией; это не равнозначно стабильной работе на любой задаче.

| Источник | Что создано или автоматизировано | Благодаря чему | Проверяемость | Что брать агенту |
|---|---|---|---|---|
| **S01 Anthropic: Claude for Creative Work** | Анализ и отладка сцен, Blender-скрипты/плагины, процедурная анимация, параметрические модели, batch-операции | Официальный Blender connector, Python API и документация | **Высокая для наличия инструмента**, низкая для художественного качества: независимого benchmark в анонсе нет | MCP использовать как интерфейс к API, а не как замену Blender-знаниям |
| **S02 ahujasid/blender-mcp** | Prompt-driven операции со сценой, объектами и материалами; screenshots; запуск Blender Python; интеграции asset/3D-сервисов | Socket bridge + MCP tools + `bpy` | **Высокая для реализации и популярности**: код открыт; качество сложной формы не доказано | Сохранить transport, но ограничить raw Python, отключить telemetry для закрытых проектов и добавить semantic tools/QA |
| **S06 VIGA** | Итеративная реконструкция и редактирование Blender-сцен | Цикл `code → render → inspect`, high-level graphics skills, read-only observation, bounded multimodal memory | **Сильная research evidence**, но preprint и авторская оценка | Разделить inspection/mutation; хранить только короткую память; править один дефект |
| **S07 Thinking in Blender** | Single-image reconstruction с отдельной оптимизацией формы, материала, композиции и света | Staged inverse graphics + verifier/checklist каждого этапа | **Сильная, но свежая preprint evidence** | Запретить material/light этапам менять geometry; approve/checkpoint каждого stage |
| **S08 BlenderGym** | Benchmark реальных Blender-editing задач и систем, а не одна showcase-сцена | 245 задач, human baseline, автоматические и человеческие оценки | **Высокая как benchmark**, но не доказывает конкретный production workflow | Не доверять одному visual score; проверять API, сцену и результат человеком на спорных местах |
| **S09 3DCodeBench** | Procedural 3D-модели через код; сравнение 12 VLM/agent systems | Исполняемый Blender-код, multi-turn refinement, human preference arena | **Сильная benchmark evidence**, очень свежая | Capability probe, structural QA и multi-turn refinement обязательны; render success недостаточен |
| **S10–S11 BlenderRAG** | Генерация Blender Python по похожим экспертным примерам; заявлено улучшение compilation и semantic similarity | 500 валидированных примеров + retrieval/vector DB + code synthesis | **Средне-высокая**: dataset/код есть, результаты в основном авторские, adoption небольшое | Локальная база `описание + код + параметры + результат + failures`; top-3/5 retrieval |
| **S12 LL3M** | Редактируемые procedural objects/scenes с bmesh, modifiers и shader nodes | Специализированные planner/retriever/coder/debugger/refiner роли | **Research prototype** | Разделять роли логически, но не обязательно держать много параллельных агентов |
| **S13 SceneCraft** | Сложные сцены из множества assets с пространственными ограничениями | Scene graph, численные constraints, render feedback, reusable function library | **Research evidence** | До кода строить scene graph и reusable semantic functions; связи задавать числами |
| **S14 3D-GPT** | Procedural 3D content из текстовой задачи | Task dispatch → conceptualization → modeling agents | **Ранний research prototype** | Полезна декомпозиция, но старый prototype не считать production guarantee |
| **S15 Planner–Actor–Critic** | Co-creation workflow с human supervision и критиком | Планировщик, исполнитель, checklist-критик, пользовательские checkpoints | **Средне-высокая research evidence** | Критик должен назвать доминирующий дефект и следующую одну правку; человек выбирает A/B при неоднозначности |
| **S16 3Dify** | Procedural generation с MCP/RAG и выбором вариантов | Retrieval + параметры + candidate selection, включая local LLM workflow | **Средняя**: system description, ограниченная независимая проверка | Сохранять preference log; варианты генерировать только там, где reference неоднозначен |
| **S17 Proc3D** | Параметрические модели, которые можно править без полной регенерации | Компактный procedural graph и exposed parameters | **Средне-высокая research evidence** | Именованные части, non-destructive modifiers и editable parameters важнее «финального» монолитного mesh |
| **S18 Blendify** | Высокоуровневое Python-создание сцен, материалов, цветов и renders | Обёртка над сложным Blender API | **Код + technical report**, больше про rendering | Semantic API уменьшает API errors и объём кода |
| **S19 EZBlender** | Планируемое 3D-editing с локальными реактивными исправлениями | Глобальный plan + локальный ReAct loop | **Research evidence** | Планировать stage один раз, затем делать малые scoped corrections вместо полной перестройки |
| **S20 Assembly Skill** | Более связные multi-part assemblies: детали, пальцы, мебельные части | Connection map, world-space bounds, overlap и transform audit | **Открытый узкий skill**, небольшой community signal | Expected contacts и gaps проверять машинно; это прямое лечение floating fingers/parts |
| **S21 AGNO 17-agent studio** | Заявленный полный pipeline: modeling, shading, animation, render и память | 17 специализированных агентов и orchestration | **Код/README есть, evidence слабее**; demo-link в README неполный | Специализация возможна, но 17 активных агентов не добавлять без измеримой пользы |
| **S22 LLM-Blender-Agent** | Работа с несколькими LLM, function calling, assets и внешними text/image-to-3D | Provider adapters + Gradio + Blender actions/external generators | **Открытый код, небольшое adoption** | Provider abstraction полезна; imported AI mesh не считать обучением modeling from scratch |
| **S23 sandraschi/blender-mcp** | Live/headless automation, exports, VSE, Geometry Nodes и широкие tool families | Более явные инструменты и headless execution | **Открытый код/тесты, небольшой user signal** | Headless smoke tests и узкие tool families полезнее одного бесконечного executor |
| **S27–S29 YouTube demos** | Установка MCP, text-to-Blender демонстрации, assembly workflow | Пошаговый UI/prompt workflow | **Демонстрационная evidence**; не benchmark | Из видео извлекать только воспроизведённый recipe с version, code, render и test |

## Общий знаменатель успешных кейсов

1. Результат строится как **редактируемая программа/scene graph**, а не как одноразовая картинка.
2. Агенту дают **high-level операции**, а не заставляют каждый раз вспоминать весь `bpy`.
3. Работа разбивается на **малые этапы и малые исправления**.
4. После кода агент получает **render и структурное состояние сцены**.
5. Успешные решения превращаются в **проверенные examples**, а не в длинную историю чата.
6. Пользователь нужен для **неоднозначного художественного выбора**, а не для ручного микроменеджмента каждой координаты.

## Где демонстрации чаще всего вводят в заблуждение

- Показывают только front render, но не side/back и не `.blend`.
- Смешивают modeling from scratch с импортом готового/generated mesh.
- Не указывают Blender/MCP/model versions и число неудачных итераций.
- Называют красивый screenshot «готовым 3D», не проверяя topology, connections, UV и GLB.
- Публикуют лучший единичный результат без success rate.
