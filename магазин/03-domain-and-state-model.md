# Доменная модель и состояния

## Источник истины

Браузер хранит намерение пользователя, но не определяет итоговую цену, скидку, налог, доставку, наличие, слот или статус платежа. Перед созданием заказа сервер заново рассчитывает коммерческие условия по идентификаторам и правилам.

## Базовые сущности

| Сущность | Минимальные поля | Кто подтверждает |
| --- | --- | --- |
| `Product` | id, title, description, media, category, status | каталог/CMS |
| `Variant` | id, productId, SKU, attributes, price, inventoryPolicy | commerce backend |
| `MenuItem` | id, locationIds, basePrice, composition, allergens, availability | menu/POS |
| `ModifierGroup` | id, min, max, required, options | menu/POS |
| `Service` | id, duration, priceModel, preparation, cancellationPolicy | booking backend |
| `StaffOrResource` | id, serviceIds, locationId, schedule | booking backend |
| `Slot` | start, end, timezone, resourceId, availabilityVersion | booking backend |
| `CartLine` | purchasableId, variant/modifiers, quantity | серверная проверка |
| `PriceQuote` | subtotal, discounts, delivery, tax, total, currency, expiresAt | pricing service |
| `Order` | publicId, lines, customer, fulfillment, payment, status | order backend |
| `Booking` | publicId, service, slot, customer, payment, status | booking backend |
| `ConsentReceipt` | purpose, policyVersion, timestamp, source | consent store |

## Инварианты

- денежные значения хранятся в минимальных единицах валюты, а не `float`;
- валюта явная и одна для каждого расчёта;
- строка корзины хранит ID выбранных вариантов/модификаторов и количество, а не доверенный клиентский total;
- промокод валидируется сервером с причиной отказа;
- checkout получает снапшот расчёта с временем истечения;
- создание заказа и обработка webhook идемпотентны;
- публичный ID заказа не раскрывает последовательный внутренний ID;
- персональные данные не попадают в URL, аналитику и клиентские логи;
- смена адреса, ресторана, слота или способа получения запускает повторную проверку цены и доступности;
- подтверждение не показывается, пока backend не зафиксировал заказ/запись.

## Состояния корзины

```text
empty → active → repricing → ready → checkout_started
                           ↘ invalid_item / unavailable / quote_expired
checkout_started → submitted → converted
                 ↘ payment_failed → ready
                 ↘ expired → active
```

На каждом отклонении интерфейс показывает: что изменилось, какие строки затронуты, новый итог и доступное действие.

## Состояния заказа еды

```text
draft
→ pending_payment
→ paid
→ pending_acceptance
→ accepted
→ preparing
→ ready_for_pickup | out_for_delivery
→ completed
```

Ветки: `payment_failed`, `rejected`, `canceled`, `refund_pending`, `refunded`. Оплата и принятие рестораном — разные факты. Если заказ оплачен, но ресторан не может его исполнить, должен существовать явный процесс возврата и уведомления.

## Состояния записи

```text
selecting → slot_held → payment_required | confirmation_required → confirmed → completed
                     ↘ hold_expired
confirmed → rescheduled | canceled | no_show
```

Hold имеет срок. Кнопка подтверждения повторно проверяет доступность; конфликт слота возвращает пользователя к выбору времени, сохраняя услугу и контактные данные, где это допустимо.

## Состояния заявки на расчёт

```text
draft → submitted → acknowledged → in_review → clarification_needed → quoted → accepted | declined | expired
```

Экран после отправки показывает идентификатор, сохранённые вводные, обещанный срок ответа и канал связи. Текст `Спасибо!` без следующего шага не является полноценным подтверждением.

## Ошибки, которые проектируются заранее

- товар закончился после добавления;
- цена или акция изменились;
- адрес вне зоны или ресторан закрылся;
- обязательный модификатор не выбран;
- слот занял другой клиент;
- платёж в обработке, отклонён или завершён после закрытия вкладки;
- webhook пришёл повторно или не по порядку;
- подтверждение отправлено, но email/SMS не доставлены;
- заказ создан, но внешняя система исполнения недоступна;
- пользователь обновил страницу на каждом шаге.
