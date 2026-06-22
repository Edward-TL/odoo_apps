# `odoo_apps.type_hints` — Literal Types for Odoo Selection Fields

`typing.Literal` aliases that mirror the allowed values of Odoo **selection
fields**, so object dataclasses and manager methods get IDE autocompletion and
static checking instead of free-form strings.

## Files

| File | Provides |
|------|----------|
| `account.py` | `AccountType` (`'asset_receivable'`, `'expense'`, …). |
| `appointments.py` | Appointment selection values (activity decorators, etc.). |
| `calendar.py` | Recurrence `Frequency` (`'daily'`, `'weekly'`, …). |
| `contacts.py` | `res.partner` selections (`ActivityState`, `AutopostBills`, …). |
| `media_relations.py` | Display options (`AvatarsDisplay`, …). |
| `sales.py` | Sale order selections. |
| `stock.py` | Stock/attribute display types (`DisplayTypes`, …). |
| `time_zone.py` | Short curated `TimeZone` literal (Mexico City, Monterrey, UTC). The full IANA list lives in `odoo_apps/utils/timezones.py` as `TzNames`. |

`__init__.py` re-exports the appointment, calendar, media-relations, and stock
hints with `*` imports.

## Usage

```python
from odoo_apps.type_hints.account import AccountType

def make_account(name: str, account_type: AccountType) -> None: ...
```

## Notes

- These literals are **snapshots of an Odoo 18 database** — selection values can
  vary per Odoo version and installed modules. Verify against your instance with
  `client.get_models_fields(model, attributes=True)`.
- Keep new module-specific hints here (one file per Odoo app) rather than
  inlining literals in objects.
