# Карточка разбора референса

Заполнить до моделирования. Не оставлять цель неявной.

```yaml
asset_name: ""
reference_path: ""
reference_resolution: [0, 0]
reference_has_alpha: false

mode: "FRONT_2_5D | TRUE_360 | HYBRID_HERO"
main_camera:
  type: "ORTHO | PERSPECTIVE"
  exact_resolution_required: true
  allowed_orbit_degrees: 0

usage:
  glb_for_web: true
  animation_required: false
  deformation_required: false
  max_triangles: 80000

observed_parts:
  - name: ""
    primitive_guess: "ELLIPSOID | ROUNDED_BOX | TUBE | CONTOUR | CUSTOM"
    front_of: []
    behind: []
    symmetry: "NONE | MIRROR_X | APPROXIMATE"

silhouette_landmarks:
  - name: ""
    pixel_xy: [0, 0]
    meaning: "tip | valley | contact | corner | tangent"

negative_spaces:
  expected_holes: 0
  critical_gaps: []

hidden_geometry_policy:
  source: "USER_REFERENCE | CATEGORY_PRIOR | DESIGN_ASSUMPTION"
  assumptions: []

quality_targets:
  mask_iou_min: 0.85
  boundary_f1_min: 0.90
  boundary_tolerance_px: 3
  required_views: ["FRONT"]

open_questions: []
```

## Правила заполнения

- Для маленького размытого изображения не повышать численные target автоматически.
- Если `TRUE_360`, добавить `LEFT`, `RIGHT`, `BACK`, `THREE_QUARTER` в required views.
- Если прозрачности нет, не считать цветовую threshold‑маску надёжной без ручной проверки.
- Любая придуманная скрытая поверхность должна попасть в `hidden_geometry_policy.assumptions`.
