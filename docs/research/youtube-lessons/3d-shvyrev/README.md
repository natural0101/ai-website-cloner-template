# База уроков 3D SHVYREV

Цель базы — не сохранить пересказы роликов, а превратить весь канал
`@3D_SHVYREV` в проверяемые улучшения Blender-процесса проекта.

## Охват

- 40 обычных видео.
- 197 Shorts.
- 237 уникальных публикаций суммарно.
- 237/237 публикаций имеют сохранённые storyboard-кадры: 1 350 страниц.
- 237/237 публикаций получили формализованный source finding:
  231 по транскрипту и 6 по визуальному разбору.
- Для 3 визуально просмотренных источников недостаточно доказательств, чтобы
  назначить точную воспроизводимую технику: `6GLHDS2vRd0`,
  `u9n5PJZMzLU`, `kvYqHYgHXSI`. Они классифицированы как
  `showcase_only`/`not_applicable`, а недостаток доказательств сохранён отдельно.
- 71 schema-valid нормализованная техника после topic-level канонизации.
- 441/441 кандидатная тема получила явное решение; для 308/308 применимых тем
  это `propose_new`, `map_existing`, `duplicate_supporting`,
  `defer_version_runtime` или `reject_noncanonical`.
- 338 упоминаний аддонов сведены в 301 нормализованную запись. Все остаются
  `inventory_only` до vendor/license/security/runtime проверки.
- `shvyrev_progressive_fidelity_passes` уже применена к v4 кота как
  staged blockout/refinement/presentation workflow; текущий проход рук также
  сохранён отдельным checkpoint и multi-view QA.
- Исходный каталог: `channel_catalog.json`, `channel_catalog.csv`,
  `channel_catalog.md`.
- Состояние получения доказательств: `coverage.json`, `coverage.md`.
- Очередь и итоги разбора: `source_reviews.json`, `source_reviews.md`,
  `source_findings.jsonl`, `missing_visual_or_audio.json`.
- Визуальное покрытие: `visual_coverage.json`.
- Topic-level решения и полнота:
  `topic_resolutions.jsonl`, `technique_coverage_audit.json`,
  `technique_coverage_audit.md`, `canonicalization_merge_report.json`.
- Инвентарь аддонов: `addon_inventory.json`, `addon_inventory.md`.
- Проверка возможностей установленного Blender 5.1:
  `blender-workbench/artifacts/reports/shvyrev_blender_5_1_runtime_capability_probe.json`
  и `blender-workbench/artifacts/reports/shvyrev_blender_5_1_builtin_runtime_test.json`.
  Transient fixture создал и удалил 15 тестовых наборов: 14 прошли, точный
  `CompositorNodeWhiteBalance` отсутствует в Blender 5.1.1 и остаётся
  version-gated; после cleanup не осталось тестовых datablocks.
- Единый список данных, которые могут понадобиться от пользователя:
  `missing_user_data.md`.

## Уровни достоверности

1. `CATALOGED` — ссылка и метаданные зафиксированы.
2. `TRANSCRIPT_REVIEWED` — речь просмотрена с таймкодами.
3. `VISUALLY_REVIEWED` — проверены необходимые кадры интерфейса/результата.
4. `EXTRACTED` — приём записан в воспроизводимом формате.
5. `RUNTIME_TESTED` — приём проверен в совместимой версии Blender.
6. `ADOPTED` — улучшение встроено в активный workflow, skill или QA.
7. `REJECTED` — приём устарел, неприменим, небезопасен или не подтвердился.

Транскрипт или красивый кадр сами по себе не считаются проверенным улучшением.

## Формат улучшения

Каждая запись должна содержать:

- источник, ID ролика и точные таймкоды;
- версию Blender и необходимые аддоны;
- задачу и ожидаемый результат;
- prerequisites;
- последовательность действий;
- существенные параметры и их допустимые диапазоны;
- способ проверки;
- типовые ошибки и исправления;
- влияние на текущий проект;
- статус проверки.

## Порядок обработки

1. Получить полный каталог без дублей.
2. Получить русские оригинальные/автоматические субтитры и превью.
3. Для роликов без достаточной речи выбрать опорные кадры.
4. Выделить законченные приёмы и убрать рекламу, повторы и развлекательные
   фрагменты без технической ценности.
5. Объединить дублирующие советы между Shorts и длинными уроками.
6. Сверить приём с текущей версией Blender и существующей базой примеров.
7. Проверить значимые изменения на чистой сцене.
8. Только после проверки переносить их в активные инструкции и
   `examples.jsonl`.
