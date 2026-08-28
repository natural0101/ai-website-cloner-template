# Commerce state model

## Systems of record

| Fact | System/API | Owner | Freshness | Failure contract |
| --- | --- | --- | --- | --- |
| price |  |  |  |  |
| availability/slot |  |  |  |  |
| order/booking |  |  |  |  |
| payment |  |  |  |  |

## Entities

| Entity | ID | Required fields | Sensitive fields | Persistence |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## State machines

```text
cart:

order/booking/quote:

payment:
```

## Server invariants

- Price recalculation:
- Idempotency key:
- Webhook verification/deduplication:
- Reservation/hold expiry:
- Public ID policy:
- PII log/analytics exclusion:

## Event contract

| Event | Trigger | Server/client | Deduplication | Analytics mapping |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |
