# TeamON frozen KB batch: server-only contract

This complements the existing One/Codex and native-copy contract; current owner instructions have priority.

## Серверная серия: frozen authority, упаковка и semantic QA — 07.10.2026

### Источник и формат

- До сборки объявить exact frozen ordered pages, их SHA и sourceDigest. Supplemental
  HTTP/rendered/mobile архивы сохранять, но не подменять ими уже проверенную authority
  и char spans. Обновление подтверждённого факта требует новой версии источника/pin.
- Для TenChat весь код, исходники, corpus, screenshots, PDF/PPTX, proofs и backup
  остаются в разрешённом серверном контуре. SSH stdin и память транспорта не являются
  разрешением записывать эти материалы в локальный файл, TEMP или Downloads.
- Existing frontend knowledge.text имеет предел в UTF-8 bytes, а не characters.
  Использовать lossless dictionary D, ordered sequences S и page metadata P;
  проверять round-trip, dictionary/full payload SHA, порядок и единицы.
- Пример проверенного формата: `EXACT_DSP_DEFLATE_BASE64_V1`, zlib+base64.
  Decoder открывается только для exact digest-pinned source; проверяет encoding,
  decoded SHA/length, размеры таблиц, все индексы и предел каждого restored page.
  Проверенные границы серии: packed text <=360000 UTF-8 bytes, page <=360000 UTF-8
  bytes, inflate <=16 MiB. Не усекать corpus для прохождения gate.
- В той же immutable source.text сохранять READABLE_FROZEN_FACT_PROJECTION:
  literal answer/quote, source URL/title, capture date, spans и verified units/terms.
  Projection и compressed payload вместе входят в sourceDigest. Opaque base64
  сам по себе не доказывает, что One/Codex fallback понимает полную БЗ: проверить
  существующий путь передачи source evidence, иначе сохранять CONFIGURED_UNTESTED.
- Literal provenance не менять при исправлении metadata. Price quote с названием
  услуги может поддерживать services facet; срок изготовления — duration;
  состав и порядок — conditions/process; указанная география — scope.
  Контакты выбирать по заявленному методу/отделу и source purpose. Privacy email
  не является sales/service contact; legal identity не доказывает договорную роль.

### Исправлять значение, а не контрольную фразу

- FAQ — независимая проверочная выборка, не словарь ответов. Сохранять исходные
  вопросы и failed proofs; не переименовывать вопросы ради PASS.
- Отделять exact expected-byte match от semantic relevance. Другой подтверждённый
  email/phone может правильно отвечать на «Как связаться?»; явный запрос телефона
  требует телефона. Specific service quote может быть правильнее общего overview.
- Source-derived aliases нормализуют declensions и явно обнаруженные mixed-script
  слова в metadata; literal quote остаётся прежней. Не добавлять произвольные темы.
- Точная entity нужна в следующем turn. Вывести service/product taxonomy из source
  headings/quotes, включая отдельный service facet у конкретного priced entity.
  Явно названная entity/topic в текущем вопросе имеет приоритет над прошлой темой;
  общий follow-up требует настоящего scoped One history.
- Общие intent classes допустимы только в обозначенной новой cohort/version:
  minimum order, composition, payment, duration, geography, catalog identifier,
  contact method. Например monetary price intent перед opening «заезд/выезд».
  Не подставлять проверочную фразу и не менять unrelated/legacy sources.
- Numeric exception допускает лишь exact source-declared catalog identifier,
  либо brand, одновременно присутствующий в frozen title и official host.
  Не принимать неизвестные размеры, пользовательские суммы, current stock,
  свободные даты, commands или prompt/credential injection. Source listing
  не доказывает сегодняшнее наличие.
- До root apply: node syntax, literal restored-quote audit, semantic sample,
  source/number/stock/injection negative checks и differential legacy lookup.
  Mock history проверяет selector; реальный BASIC_KB_PASS требует public transport
  и native One read-back. First accepted jobs/projections не перезаписывать.

### Проверка source freshness и native pixels

- Encoding/header/meta сначала, затем HTML parse: ошибочное inferred encoding
  может создать ложное расхождение адреса/цены. HTML entity или whitespace
  эквивалентность проверять отдельно, сохраняя raw bytes и original spans.
- Проверить язык и final URL. Source HTTP ru-RU и browser en-US могут расходиться
  из-за native locale redirect; не считать это изменением цены и не переделывать
  дизайн. Сделать отдельный locale-controlled reference, не перезаписывая старый.
- Network idle/CLI timeout не являются критериями пустой страницы. При доказанном
  HTTP source прогрессе сменить способ на CDP DOMContentLoaded + реальные desktop/
  mobile screenshot, body/text/images/geometry и native control checks.
  DOM и HTTP200 не заменяют painted-pixel review.

### Owner-scoped source admission и бюджет

- Reuse existing frontend job collector, existing One/Lite, native history and
  failure contract. Не добавлять backend/store и не запускать provider build turn
  для admission precompiled frozen knowledge.
- Новый owner-authorized bounded batch отделять от public intake cap. Зафиксировать
  OWNER-SCOPE/SELECTION SHA, exact owner/date/count/stable identities, fresh UUIDs,
  expectedBeforeJobs, TTL и узкий operator ceiling. Пример 07.10: existing62 +23
  =85 manual jobs, public intake60 unchanged. Не удалять прежние jobs и не резать TTL.
- Preflight использует fully resolved absolute paths; symlink/current aliases
  отклоняются existing safe gate. Effectless validate/pinned/fingerprint отделены
  от install. Static proofs остаются PENDING до реального root publication и
  fresh cache-busting external GET/SHA entry/native/CSS/JS/PDF/PPTX.
- Root — единственный production writer/sender. Применение требует backup,
  rollback, сохранения старых state/knowledge bytes и неизменного One host PID.
  Frontend reload только после отдельно подтверждённого idle.
- Планировать суммарные public API/UI requests, реальные instances и natural TTL.
  В серии rate60/IP/hour, One instance ceiling и public intake не отключались.
  Не ротировать IP, не удалять sessions и не дублировать API+UI instances без
  учтённого бюджета. 429 — не BASIC PASS; uncertain request сначала reconciled.
- Public supported entity -> short follow-up -> contact/another supported fact
  проверять в одной сессии с actual access-log bind/native SQL knowledge trace.
  Known unsupported contacts/prices/legal role тестировать отдельно как GAP.
  HTTP bytes, browser controls, PDF pixels, owner acceptance, sent receipt и
  CRM reconciliation считать разными результатами.
