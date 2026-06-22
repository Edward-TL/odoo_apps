# `odoo_apps.mrp` — Manufacturing (MRP)

Wrapper around Odoo's Manufacturing app: **Bills of Materials** (`mrp.bom`,
`mrp.bom.line`) and **Production Orders** (`mrp.production`).

## Files

| File | Purpose |
|------|---------|
| `objects.py` | `Bom`, `BomLine`, and `ProductionOrder` dataclasses mirroring the Odoo models, with field validation via `__setattr__` and `export_to_dict()` for RPC payloads. |
| `manager.py` | `Factory` manager (uses `RPCHandlerMetaclass`). BoM lifecycle: `create_bom`, `create_bom_line`, `append_bom_line`, `update_bom_line`, `delete_bom`, `delete_bom_lines`. Production: `create_production_order`, `confirm_production_order`, `check_components_availability`. |

## Usage

```python
from odoo_apps.mrp.manager import Factory
from odoo_apps.mrp.objects import Bom, BomLine, ProductionOrder

factory = Factory(client=client)

bom = Bom(product_tmpl_id=42, product_qty=1)
bom_response = factory.create_bom(bom)

line = BomLine(bom_id=bom_response.object, product_id=7, product_qty=3)
factory.create_bom_line(line)

order = ProductionOrder(product_id=42, product_qty=10, bom_id=bom_response.object)
order_response = factory.create_production_order(order)
factory.confirm_production_order(order_response.object)
factory.check_components_availability(order_response.object)
```

## Notes

- `confirm_production_order` and `check_components_availability` call Odoo
  server actions (`action_confirm`, `action_assign`) rather than plain CRUD.
- Model name constants live in `odoo_apps/models.py` as `MANUFACTORY`
  (aliased `FACTORY`).
- Covered by offline unit tests in `tests/test_mrp_manager_unit.py`.
- The `BomLine` dataclass previously had a field-ordering bug that made the
  whole module unimportable; fixed in Plan Phase 2 (`product_uom_id`/`id`
  defaulted). When constructing `BomLine`, set `product_uom_id` explicitly.
