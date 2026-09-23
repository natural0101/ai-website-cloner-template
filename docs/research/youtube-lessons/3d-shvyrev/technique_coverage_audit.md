# Аудит покрытия техник 3D SHVYREV

Детерминированный аудит связывает полный каталог источников с канонической базой техник.

## Сводка

- Каталог и source findings: **237/237**.
- Канонические техники: **71**.
- Применимые источники (`new_improvement` + `mixed`): **94**.
- Кандидатные темы в применимых источниках: **308**.
- Применимые источники с хотя бы одной source-level связью: **89**.
- Применимые источники без source-level связи: **5**.
- Topic-level решений: **441/441**.
- Применимых тем с явным решением: **308/308**.

Source-level link не обязателен, если все темы источника явно отклонены или отложены с причиной. Полноту доказывает `topic_resolutions.jsonl`.

## Незакрытые гейты

- Нет.

## Применимые источники без канонической связи

- `nMHUAoneJ-w` — темы разрешены как reject/defer без искусственной канонизации: Blender 5.1 Raycast node для толщины, X-ray и outline shader
- `F6Wsf1kfF6I` — темы разрешены как reject/defer без искусственной канонизации: Drag-to-duplicate с ориентацией по поверхности; Alt+V операция для создания угла — распознано неуверенно; Driver/expression для автоматического мигания emission
- `br_S9ZiB644` — темы разрешены как reject/defer без искусственной канонизации: Affect Only Locations при раздвижении объектов Scale; Separate by Loose Parts; Выравнивание выбранных точек масштабом 0 по оси
- `VO_0mw_rYk8` — темы разрешены как reject/defer без искусственной канонизации: Particle/Hair system и Hair Dynamics для шерсти
- `H-BM3X4Z8oM` — темы разрешены как reject/defer без искусственной канонизации: Минимальный armature rig для простых конечностей; Pose blocking прыжка: сгибание, приседание, выпрямление и контактные кадры

## Источники с неполным визуальным/аудио-доказательством

- `6GLHDS2vRd0` — All storyboard pages show only the finished animated short and credits. No Blender interface, production breakdown, readable tool name, modifier, addon, or parameter is visible, and captions/audio are unavailable. A production technique cannot be inferred safely from the rendered result.
- `u9n5PJZMzLU` — The sole low-resolution storyboard repeats vertically cropped footage of a person or television scene. It contains no readable Blender interface, technique, addon, or technical on-screen text; metadata and title alone are insufficient.
- `kvYqHYgHXSI` — The storyboards visibly show a stylized snow mesh being added around the house, then manually stretched and refined, but the triggering operator or addon name and its settings are never legible. The audio caption at that moment is corrupted as «нажимаем отно». The evidence cannot distinguish a snow addon/operator from a manual, metaball, remesh, particle, or other geometry workflow, so no exact technique or addon was assigned.
