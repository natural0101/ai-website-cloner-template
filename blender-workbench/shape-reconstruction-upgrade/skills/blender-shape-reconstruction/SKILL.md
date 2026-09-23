---
name: blender-shape-reconstruction
description: Builds editable stylized volumetric figures in Blender 5.1 from semantic primitives and reconstructs reference-image assets using explicit FRONT_2_5D, TRUE_360, or HYBRID_HERO workflows. Use for hands, mascots, sculpt-like web icons, silhouette matching, contours, masks, 2.5D relief, single-image reconstruction, voxel union, multiview review, and web GLB validation. Do not activate for ordinary 3D text or material-only edits.
license: MIT
compatibility: Blender 5.1.x with Python through MCP; Shape Reconstruction Upgrade tools must be importable. OpenCV comparison runs outside Blender.
metadata:
  version: "1.0.0"
  language: "ru"
---

# Blender Shape Reconstruction

## Перед началом

1. Вызови базовый `scene.inspect` и checkpoint при непустой сцене.
2. Вызови `shape.scene_report`.
3. Объяви ровно один target mode: `FRONT_2_5D`, `TRUE_360` или `HYBRID_HERO`.
4. Не называй скрытую геометрию восстановленной из одного изображения.
5. Прочитай только один подходящий reference‑файл ниже.

## Маршрутизация

- Выбор режима и ограничения: `references/decision-modes.md`.
- Объём с нуля, руки, mascot: `references/blockout-hands.md`.
- Masks, contours, layer stack, overlay: `references/reference-pipeline.md`.
- Метрики, topology, GLB: `references/qa-export.md`.
- Доступные actions: `references/tool-catalog.md`.
- Внешние AI‑инструменты: `references/optional-tools.md`.

## Обязательный порядок

1. Camera/resolution.
2. Semantic decomposition.
3. Large-mass blockout.
4. Front silhouette review.
5. Side/3⁄4 volume review, если режим не `FRONT_2_5D`.
6. Voxel union только после overlap; SOURCE сохранить.
7. Локальное исправление одной категории ошибки.
8. Материал и свет только после shape gate.
9. Validation.
10. GLB + `.blend` + отчёт.

## Запреты

- Не строить пальцы как одинаковые параллельные цилиндры.
- Не превращать блики/тени в геометрию.
- Не выполнять destructive union над единственной копией.
- Не загружать готовые модели при запросе «с нуля».
- Не устанавливать OpenCV/PyTorch в Blender Python.
- Не считать высокий front IoU доказательством хорошего 360° объёма.
- Не менять material/light для исправления silhouette.

## Definition of done

- target mode и допустимый camera range указаны;
- SOURCE и OUTPUT разделены;
- silhouette gate пройден или честно указан failure;
- для TRUE_360 просмотрены front, 3⁄4, side и back;
- validation не содержит errors;
- PNG, `.blend` и GLB существуют;
- указаны triangle count, warnings и предположения скрытой формы.
