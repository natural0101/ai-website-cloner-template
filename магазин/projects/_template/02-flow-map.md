# Flow map

## Happy path

```text
entry → selection → configuration → price/conditions → cart/slot/quote → checkout/submit → server confirmation → fulfillment/manage
```

## Decision points

| Step | User decision | Required data | Source of truth | Next state |
| --- | --- | --- | --- | --- |
| 1 |  |  |  |  |

## Failure and recovery paths

Заполнить минимум 8 фактических веток.

| ID | Failure | Visible message | Preserved data | Recovery action | Verification |
| --- | --- | --- | --- | --- | --- |
| ERR-001 | price changed |  |  |  |  |
| ERR-002 | unavailable item/slot |  |  |  |  |
| ERR-003 | payment pending/failed |  |  |  |  |
| ERR-004 | double submit/retry |  |  |  |  |
| ERR-005 | refresh/back |  |  |  |  |
| ERR-006 | provider/backend timeout |  |  |  |  |
| ERR-007 | expired cart/quote/slot hold |  |  |  |  |
| ERR-008 | confirmation notification failed |  |  |  |  |

## Post-purchase/manage flow

- Status route:
- Safe access model:
- Cancel/reschedule/return path:
- Support escalation:
- Reorder/rebook:
