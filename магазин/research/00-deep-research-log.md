# Deep research log

Дата: 2026-08-18. Цель: выделить из исследований и живых коммерческих продуктов решения для `catalog`, `pizzeria`, `booking` и `quote`, а не собрать декоративный moodboard.

## Решения, подтверждённые несколькими источниками

| Решение | Источники | Сила | Что может отменить |
| --- | --- | --- | --- |
| Для еды сначала определить delivery/pickup и локацию | Domino’s, Papa Johns, Chipotle | strong, наблюдаемый production pattern | единая точка с одной зоной и одинаковыми условиями |
| Для записи: услуга → специалист optional → реальный слот → review | Fresha official flow, Booksy product flow | strong | услуга без календаря, только заявка/quote |
| Показывать существенные атрибуты прямо в списке | Baymard product listing research, NN/g list entry hierarchy | strong | ассортимент из 1–3 позиций без сравнения |
| Полная стоимость и доставка до начала checkout | Baymard PDP/checkout research | strong | доставка всегда нулевая и это явно обещано |
| Гостевой checkout и короткие формы | Baymard checkout, W3C forms | strong | регулируемая идентификация или договорное ограничение |
| Повтор прошлой покупки заметен в food/grocery | Baymard food delivery research | medium/strong | первый запуск без returning-user history |
| Сервер и webhook подтверждают оплату/заказ | Stripe official lifecycle; общий payment architecture inference | strong technical pattern | иной провайдер с эквивалентным server callback, но не client redirect |
| Structured data соответствует типу коммерции | Google Search Central ecommerce/local business docs | strong official | конкретный тип не поддерживается Google rich results; Schema.org всё равно не гарантирует показ |
| Motion объясняет state change и имеет reduced-motion path | W3C WCAG 2.2, Motion docs, NN/g animation usability | strong | статичный UI может быть яснее и дешевле |
| Performance — часть коммерческого качества | web.dev thresholds and ecommerce case studies | strong thresholds, case-specific uplift | конкретный uplift нельзя переносить между продуктами |

## Числа, которые нельзя превращать в универсальные обещания

- Baymard публикует средний cart abandonment около 70%, но это benchmark, не прогноз конкретного магазина.
- В отдельных web.dev case studies рост конверсии коррелировал или следовал за performance work, но проценты не переносятся на новый проект.
- Проценты по отсутствующим фильтрам, плохим спискам и checkout описывают выборку Baymard, а не гарантированный uplift.

## Источники по evidence lane

### Ecommerce UX

- https://baymard.com/research/checkout-usability
- https://baymard.com/learn/checkout-flow-ux-optimization
- https://baymard.com/blog/product-listing-information
- https://baymard.com/blog/current-state-product-list-and-filtering
- https://baymard.com/research/product-page
- https://baymard.com/blog/show-shipping-costs-on-product-pages
- https://baymard.com/blog/grocery-food-delivery-orders

### Accessibility and forms

- https://www.w3.org/TR/WCAG22/
- https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/
- https://www.w3.org/WAI/tutorials/forms/

### Performance

- https://web.dev/articles/vitals
- https://web.dev/case-studies/rakuten
- https://web.dev/case-studies/farfetch

### Payments

- https://docs.stripe.com/payments/checkout/how-checkout-works
- https://docs.stripe.com/payments/checkout/quickstarts

### SEO and structured data

- https://developers.google.com/search/docs/specialty/ecommerce/include-structured-data-relevant-to-ecommerce
- https://developers.google.com/search/docs/appearance/structured-data/product
- https://developers.google.com/search/docs/appearance/structured-data/merchant-listing
- https://developers.google.com/search/docs/appearance/structured-data/local-business

### Russian launch gate

- https://publication.pravo.gov.ru/Document/View/0001202101090017
- https://76.rospotrebnadzor.ru/Dlja_predprinimatele/5407/
- https://www.13.rospotrebnadzor.ru/content/o-pravah-potrebiteley-pri-distancionnyh-sposobah-prodazhi-tovara-0
- https://www.nalog.gov.ru/rn77/about_fts/docs/3909988/
- https://www.nalog.gov.ru/rn77/taxation/reference_work/knd/
- https://government.ru/docs/all/98196/

## Ограничения исследования

- Не выполнялась покупка и реальная оплата на сайтах-референсах.
- Premium flows Page Flows использованы только как каталог сценариев; скрытые экраны не считаются проверенными.
- Не копировались изображения, тексты, отзывы, брендинг или proprietary code.
- Российский legal gate требует повторной проверки на дату запуска.
