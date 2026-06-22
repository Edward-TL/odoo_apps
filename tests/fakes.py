"""
Lightweight, offline test doubles.

These avoid any network / XML-RPC connection so the correctness fixes can be
regression-tested without a live Odoo instance. This is the seed of
IMPROVEMENT_PLAN Phase 2.1 (`FakeOdooClient`).
"""
from __future__ import annotations

from typing import Any, Optional

from odoo_apps.client import OdooClient
from odoo_apps.response import Response


class FakeServerProxy:
    """
    Stand-in for the xmlrpc `models` ServerProxy used by `OdooClient`.

    Records every call on ``self.calls`` and returns a preconfigured ``result``
    (or raises ``raises``), so a single client/manager method can be exercised
    in isolation.
    """

    def __init__(self, result: Any = True, raises: Optional[BaseException] = None):
        self.result = result
        self.raises = raises
        self.calls: list[dict] = []

    def execute_kw(self, db, uid, password, model, method, args, kwargs=None):
        self.calls.append(
            {
                "api": "execute_kw",
                "model": model,
                "method": method,
                "args": args,
                "kwargs": kwargs,
            }
        )
        if self.raises is not None:
            raise self.raises
        return self.result

    def execute(self, db, uid, password, model, method, vals):
        self.calls.append(
            {"api": "execute", "model": model, "method": method, "vals": vals}
        )
        if self.raises is not None:
            raise self.raises
        return self.result


def make_client(models: FakeServerProxy) -> OdooClient:
    """
    Build an `OdooClient` without opening a connection, wired to a fake proxy.

    Bypasses ``__init__`` (and therefore ``__post_init__``/authentication) and
    sets only the attributes the CRUD methods read.
    """
    client = OdooClient.__new__(OdooClient)
    client.db = "test-db"
    client.uid = 1
    client.password = "test-key"
    client.models = models
    return client


class FakeOdooClient:
    """
    Minimal reimplementation of the `OdooClient` surface that managers use.

    Only the methods managers actually call are provided. ``create`` returns the
    preconfigured ``create_result`` Response; ``search`` / ``search_read`` return
    their preconfigured payloads. Every call is recorded on ``self.calls``.
    """

    def __init__(
        self,
        *,
        create_result: Optional[Response] = None,
        update_result: Optional[Response] = None,
        delete_result: Optional[Response] = None,
        execute_kw_result: Any = True,
        search_result: Optional[list] = None,
        search_read_result: Optional[list] = None,
        models: Optional[FakeServerProxy] = None,
    ):
        self.db = "test-db"
        self.uid = 1
        self.password = "test-key"
        self.models = models or FakeServerProxy()
        self._create_result = create_result
        self._update_result = update_result
        self._delete_result = delete_result
        self._execute_kw_result = execute_kw_result
        self._search_result = search_result if search_result is not None else []
        self._search_read_result = (
            search_read_result if search_read_result is not None else []
        )
        self.calls: list[dict] = []

    def search(self, model, domain):
        self.calls.append({"method": "search", "model": model, "domain": domain})
        return self._search_result

    def search_read(self, model, domain=None, fields=None, limit=None, order=None):
        self.calls.append(
            {
                "method": "search_read",
                "model": model,
                "domain": domain,
                "fields": fields,
                "limit": limit,
                "order": order,
            }
        )
        return self._search_read_result

    def get_models_fields(self, model, attributes=False):
        self.calls.append({"method": "get_models_fields", "model": model})
        return ()

    def create(self, model, vals, **kwargs):
        self.calls.append(
            {"method": "create", "model": model, "vals": vals, "kwargs": kwargs}
        )
        return self._create_result

    def update(self, model, records_ids, new_vals, printer=False):
        self.calls.append(
            {
                "method": "update",
                "model": model,
                "records_ids": records_ids,
                "new_vals": new_vals,
            }
        )
        return self._update_result

    def delete(self, model, ids, printer=False):
        self.calls.append({"method": "delete", "model": model, "ids": ids})
        return self._delete_result

    def execute_kw(self, model, kw, data, *args, **kwargs):
        self.calls.append(
            {"method": "execute_kw", "model": model, "kw": kw, "data": data}
        )
        return self._execute_kw_result


class StubRecord:
    """
    Minimal stand-in for the record objects managers consume.

    Exposes the trio every object-consuming manager touches: a search
    ``domain``, an ``export_to_dict()`` payload, and a writable ``id``. Extra
    attributes (e.g. ``name``, ``product_lines``) can be passed as kwargs.
    """

    def __init__(self, vals=None, domain=None, **attrs):
        self._vals = vals or {}
        self.domain = domain if domain is not None else [("name", "=", "stub")]
        self.id = None
        for key, value in attrs.items():
            setattr(self, key, value)

    def export_to_dict(self, *args, **kwargs):
        return dict(self._vals)
