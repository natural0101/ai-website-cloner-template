# Проверенные примеры

`examples.jsonl` содержит метаданные и пути, а не дублирует большие скрипты.

Статусы:

- `RUNTIME_TESTED`: в исходном kit сохранены реальные Blender outputs/reports.
- `STATIC_ONLY`: код/recipe прошёл только статическую проверку в этом обновлении.
- `RESEARCH_PATTERN`: архитектурный паттерн; требует первого runtime запуска в вашей Blender.

Запуск поиска:

```bash
python retrieval_index.py examples.jsonl "stylized hand sphere floating fingers" --top-k 3
```
