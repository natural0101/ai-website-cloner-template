# Подключение к MCP

## Вариант A: semantic tools

Отобразите tools из `tool_manifest_shape.json` на вызовы `shape_dispatcher.dispatch_json`.

Каждый tool преобразуется в payload:

```json
{
  "action": "shape.create_hand_sphere",
  "arguments": {"name": "Hero"}
}
```

## Вариант B: существующий execute-code MCP

На стороне MCP используйте `semantic_shape_adapter.py`, который создаёт короткий фиксированный код:

```python
from semantic_shape_adapter import build_blender_code

code = build_blender_code(
    shape_tools_dir=r"C:\AI_Blender_Agent_Kit\shape_reconstruction_upgrade\04_blender_tools",
    action="shape.scene_report",
    arguments={}
)
```

## Правила

1. Не передавать модели право менять `shape_dispatcher.py` во время задачи.
2. Возвращать агенту весь stdout JSON.
3. Namespaced tools включать только при активации shape skill.
4. Внешний OpenCV tool не должен исполняться внутри Blender MCP.
5. Пути reference/output передавать абсолютными.
6. Перед `shape.apply_reference_fit` требовать `confirm=true`.
