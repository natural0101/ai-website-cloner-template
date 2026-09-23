# Routing tools

| Намерение | Tool |
|---|---|
| понять созданные объекты | `shape.scene_report` |
| создать массу/палец/манжету | `shape.create_part` |
| слить пересекающиеся части | `shape.voxel_union` |
| стартовый пример руки/шара | `shape.create_hand_sphere` |
| построить одну руку | `shape.create_cupping_hand` |
| импортировать одну mask | `shape.import_contours` |
| импортировать перекрывающиеся masks | `shape.import_layer_stack` |
| зафиксировать reference view | `shape.setup_reference_camera` |
| получить mask кандидата | `shape.render_silhouette` |
| применить измеренный root transform | `shape.apply_reference_fit` |
| topology/triangle check | `shape.validate` |
| финальный web‑файл | `shape.export_glb` |

Сначала высокоуровневый tool. `shape.create_part` использовать для локальной сборки, а не создавать весь объект одним огромным вызовом.
