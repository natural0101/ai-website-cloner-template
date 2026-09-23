# Blender Shorts Lifehack Log

Цель: постепенно разобрать примерно 1000 Blender Shorts и превратить их в короткую рабочую базу приемов для следующих Blender-сцен.

## Правило разбора

1. Нумерация идет в локальном порядке просмотра/разбора: `001`, `002`, `003`...
2. В `shorts-queue.md` попадает источник, тема, статус и короткая выжимка.
3. В `lifehacks.md` попадает только прием, который можно реально применить в сцене, скрипте, lookdev, анимации или web-экспорте.
4. Если доступен только заголовок/описание, статус остается `queued` или `metadata-reviewed`; такой ролик не считается полноценно выученным.
5. Лицензионный арт, персонажи, логотипы и платные наборы не копируются. Забирается только общий производственный прием.

## Статусы

| Статус | Значение |
|---|---|
| `applied` | Прием уже использован в сцене или коде |
| `reviewed` | Прием разобран и превращен в lifehack |
| `metadata-reviewed` | Есть надежная идея из заголовка/сниппета, но нужен визуальный повторный просмотр |
| `queued` | Источник добавлен в очередь |
| `needs-test` | Прием надо прогнать в Blender на маленькой сцене |

## Файлы

- `shorts-queue.md` - очередь источников до цели 1000.
- `lifehacks.md` - сжатые приемы, которые надо использовать в будущих Blender задачах.
- `session-001.md` - первая партия после JoJo cards сцены.
- `session-002.md` ... `session-019.md` - последующие партии и checkpoint test-assets.

Текущий прогресс: 1000 источников занесены в очередь, 359 приемов сформулированы, 308 приемов уже применены в Blender-сценах или test-ассетах.

Целевой счетчик `1000` достигнут. `metadata-reviewed` источники остаются помеченными для будущего полного визуального ревизита, если потребуется углубленный повторный просмотр.

Последний test-asset: `blender_shorts_lifehack_lab_v18`.

- применяет `BH-340` ... `BH-359`;
- validation: `0 errors`, `0 warnings`, `19,086` triangles, 116 exportable objects, 6 animated roots;
- exact GLB helper leaks: `0`;
- GLB: `artifacts/exports/blender_shorts_lifehack_lab_v18.glb`;
- site copy: `public/models/blender_shorts_lifehack_lab_v18.glb`;
- blend: `artifacts/blend/blender_shorts_lifehack_lab_v18.blend`;
- preview: `artifacts/renders/blender_shorts_lifehack_lab_v18_preview_frame_024.png`.
