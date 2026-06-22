# `odoo_apps` — Core Package

The main package of the library. It translates Odoo's XML-RPC external API into
Pythonic classes: a low-level **client**, a catalog of **model names**, typed
**request/response** objects, and one subpackage per Odoo business app
(product, stock, sales, appointment, etc.).

## Architecture

```
OdooClient (client.py)          ← raw XML-RPC transport + generic CRUD
    ▲
    │ injected into
Managers (one per subpackage)   ← business workflows (ProductManager, SalesManager, …)
    ▲
    │ consume / produce
Objects (one per subpackage)    ← dataclasses mirroring Odoo records (ProductTemplate, Quotation, …)
    │
Response (response.py)          ← uniform result wrapper with HTTP-like status codes
```

## Top-level modules

| File | Purpose |
|------|---------|
| `client.py` | `OdooClient`: authentication and generic `search`, `read`, `search_read`, `create`, `update`, `delete`, `execute_kw`, plus field-introspection helpers. Includes `handle_xmlrpc_fault` decorator and `RPCHandlerMetaclass`, which auto-wraps every public method of a class with XML-RPC fault handling. |
| `models.py` | Constants for Odoo technical model names, grouped by app (`PRODUCT.TEMPLATE` → `'product.template'`, `STOCK.PICKING` → `'stock.picking'`, …). Avoids magic strings across the codebase. |
| `request.py` | Dataclasses describing RPC requests (`SearchRequest`, `ReadRequest`, `SearchReadRequest`, `CreateRequest`, `UpdateRequest`, `DeleteRequest`). |
| `response.py` | `Response` dataclass with HTTP-like `status_code`/`status`/`msg`/`object`, plus `standarize_response()` to wrap results as Flask responses for web endpoints. |

## Subpackages

| Package | Odoo app | Status |
|---------|----------|--------|
| [`account/`](account/README.md) | Accounting (chart of accounts) | Basic |
| [`appointment/`](appointment/README.md) | Appointments / online booking | Mature |
| [`calendar/`](calendar/README.md) | Calendar events | Mature |
| [`contact/`](contact/README.md) | Partners / contacts (`res.partner`) | Functional |
| [`kitchen/`](kitchen/README.md) | Restaurant kitchen orders | Prototype / WIP |
| [`mrp/`](mrp/README.md) | Manufacturing (BoMs, production orders) | Functional |
| [`pos/`](pos/README.md) | Point of Sale | Partial (read-only) |
| [`product/`](product/README.md) | Products, categories, attributes, variants | Mature (largest module) |
| [`sales/`](sales/README.md) | Quotations, sale orders, invoicing | Functional |
| [`stock/`](stock/README.md) | Inventory, pickings, initial stock loads | Functional |
| [`type_hints/`](type_hints/README.md) | `Literal` types for Odoo selection fields | Support |
| [`utils/`](utils/README.md) | Domains, datetimes, timezones, images, helpers | Support |

## Conventions

- **Managers** are dataclasses that receive an `OdooClient` and use
  `RPCHandlerMetaclass` so any XML-RPC `Fault` is re-raised as a clear `RuntimeError`.
- **Objects** are dataclasses mirroring Odoo record fields, with an
  `export_to_dict()` method that produces the `vals` payload for `create`/`write`.
- **Every write operation** returns a `Response` (status `200` = already existed,
  `201` = created, `400/404/406/409` = failures), never a bare ID.
- `client.create()` is **idempotent by default**: it searches for an existing
  record matching the domain (default: same `name`) before creating; pass
  `hard=True` to skip the check and force creation.
