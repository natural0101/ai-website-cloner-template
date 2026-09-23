# Итог мирового поиска

## Что действительно реализовано

- Blender уже официально подключается к AI через MCP/Python API. Это реальный инструмент автоматизации, обучения, анализа сцены и генерации скриптов.
- Самый заметный открытый Blender MCP имеет крупное сообщество. Это подтверждает популярность интерфейса, но не подтверждает качество сложного моделинга.
- Исследовательские системы уже создают и редактируют Blender-сцены через код, scene graphs, RAG, multi-view renders и iterative critique.
- Есть работающие специализации: procedural modeling, scene layout, materials, lighting, assembly auditing и single-image staged reconstruction.

## Что пока не доказано

- Нет надёжного подтверждения, что обычный универсальный агент с одним `execute_blender_code` стабильно работает как опытный 3D-художник.
- Нет гарантированных 95% для полноценного 360° объекта из одной маленькой картинки.
- GitHub stars, YouTube-демо и vendor testimonials не являются независимым качественным benchmark.
- Visual verifier тоже ошибается: красивый фронтальный render может скрывать floating parts, плохую topology и неверную заднюю поверхность.

## Устойчивый общий паттерн

`reference/spec → scene graph → semantic tools → small edit → render/inspect → scoped critique → commit/rollback → structural validation → export`

Качество растёт не от длинного system prompt, а от пяти вещей:

1. Проверенных high-level skills вместо постоянного raw `bpy`.
2. Разделения geometry/material/composition/lighting.
3. Multi-view и machine-readable scene inspection.
4. Базы удачных примеров `описание + код + параметры + render + failures`.
5. Ограниченной памяти и строгого критерия готовности.

## Практический вывод для этого агента

Добавлять ещё один огромный агентный фреймворк не нужно. Нужны staged mode, retrieval, structural QA, compatibility probe и security guard. Они включены в v4 и загружаются только по задаче.
