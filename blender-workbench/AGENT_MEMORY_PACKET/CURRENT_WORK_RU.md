# Current Work

Дата состояния: 2026-06-23.

## Цель

Собрать качественный soft 3D web asset по референсу: две мягкие оранжевые руки держат зеленый шар, с розовыми манжетами, в стиле clean 3D icon.

Primary reference:

```text
blender-workbench/references/hands-sphere-primary.png
```

## Текущий web preview

```text
http://127.0.0.1:3000/bottom-hand-part
```

## Текущий лучший нижний hand asset

```text
bottom_hand_result_v5
```

Файлы:

```text
blender-workbench/scripts/blender_create_bottom_hand_result_v5.py
public/models/bottom_hand_result_v5.glb
blender-workbench/artifacts/exports/bottom_hand_result_v5.glb
blender-workbench/artifacts/blend/bottom_hand_result_v5.blend
```

Рендеры:

```text
blender-workbench/artifacts/renders/bottom_hand_result_v5_01_clay_front_with_guide.png
blender-workbench/artifacts/renders/bottom_hand_result_v5_02_clay_front_hand_only.png
blender-workbench/artifacts/renders/bottom_hand_result_v5_03_clay_front_3q.png
blender-workbench/artifacts/renders/bottom_hand_result_v5_04_clay_side.png
blender-workbench/artifacts/renders/bottom_hand_result_v5_05_opaque_front_fixed.png
```

Отчеты:

```text
blender-workbench/artifacts/reports/bottom_hand_result_v5_scene_report.json
blender-workbench/artifacts/reports/bottom_hand_result_v5_scene_graph.json
blender-workbench/artifacts/reports/bottom_hand_result_v5_qa.json
```

## Технический статус v5

- triangles: `28 324`
- validation errors: `0`
- validation warnings: `0`
- structural QA: wrist/cuff contact fixed to `OVERLAP`
- site route `/bottom-hand-part` loads `bottom_hand_result_v5.glb`
- `npm run typecheck` проходил после подключения v5

## Честная визуальная оценка

`v5` лучше предыдущих попыток, потому что:

- рука стала более компактной;
- palm cup больше похожа на поддерживающую ладонь;
- wrist/cuff контакт стал нормальнее;
- пальцы меньше выглядят как случайный веер трубок.

Но это не финал:

- несколько кончиков пальцев частично съедены palm/root mass;
- нижняя рука еще не настолько похожа на reference, как требуется;
- нужно улучшить читаемость пальцев без возврата к fan-like форме v4;
- нужно не потерять side thickness.

## Предыдущие важные уроки

- `bottom_hand_part_v1` был технически валиден, но визуально отвергнут.
- `bottom_hand_result_v3` был чище, но еще не принят.
- `bottom_hand_result_v4` слишком буквально пошел по target centerlines и стал fan-like.
- `bottom_hand_result_v5` сохранил fingertip target, но спрятал roots в компактную palm cup. Это лучшая база для следующей итерации.

