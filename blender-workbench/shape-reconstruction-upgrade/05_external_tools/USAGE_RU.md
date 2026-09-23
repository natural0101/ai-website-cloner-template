# Использование reference_preprocess.py

## Mask → contour JSON

```bash
python reference_preprocess.py extract object_mask.png object.contours.json \
  --epsilon-ratio 0.002 \
  --minimum-reconstruction-iou 0.985 \
  --output-reconstructed object.reconstructed.png
```

Tool сохраняет hierarchy и holes. Если упрощение слишком грубое, epsilon автоматически уменьшается.

## Blender silhouette → compare

```bash
python reference_preprocess.py compare reference_mask.png blender_mask.png report.json \
  --tolerance-px 3 \
  --world-height 4.0 \
  --gate-iou 0.85 \
  --gate-boundary-f1 0.90 \
  --overlay overlay.png \
  --difference difference.png
```

По умолчанию alignment=`none`: camera/transform ошибки остаются видимыми.

Диагностический alignment:

```bash
--alignment bbox-uniform
```

Не использовать aligned score как финальное доказательство: он скрывает ошибку масштаба/позиции.

## Цвет масок

Foreground должен быть белым, background чёрным. Для тёмного объекта используйте `--invert`.
