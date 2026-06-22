# `odoo_apps.sales` — Quotations, Sale Orders & Invoicing

Wrapper around Odoo's Sales app (`sale.order`, `sale.order.line`,
`account.move` for invoices). Covers the quotation → confirmed order → invoice
lifecycle plus daily sales reporting.

## Files

| File | Purpose |
|------|---------|
| `objects.py` | Curated dataclasses: `Quotation` and `QuotationLine` (with `export_to_dict()` and `upload(odoo)`), plus a small `Invoice` object. |
| `raw_objects.py` | Full generated mirrors of `sale.order` (`Sale`) and `sale.order.line` (`OrderLine`) with every field — reference only. |
| `manager.py` | `SalesManager` (uses `RPCHandlerMetaclass`). |

## `SalesManager` capabilities

- `create_quotation(quotation)` — create the draft sale order.
- `add_quotation_line(quotation, line)` — append a product line.
- `confirm_sale_order(quotation)` — `action_confirm` server action.
- `make_invoice(quotation)` — generate the invoice from the order.
- `update_quotation` / `update_quotation_line` / `delete_quotation`.
- `sales_of_the_day(...)` — daily sales report query.

## Usage

```python
from odoo_apps.sales.manager import SalesManager
from odoo_apps.sales.objects import Quotation, QuotationLine

sm = SalesManager(client=client)

quotation = Quotation(partner_id=7)
q_resp = sm.create_quotation(quotation)

line = QuotationLine(order_id=q_resp.object, product_id=42, product_uom_qty=2)
sm.add_quotation_line(quotation, line)

sm.confirm_sale_order(quotation)
sm.make_invoice(quotation)
```

## Notes

- Order confirmation and invoicing use Odoo **server actions**, not plain CRUD,
  so they reproduce the same side effects as the UI (stock moves, journal entries).
- The curated/raw object split mirrors [`contact/`](../contact/README.md).
- No dedicated tests yet.
