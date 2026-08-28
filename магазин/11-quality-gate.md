# Quality gate магазина

Результат считается готовым только по фактическим проверкам. Каждый пункт имеет `PASS`, `FAIL`, `BLOCKED` или `N/A` с причиной.

## Стратегия

- [ ] выбран один основной режим;
- [ ] названы объект продажи, аудитория, рынок и основная конверсия;
- [ ] CTA описывает точное действие;
- [ ] цена/география/срок/способ получения доступны до коммита;
- [ ] маркетинговая страница ведёт в тот же коммерческий flow.

## Данные и backend

- [ ] источник цены задокументирован;
- [ ] источник availability/stock/slot задокументирован;
- [ ] сервер пересчитывает итог перед заказом;
- [ ] idempotency защищает double-submit;
- [ ] webhook подпись и повторы обрабатываются;
- [ ] order/booking ID создаётся сервером;
- [ ] refresh/back не теряют или не дублируют заказ;
- [ ] персональные данные не попадают в URL/analytics/logs;
- [ ] fixture/demo данные явно маркированы и не выглядят real proof.

## Каталог/меню/услуги

- [ ] карточки имеют сравнимую иерархию атрибутов;
- [ ] поиск/категории/фильтры соответствуют размеру ассортимента;
- [ ] active filters и reset видимы;
- [ ] варианты/модификаторы имеют unavailable и invalid states;
- [ ] empty state и network error различаются;
- [ ] смена локации/слота пересчитывает зависимые данные;
- [ ] все изображения имеют размеры, crop policy и alt policy.

## Корзина/запись/заявка

- [ ] выбранное можно проверить и изменить;
- [ ] обязательные модификаторы валидируются;
- [ ] subtotal, скидка, доставка/сборы и total видимы;
- [ ] repricing показывает, что изменилось;
- [ ] slot/stock expiration имеет recovery;
- [ ] минимальная сумма/зона/часы проверяются до оплаты;
- [ ] quote receipt содержит ID, введённые данные и SLA.

## Checkout и оплата

- [ ] гостевой путь есть или его отсутствие обосновано;
- [ ] запрашиваются только необходимые данные;
- [ ] labels, autocomplete и мобильные input modes корректны;
- [ ] field errors и summary доступны;
- [ ] payment pending/failed/canceled/paid/refund states различаются;
- [ ] success page читает server status;
- [ ] purchase/booking analytics отправляется после подтверждения;
- [ ] электронное подтверждение содержит order ID и условия исполнения.

## Pizzeria

- [ ] delivery/pickup выбран до финальных условий;
- [ ] location/address определяют меню, цену и ETA;
- [ ] required/min/max modifiers работают;
- [ ] allergens/composition выводятся из утверждённых данных;
- [ ] закрытие, стоп-лист, перегрузка и POS rejection обработаны;
- [ ] tracker различает оплату, принятие и выполнение;
- [ ] reorder не требует заново собирать типовой заказ и повторно валидируется.

## Booking/quote

- [ ] booking и quote не смешаны;
- [ ] timezone, duration, staff/resource и policy видимы;
- [ ] slot hold и collision обработаны;
- [ ] депозит/оплата и refund terms объяснены;
- [ ] отмена, перенос, опоздание и no-show имеют состояния;
- [ ] upload показывает лимиты, прогресс, ошибки и удаление;
- [ ] ручная оценка не обещана как мгновенная покупка.

## Trust, SEO и legal

- [ ] каждый claim имеет evidence owner;
- [ ] нет fake reviews/logos/counters/scarcity;
- [ ] реквизиты, контакты и политики соответствуют рынку;
- [ ] offer/terms, delivery/return или booking/cancellation доступны до коммита;
- [ ] privacy/consent/retention/processors подтверждены владельцем;
- [ ] фискализация и чек проверены для рынка;
- [ ] structured data соответствует видимому содержанию;
- [ ] canonical, robots и sitemap проверены;
- [ ] отраслевые ограничения получили owner approval.

## Accessibility и performance

- [ ] полный flow проходит с клавиатуры;
- [ ] фокус видим и не закрыт sticky UI;
- [ ] target size/spacing соответствует WCAG 2.2;
- [ ] screen reader объявляет total/status/error без лишнего шума;
- [ ] 200% zoom и mobile reflow без горизонтального checkout;
- [ ] reduced motion сохраняет функциональную обратную связь;
- [ ] LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 подтверждены field data или помечены UNKNOWN;
- [ ] third-party scripts имеют budget и consent;
- [ ] изображения и шрифты не создают CLS и чрезмерный transfer.

## Финальное решение

`PASS` разрешён, когда happy path и заранее выбранные failure paths реально пройдены, серверные инварианты доказаны тестом/логом, юридические UNKNOWN перечислены и нет блокирующих `FAIL`.
