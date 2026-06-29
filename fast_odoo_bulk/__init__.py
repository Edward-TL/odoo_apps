"""
fast_odoo_bulk — fast bulk loading into Odoo.

Two pieces, used together:

- :class:`~fast_odoo_bulk.client.InProcessClient` — an ``OdooClient`` look-alike backed by a
  live Odoo ``env`` (run inside ``odoo shell``), so an existing RPC-based ETL runs in-process
  with zero XML-RPC overhead and full ORM integrity. Importing it requires the Odoo runtime.
- :mod:`fast_odoo_bulk.launcher` — host-side helper that pipes an entrypoint into a
  container's ``odoo shell``. Importable without Odoo.
- :mod:`fast_odoo_bulk.pg_read` — optional Postgres read/verify helpers (never writes).

``InProcessClient`` is exposed lazily so ``launcher`` / ``pg_read`` stay importable on a host
that has no Odoo installed.
"""
from __future__ import annotations

__all__ = ["InProcessClient", "launcher", "pg_read"]


def __getattr__(name):
    if name == "InProcessClient":
        from .client import InProcessClient

        return InProcessClient
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
