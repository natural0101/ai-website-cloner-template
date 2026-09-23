# Next Steps

## Следующий правильный Blender-проход

Не делать новый финальный full icon сразу.

Продолжить от:

```text
bottom_hand_result_v5
```

Один главный дефект:

```text
улучшить читаемость кончиков пальцев нижней руки, не разрушив compact palm cup
```

## План v6

1. Скопировать `blender_create_bottom_hand_result_v5.py` в новый скрипт:

```text
blender-workbench/scripts/blender_create_bottom_hand_result_v6.py
```

2. Сохранить v5 как baseline. Не перезаписывать v5.

3. В геометрии менять только:

- видимые finger midpoints;
- fingertip caps;
- palm/root pad coverage;
- valleys между пальцами.

4. Не менять в первом проходе:

- cuff material;
- lighting;
- camera;
- web route layout;
- full icon scene.

5. Сделать новые артефакты:

```text
bottom_hand_result_v6.glb
bottom_hand_result_v6.blend
bottom_hand_result_v6_01_clay_front_with_guide.png
bottom_hand_result_v6_02_clay_front_hand_only.png
bottom_hand_result_v6_03_clay_front_3q.png
bottom_hand_result_v6_04_clay_side.png
bottom_hand_result_v6_05_opaque_front_fixed.png
bottom_hand_result_v6_scene_report.json
bottom_hand_result_v6_scene_graph.json
bottom_hand_result_v6_qa.json
```

6. Проверить:

```powershell
npm run typecheck
```

7. Подключить site preview только если v6 реально лучше v5.

## Visual gate для v6

v6 лучше v5 только если:

- пальцы читаются как 4 мягких пальца;
- tips не съедены ладонью;
- рука остается чашей под шаром;
- wrist входит в cuff без грязного разрыва;
- side view показывает толщину, а не плоский relief;
- шар визуально лежит/перекрывает руку корректно;
- нет jagged edges и случайных зубцов.

## Если v6 хуже

Не подключать его к сайту.

Оставить v5 в `public/models/` и записать в report, почему v6 не принят.

