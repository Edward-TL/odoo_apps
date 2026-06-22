# `tests` — Test Suite

Two tiers:

- **Offline unit tests** (default) — run with no network using the in-memory
  doubles in [`fakes.py`](fakes.py). These are the CI suite.
- **Live integration tests** — marked `@pytest.mark.live`, they connect to a
  real Odoo instance configured in `tests/test.env`. Skipped by default.

## Layout

| File | Tier | Covers |
|------|------|--------|
| `fakes.py` | — | `FakeServerProxy`, `make_client()`, `FakeOdooClient`, `StubRecord` test doubles. |
| `conftest.py` | — | Fixtures: `odoo` (live client, skips if unreachable), `stock_manager`, `scheduler`, `appointment_manager`. |
| `test_client_unit.py` | offline | `OdooClient.update` / `search_read` correctness. |
| `test_request_unit.py` | offline | `request.py` dataclass defaults. |
| `test_response_unit.py` | offline | `Response` status-code derivation. |
| `test_utils_unit.py` | offline | Domain builders + datetime helpers. |
| `test_appointment_slots_unit.py` | offline | `events_overlaps` availability logic. |
| `test_stock_manager_unit.py` | offline | `StockManager.create_picking_order`. |
| `test_pos_manager_unit.py` | offline | `PosManager.day_sales` bounding. |
| `test_account_manager_unit.py` | offline | `AccountManager.create_account`. |
| `test_mrp_manager_unit.py` | offline | `Factory` BoM / production order wiring. |
| `test_sales_manager_unit.py` | offline | `SalesManager` quotation / confirm / delete. |
| `test_contact_unit.py` | offline | `ContactBook` lookups. |
| `test_product_manager_unit.py` | offline | `ProductManager.create_category`. |
| `test_client.py` | live | CRUD round-trip on product categories. |
| `test_stock_manager.py` | live | Product-attribute management. |
| `test_calendar_scheduler.py` | live | `Scheduler` event creation. |
| `test_appointment_manager.py` | live | `AppointmentManager` booking. |
| `test.env` | live | Odoo credentials (git-ignored). **Never point at production.** |

## Running

```bash
pytest                 # offline suite only (default: -m "not live")
pytest -m live         # integration suite (needs tests/test.env)
pytest tests/test_utils_unit.py
pytest --cov=odoo_apps  # coverage (needs pytest-cov)
```

The offline/live split is enforced in `pyproject.toml`
(`[tool.pytest.ini_options] addopts = -m "not live"`). The `-m live` on the
command line overrides that default.

## Writing offline tests

- Test a **manager** by injecting a `FakeOdooClient` (preconfigure
  `create_result` / `update_result` / `delete_result` / `execute_kw_result` /
  `search_read_result`) and asserting against `client.calls`. Use `StubRecord`
  for the record object a manager consumes.
- Test the **client** itself with `make_client(FakeServerProxy(...))`, which
  builds an `OdooClient` without connecting.

## Caveats

- Live tests are **pre-existing integration tests**; in the Phase 2 refactor
  their client construction moved into fixtures, but their bodies were not
  re-validated against a database. Some carry known staleness (e.g. category
  tests call a `StockManager` method that lives on `ProductManager`). Run
  `pytest -m live` against a staging database before relying on them.
