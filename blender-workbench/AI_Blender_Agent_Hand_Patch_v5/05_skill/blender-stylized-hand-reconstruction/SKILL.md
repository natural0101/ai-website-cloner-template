---
name: blender-stylized-hand-reconstruction
description: Reconstructs stylized hands, fingers, cuffs, and hand-object interactions from a single image using a locked camera, semantic landmarks, visible and hidden contours, centerline-radius targets, a reusable project-owned hand base, silhouette metrics, and clay multiview rejection gates. Use only for hands or organic limbs. Do not activate for text, materials, lighting, or generic hard-surface objects.
license: MIT
compatibility: Blender 5.1.x through Python/MCP; target-board utilities run outside Blender with Pillow.
metadata:
  version: "1.0.0"
  language: "ru"
  activation: "hands_only"
---

# Blender Stylized Hand Reconstruction

## Сначала прочитать

1. `../../01_agent_memory/PASTE_INTO_AGENT_PROMPT_RU.md`.
2. `../../02_spec/HAND_TARGET_SPEC_RU.md`.
3. `../../03_workflow/HAND_FROM_SINGLE_REFERENCE_RU.md`.
4. `../../03_workflow/QA_GATES_AND_REJECTION_RU.md`.

## Обязательный режим

Объяви один режим:

- `FRONT_MATCHED`;
- `HYBRID_HERO`;
- `TRUE_360`.

Не называй скрытую сторону восстановленной из одного изображения.

## Первый gate

До финального Blender mesh должны существовать:

- hand-target JSON;
- target board PNG;
- validation JSON;
- пользовательское подтверждение target board.

## Представление руки

Используй одновременно:

- visible contour;
- hidden inferred contour;
- landmarks;
- centerlines;
- radius profile;
- depth profile;
- layer graph.

Silhouette без centerlines не является достаточной спецификацией.

## Моделирование

1. Предпочитай canonical project-owned hand base.
2. Храни SOURCE и OUTPUT отдельно.
3. Подгоняй pose до union.
4. Вводи finger roots в palm mass.
5. Сохраняй finger valleys и thumb web.
6. Выполняй destructive remesh только над OUTPUT.
7. Возвращай front fit после каждого volume change.
8. Используй clay renders до shape approval.

## Проверка

- filled-mask IoU;
- boundary F1 с tolerance;
- landmark RMSE;
- negative-space check;
- front clay;
- 3/4 clay;
- side clay;
- topology audit.

## Запреты

- raw raster contour → final extrusion;
- одинаковые параллельные finger tubes;
- оценка одним edge IoU;
- материал до shape gate;
- заявление «готово» без QA JSON;
- просьба пользователю вручную выполнять разметку до собственной попытки агента;
- потеря SOURCE после union.

## Definition of done

- target board утверждён;
- camera locked;
- semantic hand structure полна;
- active gates пройдены;
- front silhouette не рваный;
- side view не plate-like;
- SOURCE сохранён;
- OUTPUT проверен;
- отчёт не скрывает допущения.
