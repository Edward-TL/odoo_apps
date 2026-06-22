"""
Offline unit tests for `StockManager` correctness fixes (Phase 1.2 & 1.6).
"""
from odoo_apps.response import Response
from odoo_apps.stock.manager import StockManager
from tests.fakes import FakeOdooClient, FakeServerProxy


def _ready_manager(client) -> StockManager:
    # Provide every id so __post_init__ performs no client lookups.
    return StockManager(
        client=client,
        picking_type_id=1,
        location_src_id=8,
        location_dest_id=9,
        internal_stock_id=5,
    )


class TestCreatePickingOrder:
    """Phase 1.2: must return its `Response` and reflect confirm failures."""

    def test_returns_response_on_confirm_success(self):
        created = Response(action="create", model="stock.picking",
                           status_code=201, object=42)
        client = FakeOdooClient(create_result=created,
                                models=FakeServerProxy(result=True))
        resp = _ready_manager(client).create_picking_order([[0, 0, {}]])
        assert isinstance(resp, Response)
        assert resp.status_code == 201
        assert resp.object == 42

    def test_confirm_failure_reflected_in_response(self):
        # Regression: action_confirm failure was only printed and the method
        # returned None.
        created = Response(action="create", model="stock.picking",
                           status_code=201, object=42)
        client = FakeOdooClient(create_result=created,
                                models=FakeServerProxy(result=False))
        resp = _ready_manager(client).create_picking_order([[0, 0, {}]])
        assert resp is not None
        assert resp.status_code == 406
        assert "action_confirm" in resp.msg

    def test_creation_failure_returned_as_is(self):
        failed = Response(action="create", model="stock.picking",
                          status_code=406, msg="nope")
        client = FakeOdooClient(create_result=failed,
                                models=FakeServerProxy(result=True))
        resp = _ready_manager(client).create_picking_order([[0, 0, {}]])
        assert resp.status_code == 406
        # Confirmation must not have been attempted.
        assert client.models.calls == []


def test_post_init_is_silent(capsys):
    """Phase 1.6: construction must not print debug output."""
    _ready_manager(FakeOdooClient())
    assert capsys.readouterr().out == ""
