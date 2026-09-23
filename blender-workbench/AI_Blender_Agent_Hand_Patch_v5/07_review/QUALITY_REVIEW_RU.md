# Quality review

## Вывод

Патч нужен и не должен мешать обычным Blender-задачам при соблюдении activation policy `hands_only`.

## Что добавлено оправданно

1. Hand-target сочетает silhouette и внутреннюю структуру формы.
2. Hidden contour отделён от реально наблюдаемой геометрии.
3. Centerline-radius representation предотвращает случайные одинаковые tubes.
4. Canonical project-owned base уменьшает повторяемые ошибки агента.
5. Filled-mask IoU и tolerance-aware boundary F1 полезнее одиночного raw edge IoU.
6. Side clay gate запрещает принимать плоский relief как полноценную руку.
7. SOURCE/OUTPUT policy сохраняет редактируемость.
8. Target board переносит участие пользователя к одному подтверждению направления.

## Почему не добавлены новые MCP tools

Проблема находится в спецификации и порядке выполнения, а не в недостатке глобальных команд. Новые tools увеличили бы routing noise и могли бы активироваться в нерелевантных задачах.

## Изоляция

- skill активируется только для рук;
- Blender add-on не устанавливается;
- существующие text/design/shape workflows не изменяются;
- target-board scripts работают вне Blender;
- сторонние модели не загружаются;
- canonical base создаётся внутри проекта.

## Ограничения

1. Один референс не раскрывает настоящую заднюю сторону руки.
2. Target board не заменяет художественное решение скрытого объёма.
3. Пороги метрик требуют корректной reference mask.
4. Синтетический пример демонстрирует формат, а не готовую форму для конкретного референса.
5. Blender runtime geometry этим patch не тестируется, потому что патч не добавляет bpy-код.

## Проверка

- JSON Schema: проверен.
- Example hand-target: проверен.
- Semantic validator: пройден.
- Target-board generator: пройден.
- Skill frontmatter: проверен.
- Build-path hygiene: проверен.
- Новых MCP tools: `0`.
