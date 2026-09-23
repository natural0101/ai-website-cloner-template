# Blender read-only QA

## `capability_probe.py`

Проверяет фактическую Blender version и наличие ключевых operators/types до генерации кода.

## `scene_qa.py`

Возвращает:

- world-space bounds/dimensions;
- scale/parent/collection/modifier summary;
- mesh topology counters;
- AABB contact graph;
- heuristic floating components;
- duplicate-style names;
- errors/warnings.

AABB — грубая проверка. Для критичной инженерной точности нужен exact collision/mesh-distance tool. Модуль read-only и не заменяет визуальный review.
