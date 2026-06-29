"""
``InProcessClient`` — an :class:`odoo_apps.client.OdooClient` look-alike that talks to a
live Odoo ``env`` instead of XML-RPC.

The whole point is *speed*: every call on a normal ``OdooClient`` is an XML-RPC round-trip
(serialize → HTTP → Odoo → deserialize). When the loader runs **inside** the Odoo process
(via ``odoo shell`` in the container), those round-trips disappear — we call the ORM
directly through :func:`odoo.api.call_kw`, which is exactly what the XML-RPC endpoint
dispatches to, minus the network.

Design: ``InProcessClient`` *subclasses* ``OdooClient`` and only swaps the transport. The
base class' ``search`` / ``read`` / ``search_read`` / ``create`` / ``update`` /
``get_models_fields`` / ``execute_kw`` methods funnel everything through ``self.models``
(an XML-RPC ``ServerProxy``). We replace ``self.models`` with :class:`_InProcModels`, a
shim exposing ``execute`` / ``execute_kw`` backed by ``call_kw``. Result: the existing
field-filtering, idempotent-dedup and ``Response`` logic is reused verbatim — no behavioural
drift between the RPC and in-process engines.
"""
from __future__ import annotations

from typing import Any, Optional

from odoo import SUPERUSER_ID  # type: ignore[import-not-found]
from odoo.models import BaseModel  # type: ignore[import-not-found]

try:  # Odoo <= 18 exposes call_kw on odoo.api
    from odoo.api import call_kw  # type: ignore[import-not-found]
except ImportError:  # Odoo 19 moved it to odoo.service.model
    from odoo.service.model import call_kw  # type: ignore[import-not-found]

from odoo_apps.client import OdooClient

# Methods that only read — they must NOT trigger a commit, and their results are already
# plain JSON-able data (lists/dicts) so they skip recordset→ids normalization for create.
_READONLY_METHODS = frozenset({
    "search", "read", "search_read", "search_count", "search_fetch", "fields_get",
    "name_search", "name_get", "default_get", "read_group", "_read_group",
    "get_views", "fields_view_get", "exists", "browse", "check_access_rights",
})


class _InProcModels:
    """
    Stand-in for ``OdooClient.models`` (an ``xmlrpc.client.ServerProxy``).

    Reproduces the two entry points the base client uses — ``execute`` (legacy, used by
    ``OdooClient.create``) and ``execute_kw`` (everything else) — by dispatching through
    :func:`odoo.api.call_kw`, which binds the first positional arg as record ids for record
    methods (e.g. ``write`` / ``action_post``) exactly like the XML-RPC layer.
    """

    def __init__(self, owner: "InProcessClient") -> None:
        self._owner = owner
        # fields_get is called once per create() on the base client; cache it per model so
        # it costs nothing after the first lookup.
        self._fields_cache: dict[str, Any] = {}

    @property
    def env(self):
        return self._owner.env

    # -- public surface mirroring xmlrpc.client.ServerProxy ----------------------------

    def execute_kw(self, db, uid, password, model, method, args, kwargs=None):
        return self._dispatch(model, method, list(args), dict(kwargs or {}))

    def execute(self, db, uid, password, model, method, *args):
        # Legacy positional form used by ``OdooClient.create`` (``models.execute(... , 'create', vals)``).
        return self._dispatch(model, method, list(args), {})

    # -- internals ---------------------------------------------------------------------

    def _dispatch(self, model: str, method: str, args: list, kwargs: dict):
        if method == "fields_get" and model in self._fields_cache:
            return self._fields_cache[model]

        result = call_kw(self.env[model], method, args, kwargs)
        result = self._normalize(method, args, result)

        if method == "fields_get":
            self._fields_cache[model] = result
        elif method not in _READONLY_METHODS:
            # odoo shell does NOT autocommit; the RPC transport commits per call. Mirror
            # that so each create/write/post is durable and re-runs stay idempotent, then
            # drop the ORM cache to bound memory across hundreds of records.
            self.env.cr.commit()
            invalidate = getattr(self.env, "invalidate_all", None)
            if invalidate is not None:
                invalidate()

        return result

    @staticmethod
    def _normalize(method: str, args: list, result: Any):
        """
        Match XML-RPC return shapes. The ORM hands back recordsets where XML-RPC returns
        ids: ``create`` → int (single dict) or list[int] (list of dicts); ``search`` and
        other record-returning methods → list[int]. Plain data (read/search_read/fields_get)
        passes through untouched.
        """
        if not isinstance(result, BaseModel):
            return result
        if method == "create":
            vals = args[0] if args else None
            if isinstance(vals, list):
                return result.ids
            return result.id if result else False
        return result.ids


class InProcessClient(OdooClient):
    """
    Drop-in ``OdooClient`` backed by a live Odoo ``env``.

    Build it inside ``odoo shell`` where ``env`` is in scope::

        client = InProcessClient(env)
        run_migration.run(args, client=client)

    Runs as superuser (a migration), with ``allowed_company_ids`` covering every company so
    multi-company (branch) creates/posts don't hit access errors, and with mail/tracking
    disabled for speed.
    """

    def __init__(
        self,
        env,
        *,
        performance_context: bool = True,
        all_companies: bool = True,
    ) -> None:
        # NOTE: we deliberately bypass OdooClient.__init__/__post_init__ (which would open an
        # XML-RPC connection). Only the small transport surface below is needed.
        ctx = dict(env.context)
        if performance_context:
            ctx.update(
                tracking_disable=True,
                mail_create_nolog=True,
                mail_notrack=True,
            )
        if all_companies:
            company_ids = env["res.company"].sudo().search([]).ids
            if company_ids:
                ctx["allowed_company_ids"] = company_ids

        self.env = env(user=SUPERUSER_ID, context=ctx)
        self.db = self.env.cr.dbname
        self.uid = self.env.uid
        self.password = "inproc"  # never used; present for API parity
        self.models = _InProcModels(self)

    # ``create_conection_with_server`` is the only base method that assumes XML-RPC; make it
    # a no-op so any accidental call (e.g. a reconnect helper) doesn't try to open a socket.
    def create_conection_with_server(self) -> None:  # noqa: D401 - parity with base name
        return None
