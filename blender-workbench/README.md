# Blender Workbench

Эта папка - рабочая память проекта по Blender/3D. Ее цель: любой следующий агент должен открыть этот каталог и сразу понять, что уже сделано, где артефакты, как подключиться к Blender MCP и как продолжать без угадываний.

## Быстрый старт

1. Открой `HANDOFF.md` - там текущее состояние и ближайшие шаги.
2. Открой `CURRENT_STATE.md` - там таблица активов, путей и известных проблем.
3. Перед любой доработкой открой `QUALITY_GATE.md` - там критерий "готово".
4. Для задач "повтори как на картинке" открой `REFERENCE_MATCHING.md`.
5. Если нужен полный контекст скилла, смотри `skill-snapshot/`.
6. Для hands/figures/single-image reconstruction смотри `shape-reconstruction-upgrade/` и `skill-snapshot/blender-shape-reconstruction/`.
7. Для любых новых Blender-задач сначала открой `AGENT_START_HERE.md`.

## Blender MCP

Blender MCP уже настроен на порт `9876`.

Проверка связи из корня репозитория:

```powershell
py -3.11 blender-workbench/scripts/blender_socket_call.py --type get_scene_info --params-json "{}"
```

Запуск Blender Python-скрипта через MCP:

```powershell
py -3.11 blender-workbench/scripts/blender_socket_call.py --type execute_code --code-file blender-workbench/scripts/blender_create_hands_sphere_icon_mask_relief.py
```

Если порт другой:

```powershell
$env:BLENDER_PORT="9876"
```

## Структура

```text
blender-workbench/
  artifacts/
    blend/            # Сохраненные .blend сцены
    exports/          # GLB для сайта/проверки
    renders/          # PNG preview и overlay
    reports/          # JSON-отчеты сцен, validation и overlay metrics
    reference_masks/  # Маски, извлеченные из референса hands+sphere
  references/         # Стабильные копии пользовательских/найденных референсов
  scripts/            # MCP helper, генераторы сцен, compare overlay
  skill-snapshot/     # Снимок Blender-скилла и ключевых рецептов
  shape-reconstruction-upgrade/ # V3: silhouette/mask/layer-stack/shape tools
  research-feedback-upgrade/ # V4: staged production, retrieval, structural QA, security
  notes/              # Свободные заметки, если появятся новые исследования
```

## Важное

- `artifacts/` - это snapshot внутри репо. Исторический внешний output root: `C:\Users\se-20\Documents\Codex\blender-agent-output`.
- Не считать PNG с сайта "исходником". Для 3D он только референс: геометрию, материалы, свет и камеру нужно восстанавливать отдельно.
- Для серебра/chrome простой серый материал не подходит. Нужны metallic material, roughness, contrast reflections, reflection cards/environment и проверка бликов.
- Для точного повтора иконки нужен reference-matching цикл: reference -> breakdown -> Blender scene -> render -> overlay -> metric -> iteration.
- Для одной картинки нельзя обещать честный 360. До моделинга выбирай `FRONT_2_5D`, `TRUE_360` или `HYBRID_HERO`.
- V4 включается для сложной формы, повторных провалов, multi-part assembly, reference matching или unusual lookdev. Простые задачи остаются на базовом workflow.
