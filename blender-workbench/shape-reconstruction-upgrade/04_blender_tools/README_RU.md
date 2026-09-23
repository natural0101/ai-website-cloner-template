# Blender tools

## Файлы

- `shape_tools.py` — реализации Blender 5.1.
- `shape_dispatcher.py` — allow‑listed JSON dispatcher для MCP.

## Actions

| Action | Назначение |
|---|---|
| `shape.scene_report` | состояние созданных/экспортируемых объектов |
| `shape.create_part` | ellipsoid, rounded box или tapered tube |
| `shape.voxel_union` | мягко объединить части, сохранив SOURCE |
| `shape.create_cupping_hand` | одна semantic рука |
| `shape.create_hand_sphere` | пример полноценной фигуры: шар + две руки |
| `shape.import_contours` | contour JSON → 2.5D relief с holes |
| `shape.import_layer_stack` | несколько contour layers с depth order |
| `shape.setup_reference_camera` | точная orthographic camera по resolution |
| `shape.render_silhouette` | белая mask без влияния материалов/света |
| `shape.apply_reference_fit` | применить transform suggestion только с `confirm=true` |
| `shape.validate` | triangles, boundary/non-manifold, materials |
| `shape.export_glb` | экспорт только указанных/tagged объектов |

## Безопасность

- модуль не удаляет пользовательскую сцену;
- `voxel_union` через dispatcher всегда сохраняет source parts;
- `apply_reference_fit` требует явного подтверждения;
- нет сети, downloads, shell и установки пакетов;
- объекты помечаются `abt_shape_generated`, `abt_shape_role`, `abt_shape_export`;
- shape‑модуль не monkey‑patch базовый toolkit.

## Coordinate convention

- X — горизонталь изображения;
- Z — вертикаль изображения;
- reference camera находится на отрицательной Y и смотрит в +Y;
- более отрицательный Y визуально ближе к камере.
