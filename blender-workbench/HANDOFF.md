# Blender Handoff

## Контекст

Пользователь хочет, чтобы 3D-часть проекта стала воспроизводимой: не "я на глаз что-то сделал", а рабочий процесс, который можно передать другому агенту. Текущие задачи вокруг Blender:

- серебряная 3D-надпись Bite для лендинга;
- soft 3D icon "руки держат зеленый шар" по референсу;
- улучшение качества до уровня "похоже на референс", а не просто "по мотивам";
- web-ready экспорт GLB и PNG preview.

## Где подключаться

- Blender MCP: `127.0.0.1:9876`
- Проверка: `py -3.11 blender-workbench/scripts/blender_socket_call.py --type get_scene_info --params-json "{}"`
- Execute code: `py -3.11 blender-workbench/scripts/blender_socket_call.py --type execute_code --code-file blender-workbench/scripts/<script>.py`

## Внешние рабочие пути

- AI Blender Agent Kit: `C:\Users\se-20\Documents\Codex\AI_Blender_Agent_Kit`
- Активный Codex skill: `C:\Users\se-20\.codex\skills\blender-web-3d`
- Исторический output root: `C:\Users\se-20\Documents\Codex\blender-agent-output`
- Snapshot внутри репо: `blender-workbench/`

## V3 Shape Reconstruction

Добавлен пакет `AI_Blender_Agent_Kit_v3_shape_reconstruction`:

- установлен локальный Codex skill: `C:\Users\se-20\.codex\skills\blender-shape-reconstruction`;
- snapshot skill: `skill-snapshot/blender-shape-reconstruction/`;
- полный upgrade snapshot: `shape-reconstruction-upgrade/`;
- основной режим для hands+sphere: `HYBRID_HERO`, потому что один референс даёт точный фронт, но не честную заднюю геометрию.

## V4 Research Feedback

Добавлен v4 слой `research-feedback-upgrade/`. Он не заменяет базовый toolkit и v3 shape reconstruction; он включается для сложных Blender-задач и провалов:

- staged workflow: `INITIALIZATION -> GEOMETRY -> MATERIAL -> COMPOSITION -> LIGHTING -> EXPORT_QA`;
- scene graph с named parts, dimensions, expected contacts и acceptance criteria;
- example retrieval перед незнакомой геометрией/material code;
- structural QA для gaps/floating parts/contacts;
- security preflight перед arbitrary Python, local file ingestion, downloads или записью вне workbench/output roots.

В локальные Codex skills добавлены: `blender-staged-production`, `blender-structural-qa`, `blender-example-retrieval`, `blender-mcp-security`.

## V5 Hand Patch

Добавлен пакет `AI_Blender_Agent_Hand_Patch_v5/` из `pormt.zip`.

Обязательные стартовые файлы для задач руки:

- `AI_Blender_Agent_Hand_Patch_v5/00_start/START_HERE_RU.md`
- `AI_Blender_Agent_Hand_Patch_v5/01_agent_memory/PASTE_INTO_AGENT_PROMPT_RU.md`

Главное изменение процесса: при rejected hand нельзя продолжать "подкручивать" Blender-примитивы. Сначала нужен утверждённый 2D hand target board.

## Текущее состояние Bite

Серебряная 3D-надпись Bite уже есть как web asset:

- GLB snapshot: `artifacts/exports/bite_3d_logo.glb`
- Site copy: `public/models/bite_3d_logo.glb`
- Clean render: `artifacts/renders/bite_site_silver_logo_clean.png`
- Beauty render: `artifacts/renders/bite_site_silver_logo_beauty_view.png`
- Blend scenes:
  - `artifacts/blend/bite_site_silver_logo_clean.blend`
  - `artifacts/blend/bite_site_silver_logo_beauty_view.blend`

Статус: годится как рабочий hero-актив, но при следующей итерации нужно проверять chrome/silver по рецептам из `skill-snapshot/style-recipes/`, а не возвращаться к плоскому серому материалу.

## Текущее состояние hands+sphere

Основной референс сохранен стабильно:

- `references/hands-sphere-primary.png`
- full-scene audit: `AUDIT_2026-06-22_HANDS_SPHERE.md`

Есть три ветки:

| Asset | Роль | Triangles | Overlay edge_iou | Статус |
|---|---:|---:|---:|---|
| `hands_sphere_icon` | первая 3D-попытка | 52 408 | не актуально | concept only |
| `hands_sphere_icon_matched` | web-friendly, без validation warnings | 54 932 | 0.3069 | лучше для GLB-бюджета |
| `hands_sphere_icon_mask_relief` | ближе к силуэту референса | 77 504 | 0.3626 | ближе визуально, но over budget |
| `hands_sphere_icon_v3_hybrid` | V3 layer-stack HYBRID_HERO | 57 080 | mask_iou 0.8658 | чистый GLB, лучше shape pipeline, не true 360 |
| `hands_sphere_icon_v4_organic` | V4 real organic primitives + voxel-union hands | 88 102 | edge_iou 0.3647 / mask_iou 0.5785 | текущий holding-pose asset для web, но не 95% reference-match |

Важно: ни одну hands+sphere ветку нельзя называть "95% готово". Они полезны как база, но текущая проблема - недостаточно точная форма кистей/пальцев, depth layering, cuff angles, side view и soft toy lighting.

V3 HYBRID уже проходит web-export без errors, но это всё ещё front-relief reconstruction, а не полноценная скульптура руки. Closed-mesh diagnostic ожидаемо ругается на boundary edges у 2.5D contour layers.

V4 ORGANIC после rejection v3:

- script: `scripts/blender_create_hands_sphere_v4_organic.py`
- blend: `artifacts/blend/hands_sphere_icon_v4_organic.blend`
- GLB: `artifacts/exports/hands_sphere_icon_v4_organic.glb`
- site copy: `public/models/hands_sphere_icon_v4_organic.glb`
- live pages: `/organic-icon`, `/silver-landing`
- renders:
  - `artifacts/renders/hands_sphere_icon_v4_organic_01_primitives.png`
  - `artifacts/renders/hands_sphere_icon_v4_organic_02_joined_form.png`
  - `artifacts/renders/hands_sphere_icon_v4_organic_03_smoothed_form.png`
  - `artifacts/renders/hands_sphere_icon_v4_organic_04_final_front.png`
  - `artifacts/renders/hands_sphere_icon_v4_organic_05_final_front_3q.png`
  - `artifacts/renders/hands_sphere_icon_v4_organic_06_final_side.png`
- reports:
  - `artifacts/reports/hands_sphere_icon_v4_organic_scene_graph.json`
  - `artifacts/reports/hands_sphere_icon_v4_organic_scene_report.json`
  - `artifacts/reports/hands_sphere_icon_v4_organic_structural_qa.json`
  - `artifacts/reports/hands_sphere_icon_v4_organic_silhouette_metrics.json`
  - `artifacts/reports/hands_sphere_icon_v4_organic_overlay_metrics.json`

V4 fixes the user's core complaint better than the earlier pass: hands are no longer flat masks and the current pose visibly holds the green sphere. Final export objects are separate semantic pieces: green sphere, left hand, right hand, left cuff, right cuff. Hands are built from palm ellipsoid + unequal finger capsules + thumb + wrist, then voxel-unioned into smooth closed meshes. Do not pitch v4 as 95% reference-match: the silhouette gate still fails, the side view is weak, and the top/lower hand shapes still need a dedicated silhouette-fit sculpt pass.

## Part-by-part recovery

The full object should not be repaired as one monolithic scene. Continue by accepting one part at a time.

Part 01:

- asset: `green_sphere_part_v1`
- script: `scripts/blender_create_green_sphere_part.py`
- GLB: `artifacts/exports/green_sphere_part_v1.glb`
- site copy: `public/models/green_sphere_part_v1.glb`
- web preview: `/sphere-part`
- render: `artifacts/renders/green_sphere_part_v1_02_final_front.png`
- report: `artifacts/reports/green_sphere_part_v1_scene_report.json`
- validation: 5 040 triangles, 0 errors, 0 warnings.
- status: technical pass; wait for user verdict before modeling hands.

Part 02:

- asset: `bottom_hand_part_v1`
- script: `scripts/blender_create_bottom_hand_part.py`
- GLB: `artifacts/exports/bottom_hand_part_v1.glb`
- site copy: `public/models/bottom_hand_part_v1.glb`
- web preview: `/bottom-hand-part`
- renders:
  - `artifacts/renders/bottom_hand_part_v1_01_primitives.png`
  - `artifacts/renders/bottom_hand_part_v1_04_final_front_with_guide.png`
  - `artifacts/renders/bottom_hand_part_v1_05_final_front_hand_only.png`
  - `artifacts/renders/bottom_hand_part_v1_06_final_front_3q.png`
  - `artifacts/renders/bottom_hand_part_v1_07_final_side.png`
- report: `artifacts/reports/bottom_hand_part_v1_scene_report.json`
- validation: 32 544 triangles, 0 errors, 0 warnings.
- latest pass: lower finger-base cleanup. Added `BHP_FingerBaseBlend` and `BHP_LowerFingerBlend`, pushed finger starts deeper into the palm mass, and widened the transition zone to reduce crooked/tube-like bases.
- status: rejected visually by user. Do not continue with final Blender geometry from this candidate.

V5 bottom-hand target proposal:

- folder: `artifacts/reference_masks/bottom_hand_target_v1/`
- target JSON: `hand_target.json`
- board: `hand_target_board.png`
- overlay: `hand_target_overlay.png`
- validation: `hand_target_validation.json`
- readable landmarks: `landmarks.md`
- validation status: pass
- counts: 16 landmarks, 7 centerlines, 5 layers, 3 negative spaces
- warning: full JSON Schema validation was skipped because `jsonschema` is not installed in Python 3.11.

This board is internal target evidence. It was originally meant to be shown for a `верно` / `нет` verdict, but the user later clarified: "я не разбираюсь мне нужен результат". Do not force the user to reason about technical landmarks; the agent must own the visual critique and only ask for a simple visual verdict when necessary.

Current lower-hand working replacement:

- asset: `bottom_hand_result_v5`
- script: `scripts/blender_create_bottom_hand_result_v5.py`
- GLB: `artifacts/exports/bottom_hand_result_v5.glb`
- site copy: `public/models/bottom_hand_result_v5.glb`
- blend: `artifacts/blend/bottom_hand_result_v5.blend`
- web preview: `/bottom-hand-part`
- page component now loads `bottom_hand_result_v5.glb`
- validation: 28 324 triangles, 0 errors, 0 warnings
- key modeling changes:
  - v3 replaced lumpy metaball fingers with controlled smooth tapered tube meshes plus separate tip caps.
  - v4 used `hand_target.json` centerlines/radii directly; this was technically clean but visually too fan-like.
  - v5 keeps target fingertip landmarks while tucking hidden roots into a compact palm cup; wrist/cuff contact is now `OVERLAP`.
- visual status: best current lower-hand candidate, but not accepted/final and not 95% reference-match. The next pass should improve fingertip readability without losing the compact palm cup.

Research/training notes from the autonomous learning pass:

- `RESEARCH_LOG_2026-06-23_HANDS.md`

LL3M note: `https://threedle.github.io/ll3m/#` was checked as a process reference, not as a live production generator. Its useful pattern for this project is planner/code/render/critic iteration; the local source of truth remains the staged Blender scripts, PNG renders, `.blend`, GLB and validation reports.

## Основная проблема

Плохой результат появился не из-за отсутствия Blender как инструмента, а из-за неверного процесса:

1. Референс был воспринят как общая идея, а не как жесткая спецификация.
2. Не был сразу построен разбор: силуэт, occlusion order, пропорции, crop, материалы, освещение.
3. Не было обязательного overlay/edge сравнения после каждого рендера.
4. Для 95% похожести нужно сначала попасть во front-view silhouette, а уже потом делать объем и web export.

Если пользователь говорит "похоже на 95%", агент обязан работать через `REFERENCE_MATCHING.md`, а не через свободную фантазию.

## Следующие правильные шаги

1. Открыть `REFERENCE_MATCHING.md` и `QUALITY_GATE.md`.
2. Проверить Blender MCP через `get_scene_info`.
3. Если сцена не пустая и будут существенные изменения, сделать checkpoint.
4. Для hands+sphere organic production продолжать от `scripts/blender_create_hands_sphere_v4_organic.py`. Для silhouette-only studies можно смотреть v3 masks/layer stack, но не выдавать relief как органический 3D.
5. Сохранить новый PNG в `artifacts/renders/`.
6. Сравнить с референсом:

```powershell
py -3.11 blender-workbench/scripts/compare_reference_overlay.py `
  --reference blender-workbench/references/hands-sphere-primary.png `
  --render blender-workbench/artifacts/renders/<new-render>.png `
  --out blender-workbench/artifacts/renders/<new-overlay>.png `
  --size 1024x768
```

7. Сохранить JSON метрики в `artifacts/reports/`.
8. Запускать GLB export только после validation без errors.
9. Если triangles больше 60k для иконки, записать warning и отдельно решить: optimize или принять качество.

## Нельзя

- Нельзя делать reset сцены без явного подтверждения пользователя.
- Нельзя удалять старые объекты без checkpoint.
- Нельзя выдавать screenshot/PNG за "исходники сайта".
- Нельзя считать плоский grey material серебром.
- Нельзя говорить "готово", если есть только GLB без PNG preview, overlay и validation report.
