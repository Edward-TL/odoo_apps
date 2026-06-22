# `odoo_apps.utils` — Shared Utilities

Cross-cutting helpers used by the client and every manager: domain building,
datetime/timezone normalization, dict transforms, env-var loading, and images.

## Files

| File | Purpose |
|------|---------|
| `cleaning.py` | The workhorse. `check_domains()` / `gen_domains_from_str()` / `gen_domains_from_list()` build Odoo search domains from `vals` (used by `client.create` for idempotency checks). Also `generate_dict()` (dataclass → dict), `flat_list`, `merge_dictionaries`, `gen_matrix`, `sort_dict`, and other shaping helpers. |
| `operators.py` | `Operator` — `Literal` of all valid Odoo domain operators (`'='`, `'!='`, `'ilike'`, `'in'`, …) with usage notes. |
| `time_management.py` | `date_normalizer()`, `standarize_datetime()` (tz-aware → UTC string for Odoo), `adapt_datetime()`, `extract_hour()`. |
| `timezones.py` | `TzNames` — `Literal` of every IANA timezone name. |
| `validators.py` | `domain_validator()` — sanity-check a domain triple. |
| `helpers.py` | `ensure_env_vars()` (load credentials from a `.env`/JSON env file) and `log` / `warning_log` / `error_log` wrappers. |
| `images.py` | `image_loader()` — read an image file as base64 for Odoo binary fields. |
| `multicompany.py` | `multicompany_correction()` — patch create payloads for multi-company databases. |
| `references.py` | `ProductsReference` dataclass for product reference data. |
| `help_files.py` | `create_models_file()` — dump every `ir.model` of the instance to CSV/XLSX (the source of `odoo_tables.csv`). |
| `Domain.md` | Notes on Odoo domain syntax. |
| `msg_response_guides.md` | Notes on response message conventions. |

## Usage

```python
from odoo_apps.utils.cleaning import check_domains
from odoo_apps.utils.time_management import standarize_datetime

domains = check_domains(domain_fields="name", domain_operators="=",
                        vals={"name": "Laptop Pro"})
# → [('name', '=', 'Laptop Pro')]

utc_str = standarize_datetime("2026-06-15 10:00:00", "America/Mexico_City")
```

`__init__.py` re-exports the most used pieces: `generate_dict`,
`standarize_datetime`, `Operator`.

## Notes

- `cleaning.py` mixes domain logic with DataFrame/dict reshaping — candidates
  for a future split (`domains.py` vs `transforms.py`).
- `help_files.py` duplicates `create_models_file` defined at the bottom of
  `odoo_apps/client.py`; the utils version is the importable one.
