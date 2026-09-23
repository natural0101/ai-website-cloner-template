# FRONT_2_5D: точное совпадение с главной камерой

## Pipeline

1. Получить clean mask каждой перекрывающейся части.
2. Выполнить `reference_preprocess.py extract`.
3. Зафиксировать reference resolution и ортографическую camera.
4. Импортировать contour JSON с `shape.import_contours`.
5. Задать `depth_y`, thickness и bevel для каждой части в layer stack.
6. Render silhouette с тем же resolution.
7. Выполнить `compare`; сначала без автоматического alignment.
8. Исправить camera/framing, затем общий transform, затем локальный contour.
9. Проверить holes/negative space.
10. После shape gate добавить материал и свет.

## Ограничения

- Это объёмный рельеф, а не доказанная задняя геометрия.
- Сильный bevel меняет silhouette; для первичной проверки использовать `bevel=0`.
- В Layer Stack более отрицательный Y находится ближе к reference camera.
- Нельзя оценивать форму по RGB, пока silhouette не прошла gate.
