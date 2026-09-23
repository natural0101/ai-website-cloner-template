# AI Blender Agent — Lookdev & Lighting Patch v6

Патч учит агента доводить уже собранную Blender-сцену до production-ready вида: геометрическая детализация, физически правдоподобные PBR-материалы, световая иерархия, экспозиция, диагностические рендеры и проверка соответствия GLB/web-viewer.

## Когда активировать

Только после утверждения основных форм, пропорций, камеры и композиции. Патч не должен вмешиваться в этап реконструкции силуэта или моделирования рук.

## Порядок чтения агентом

1. `00_start/START_HERE_RU.md`
2. `01_agent_memory/PASTE_INTO_AGENT_PROMPT_RU.md`
3. `02_diagnosis/CURRENT_SCENE_REVIEW_RU.md`
4. `03_workflow/PRODUCTION_LOOKDEV_PIPELINE_RU.md`
5. `04_recipes/GAS_STATION_SCENE_RECIPE_RU.md`
6. `06_skill/blender-production-lookdev/SKILL.md`

## Что внутри

- разбор текущего кадра с объективной проверкой клиппинга;
- staged workflow: geometry → materials → lighting → render → web parity;
- рецепты света и материалов;
- Blender Python helpers без удаления пользовательской сцены;
- read-only scene audit;
- PNG-аудит экспозиции;
- отдельная инструкция для GLB/Three.js;
- QA-gates и критерии отклонения результата.

## Установка

Распаковать рядом с остальными пакетами агента. Никаких Blender add-on устанавливать не нужно. Скрипты запускаются через MCP `execute_blender_code` или Blender Text Editor.

Для `image_quality_audit.py` используется существующее внешнее Python/OpenCV-окружение. Новый системный софт не требуется.
