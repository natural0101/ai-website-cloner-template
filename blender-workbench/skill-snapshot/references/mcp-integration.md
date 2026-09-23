# MCP integration

## Минимальный вариант

Существующий MCP выполняет код:

```python
import sys
sys.path.insert(0, r"C:\AI_Blender_Agent_Kit\python")
import ai_blender_toolkit as abt
print(abt.dispatch_json({"action": "scene.inspect", "arguments": {}}))
```

## Рекомендуемый вариант

Используй `mcp/tool_manifest.json` и создай отдельные tools. Каждый tool:

1. принимает аргументы по JSON Schema;
2. вызывает соответствующий dispatcher action;
3. возвращает JSON как structured content;
4. для render возвращает PNG как image content.

## Что не делать

- Не показывать модели десятки сырых `bpy` operations как отдельные tools.
- Не передавать только screenshot без scene JSON.
- Не обрезать scene inspection первыми десятью объектами без признака truncation.
- Не смешивать результаты разных действий в неструктурированную строку.
- Не разрешать reset/rollback без подтверждения.

## Почему изображения важны

Структурированное состояние обнаруживает типы, размеры и topology. PNG обнаруживает художественные дефекты, которые нельзя надёжно вывести из JSON. Нужны оба канала.
