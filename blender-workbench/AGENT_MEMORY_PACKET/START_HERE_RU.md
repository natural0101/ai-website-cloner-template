# Start Here For New Agent

Ты продолжаешь уже начатую Blender/web задачу. Не начинай с нуля.

## Репозиторий

```text
C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template
```

Все пути ниже относительны к корню этого репозитория.

## Сначала прочитай

1. `blender-workbench/AGENT_MEMORY_PACKET/CURRENT_WORK_RU.md`
2. `blender-workbench/AGENT_MEMORY_PACKET/BLENDER_RULES_RU.md`
3. `blender-workbench/AGENT_MEMORY_PACKET/NEXT_STEPS_RU.md`
4. `blender-workbench/AGENT_MEMORY_PACKET/ARTIFACTS_INDEX_RU.md`
5. `blender-workbench/QUALITY_GATE.md`
6. `blender-workbench/REFERENCE_MATCHING.md`

Если задача касается рук, также прочитай:

```text
blender-workbench/AI_Blender_Agent_Hand_Patch_v5/00_start/START_HERE_RU.md
blender-workbench/AI_Blender_Agent_Hand_Patch_v5/01_agent_memory/PASTE_INTO_AGENT_PROMPT_RU.md
blender-workbench/RESEARCH_LOG_2026-06-23_HANDS.md
```

## Режим задачи

Перед Blender-задачей выбери один режим:

- `text/design` - 3D текст, серебро, логотипы, simple hero lettering.
- `shape reconstruction` - повторение объекта по референсу, силуэт, маски.
- `organic object` - рука, мягкая форма, sculpt-like object.
- `icon/hero object` - web-ready GLB hero asset.
- `GLB export` - экспорт/оптимизация уже готовой модели.

Для текущей нижней руки режим:

```text
shape reconstruction + organic object + icon/hero object
```

## Главная правда

Текущий лучший asset нижней руки:

```text
bottom_hand_result_v5
```

Он технически валиден, но визуально не принят как финал. Его нельзя называть production quality или 95% match.

Продолжай от `v5`, если пользователь явно не просит начать новую архитектуру.

## Нельзя

- Не выдавать плоскую маску/extrusion за настоящую 3D руку.
- Не делать пальцы одинаковыми трубками.
- Не строить руку "по смыслу" без сверки с референсом.
- Не прятать плохой силуэт материалами, bloom, тенями или камерой.
- Не говорить "готово", если нет render preview, web preview, validation report и честной самооценки.
- Не заставлять пользователя разбирать технические landmark board, если он просит просто результат.

## Обязательный цикл

1. Найди текущий asset и референс.
2. Определи один главный дефект.
3. Меняй только его.
4. Сохрани новый скрипт/GLB/render/report с новой версией.
5. Проверь front, 3/4 и side.
6. Проверь web route.
7. Сравни с референсом или с предыдущим лучшим render.
8. Если стало хуже - вернись к предыдущему лучшему asset.

