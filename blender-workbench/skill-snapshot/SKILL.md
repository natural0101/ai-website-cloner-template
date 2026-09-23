---
name: blender-web-3d
description: Creates and reviews Blender 5.1 web-ready 3D assets through MCP, including plasticine/clay text, rounded icons, organic blobs, tube-based custom forms, PBR materials, lighting, camera framing, PNG previews, validation and GLB export. Use for Blender modeling, 3D typography, website 3D, GLB/glTF, procedural shapes, scene repair or export verification.
license: MIT
metadata:
  version: "1.0.0"
  language: "ru"
---

# Blender Web 3D

## Цель

Создавать 3D‑объекты не одноразовым монолитным скриптом, а контролируемым циклом с измеряемым состоянием, превью, проверкой и экспортом.

## Перед началом

1. Прочитай `references/agent-system-prompt-ru.md`.
2. Прочитай `references/tool-catalog.md`.
3. Определи режим задачи: `text/design`, `shape reconstruction`, `organic object`, `icon/hero object`, `GLB export`.
4. Найди подходящий skill/workflow: базовый `blender-web-3d`, `blender-shape-reconstruction`, `blender-staged-production`, `blender-structural-qa`, `blender-example-retrieval` или `blender-mcp-security`.
5. Вызови `scene.inspect`.
6. При непустой сцене и существенных изменениях вызови `scene.checkpoint`.
7. Не выполняй reset без явного подтверждения пользователя.
8. Не используй MCP как «просто выполнить случайный bpy-код»: сначала ищи tool/action/workflow из AI Blender Agent Kit.

## V4 Research Feedback Routing

Для сложной формы, repeated failures, multi-part assemblies, reference matching, unusual lookdev или сомнений в API активируй v4-слой:

- staged production: `blender-staged-production`;
- structural contacts/gaps/floating parts: `blender-structural-qa`;
- неизвестный geometry/material паттерн или первая неудача: `blender-example-retrieval`;
- arbitrary Python, local file ingestion, downloads, внешние сервисы или запись вне output root: `blender-mcp-security`.

Работай этапами `INITIALIZATION → GEOMETRY → MATERIAL → COMPOSITION → LIGHTING → EXPORT_QA`. После каждого этапа делай render/overlay/inspection. Если результат хуже, возвращайся к checkpoint/лучшей попытке, а не наслаивай хаотичные правки.

## Design Upgrade

Для задач с референсом, сайтом, hero-ассетом, цветом, материалом, серебром/chrome, liquid metal, brushed silver, clay, puffy/bubble, acrylic/glass:

1. Прочитай `design_upgrade/00_agent_memory/PASTE_INTO_AGENT_PROMPT_RU.md`.
2. Прочитай `design_upgrade/01_design_reference_system/TERMS_AND_TAXONOMY_RU.md`.
3. Выбери один рецепт из `design_upgrade/02_style_recipes/`.
4. Для chrome/silver обязательно используй reflection cards или web environment/reflections; простой серый материал не является серебром.
5. Используй `design_upgrade/03_blender_tools/design_tools.py` как высокоуровневый API, если базового dispatcher action недостаточно.
6. После рендера прочитай и пройди `design_upgrade/05_checklists/VISUAL_REVIEW_CHECKLIST_RU.md`.
7. Перед финалом проверь не только GLB, но и текущую Blender-сцену: в viewport/render/export не должно быть случайных старых объектов, тестовых ассетов или дублей.

## Выбор процедуры

- Пластилиновые буквы, 3D‑слово, логотип: прочитай `references/plastic-text.md`.
- Мягкая иконка, blob, rounded box, линия или контур по точкам: прочитай `references/soft-shapes.md`.
- Повторить объект/иконку по картинке или найденному референсу: прочитай `references/reference-matching-3d.md`.
- Материал, свет, камера или композиция: прочитай `references/materials-light-camera.md`.
- GLB, треугольники, topology, web‑доставка: прочитай `references/validation-export.md`.
- Ошибка, плохой рендер, rollback: прочитай `references/failure-recovery.md`.
- Настройка MCP‑адаптера: прочитай `references/mcp-integration.md`.
- Серебро/chrome: прочитай `design_upgrade/02_style_recipes/CHROME_SILVER_LETTERS_RU.md`.
- Brushed/satin silver: прочитай `design_upgrade/02_style_recipes/BRUSHED_SILVER_RU.md`.
- Liquid metal/Y2K: прочитай `design_upgrade/02_style_recipes/LIQUID_METAL_Y2K_RU.md`.
- Website 3D hero: прочитай `design_upgrade/02_style_recipes/WEBSITE_HERO_3D_EXPORT_RU.md`.

## Reference Matching

Если пользователь говорит «как на картинке», «повтори», «похоже/не похоже», «95%», или если референса нет, но стиль должен быть узнаваемым:

1. Используй предоставленную картинку как primary reference; если картинки нет, найди 3–6 похожих референсов сам.
2. Не начинай моделить, пока не выписаны силуэт, пропорции, occlusion order, палитра, материал, камера и crop.
3. В Blender обязательно поставь reference image как camera background или reference plane.
4. Делай preview-render и сравнение с референсом через overlay/edge-mask. Для этого можно использовать `scripts/compare_reference_overlay.py`.
5. Не называй результат готовым, если он только «по мотивам». Продолжай итерации или явно перечисли оставшиеся расхождения.

## Рабочий цикл

1. Inspect.
2. Краткий план.
3. Один workflow либо 1–3 атомарных actions.
4. Inspect.
5. Studio + camera frame.
6. Render preview.
7. Визуальная проверка.
8. Локальная правка.
9. Validate.
10. Export GLB и сохранить `.blend`.

## Приоритет действий

1. Для стандартной задачи используй готовый workflow.
2. Для локальных правок используй semantic actions.
3. Пиши произвольный `bpy`‑код только при отсутствии нужной операции.
4. После произвольного кода обязательно повтори inspect, render и validate.

## Обязательная визуальная проверка

Проверь:

- читаемость текста;
- узнаваемый силуэт;
- отсутствие пересечений и случайных объектов;
- достаточное скругление без потери формы;
- светлые и тёмные области без клиппинга;
- центрирование и заполнение кадра;
- соответствие материала стилю;
- для chrome/silver: metallic/roughness, edge highlights, чёрно-белые reflection bands, web environment;
- отсутствие preview floor/camera/lights в GLB.

## Definition of done

Не объявляй задачу завершённой, пока:

- `asset.validate` не содержит errors;
- PNG существует и просмотрен;
- GLB существует и имеет ненулевой размер;
- `.blend` сохранён;
- указан triangle count;
- `scene.inspect` или scene report подтверждает, что случайные старые объекты скрыты/не экспортируются;
- пользователю перечислены оставшиеся warnings.
