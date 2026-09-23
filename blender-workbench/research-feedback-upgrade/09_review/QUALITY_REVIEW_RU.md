# Ревью качества v4

## Что добавлено обоснованно

- Staged isolation подтверждается несколькими независимыми research directions и напрямую устраняет смешивание geometry/material/light.
- Read-only vs mutation separation снижает риск случайных изменений при inspection.
- Bounded memory предотвращает накопление неудачных попыток.
- Example retrieval полезнее огромного prompt и не требует fine-tuning.
- Structural QA закрывает recurring failure “красиво спереди, но части висят”.
- Capability probe адресует API mismatch.
- Security preflight адресует реальные риски local paths/arbitrary code.

## Почему это не мешает агенту

1. Всё v4 optional и включается только на сложных задачах.
2. В prompt добавлено 12 коротких правил, а не мировая база источников.
3. Retrieval возвращает максимум 5 records.
4. Новых MCP contracts только четыре, три из них read-only.
5. Нет новых обязательных dependencies.
6. Нет автозагрузки vendor code, моделей или видео.
7. Нет обещания, что heuristic QA заменяет Blender artist review.

## Измеренные проверки v4

- 4/4 pure-Python unit tests: PASS.
- 6/6 новых Python-файлов: AST/syntax PASS.
- 32 research sources: уникальные ID, HTTPS и согласованные CSV/JSON.
- 11 example records: schema/evidence labels/source paths проверены.
- 4 optional MCP contracts: уникальные имена; 3 read-only, 1 state mutation.
- Все v4 entry points и referenced files существуют.
- Package namespace collisions: 0.
- Generated caches/build paths в release: 0.

Машиночитаемый отчёт: `STATIC_VALIDATION.json`; общий package report: `../../demo_outputs/package_validation.json`.

## Честная граница проверки

Новые pure-Python modules проверены локально автоматическими тестами и статической компиляцией. JSON/CSV/JSONL и manifests проверены. Blender-specific v4 modules прошли Python syntax/AST validation, но в текущем контейнере нет Blender executable, поэтому их новый runtime test не выполнялся. Архив сохраняет реальные Blender 5.1.2 runtime artifacts v3; для v4 предусмотрен `FIRST_RUNTIME_CHECK_RU.md`.

## Решение

Добавление рекомендуется. Оно уменьшает хаос и не раздувает стандартный context при соблюдении activation policy.
