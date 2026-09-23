# Рука по одному референсу: production workflow

## Stage 0 — Reference lock

1. Сохрани оригинальный файл без изменений.
2. Зафиксируй native resolution и crop.
3. Создай увеличенную рабочую копию только для разметки.
4. Установи ортографическую камеру.
5. Совмести frame с референсом.
6. Заблокируй camera transform.

## Stage 1 — Semantic reading

1. Назови руку и её роль в композиции.
2. Определи количество читаемых пальцев.
3. Определи жест.
4. Определи точки контакта или перекрытия с предметом.
5. Построй layer graph.
6. Отдели видимую геометрию от предполагаемой скрытой.

## Stage 2 — Target board

1. Разметь обязательные landmarks.
2. Построй centerlines.
3. Укажи radius profile.
4. Построй сглаженный visible contour.
5. Построй dashed hidden contour.
6. Отметь negative spaces.
7. Сохрани hand-target JSON.
8. Запусти validator.
9. Создай target board.
10. Получи от пользователя `верно` или `нет`.

## Stage 3 — Editable blockout

1. Возьми canonical project-owned hand base.
2. Создай базу с нуля, если её нет.
3. Поставь wrist axis.
4. Совмести palm center.
5. Подгони длины пальцев.
6. Подгони дуги centerlines.
7. Подгони radii.
8. Подгони thumb web.
9. Проверь negative spaces.
10. Сохрани SOURCE collection.

## Stage 4 — Front fit

1. Рендери белую маску без света и теней.
2. Downsample до native resolution.
3. Посчитай filled-mask IoU.
4. Посчитай boundary F1.
5. Посчитай landmark RMSE.
6. Исправь camera только при доказанной ошибке camera calibration.
7. Исправляй одну semantic mass за итерацию.
8. Не выполняй destructive union до прохождения gate.

## Stage 5 — Volume fit

1. Создай OUTPUT-дубликат.
2. Обеспечь overlap пальцев с ладонью.
3. Выполни union/remesh на OUTPUT.
4. Сохрани SOURCE без изменений.
5. Сгладь локально переходы.
6. Сохрани finger valleys.
7. Сохрани thumb web.
8. Проверь front mask повторно.
9. Рендери 3/4 clay view.
10. Рендери side clay view.

## Stage 6 — Surface and topology

1. Удали stair-step contour artifacts.
2. Удали самопересечения.
3. Проверь manifold state.
4. Проверь нормали.
5. Проверь толщину.
6. Проверь соединение руки и манжеты.
7. Сделай retopo только после утверждения формы.

## Stage 7 — Look development

1. Добавь материал после shape approval.
2. Настрой свет после shape approval.
3. Сравни shading отдельно от silhouette.
4. Не изменяй геометрию для копирования запечённого блика.

## Stage 8 — Delivery

1. Сохрани target board.
2. Сохрани overlay.
3. Сохрани front clay render.
4. Сохрани 3/4 clay render.
5. Сохрани side clay render.
6. Сохрани QA JSON.
7. Сохрани SOURCE `.blend`.
8. Сохрани OUTPUT `.blend`.
9. Экспортируй GLB после topology gate.
