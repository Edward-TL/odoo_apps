# Specification — `odoo_apps` (Odoo RPC Client Library)

| | |
|---|---|
| **Status** | Draft v1.1 — Phase 0 decisions recorded, 2026-06-13 |
| **Owner** | Edward Toledo Lopez (@Edward-TL) |
| **Version covered** | 0.5.0 (next release target: 0.6.0) |
| **Target runtime** | Python ≥ 3.13, Odoo 18 external API (XML-RPC) |
| **Roadmap** | [IMPROVEMENT_PLAN.md](IMPROVEMENT_PLAN.md) |

---

## 1. Purpose

`odoo_apps` is a Python library that translates Odoo's XML-RPC external API
into an object-oriented, typed interface. It lets backend services and scripts
manage Odoo business records (products, inventory, sales, contacts, calendar,
appointments, manufacturing, accounting) **without writing raw
`execute_kw` calls**, and exposes results in a uniform, HTTP-friendly
`Response` shape so the library can sit directly behind a web service
(e.g. a Flask booking API).

## 2. Goals

- **G1.** One generic client (`OdooClient`) covering authentication and the six
  primitive operations: `search`, `read`, `search_read`, `create`, `update`
  (write), `delete` (unlink), plus arbitrary `execute_kw`.
- **G2.** One *manager* per Odoo business app encapsulating multi-step
  workflows (e.g. quotation → confirm → invoice; slot lookup → book).
- **G3.** One *object* dataclass per Odoo record type that serializes itself to
  a valid RPC payload (`export_to_dict()`).
- **G4.** Uniform error semantics: XML-RPC faults are never leaked raw; write
  operations return a `Response` with an HTTP-like status code.
- **G5.** Idempotent record creation by default (search-before-create).
- **G6.** Type safety: model names as constants (`models.py`), selection-field
  values as `Literal` types (`type_hints/`), domain operators as `Operator`.

## 3. Non-Goals

- Not an ORM: no lazy loading, relations traversal, or session/identity map.
- No JSON-RPC transport (XML-RPC only, for now).
- No Odoo module/addon development — external API consumption only.
- No async support.
- No coverage of every Odoo app; modules are added as business needs appear.

## 4. Users & Primary Use Cases

| Actor | Use case |
|-------|----------|
| Backend developer | Build a booking web service: query free slots, book/reschedule/cancel appointments, returning proper HTTP statuses (200/201/400/409). |
| Operations engineer | Bootstrap a new Odoo database: load catalog (categories, attributes, templates) and initial stock from spreadsheets. |
| Business analyst / script author | Pull daily POS or sales data into pandas for reporting. |
| Integrator | Sync external systems with contacts, quotations, invoices, and manufacturing orders. |

## 5. Architecture

```
                ┌────────────────────────────────────────────┐
 caller ──────► │ Managers: Product, Stock, Sales, Pos,      │
 (script /      │ Appointment, Scheduler, ContactBook,       │
  Flask app)    │ Factory (mrp), Account, [Kitchen WIP]      │
                └───────────────┬────────────────────────────┘
                                │ uses                ▲ returns
                ┌───────────────▼──────────┐   ┌──────┴────────┐
                │ OdooClient (client.py)   │   │ Response      │
                │  - authenticate (uid)    │   │ (response.py) │
                │  - CRUD + execute_kw     │   └───────────────┘
                └───────────────┬──────────┘
                                │ xmlrpc.client
                        Odoo /xmlrpc/2/{common,object}
```

Supporting layers: `models.py` (model-name constants), `request.py` (typed
request dataclasses), `type_hints/` (selection literals), `utils/` (domains,
datetimes, timezones, env loading).

## 6. Functional Requirements

### 6.1 Client (`odoo_apps/client.py`)

- **FR-C1.** The client SHALL authenticate on construction, from either explicit
  `url/db/username/password` or a `user_info` mapping with uppercase keys
  `URL`, `DB`, `USERNAME`, `PASSWORD`; constructing with neither SHALL raise
  `ValueError` with guidance.
- **FR-C2.** Failed authentication (Odoo returns `uid = False`) SHALL raise a
  `RuntimeError` explaining likely causes (DB name, login email, API key).
- **FR-C3.** `search(model, domain) -> list[int]`.
- **FR-C4.** `read(model, ids, fields=['name']) -> list[dict]`.
- **FR-C5.** `search_read(model, domain=None, fields=None, limit=None, order=None)`;
  when `fields` is omitted, all model fields SHALL be fetched
  (`get_models_fields`); when `domain` is omitted, all records match.
- **FR-C6.** `create(model, vals, ...) -> Response`:
  - SHALL drop keys of `vals` not present on the target model (unless `hard=True`);
  - SHALL search for an existing record using domains derived from
    `domain_fields`/`domain_operators` (default `name =`) and return `200` +
    the existing id when found;
  - SHALL create and return `201` + new id otherwise;
  - SHALL return `406` + the error message on failure (no exception).
- **FR-C7.** `update(model, records_ids, new_vals) -> Response` (`201` on
  success, `406` on failure); int ids SHALL be normalized to lists.
- **FR-C8.** `delete(model, ids) -> Response` (`200` on success, `406` on failure).
- **FR-C9.** `get_models_fields(model, attributes=False)` SHALL return field
  names (tuple) or the full `fields_get` mapping.
- **FR-C10.** Every public method of a class using `RPCHandlerMetaclass` SHALL
  convert `xmlrpc.client.Fault` into `RuntimeError("XML-RPC Fault: <faultString>")`.

### 6.2 Response contract (`odoo_apps/response.py`)

- **FR-R1.** `Response` SHALL carry `action`, `model`, `object` (id/ids/False),
  `status` (`'OK'|'CREATED'|'BAD REQUEST'|'NOT FOUND'|'NOT ACCEPTABLE'|'CONFLICT'`),
  `status_code` (200/201/400/404/406/409), and `msg`; status and status_code
  SHALL be derivable from each other.
- **FR-R2.** `standarize_response(request, response)` SHALL wrap a `Response`
  into a `flask.Response` with `{message, success, status, body, metadata}`.

### 6.3 Domain modules

(Per-module detail lives in each package README; the spec-level contracts are:)

- **FR-M1 Product.** Create/lookup categories (internal, POS, public),
  attributes and values; create product templates with attribute lines so Odoo
  generates variants; bulk import/analysis from DataFrames; archive products.
  Manager MAY preload `{name: id}` caches at init.
- **FR-M2 Stock.** Auto-discover incoming picking type and locations; build
  picking lines; create + confirm incoming pickings; bootstrap initial
  inventory from a DataFrame (create missing products, set `stock.quant`).
- **FR-M3 Sales.** Quotation lifecycle: create, add lines, update, delete,
  confirm (server action), generate invoice; daily sales query.
- **FR-M4 Calendar.** Create events only when the time range is free (else
  `409`), move and cancel events; datetimes normalized to UTC.
- **FR-M5 Appointment.** Validate requested date/hour ranges (`400` on bad
  input); compute available slots from appointment configuration minus
  overlapping calendar events; book/reschedule/cancel returning Flask
  responses; expose the public booking URL.
- **FR-M6 Contact.** Resolve contact ids by name/phone/etc.; batch-verify
  registration; create partners idempotently via `Partner.upload()`.
- **FR-M7 MRP.** CRUD for BoMs and BoM lines; create, confirm, and check
  component availability of production orders (server actions).
- **FR-M8 Account.** Create chart-of-accounts entries.
- **FR-M9 POS.** Query order lines for a date (`day_sales`). `register_sale`,
  `correct_sale`, `cancel_sale` are declared and **pending implementation**.
- **FR-M10 Kitchen.** *Reserved.* Module exists as prototype only; no public API.

### 6.4 Utilities

- **FR-U1.** `check_domains` SHALL build valid Odoo domain triples from
  `vals` + field/operator specs (str or list forms).
- **FR-U2.** `standarize_datetime` SHALL convert naive/aware datetimes in a
  named timezone to the UTC string format Odoo expects.
- **FR-U3.** `ensure_env_vars` SHALL load credentials from `.env`/JSON files.
- **FR-U4.** `create_models_file` SHALL export the instance's `ir.model`
  catalog to CSV and XLSX.

## 7. Non-Functional Requirements

- **NFR-1 Compatibility.** Python ≥ 3.13; Odoo 18 external API. Model constants
  and type hints are snapshots — behavior on other Odoo versions is best-effort.
- **NFR-2 Error transparency.** No raw `xmlrpc.client.Fault` may escape a
  manager; failures surface either as `Response(status_code >= 400)` or
  `RuntimeError` with the fault string.
- **NFR-3 Idempotency.** Re-running a creation script against the same database
  SHALL NOT duplicate records (default `create` path).
- **NFR-4 Statelessness.** Managers hold only lookup caches; no local
  persistence. Credentials are never written to disk by the library.
- **NFR-5 Performance.** Bulk flows SHOULD minimize RPC round-trips (preloaded
  caches; `search_read` over search+read). No hard latency targets.
- **NFR-6 Security.** Credentials come from env/config files that stay out of
  version control (`test.env` is git-ignored); hosted instances use API keys.

## 8. External Interfaces & Dependencies

- **Odoo XML-RPC**: `/xmlrpc/2/common` (auth) and `/xmlrpc/2/object` (calls).
- **Runtime deps**: `pandas` + `openpyxl` (bulk/catalog flows), `flask`
  (response standardization), `pytz` (timezones), `python-dotenv` (credentials),
  `requests`, `pydantic` (declared; barely used today).
- **Packaging**: `pyproject.toml` (Poetry, v0.4.0) and `setup.py` (v0.5.0)
  coexist — single source of truth pending (§10).

## 9. Testing Strategy

Two tiers (implemented in Plan Phase 2):

- **Offline unit tests** (default suite, runs in CI): use in-memory doubles in
  `tests/fakes.py` (`FakeServerProxy`, `make_client`, `FakeOdooClient`,
  `StubRecord`) — no network. Cover the client CRUD contracts, `Response`
  derivation, domain/datetime helpers, slot-overlap logic, and one happy- +
  failure-path per write method across the account/mrp/sales/stock/pos/product
  managers and the contact book.
- **Live integration tests**: marked `@pytest.mark.live`, connect to the
  database in `tests/test.env` via the `odoo` fixture (skips, never errors, when
  absent/unreachable). Cover client CRUD, stock, calendar, appointment.

Enforced in `pyproject.toml`: `addopts = -m "not live"` (offline by default);
`pytest -m live` runs the integration suite. CI (`.github/workflows/ci.yml`)
runs ruff critical rules + the offline suite on Python 3.13.

- **Required for new modules**: at least one happy-path and one failure-path
  offline test per manager method that writes data.
- **Desired** (not yet done): coverage measurement gate; re-validation of the
  pre-existing live tests against a staging database.

## 10. Known Gaps / Open Questions

Status key: **[resolved]** = settled in §11 decisions (implementation pending);
**[open]** = still to be decided/built.

1. **[resolved → ADR-1]** Version mismatch: `pyproject.toml` (0.4.0) vs
   `setup.py` (0.5.0); two build systems maintained in parallel.
2. **[fixed — Phase 2]** Tests can now run offline (in-memory doubles +
   fixtures + `live` marker); CI runs the offline suite on 3.13.
3. **[open]** POS write operations and the whole kitchen module are
   unimplemented. *(Plan Phase 5; kitchen disposition set by ADR-3.)*
4. **[fixed — Phase 1]** `update()` now returns a `406` `Response` when Odoo's
   `write` returns falsy without raising; `create_picking_order` returns its
   `Response` (creation result, or `406` on confirm failure). *(Per ADR-3.)*
5. **[partially fixed — Phase 1]** Mutable default in `search_read` removed
   (`domain=None`); debug `print`s removed from `StockManager.__post_init__`.
   *Remaining:* commented-out exploratory code in `client.py`/`request.py`
   *(Plan Phase 3.3)*.
6. **[resolved → ADR-4]** `flask` is a hard dependency even for non-web users —
   should it be an extra?
7. **[open]** No retry/backoff or connection pooling policy for flaky networks.
   *(Plan Phase 4.5.)*
8. **[resolved → ADR-2]** Should `request.py` request objects become the single
   calling convention (currently the client takes loose kwargs and the request
   classes are mostly unused)?

Found during Phase 2 (the offline tests surfaced these):

9. **[fixed — Phase 2]** `mrp/objects.py` `BomLine` had non-default fields
   (`product_uom_id`, `id`) after defaulted ones, so the dataclass raised
   `TypeError` at definition and the **entire MRP module was unimportable**.
   Both given `= None` defaults.
10. **[open]** `ContactBook.get_contact_id` does `search_read(...)[0]['id']`,
    raising `IndexError` when the contact is missing — so the `None`/missing
    branch in `check_register_contacts` is unreachable dead code. *(Plan Phase 1
    follow-up.)*
11. **[open]** `SalesManager.make_invoice` calls `client.execute_kw(model, kw,
    data, {'context': ...})` with a 4th argument, but `OdooClient.execute_kw`
    accepts only `(model, kw, data)` → `TypeError`. *(Plan Phase 1 follow-up.)*
12. **[open]** Two CI workflows now exist: `ci.yml` (Phase 2, installs the
    package + ruff + offline pytest) and the older `python-package.yml`
    (flake8). Consolidate to one. *(Plan Phase 3.)*

## 11. Architecture Decisions (ADR Log)

Decisions taken in **Phase 0** of [IMPROVEMENT_PLAN.md](IMPROVEMENT_PLAN.md).
Each is binding for the listed implementation phase; status `Accepted` means
decided, not yet implemented.

### ADR-1 — Single packaging source of truth
- **Status:** Accepted (2026-06-13) · implement in Plan Phase 3.1
- **Context:** `pyproject.toml` (Poetry, v0.4.0) and `setup.py` (setuptools,
  v0.5.0) coexist; `setup.py` also misplaces dependency specs inside
  `find_packages(include=[...])`, where they have no effect.
- **Decision:** Keep **`pyproject.toml`** as the only build/metadata file and
  delete `setup.py`. The next release is **0.6.0** (minor bump; Phase 2 adds a
  return type to `update()` — additive, not breaking).
- **Consequences:** One version string. `pip install -e .` resolves via
  `pyproject`. `pytest` moves to dev-dependencies (ADR-4).

### ADR-2 — Calling convention: loose kwargs, not request objects
- **Status:** Accepted (2026-06-13) · implement in Plan Phase 3.3
- **Context:** `request.py` defines `SearchRequest`/`ReadRequest`/… but the
  client is called with loose kwargs; the request classes are unused, and
  `ReadRequest`/`SearchReadRequest` are currently broken
  (`field(default_factory=['name'])` — a list is not callable, raises
  `TypeError` on instantiation).
- **Decision:** The **loose-kwargs client API is the single calling
  convention.** Remove the request dataclasses from the public surface (delete
  or quarantine `request.py`). Re-introduce serializable request objects only
  if/when a web layer demonstrably needs them.
- **Consequences:** `response.py`'s `Request` union and `standarize_response`
  drop their dependency on `request.py`. Removes a broken, confusing API path.

### ADR-3 — Uniform return contract: managers return `Response`
- **Status:** Accepted (2026-06-13) · implement in Plan Phases 1 & 4.1
- **Context:** Managers return a mix of `Response`, `flask.Response`, raw
  lists, and `None`, making composition unpredictable.
- **Decision:** Every manager **write** method returns a `Response` on all
  paths (including failure). Read methods may return plain Python data. Flask
  conversion happens only at the web boundary via explicit `*_endpoint()`
  wrappers (appointment/calendar), not inside core managers. The kitchen
  module is **deleted** until specced (its draft remains in git history).
- **Consequences:** Phase 1 fixes `update()` and `create_picking_order()` to
  this contract immediately; Phase 4 migrates appointment/calendar/sales/stock
  fully and adds the thin endpoint wrappers.

### ADR-4 — Core install is dependency-light; pandas/flask are extras
- **Status:** Accepted (2026-06-13) · implement in Plan Phases 3.1–3.2
- **Context:** `flask`, `pandas`, and `openpyxl` are mandatory today even for a
  user who only wants RPC CRUD; `pydantic` and `requests` are declared but
  effectively unused.
- **Decision:** Core runtime deps = stdlib + `pytz` + `python-dotenv`.
  Extras: **`odoo_apps[data]`** → `pandas`, `openpyxl`;
  **`odoo_apps[web]`** → `flask`. **Drop** `pydantic` and `requests`.
  `pytest` becomes a dev-dependency. Modules needing an extra import it lazily
  and raise a guided `ImportError` naming the missing extra.
- **Consequences:** `import odoo_apps` works on a core-only install; the
  product/stock DataFrame flows and the web wrappers require their extra.

### ADR-5 — Pre-1.0 renames ship with deprecation aliases
- **Status:** Accepted (2026-06-13) · implement in Plan Phase 4.2
- **Context:** Several public names carry typos
  (`create_conection_with_server`, `standarize_*`, `MANUFACTORY`, internal
  `avialable_fields`).
- **Decision:** Rename to correct spellings now, but keep the old public names
  as **deprecated aliases for one minor version**, emitting
  `DeprecationWarning`. Purely internal names are renamed outright.
- **Consequences:** Callers on 0.6.x keep working; aliases removed in 0.8.0.
  A CHANGELOG entry documents each rename.

## 12. Glossary

- **Domain**: Odoo's search filter — list of `(field, operator, value)` triples.
- **Server action**: an Odoo model method beyond CRUD (e.g. `action_confirm`)
  invoked through `execute_kw`, reproducing UI-side effects.
- **Picking**: a stock transfer document (`stock.picking`).
- **BoM**: Bill of Materials (`mrp.bom`).
- **Manager**: library class orchestrating a business workflow over `OdooClient`.
