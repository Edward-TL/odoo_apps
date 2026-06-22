# `odoo_apps.pos` — Point of Sale (partial)

Read-oriented wrapper around Odoo's POS app. Currently supports **querying
daily sales**; write operations are declared but not yet implemented.

## Files

| File | Purpose |
|------|---------|
| `manager.py` | `PosManager` dataclass (uses `RPCHandlerMetaclass`). Optionally preloads a `ProductManager` for product/category lookups. |
| `objects.py` | Empty placeholder — future POS order/line dataclasses. |

## Implemented

- `day_sales(check_date, fields=...)` — returns `pos.order.line` records created
  after the given date (name, product, qty, attribute values, create date).
  Queries by **order line**, not by order.

## Declared but not implemented (stubs)

- `register_sale(sale_date, product, client)`
- `correct_sale(sale_id, ...)`
- `cancel_sale(sale_id, ...)`

## Usage

```python
from odoo_apps.pos.manager import PosManager

pm = PosManager(client=client)          # preload=True builds a ProductManager
todays_lines = pm.day_sales("2026-06-12")
```

## Notes

- `day_sales(check_date)` is bounded to the **calendar day** of `check_date`
  (`create_date >= day 00:00:00` and `< next day 00:00:00`); any time component
  in `check_date` is ignored.
- POS model constants (`POS.ORDER`, `POS.ORDER_LINE`, `POS.SESSION`,
  `POS.PAYMENT`, …) are available in `odoo_apps/models.py` for direct queries.
