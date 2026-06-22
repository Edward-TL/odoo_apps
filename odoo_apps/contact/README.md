# `odoo_apps.contact` — Contacts (`res.partner`)

Wrapper around Odoo's contact model. Provides a `Partner` record object and a
small `ContactBook` lookup helper.

## Files

| File | Purpose |
|------|---------|
| `objects.py` | Curated `Partner` dataclass (the fields you actually set: name, email, phone, company flags…), with `export_to_dict()` and `upload(odoo)` to create itself through an `OdooClient`. Loads field documentation from `docs.md` into the class docstring via `load_docstring_from_md()`. |
| `raw_objects.py` | The **full** `Partner` dataclass with every `res.partner` field, kept as generated reference. Prefer `objects.py` in application code. |
| `book.py` | `ContactBook`: `get_contact_id(name/phone/...)` and `check_register_contacts(references, by_field='phone')` — resolve or batch-verify contacts by a reference field. |
| `docs.md` | Markdown documentation of `res.partner` fields (consumed at import time). |

## Usage

```python
from odoo_apps.contact.book import ContactBook
from odoo_apps.contact.objects import Partner

cb = ContactBook(client=client)
partner_id = cb.get_contact_id("John Doe")
missing = cb.check_register_contacts(["+521234567890"], by_field="phone")

partner = Partner(name="John Doe", email="john@example.com", phone="+521234567890")
response = partner.upload(client)   # Response with created/found id
```

## Notes

- `Partner.upload()` relies on `client.create()`'s idempotent behavior — an
  existing partner with the same name returns `200` with its id instead of a duplicate.
- The `raw_objects.py` / `objects.py` split (full generated mirror vs. curated
  subset) is a pattern shared with [`sales/`](../sales/README.md).
