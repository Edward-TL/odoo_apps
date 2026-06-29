# fast_odoo_bulk

Fast bulk loading into Odoo for ETLs already written against
[`odoo_apps`](../odoo_apps) (the XML-RPC client).

## Why

Every `OdooClient` call is an XML-RPC round-trip (serialize → HTTP → Odoo → deserialize).
Loading hundreds of records (invoices, partners, products) means hundreds of serial
round-trips — slow, even when the payloads themselves batch. The fix: run the **same loader
code in-process**, inside the Odoo container, where ORM calls are local.

## How it works

`InProcessClient` subclasses `OdooClient` and swaps only the transport: instead of an
`xmlrpc.client.ServerProxy`, `self.models` is a shim that dispatches through
`odoo.api.call_kw` — exactly what the XML-RPC endpoint calls, minus the network. All of the
base client's logic (field filtering, idempotent dedup, `Response` building, recordset→id
normalization) is reused unchanged, so the RPC and in-process engines behave identically.

Key behaviours:
- **Writes only through the ORM** — taxes, journal items, sequences and balances stay
  correct. Postgres is used (via `pg_read`) only for fast dedup reads and verification.
- **Commits per mutating call** (`odoo shell` has no autocommit), then drops the ORM cache to
  bound memory across large runs.
- Runs as superuser with `allowed_company_ids` covering every company (multi-company safe),
  and disables mail/tracking for speed.

## Usage

Inside `odoo shell` (where `env` is in scope):

```python
from fast_odoo_bulk import InProcessClient
client = InProcessClient(env)
# hand `client` to any code that expects an OdooClient
```

From the host, drive a container's shell:

```bash
python -m fast_odoo_bulk.launcher --container odoo19 --db rio_teapa_test \
    --entry import_code/_inproc_entry.py -- --section invoices --limit 50
```

## Modules

| Module | Imports Odoo? | Purpose |
|---|---|---|
| `client` (`InProcessClient`) | yes (runs in the container) | the in-process adapter |
| `launcher` | no | host-side `docker exec … odoo shell` runner |
| `pg_read` | no (lazy `psycopg2`) | dedup reads + verification queries (never writes) |
