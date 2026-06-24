# Improvement Plan — `odoo_apps`

| | |
|---|---|
| **Status** | Proposed — 2026-06-12 |
| **Baseline** | [SPEC.md](SPEC.md) §10 (Known Gaps) + per-package READMEs |
| **Strategy** | Fix correctness first, then make the suite runnable offline, then unify design. Ship in small, independently mergeable phases. |

Each task lists **acceptance criteria (AC)** so a phase is "done" by
verification, not by feel. Effort: S < 1 h, M = half day, L = 1–2 days.

---

## Phase 0 — Decisions (blockers for later phases) — ✅ DONE (2026-06-13)

No code; each decision recorded in [SPEC.md](SPEC.md) §11 as an ADR.

| # | Decision | Resolution | ADR |
|---|----------|------------|-----|
| 0.1 | Single packaging source | Keep `pyproject.toml`, delete `setup.py`. Next release **0.6.0**. | ADR-1 |
| 0.2 | Fate of `request.py` request objects | **Removed** from public API; loose-kwargs client is the single convention (request classes are unused and `ReadRequest`/`SearchReadRequest` are broken today). | ADR-2 |
| 0.3 | Manager return-type contract | Managers always return `Response`; Flask conversion only at the web boundary via `*_endpoint()` wrappers. Kitchen module deleted until specced. | ADR-3 |
| 0.4 | Optional dependencies | Core = stdlib + `pytz` + `python-dotenv`. Extras: `odoo_apps[data]` → pandas/openpyxl; `odoo_apps[web]` → flask. Drop `pydantic` + `requests`; `pytest` → dev-dep. | ADR-4 |
| 0.5 | Public-name typo policy | Rename now, keep deprecated aliases for one minor version (`DeprecationWarning`); aliases removed in 0.8.0. | ADR-5 |

---

## Phase 1 — Correctness fixes (highest value, lowest risk) — ✅ DONE (2026-06-13)

Bugs found during the audit. Each got an offline regression test (14 tests,
all green) backed by a new `tests/fakes.py` (`FakeOdooClient` / `FakeServerProxy`).

| # | Task | Files | Status | Acceptance criteria |
|---|------|-------|--------|---------------------|
| 1.1 | `update()` returns a `Response` on **every** path. When `write` returns falsy without raising, return `status_code=406` with an explanatory msg. | `odoo_apps/client.py` | ✅ | No code path returns `None`; falsy-write → 406 test passes. |
| 1.2 | `create_picking_order()` returns its `Response`; failed `action_confirm` reflected in `Response.msg`/406 instead of a bare `print`. | `odoo_apps/stock/manager.py` | ✅ | Returns `Response`; confirm-failure test passes. |
| 1.3 | Removed mutable default `domain=[('id','>',0)]` → `domain=None`. | `odoo_apps/client.py` | ✅ | ruff `B006/B008` clean on the file. |
| 1.4 | Fixed broken `field(default_factory=['name'])` → `lambda: ['name']` (ReadRequest, SearchReadRequest). | `odoo_apps/request.py` | ✅ | Import + instantiation of both classes works. |
| 1.5 | `day_sales(check_date)` bounded: `create_date >= day 00:00` **and** `< next day 00:00`. | `odoo_apps/pos/manager.py` | ✅ | Fake-client test asserts both bounds. |
| 1.6 | Deleted debug `print()`s in `StockManager.__post_init__`. | `odoo_apps/stock/manager.py` | ✅ | `capsys` test asserts construction is silent. |

**Tests added:** `tests/fakes.py`, `tests/test_client_unit.py`,
`tests/test_request_unit.py`, `tests/test_stock_manager_unit.py`,
`tests/test_pos_manager_unit.py`.

**Exit criteria:** ✅ six fixes applied with green offline regression tests.
⚠️ The pre-existing **live** suite (`tests/test_client.py` etc.) still requires a
test database and was not run here (no credentials in this environment); it
remains import-coupled until Phase 2.2.

---

## Phase 2 — Test infrastructure & CI (enables everything after) — ✅ DONE (2026-06-13)

Result: **53 offline tests pass in 0.04s** (no network); 13 live tests skip
without `test.env`. `pytest -m live` runs the integration suite.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 2.1 | `FakeOdooClient` / `FakeServerProxy` / `make_client` / `StubRecord` in `tests/fakes.py`. | ✅ | Records calls; configurable create/update/delete/execute_kw/search results. |
| 2.2 | Broke import-time coupling — construction moved to `tests/conftest.py` fixtures (`odoo`, `stock_manager`, `scheduler`, `appointment_manager`); missing/unreachable → `pytest.skip`. | ✅ | Offline collection no longer errors; the four live files were decoupled + marked. |
| 2.3 | `@pytest.mark.live` + `addopts = -m "not live"` + registered marker in `pyproject.toml`. | ✅ | Offline-green by default; `pytest -m live` overrides. |
| 2.4 | Pure-logic unit tests: domain builders, datetime helpers, `events_overlaps`, `Response` derivation. | ✅ | `test_utils_unit.py`, `test_appointment_slots_unit.py`, `test_response_unit.py`. (Coverage % gate deferred.) |
| 2.5 | CI `.github/workflows/ci.yml`: `pip install -e .` + ruff critical rules + offline pytest on 3.13. | ✅ | Ruff scoped to `E9,F63,F7,F82` (full lint = 65 findings, Phase 3). Old `python-package.yml` left in place — consolidate (gap #12). |
| 2.6 | Manager coverage with fakes: account, mrp, sales, contact, product (+ stock, pos from Phase 1). | ✅ | One happy + one failure path per primary write method. |

**Bonus correctness fix:** the offline tests revealed `mrp/objects.py` `BomLine`
was unimportable (non-default fields after defaults) — fixed (SPEC §10 #9).
Also logged two more found bugs (contact `IndexError`, sales `make_invoice`
arg-count) as SPEC §10 #10–#11 for a Phase 1 follow-up.

**Exit criteria:** ✅ CI runs the offline suite on every push/PR; live suite
opt-in. ⚠️ Live suite not re-validated against a database (no credentials here).

---

## Phase 3 — Packaging & hygiene

Depends on decisions 0.1/0.4.

| # | Task | Effort | Acceptance criteria |
|---|------|--------|---------------------|
| 3.1 | Delete `setup.py`; single `pyproject.toml` at v0.6.0; move `pytest` to dev-dependencies. | S | `pip install -e .` and `poetry build` both work; one version string in repo. |
| 3.2 | Implement extras: guard `flask`/`pandas` imports so `import odoo_apps` works with core-only install (lazy import inside the functions that need them, with a clear `ImportError` message naming the extra). | M | Core-only venv: client + sales/mrp/account/contact import fine; calling a pandas-backed method raises the guided error. |
| 3.3 | Remove dead code: commented blocks in `client.py`/`request.py`, duplicated `create_models_file` in `client.py` (keep `utils/help_files.py`), stray `odoo_tables.csv`/`.xlsx` out of repo root (move to `tables_files/`, git-ignored). | S | ruff `ERA` (commented-out code) clean on touched files; no duplicate definition. |
| 3.4 | `kitchen/`: port `gemini_idea.py` into `KitchenManager` + objects **or** delete the module until needed (recommended: delete, the draft stays in git history). | S–L | No empty placeholder files; package README updated. |
| 3.5 | Replace `print()` reporting with `logging` (use `utils/helpers.py` wrappers; managers get a module logger; `printer=` params keep working but route to logger). | M | `grep -rn "print(" odoo_apps/` → only CLI/help utilities remain. |

---

## Phase 4 — API unification (breaking → one minor bump, with aliases)

Depends on decisions 0.3/0.5; do after Phase 2 so renames are test-protected.

| # | Task | Effort | Acceptance criteria |
|---|------|--------|---------------------|
| 4.1 | Standardize manager returns to `Response`; add `*_endpoint()` Flask wrappers in appointment/calendar for the web use case. | L | No manager method returns `FlaskResponse` or `None`; web wrappers covered by tests. |
| 4.2 | Rename public typos with deprecation aliases: `create_conection_with_server`→`create_connection_with_server`, `avialable_fields` (internal, just fix), `MANUFACTORY`→`MANUFACTURING` (keep old constant assigned to same object), `standarize_*`→`standardize_*` in utils/response. | M | Old names still work but emit `DeprecationWarning`; docs/READMEs use new names. |
| 4.3 | English-first docstrings on public API (managers, client, objects); Spanish comments may remain internally. | M | All public classes/methods have English docstrings (checked with ruff `D` subset). |
| 4.4 | Split `utils/cleaning.py` into `utils/domains.py` (domain building) and `utils/transforms.py` (dict/DataFrame shaping); `cleaning.py` re-exports for compatibility. | M | Imports elsewhere unchanged; new modules unit-tested. |
| 4.5 | Add retry policy: small `tenacity`-free backoff wrapper (3 attempts, exponential) around transport errors only — never around `create` (idempotency check makes retry safe, but keep conservative). | M | Transient `ConnectionError` test passes with fake flaky proxy. |

---

## Phase 5 — Feature completion (separate track, needs business input)

| # | Task | Effort | Notes |
|---|------|--------|-------|
| 5.1 | Implement `PosManager.register_sale/correct_sale/cancel_sale` via `pos.order` + session handling. | L | Requires defining how sessions are opened/closed headlessly — spec first (add FRs to SPEC.md §6.3). |
| 5.2 | Kitchen module (if 3.4 chose "port"): order intake + state updates. | L | Spec first. |
| 5.3 | JSON-RPC transport option behind the same `OdooClient` interface. | L | Optional; revisit after 1.0. |

---

## Sequencing & risk

```
Phase 0 ──► Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5
(decide)    (fix bugs)  (tests/CI)  (packaging)  (API)       (features)
```

- Phases 1–3 are non-breaking for callers (1.1's `update()` now returns a
  `Response` where it returned `None` — strictly an improvement).
- Phase 4 is the only deliberately breaking phase; aliases + a CHANGELOG entry
  cover migration. Tag **0.6.0** after Phase 3, **0.7.0** after Phase 4,
  reserve **1.0.0** for after Phase 5 decisions.
- Biggest risk: Phase 2.2 (moving construction into fixtures) touches every
  test file — do it in one PR with the live suite run once against the test DB
  before and after.

## Suggested first PR

Phase 0 decisions recorded + tasks 1.1–1.6 with their regression tests using a
minimal `FakeOdooClient` (seed of 2.1). Small, high-value, and it unblocks the
rest.
