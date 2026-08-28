# Reference board

Сюда попали только источники, которые уже преобразованы в конкретное решение.

| ID | URL / access | Lane and closeness | Borrow / transform | Do not copy | Section | Risk and QA |
| --- | --- | --- | --- | --- | --- | --- |
| REF-001 | https://www.chipotle.com/order/find-a-chipotle — live | direct: food ordering, pickup/delivery, location gate | двухвариантный fulfillment selector и ввод адреса до меню; адаптировать к локальной географии | campaign copy, photography, brand layout | pizzeria hero / location gate | geolocation permission; проверить ручной адрес и отказ |
| REF-002 | https://www.dominos.com/pages/order/menu — live | direct: pizzeria menu, local price and customization | локальный каталог, категории, размер/тесто/соус/топпинги | proprietary configurator, coupons, claims | menu, item configurator | сложность modifiers; тест min/max/incompatibility |
| REF-003 | https://www.papajohns.com/ordering/ — live | direct: guest pizza ordering, delivery/carryout, tracking | понятная последовательность и guest path; превратить в короткий локальный flow | loyalty mechanics и ограничения конкретного рынка | checkout / confirmation | local payment differences; проверить гостя и tracker states |
| REF-004 | https://www.fresha.com/help-center/knowledge-base/online-profile/101646-learn-how-clients-book-appointments-online — live | direct: booking workflow and real availability | service → staff optional → slot → review | marketplace IA, business claims | booking flow | slot race; проверить hold expiry и conflict recovery |
| REF-005 | https://booksy.com/en-gb — live | adjacent: local service discovery, reviews, portfolio, reschedule | связать доказательства с выбором услуги и показать manage booking | marketplace density, app-promotion bias | service landing / trust / manage | fake reviews; использовать только собственные verified data |
| REF-006 | https://baymard.com/blog/grocery-food-delivery-orders — live | adjacent: repeat behavior in food/grocery | prominent past purchases/reorder после первого заказа | выводить пустой/выдуманный history block | returning home | privacy and stale availability; revalidate every line |
| REF-007 | https://www.allbirds.com/shop — live | visual: scannable categories and product-led merchandising | ясная навигация по полу/типу и компактная ассортиментная иерархия | sustainability claims, product imagery, exact mega-nav | catalog header / category | mega-nav overload; keyboard and mobile test |
| REF-008 | https://www.fresha.com/ — live | visual: search frame built around treatment/location/time | один intent frame над social proof; для одного бизнеса упростить до service/location | marketplace counters, testimonials, imagery | booking hero | counters require evidence; avoid three competing inputs when location fixed |
| REF-009 | https://www.chipotle.com/order/find-a-chipotle — live | visual: bold product imagery around operational CTA | отделить expressive campaign block от functional selector | seasonal campaign and typography | pizzeria hero / campaign | marketing content must not push address selector below fold |
| REF-010 | https://motion.dev/docs/react-layout-animations — live | motion: layout changes, cart/filter reflow | short transform-based reflow for selected card/cart line | decorative shared transitions across checkout | filters / cart | distortion and bundle; reduced motion + INP check |
| REF-011 | https://motion.dev/docs/react-animate-presence — live | motion: enter/exit and removal feedback | animate removal while preserving status/undo and focus | long exit that delays input | cart line / drawer / toast | focus loss; screen-reader and interruption test |
| REF-012 | https://pageflows.com/post/ios/ordering-food/grab/ — account/premium for full flow | workflow: food search → item → options → basket → order → confirmation | use visible step inventory to enumerate screens and errors | gated screenshots/video, mobile app styling | flow map / QA | access and copyright; reference-only, no asset copying |

## Promoted decisions

- Pizzeria hero starts with fulfillment/location, not an abstract brand headline.
- Product/menu lists show decision attributes without requiring every detail page.
- Booking makes availability a data-backed state, not a decorative calendar.
- Cart motion only clarifies addition/removal/repricing.
- Checkout prioritizes guest completion, visible total and server-confirmed status.

## Rejected directions

- Long cinematic restaurant homepage before the menu: hurts urgent food-order intent.
- Marketplace-scale search UI for a single local service: creates fake complexity.
- Awwwards-style page transitions in checkout: delays transactional work and increases recovery risk.
- Copied marketplace counters/reviews: unverified proof.
- Premium flow screenshots as production assets: access/license and brand mismatch.
