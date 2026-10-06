# TeamON: сайт, AI и презентация за 10 минут

## Высший приоритет TeamON: база знаний до LLM — правило владельца 06.10.2026

Для персональных копий сайтов TeamON сначала отвечает система из полной собранной
базы знаний конкретной компании. «80%» — целевой охват типовых FAQ этим базовым
слоем, а не уже измеренный результат; фактический процент требует отдельного
замера. Подтверждённый ответ, цена, адрес, условия и ссылки берутся из exact БЗ
без обращения к модели: KB-first answer, provider/LLM calls=0.
Только недостаточные, противоречивые или неподдержанные БЗ вопросы направляются
в существующий One/Codex fallback. Другой backend/provider/store не добавляется.

BASIC_KB_PASS обязателен: фактические ответы из источников, сохранение истории и
контекста уточнений, изоляция exact company/session и отказ чужому контексту
проверяются через базовую ветку с доказанными нулевыми provider calls.
Запрет новых тестовых LLM turns не запрещает эти базовые проверки и не позволяет
оставить базу непроверенной. CONFIGURED_UNTESTED относится только к fallback;
статус базы фиксируется отдельно по реальным BASIC_KB_PASS/FAIL receipts.
Исторические direct-One ответы, source-admission-only receipts и прежние правила
про LLM на каждый вопрос не разрешают обход KB-first или отказ от BASIC_KB_PASS.
Сначала записать это правило, затем исправлять поведение в разрешённом scope.

## Native iframe copies: provider isolation and actual browser paint

Before retaining a third-party widget script inside a native-source wrapper
iframe, inspect its frame detection and mount target. A provider may treat any
`window !== window.parent` as its own widget frame and mount React into
`document.body`, erasing the complete cloned page. Verified example: myReviews
`blockWidget.js` on Badaev Pro, 06.10.2026. A well-formed HTML file or HTTP200 does
not rule out this runtime replacement.

When that exact behavior is proved, keep the archived original immutable,
back up the copy bytes and remove only the offending provider script and its
matching inline initialization. Mark the existing source widget container inert;
do not invent replacement testimonials, redesign the page or disable unrelated
Tilda scripts. Verify every remaining native script byte-for-byte, source page
records and exact rollback. Require a fresh browser DOM and actual painted
desktop/mobile screenshots before claiming the copy repaired.

An IAB screenshot can be blank while an iframe has a populated DOM and visible
computed geometry when the browser surface is hidden. Compare the direct copied
source document and wrapper, inspect real rectangles/viewport, then use the
documented browser visibility control and capture painted pixels again. If the
visible surface renders the unchanged copy, fix the observation procedure;
do not change source CSS/HTML to compensate for a hidden capture. Keep DOM,
painted pixels and native-control checks as separate receipts.

Прямая инструкция владельца от 06.10.2026: использовать этот клонер; целевой предел — 10 минут на весь клиентский комплект. Это рабочий бюджет, а не заявление о уже измеренном результате. Правила полноты источников и проверки конечного результата сохраняются.

## Единый вход

1. Читать этот контракт и основной clone-website skill. Использовать существующий подготовленный workbench. Запускать `npm run clone:prepare -- --dry-run <official-url>` для точного плана и проверки изоляции. Затем выполнять подготовку по текущему output plan; не перезаписывать CURRENT_TARGETS и чужие материалы без снимка. `clone:prepare` создаёт план/каталоги, не готовый сайт, не AI и не PDF.
2. Сохранять адрес компании, exact contact mapping и разрешение на отправку отдельно от авторинга. Проверять установленный чат до сборки; форма имени/телефона и переход в мессенджер сами по себе не являются разговорным чатом.
3. Применять клонирование исходного дизайна: настоящие изображения, шрифты, геометрия и страницы. Не начинать с переписывания произвольной старой серверной копии. Уже проверенные материалы можно повторно использовать с fresh source comparison и SHA, а не объявлять их текущими по названию папки.

## Подготовка один раз на сессию

- Проверить базовый build workbench один раз. Не повторять его, установку зависимостей и общий аудит для неизменённого базового окружения каждого клиента. Изменённый сайт всё равно должен иметь собственную проверку сборки и отображения.
- Определить и закрепить рабочие Python/Node/PowerPoint пути. Для PPTX использовать bundled Python с python-pptx/lxml; для PDF — уже проверенное окружение с PyMuPDF. Не переключать случайные `python`/`py` и не устанавливать библиотеки на каждого клиента.
- Подтвердить существующий One/Lite transport/config read-back и базовую KB-first ветку фактическим BASIC_KB_PASS с provider calls=0. gpt-6-luna остаётся только существующим fallback для недостаточных/противоречивых/неподдержанных БЗ вопросов; при запрете новых LLM test turns статус только fallback — CONFIGURED_UNTESTED. Регистрация нового source-bound job — клиентская операция; повторная разработка provider/backend/store или рестарт shared сервисов не являются нормальным этапом каждого комплекта. Если существующий transport требует изменения, отделить это от обычной сборки и назвать точную причину задержки.
- Прочитать ACTIVE.json принятого TeamON sales-deck канона и повторно использовать его PPTX и готовый PowerPoint exporter. Не искать новый дизайн и не собирать презентацию с нуля.

## Бюджет одного клиента

| Время от старта | Действия |
| --- | --- |
| 0:00–0:30 | Exact identity, существующий чат, прежние сообщения и отсутствие повторной отправки |
| 0:30–3:00 | Полный доступный сайт: каталог/пагинация, цены, условия, адреса, FAQ, PDF и прайсы; извлечение исходных assets. Начинать сборку секций по мере извлечения |
| 3:00–6:00 | Довести клонированные страницы; подключить базовый KB-first ответ и только существующий One fallback. Параллельно адаптировать четыре слайда канона и экспортировать PDF |
| 6:00–8:30 | Компьютер/телефон, BASIC_KB_PASS: факт из БЗ → уточнение/ответ → другой вариант; история/контекст/изоляция; provider calls=0; переходы; фактические четыре страницы PDF |
| 8:30–10:00 | Snapshot, ограниченная публикация, внешний read-back, разрешённая отправка, native delivery и CRM read-back |

Не тратить первые минуты на длинный план или общий аудит. Независимое чтение и подготовку объединять; source extraction и секционные builders выполнять параллельно по основному skill. Один writer публикует изменения. Браузером управлять через доступный разрешённый browser tool.

## Исключить повторяемые задержки

- Один одинаковый сбой не повторять без новых данных. Через 60 секунд без прогресса менять способ; после двух FAIL одного способа прекращать этот способ.
- HTTP403 чтения HTML → сразу обычный существующий браузер. Не перебирать shell User-Agent и хосты, если браузер уже читает сайт. Не угадывать endpoint.
- В IAB проверять реальный innerWidth: hidden view может сохранить1280. Для мобильной проверки использовать документированный viewport, при необходимости visible view; после изменения ширины перезагрузить Tilda, чтобы пересчиталась начальная геометрия.
- Проверять реальные цифры и валюту в source fonts до тиражирования карточек. При исправлении CSS сразу менять cache key/имя, а не несколько раз обновлять старый URL.
- Один раз готовить изображения, wordmark и source proof. Новые версии делать лишь после конкретного FAIL. Не запускать весь publisher повторно из-за одной картинки или правила CSS.
- Проверять критические changed files, необходимый source coverage и реальный диалог. Полный повтор CDN/fleet/generic tests — только при конкретном оставшемся риске.

## Честный результат

- Недоступные страницы и противоречивые условия перечислять отдельно. Срок 10 минут не разрешает обрезать каталог, выдумать цену, пропустить мобильный экран или объявить непроверенный PDF готовым.
- На отметке10 минут указывать сделанное, точный оставшийся блокер и следующий короткий шаг. Продолжать необходимую работу в разрешённом scope; не отправлять непроверенный комплект ради счётчика.
- Записывать реальную длительность фаз в receipts. Улучшенный процесс считается доказанным по времени только после полного проверенного комплекта, выполненного за ≤600 секунд. Dry-run, базовый build и запись этих правил не доказывают 10-минутную сборку.
- Native delivery, CRM read-back, проверенные файлы и принятие дизайна — отдельные статусы. Не возобновлять остановленную массовую рассылку из-за подготовки или отправки одного клиента.

## Доказанный KB-first путь и сохранение One — 06.10.2026

### Один runtime и настоящая история

- Переиспользовать существующий One policy `resolveAnswer` до provider и
  `projectTurnText` для записи исходного вопроса. KB-first не создаёт второй
  agent, provider, Thread store, Memory или answering plane.
- Сначала проверить фактические аргументы hook. Если там нет истории, подключить
  callback в уже существующей runtime composition: читать ограниченную историю
  через public One `GET /api/product/thread/messages` собственного instance.
  Owner cookie остаётся в server-side closure; посетитель не задаёт порт, actor,
  путь, Space или World.
- Перед чтением и использованием проверить exact actor, Product, Space, World,
  thread authority и immutable sourceDigest. Сохранять существующие границы
  текущего диалога/reset; чужой источник, actor или World не допускается.
  Ограничить число и размер сообщений; убрать текущий user message из списка
  предыдущих, если One уже записал его до callback.
- Контекст брать из собственных предыдущих user turns: сохранить entity и
  qualifiers (например, онлайн/очно, квартира/дом), затем искать нужный facet
  в той же БЗ. Общий прайс после «Сколько стоит?» не доказывает такой контекст.
  Не делать отдельный cache/store истории и не читать sibling state.
- Не перезапускать disposable preview host: его close/remove может удалять
  instance roots и историю. При обновлении helper использовать подтверждённый
  idle-worker reload с сохранением roots. Frontend restart допустим только
  отдельно разрешённым apply после active=0 и queued=0; One host сохраняется.

### Frozen KB, facets и доставка до внешнего POST

- Каждая runtime quote должна находиться в expanded CURRENT frozen KB именно
  этого sourceDigest. Совпадение домена и дополнительная сохранённая страница
  той же компании не дают authority вне текущей БЗ. Более широкие private
  источники сохранять отдельно; неподдержанный runtime факт исключить или
  отправить в существующий fallback.
- Для packed source восстановить страницы и fragments в исходном порядке
  существующим deterministic decoder. Numeric/availability validation должна
  читать эти страницы, а не номера индексов и raw fragment JSON. Decoder
  разрешать только для exact digest-pinned source; guard predicates, лимиты
  и поведение неизвестных источников сохранять.
- Использовать subject/entity/facet taxonomy, не словарь контрольных вопросов.
  Не смешивать цену, период, единицу, объект, формат услуги, дату прайса и
  исключения. Case awards/компенсации не являются тарифом.
- До публичного POST прогнать existing marketing validators на всех
  authoritative runtime facts, сохранённой независимой FAQ-выборке и
  ожидаемых публичных ответах через stub transport: model/provider calls=0.
  Lookup hit считать отдельно от semantic CORRECT/PARTIAL/FAIL/FALLBACK.
- Сохранять опубликованный literal формат сумм и часов, если нормализация
  создаёт новые numeric tokens: `18.000`, `5 000р.`, `9:00`,
  `12.00 - 20.00`. Значение, единица и условия должны остаться теми же.
  Не писать числа словами или обфусцировать их ради обхода guard.
- Ошибка delivery-validator не доказывает ложность source claim. Сначала
  установить точную причину на literal источнике и существующем predicate;
  не ослаблять защиту ради PASS. Фактически поддержанную лишнюю фразу можно
  убрать для краткости, сохранив правильную классификацию причины.

### Внешний BASIC proof, изоляция и статусы

- Публичные KB-only проверки делать только через уже существующую fail-closed
  ветку exact источников: hit либо bounded insufficient, без provider fallback.
  Перед каждым POST сверять active helper/provider/runtime SHA. На неизвестный
  или изменившийся pin этот тестовый режим не распространяется.
- Сохранять request и полный response/status до assertions. При uncertain POST
  не повторять отправку: сначала сверить собственную native историю/receipt.
  Старые FAIL сохранять неизменно. Исправленный сценарий — отдельный новый
  turn с новым question/turnId и учтённым бюджетом, а не скрытый replay.
- Проверить ту же visitor UUID на разных job/company mappings. Внутри компании
  остаются одна instance и одна scoped thread authority; между компаниями
  разделены instance roots, DB и sourceDigest, нет чужих вопросов/ответов.
  Authority — `(instanceId, exact DB path, Space, World, threadId)`.
  Raw threadId может совпадать в разных капсулах: One создаёт его из
  actor/Space/World, поэтому глобальная уникальность строки не является gate.
- Не требовать sourceDigest echo, если текущий public API его не предоставляет.
  Помечать `PUBLIC_SOURCE_DIGEST_FIELD=NOT_EXPOSED`; отдельно сверять fresh
  job state digest, exact knowledge SHA, вычисленный sourceDigest, helper pin,
  public source URL/title и фактический ответ. Не выдавать disk proof за echo.
- Native read-back подтверждает точные исходные user questions, assistant
  answers, их порядок и отсутствие sibling history. У user traceId может быть
  NULL; у каждого KB assistant требуется `traceId=knowledge`. Только этот
  фактический путь с semantic read-back доказывает provider_calls=0.
- Для каждой из семи новых компаний сохранить отдельный proof: supported
  entity/facet → короткое продолжение без повторения entity → контакты,
  в одной настоящей сессии. Mock history проверяет код, но не production
  BASIC_KB_PASS. Общие услуги/контакты не заменяют уточнение с контекстом.
- Доказанная серия 06.10.2026: 15 ранее подготовленных компаний × 2 turn и
  7 новых × 3 turn = 51 доставленный ответ; один прежний HTTP503 сохранён,
  всего 52 POST, с отдельным UI turn — 53. Все семь short follow-ups прошли
  настоящий One history read-back; provider/model calls=0. Это пример
  проверенного бюджета, не разрешение повторять серию или расширять caps.
- `BASIC_KB_PASS`, `LLM_CONFIGURED_UNTESTED`, native UI/visual PASS, принятие
  дизайна, PACKAGE_READY, отправка и CRM read-back считать раздельно.
  При запрете новых LLM turns не менять fallback `qaStatus=CONFIGURED_UNTESTED`
  на VERIFIED из-за базовых KB ответов; сохранить исходные failed receipts.
