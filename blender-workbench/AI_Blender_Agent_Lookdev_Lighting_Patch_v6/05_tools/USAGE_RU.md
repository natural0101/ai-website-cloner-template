# Использование инструментов

## 1. Загрузить lookdev helpers в Blender

```python
exec(open(r"C:\path\AI_Blender_Agent_Lookdev_Lighting_Patch_v6\05_tools\production_lookdev_tools.py", encoding="utf-8").read())
```

## 2. Сохранить checkpoint

```python
save_checkpoint(r"C:\project\checkpoints\gas_station_before_lookdev.blend")
```

## 3. Read-only audit

```python
exec(open(r"C:\path\...\05_tools\scene_quality_audit.py", encoding="utf-8").read())
report = run_audit(r"C:\project\reports\scene_quality.json")
print(report["status"], report["score"])
```

## 4. Clay render

```python
set_neutral_clay_override(True)
render_png(r"C:\project\renders\clay.png", samples=128, exposure=-0.5)
set_neutral_clay_override(False)
```

## 5. Bevel pass только по утверждённому списку

```python
apply_bevel_detail_pass(
    ["Canopy", "Columns", "WindowFrames", "FuelPump"],
    width_ratio=0.004,
    segments=3,
)
```

Не применять ко всем mesh автоматически.

## 6. Создать базовый night rig

```python
create_architecture_night_rig(
    object_names=["Building", "Canopy", "FuelPump", "Ground"],
    world_strength=0.04,
)
```

Затем добавить practical lights вручную в реальные места светильников.

## 7. Материалы

```python
paint = create_pbr_material("MAT_RedPaint", "painted_metal", base_color=(0.55, 0.08, 0.04, 1))
rubber = create_pbr_material("MAT_Rubber", "rubber")
concrete = create_pbr_material("MAT_Ground", "concrete")
```

## 8. PNG-аудит

Во внешнем Python/OpenCV окружении:

```powershell
python image_quality_audit.py final.png --out final.audit.json
```

Код возврата `2` означает `REVIEW_REQUIRED`, а не сбой программы.

## 9. Важное про цвет

Значения `base_color` в `production_lookdev_tools.py` передаются в Blender как scene-linear. Цвета из CSS/Figma/sRGB сначала преобразовать в scene-linear или выставлять через Blender UI.

## 10. Тег hard-surface

`scene_quality_audit.py` требует bevel только у объектов, явно прошедших `apply_bevel_detail_pass()` или помеченных `obj["lookdev_hard_surface"] = True`. Это не создаёт ложных требований для органики и намеренного low-poly.
