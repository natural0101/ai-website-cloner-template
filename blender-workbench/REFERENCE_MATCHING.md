# Reference Matching 3D

## Главный урок

Если нужно повторить объект "как на картинке", Blender сам по себе не решает задачу. Нужен процесс, в котором картинка становится измеримой спецификацией: силуэт, пропорции, порядок перекрытий, материалы, свет, камера и crop.

Сайт или PNG не дают реальные исходники 3D-модели. Они дают визуальный референс. Реальные исходники появляются только после реконструкции: `.blend`, GLB, materials, lights, camera, scripts.

## Разбор референса hands+sphere

Primary reference: `references/hands-sphere-primary.png`

Нужно удержать:

- белый/прозрачный icon-card background;
- зеленый шар почти по центру, видимый между пальцами;
- две оранжевые мягкие руки, верхняя обхватывает шар сверху, нижняя поддерживает снизу;
- розовые цилиндрические манжеты слева и справа;
- пластичный soft 3D / toy / clay material;
- фронтальный product-icon crop, без сложной перспективы;
- пальцы должны быть широкие, гладкие, сплющенные, с округлыми кончиками;
- тени мягкие, без жесткой грязи и без металлического блеска.

## Порядок работы

1. Сохранить reference в `references/`.
2. Сделать breakdown:
   - silhouette;
   - major color blobs;
   - occlusion order;
   - camera/aspect/crop;
   - material notes;
   - lighting notes.
3. Поставить reference image как camera background или reference plane.
4. До моделинга выбрать режим: `FRONT_2_5D`, `TRUE_360` или `HYBRID_HERO`.
5. Сначала попадать в front silhouette.
6. Потом добавлять depth.
7. Потом упрощать topology под GLB.
8. Каждый preview сравнивать overlay-скриптом или v3 `reference_preprocess.py compare`.

## Overlay command

```powershell
py -3.11 blender-workbench/scripts/compare_reference_overlay.py `
  --reference blender-workbench/references/hands-sphere-primary.png `
  --render blender-workbench/artifacts/renders/<render>.png `
  --out blender-workbench/artifacts/renders/<overlay>.png `
  --size 1024x768
```

Сохраняй stdout в JSON внутри `artifacts/reports/`.

## Как читать edge_iou

- Это не "процент красоты".
- Это быстрый показатель совпадения edge mask.
- Он помогает ловить регрессии.
- Визуальное решение всегда важнее одного числа.

Текущие baseline:

- `hands_sphere_icon_matched`: `edge_iou = 0.3069`
- `hands_sphere_icon_mask_relief`: `edge_iou = 0.3626`
- `hands_sphere_icon_v3_hybrid`: `mask_iou = 0.8658`, `boundary_f1 = 0.8661`
- `hands_sphere_icon_v4_organic`: latest holding-pose pass `edge_iou = 0.3647`, `mask_iou = 0.5785`, `boundary_f1 = 0.1556`

Значит новая итерация должна либо явно выглядеть лучше, либо поднимать метрику без ухудшения дизайна.

Важно: v4 organic нельзя сравнивать с v3 только по IoU. V3 выигрывает как front-layer relief, но проигрывает по representation: это не настоящая органическая скульптура. V4 правильнее как production 3D asset и текущая поза уже лучше показывает, что руки держат шар, но требует отдельного silhouette-fit pass:

- верхнюю руку сделать компактнее и ближе к reference: меньше palm/knuckle mass, точнее 2-3 dominant top fingers, больше V-shaped gaps;
- правую/нижнюю руку сделать чашей под шаром, а не равномерным fan;
- манжеты повернуть и скадрировать ближе к reference, но не возвращаться к плоским маскам;
- после каждого geometry pass делать `01_primitives -> 02_joined -> 03_smoothed -> 04_final` и overlay.

## Где искать стиль, если референса нет

Примеры, использованные как стиль/жанр для soft 3D icon:

- `https://www.iconfinder.com/icons/10296742/hand_holding_ball_finger_sport_gesture_touch_game_green_icon`
- `https://iconscout.com/3d-icons/hands-holding-planet`
- `https://iconscout.com/3d-illustrations/hand-holding-fruit`

Это только style references. Не копировать чужие лицензированные модели как исходники.

## Что улучшать дальше

- У верхней руки сделать более плоскую/компактную ладонь и точнее V-образные просветы между пальцами.
- У нижней руки сделать поддержку шара как мягкую чашу, а не отдельные tube-fingers.
- У манжет выдержать цилиндры с плоскими мягкими торцами, правильный угол и overlap.
- У шара сохранить чистую круглую форму, не давать пальцам закрыть слишком много центра.
- Снизить triangles у `mask_relief` ниже 60k без потери silhouette.
- Проверить GLB в web viewer, а не только в Blender render.
