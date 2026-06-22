"""
Offline unit tests for `PosManager.register_sale` (pos.order creation).
"""
from odoo_apps.models import POS
from odoo_apps.pos.manager import PosManager
from odoo_apps.response import Response
from tests.fakes import FakeOdooClient, StubRecord


def _resp(model, code, obj=None):
    return Response(action="create", model=model, status_code=code, object=obj)


class TestRegisterSale:
    def test_happy_path(self):
        order = StubRecord(
            vals={"session_id": 1, "pos_reference": "REF-1"},
            domain=[("pos_reference", "=", "REF-1")],
        )
        client = FakeOdooClient(create_result=_resp(POS.ORDER, 201, 21))
        # preload=False so __post_init__ does not build a ProductManager
        manager = PosManager(client=client, preload=False)

        resp = manager.register_sale(order)

        assert resp.status_code == 201
        assert order.id == 21
        assert client.calls[-1]["model"] == POS.ORDER
        assert client.calls[-1]["vals"] == {"session_id": 1, "pos_reference": "REF-1"}


class TestOpenSession:
    def test_reuses_existing_open_session(self):
        client = FakeOdooClient(search_read_result=[{"id": 7, "state": "opened"}])
        manager = PosManager(client=client, preload=False)

        session_id = manager.open_session(config_id=3)
        assert session_id == 7
