# `odoo_apps.stock` — Inventory & Warehouse

Wrapper around Odoo's Inventory app (`stock.picking`, `stock.move`,
`stock.quant`, `stock.location`). Focused on **receiving stock** (incoming
pickings) and **bootstrapping initial inventory** from a spreadsheet.

## Files

| File | Purpose |
|------|---------|
| `manager.py` | `StockManager` dataclass (uses `RPCHandlerMetaclass`). On init it auto-discovers the internal stock location and the *incoming* picking type (source/destination locations) when ids are not provided. |
| `objects.py` | Near-empty placeholder — stock dataclasses not yet defined. |

## `StockManager` capabilities

- `create_new_picking_line(product_name, product_id, quantity)` — builds the
  `(0, 0, {...})` one2many command for a stock move line.
- `create_picking_order(picking_lines)` — creates the `stock.picking` (with
  `hard=True`, always a new record) and immediately confirms it via the
  `action_confirm` server action.
- `create_initial_inventory(products_table: pd.DataFrame)` — iterates a product
  DataFrame; creates missing products (matched by `default_code`/`barcode`) and
  sets their starting quantity through `stock.quant`.
- `_find_internal_location()` — first internal-usage location fallback.

## Usage

```python
import pandas as pd
from odoo_apps.stock.manager import StockManager

sm = StockManager(client=client)   # auto-resolves picking type & locations

lines = [
    sm.create_new_picking_line("Laptop Pro", product_id=42, quantity=10),
    sm.create_new_picking_line("Mouse", product_id=43, quantity=50),
]
sm.create_picking_order(lines)

sm.create_initial_inventory(pd.read_excel("initial_stock.xlsx"))
```

## Notes

- `create_picking_order` returns its `Response`: the creation result on
  success, or a `406` when the `action_confirm` server action fails. (Remaining
  Spanish `print()` progress messages will move to logging in Plan Phase 3.5.)
- Auto-discovery assumes a single warehouse with a location literally named
  `"Stock"`; pass explicit ids in multi-warehouse databases.
- Covered (partially) by `tests/test_stock_manager.py`.
