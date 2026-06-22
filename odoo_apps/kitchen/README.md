# `odoo_apps.kitchen` — Restaurant Kitchen Orders (WIP)

**Prototype module — not ready for use.** Intended to manage restaurant kitchen
order flow (receive an order payload, create/update its state in Odoo POS).

## Files

| File | Purpose |
|------|---------|
| `gemini_idea.py` | AI-generated draft (in Spanish): `procesar_orden_cocina(odoo_client, payload)` and `actualizar_estado_orden(odoo_client, payload)` sketching how kitchen orders would map to Odoo POS models. |
| `manager.py` | Empty placeholder — the future `KitchenManager`. |
| `objects.py` | Empty placeholder — future kitchen order dataclasses. |

## Status & next steps

Nothing here is wired into the package's public API. To productionize:

1. Define the order/line dataclasses in `objects.py` following the library
   pattern (`export_to_dict()`, type hints).
2. Port the logic from `gemini_idea.py` into a `KitchenManager` dataclass using
   `RPCHandlerMetaclass` and returning `Response` objects.
3. Add tests and delete `gemini_idea.py`.
