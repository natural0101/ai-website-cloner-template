# Подготовка масок

## Приоритет источника

1. Оригинальный alpha channel.
2. Ручная маска, проверенная человеком.
3. Segmentation model с ручной коррекцией.
4. Цветовой threshold только для действительно плоской графики.

## Отдельные маски

Создавать минимум одну mask на семантическую часть, если части перекрываются:

- `core.png`;
- `left_hand.png`;
- `right_hand.png`;
- `cuff.png`;
- `combined.png` для общей silhouette‑метрики.

## Запрещено

- извлекать форму непосредственно из блика;
- закрывать отверстия morphology без проверки;
- сглаживать contour, если после этого теряются пальцы или negative space;
- сравнивать RGB render с RGB reference до совпадения silhouette.

## Контроль

`reference_preprocess.py extract` автоматически уменьшает simplification epsilon, пока reconstruction IoU не достигнет заданного порога, и сохраняет contour hierarchy для отверстий.
