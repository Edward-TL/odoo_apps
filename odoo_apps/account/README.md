# `odoo_apps.account` — Accounting

Minimal wrapper around Odoo's Accounting app, currently focused on creating
entries in the **chart of accounts** (`account.account`).

## Files

| File | Purpose |
|------|---------|
| `objects.py` | `Account` dataclass mirroring `account.account` fields (code, name, account type, etc.), with `export_to_dict()` for RPC payloads. |
| `manager.py` | `AccountManager` (uses `RPCHandlerMetaclass`): `create_account(account) -> Response`. |

## Usage

```python
from odoo_apps.client import OdooClient
from odoo_apps.account.manager import AccountManager
from odoo_apps.account.objects import Account

client = OdooClient(...)
am = AccountManager(client=client)

account = Account(code="601.84.01", name="Software subscriptions", account_type="expense")
response = am.create_account(account)
print(response.status_code)  # 201 created / 200 already existed
```

## Status

Basic. Only account creation is implemented — no journals, payments, or invoices
(invoicing from a sale order lives in [`sales/`](../sales/README.md)). The model
constants `ACCOUNT`, `ACCOUNT_FOLLOW_UP`, `ACCOUNT_REPORTS`, and `BANK` in
`odoo_apps/models.py` already cover a much wider surface for direct
`client.search_read()` calls.
