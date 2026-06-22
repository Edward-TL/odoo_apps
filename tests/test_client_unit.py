"""
Offline unit tests for `OdooClient` correctness fixes (Phase 1.1 & 1.3).

Run with: pytest tests/test_client_unit.py
"""
import inspect

from odoo_apps.client import OdooClient
from odoo_apps.response import Response
from tests.fakes import FakeServerProxy, make_client


class TestUpdateReturnsResponse:
    """Phase 1.1: `update()` must return a `Response` on every path."""

    def test_success_returns_201(self):
        client = make_client(FakeServerProxy(result=True))
        resp = client.update("res.partner", 5, {"name": "X"})
        assert isinstance(resp, Response)
        assert resp.status_code == 201
        assert resp.object == [5]

    def test_falsy_write_returns_response_not_none(self):
        # Regression: `write` returned a falsy value without raising, and the
        # method fell through and returned None.
        client = make_client(FakeServerProxy(result=False))
        resp = client.update("res.partner", 5, {"name": "X"})
        assert resp is not None
        assert isinstance(resp, Response)
        assert resp.status_code == 406

    def test_exception_returns_406_with_message(self):
        client = make_client(FakeServerProxy(raises=Exception("boom")))
        resp = client.update("res.partner", 5, {"name": "X"})
        assert isinstance(resp, Response)
        assert resp.status_code == 406
        assert "boom" in resp.msg


class TestSearchReadDefaults:
    """Phase 1.3: no mutable default argument for `domain`."""

    def test_domain_default_is_none(self):
        sig = inspect.signature(OdooClient.search_read)
        assert sig.parameters["domain"].default is None

    def test_default_domain_applied_each_call(self):
        proxy = FakeServerProxy(result=[])
        client = make_client(proxy)

        client.search_read("res.partner", fields=["name"])
        client.search_read("res.partner", fields=["name"])

        # Both calls fall back to the catch-all domain, unshared/unmutated.
        for call in proxy.calls:
            assert call["method"] == "search_read"
            assert call["args"] == [[("id", ">", 0)]]
