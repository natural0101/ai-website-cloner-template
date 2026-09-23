# Что пишут и показывают в мире

## 1. Официальный уровень

### Anthropic — “Claude for Creative Work”
Blender connector описан как natural-language interface к Python API и документации. Указаны анализ/отладка сцен, batch changes, custom tools, scripts, procedural animation и parametric models. Это сильное подтверждение направления, но не benchmark художественного качества.

### Blender Python API
Официальная документация остаётся первичным источником сигнатур и поведения. Агент не должен полагаться на память о версии API: перед сложной операцией нужна capability probe.

### MCP
MCP решает подключение инструментов. Он не добавляет автоматически знания о topology, композиции, материалах или скульпте.

## 2. Научные системы

### VIGA
Главная идея — непрерывный `code → render → inspect` с read-only наблюдением, отдельными mutation tools и bounded multimodal memory. Это наиболее прямое объяснение, почему сырой MCP недостаточен.

### Thinking in Blender / staged inverse graphics
Разделяет reconstruction на geometry, material, composition и lighting. У каждого этапа собственный verifier и checklist. Это предотвращает типичную ошибку, когда агент, исправляя серебро, ломает форму.

### BlenderGym и 3DCodeBench
Оба показывают, что текущие модели всё ещё уступают людям. Частые проблемы: несовместимый API, неисполняемый код, неверное действие после правильной визуальной критики, disconnected/floating components и слабые verifiers.

### BlenderRAG и LL3M
Показывают пользу retrieval по экспертным примерам, специализированных ролей, bmesh/modifiers/shader nodes и общего контекста кода. Важное ограничение: результаты в основном авторские, а public adoption у BlenderRAG пока небольшой.

### SceneCraft, 3D-GPT, Proc3D, 3Dify, EZBlender
Повторяющиеся идеи: scene graph, task decomposition, reusable library, parametric representation, human candidate selection и сочетание глобального плана с локальными ReAct-правками.

## 3. Open source

### ahujasid/blender-mcp
Очень популярный транспорт/connector. Даёт screenshots, scene info, material/object control и arbitrary Python. Issues показывают реальные compatibility, transport и security failure modes.

### Blender MCP Assembly Skill
Небольшой, но очень прикладной skill: сначала карта соединений, затем bounds/overlap checks, transform audit и finalization. Полезнее для рук/маскотов, чем ещё один общий prompt.

### Multi-agent community repos
Есть системы с 17 агентами и полным production pipeline. Они доказывают техническую возможность специализации, но не доказывают, что большое число агентов повышает качество. В одном заметном README demo-link оставлен placeholder — это снижает уровень подтверждения.

## 4. Видео и социальные отзывы

Видео хорошо объясняют установку и отдельные техники. Они становятся знаниями агента только после преобразования в воспроизводимый recipe с кодом, параметрами, входами и тестом.

Отзывы полярные:

- Плюс: быстрое создание editable low-poly props, blockout, batch operations и прототипов.
- Минус: primitive-looking geometry, плохое spatial reasoning, долгие итерации, слабые детали и соединения.

Оба лагеря совместимы: агент полезен на структурированных задачах и нестабилен без constraints/verification на сложной форме.

## 5. Насколько это популярно

Популярность самого Blender MCP высокая по GitHub-сигналу и официальному connector-релизу. Экспертные надстройки, RAG и multi-agent проекты пока значительно меньше. Поэтому область уже реальна, но production best practices ещё формируются.
