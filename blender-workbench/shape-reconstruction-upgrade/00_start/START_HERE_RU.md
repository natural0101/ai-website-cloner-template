# Начать здесь

## 1. Подключить Blender‑tools

В Python, который выполняет ваш Blender MCP:

```python
import sys

SHAPE_TOOLS = r"C:\AI_Blender_Agent_Kit\shape_reconstruction_upgrade\04_blender_tools"
if SHAPE_TOOLS not in sys.path:
    sys.path.insert(0, SHAPE_TOOLS)

import shape_dispatcher
print(shape_dispatcher.dispatch_json({"action": "shape.scene_report", "arguments": {}}))
```

Ожидаемый результат: `"ok": true`, Blender `5.1.x`.

## 2. Подключить память агента

- постоянно: `../01_agent_memory/AGENT_MEMORY_CARD_RU.md`;
- при shape‑задаче: `../skills/blender-shape-reconstruction/SKILL.md`;
- не добавлять остальные документы в системный prompt целиком.

## 3. Подключить MCP

- предпочтительно: отдельные tools из `../07_mcp/tool_manifest_shape.json`;
- при строгом лимите tools: один allow‑listed dispatcher по `../07_mcp/INSTALL_MCP_RU.md`;
- не заменять базовые text/design tools: этот модуль активируется только для фигур и reference reconstruction.

## 4. Установить mask‑инструмент

Только если нужен contour/overlay pipeline:

```powershell
py -3.12 -m venv .venv-reference
.\.venv-reference\Scripts\python -m pip install -r shape_reconstruction_upgrade\05_external_tools\requirements.txt
```

OpenCV ставится **в отдельный venv**, не в Python Blender.

## 5. Первый тест

Запустить в Blender:

`../06_examples/01_create_hand_sphere_true3d.py`

Проверить:

- SOURCE‑коллекции содержат редактируемые части;
- OUTPUT содержит шар и две объединённые руки;
- validation не содержит errors;
- GLB и silhouette PNG созданы.

## 6. Реальная задача по картинке

До моделирования заполнить:

`../02_reference_intake/REFERENCE_INTAKE_TEMPLATE_RU.md`

Обязательное решение: `FRONT_2_5D`, `TRUE_360` или `HYBRID_HERO`.
