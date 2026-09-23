# Target modes

- `FRONT_2_5D`: одна фиксированная камера; contours/layers/extrusion; бок и back не являются целью.
- `TRUE_360`: semantic primitives + multiview volume design; single reference constrains only observed view.
- `HYBRID_HERO`: front match + ограниченный camera orbit, обычно ±10–20°.

Сначала зафиксируй mode, reference resolution, camera type, GLB/animation need и triangle budget. Для одного изображения hidden surfaces записывай как assumptions.
