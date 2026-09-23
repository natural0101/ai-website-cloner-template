# Ревью качества Shape Reconstruction Upgrade

Дата проверки: 22.06.2026.

## Вердикт

Модуль **реально нужен** для описанной проблемы и не дублирует text/design upgrade. Он закрывает отдельный класс задач: semantic blockout, мягкое объединение объёмов, reconstruction по маскам, silhouette QA и multi-view discipline.

Модуль **не должен мешать базовому агенту**, если подключён по приложенной activation policy:

- отдельный namespace `shape.*`;
- отдельный skill с узким trigger;
- нет monkey-patching базового `ai_blender_toolkit`;
- MCP manifest подключается опционально;
- обязательная память короткая, остальные документы загружаются по необходимости;
- optional AI models не установлены и не добавлены в prompt;
- runtime code не использует сеть и не скачивает assets;
- Voxel Remesh через dispatcher всегда сохраняет SOURCE.

## Что проверено исполняемым кодом

Среда: Blender/bpy **5.1.2**, Python **3.13.5**, background mode.

1. Создание стилизованной композиции «шар + две руки» из ellipsoid, curves, rounded boxes и Voxel Remesh.
2. Сохранение редактируемых source parts и отдельного output.
3. Silhouette render в headless Blender.
4. GLB export.
5. Mesh validation: **11496 triangles**, 0 errors, 0 warnings, closed topology.
6. GLB размер: **261856 bytes**.
7. Contour JSON import.
8. Hole-preserving contour import.
9. Explicit layer stack.
10. MCP allow-list и отказ неизвестному action.
11. Защита `apply_reference_fit`: без `confirm=true` операция отклоняется.
12. Восстановление временных render/export states после операций.

Полный отчёт: `../demo/blender_runtime/blender_runtime_tests.json`.

## Проверка silhouette pipeline

На синтетическом reference 309×250, созданном специально для пакета:

- combined contour → Blender mask: IoU **0.975973**, boundary F1 **1.000000**, gate pass;
- mask с отверстием → Blender mask: IoU **0.973586**, boundary F1 **1.000000**, 1/1 hole preserved, gate pass;
- contour simplification reconstruction IoU: 0.9801–0.9976 на bundled masks.

Эти результаты подтверждают корректность coordinate/aspect/hierarchy pipeline, но не обещают такие же значения на любой размытой пользовательской картинке.

## Исправленные в ходе ревью проблемы

1. Blender 5.1 использует доступное имя Eevee, отличающееся от жёстко заданного `BLENDER_EEVEE_NEXT`; добавлен безопасный runtime fallback и Cycles CPU для background tests.
2. Blender orthographic scale интерпретируется по горизонтальной ширине кадра; добавлен пересчёт из заданного vertical world height с учётом aspect ratio. До исправления silhouette была примерно на 23% крупнее.
3. Render resolution теперь восстанавливается после временного silhouette render.
4. Выделение и viewport hidden state восстанавливаются после GLB export.
5. Contour hierarchy/holes проверены реальным render/compare, а не только JSON.

## Что пакет сознательно не обещает

- истинную заднюю геометрию из одного изображения;
- анатомически точные руки;
- production topology для rig/deformation;
- автоматическую segmentation baked RGB без ручной проверки;
- универсальный «95%» score;
- автоматическую текстуру/UV/retopology сложного персонажа;
- качество image-to-3D моделей, которые не входят в архив.

## Что настраивать дополнительно

Обязательно только внешний Python‑venv с OpenCV, если нужен contour/overlay workflow. SAM 3.1, Depth Anything, Hunyuan3D или TRELLIS.2 ставить только при конкретном bottleneck и отдельно от Blender Python.

## Итог

Архитектура качественная для текущего этапа: агент получает не «ещё больше теории», а ограниченное пространство осмысленных действий, objective feedback и rollback-friendly SOURCE/OUTPUT workflow. Для rigging и сложной анатомии позже нужен отдельный skill, а не расширение этого prompt.
