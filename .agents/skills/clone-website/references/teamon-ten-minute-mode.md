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
