# Silhouette review loop

## Цикл

1. Render только нужных объектов белым на чёрном.
2. Compare с reference mask при том же resolution.
3. Прочитать: IoU, boundary F1, holes, bbox, centroid.
4. Исправить одну категорию ошибки.
5. Повторить render/compare.

## Метрики

- `IoU`: общая площадь совпадения.
- `Boundary F1`: совпадение границы с tolerance 2–3 px.
- `Holes`: количество отверстий должно совпадать точно.
- `Centroid/bbox`: диагностируют camera/translation/scale.

## Практические gates

Для clean mask:

- ранний blockout: IoU ≥ 0.75;
- shape gate: IoU ≥ 0.85 и boundary F1 ≥ 0.90;
- строгий front‑matched relief: стремиться к IoU ≥ 0.90, но проверять визуально.

Числа не заменяют просмотр. При blur/soft edge измеряется выбранная binary mask, а не «истинная» граница.

## Запрещённый порядок

Не менять материал, roughness, HDRI или тени, когда не совпадает silhouette. Эти действия не исправляют геометрию.
