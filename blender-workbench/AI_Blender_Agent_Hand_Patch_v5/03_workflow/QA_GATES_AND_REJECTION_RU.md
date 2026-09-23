# QA gates и отклонение

## Gate A — Target completeness

Результат отклоняется, если отсутствует хотя бы один обязательный landmark, centerline, hidden contour или layer order.

## Gate B — 2D silhouette

Рекомендуемые условия для чистого референса:

- filled-mask IoU ≥ 0.85;
- boundary F1 ≥ 0.90 при tolerance 3 px;
- landmark RMSE ≤ 3 px;
- число пальцев совпадает;
- число и положение negative spaces совпадает;
- occlusion entry/exit совпадают.

`edge_iou` не является gate без filled mask и tolerance-aware boundary metric.

## Gate C — Front 3D

После преобразования в объём фронтальные метрики не должны выйти за согласованный допуск.

Результат отклоняется, если remesh уничтожил fingertip, valley, thumb web или silhouette.

## Gate D — Volume

Результат отклоняется, если:

- side view выглядит как пластина;
- пальцы имеют одинаковую толщину;
- пальцы касаются ладони торцами;
- ладонь не имеет округлой передней и задней поверхности;
- скрытая часть ломает жест;
- thumb выглядит как пятый параллельный палец;
- cuff и wrist не соединены.

## Gate E — Surface

Результат отклоняется, если:

- видны pixel stair-steps;
- есть рваные края;
- есть non-manifold errors;
- есть self-intersections;
- normals направлены неверно;
- smoothing уничтожил negative spaces.

## Gate F — Delivery

Результат нельзя назвать готовым без:

- target board;
- front overlay;
- front clay render;
- side clay render;
- QA JSON;
- SOURCE `.blend`;
- OUTPUT `.blend`;
- GLB validation при web-delivery.

## Формат QA JSON

```json
{
  "status": "reject",
  "metrics": {
    "mask_iou": 0.82,
    "boundary_f1": 0.87,
    "landmark_rmse_px": 4.1
  },
  "failed_gates": ["B", "D"],
  "observations": [
    "little fingertip merged into ring finger",
    "side view is plate-like"
  ],
  "next_action": "adjust little-finger centerline and depth profile"
}
```

`status="accept"` разрешён только при прохождении всех активных gates.
