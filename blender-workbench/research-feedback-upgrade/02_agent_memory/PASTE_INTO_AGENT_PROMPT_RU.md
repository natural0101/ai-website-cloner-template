## Complex Blender staged mode

Активируй этот режим только для сложной формы, reference matching, нескольких связанных частей, сложного lookdev или после первой неудачной попытки.

1. Сначала выполни read-only inspection и Blender capability probe.
2. Создай scene graph с именованными parts, dimensions, relations и expected contacts.
3. Работай этапами: INITIALIZATION → GEOMETRY → MATERIAL → COMPOSITION → LIGHTING → EXPORT_QA.
4. На каждом этапе меняй только разрешённый тип данных.
5. После одной целевой правки сделай canonical renders и stage-specific checklist.
6. Не исправляй несколько независимых дефектов одним большим скриптом.
7. Geometry готова только после silhouette/profile и structural audit; фронтального render недостаточно.
8. Храни authoritative current state и максимум 5 последних попыток.
9. Перед нестандартной операцией вызови retrieval по проверенным examples.
10. При API mismatch не угадывай: остановись, inspect version/capability и выбери совместимый action.
11. Не читай/пиши вне output_root и reference_roots; network/external generators выключены по умолчанию.
12. Результат готов только после visual + structural + export validation.
