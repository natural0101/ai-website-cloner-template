# Tool catalog

Исполняй действия через:

```python
import ai_blender_toolkit as abt
result = abt.dispatch("ACTION", {"argument": "value"})
```

## Основные actions

| Action | Когда использовать |
|---|---|
| `scene.inspect` | До плана и после изменений |
| `scene.checkpoint` | Перед существенными правками существующей сцены |
| `material.create_principled` | Простой PBR/GLB‑материал |
| `typography.create_plastic_text` | Отдельное создание 3D‑текста |
| `geometry.create_soft_shape` | rounded box, sphere, blob, tube |
| `scene.setup_studio` | Key/fill/rim, world, preview floor |
| `camera.frame` | Автоматически вписать target objects |
| `render.preview` | Один PNG |
| `render.multiview` | Front/front 3Q/side PNG |
| `asset.validate` | Перед экспортом и после рискованной геометрии |
| `asset.export_glb` | GLB по выбранным объектам |
| `workflow.create_plastic_text_asset` | Полный типографический pipeline |

## Рекомендуемый первый вызов

```python
abt.dispatch("scene.inspect", {
    "object_limit": 200,
    "include_mesh_stats": True
})
```

## Готовый 3D‑текст

```python
abt.dispatch("workflow.create_plastic_text_asset", {
    "text": "TEAMON",
    "asset_name": "teamon_plastic",
    "mode": "GLYPHS",
    "size": 1.6,
    "depth": 0.28,
    "bevel": 0.14,
    "resolution": 768,
    "render": True,
    "export": True,
    "save_blend": True
})
```

## Ошибки

Dispatcher всегда возвращает словарь. При `status="error"` прочитай:

- `error_type`;
- `message`;
- `traceback_tail`.

Не повторяй тот же вызов без изменения причины ошибки.
