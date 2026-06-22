"""
Offline unit tests for the MRP `Factory` manager (Phase 2.6).
"""
from odoo_apps.models import MANUFACTORY
from odoo_apps.mrp.manager import Factory
from odoo_apps.response import Response
from tests.fakes import FakeOdooClient, StubRecord


def _resp(model, code, obj=None):
    return Response(action="create", model=model, status_code=code, object=obj)


class TestCreateBom:
    def test_happy_path(self):
        bom = StubRecord(vals={"product_tmpl_id": 42, "product_qty": 1},
                         domain=[("product_tmpl_id", "=", 42)])
        client = FakeOdooClient(create_result=_resp(MANUFACTORY.BOM, 201, 7))
        factory = Factory(client=client)

        resp = factory.create_bom(bom)

        assert resp.status_code == 201
        assert bom.id == 7
        call = client.calls[-1]
        assert call["model"] == MANUFACTORY.BOM
        assert call["vals"] == {"product_tmpl_id": 42, "product_qty": 1}

    def test_failure_path(self):
        bom = StubRecord(vals={"product_tmpl_id": 42})
        client = FakeOdooClient(create_result=_resp(MANUFACTORY.BOM, 406, False))
        factory = Factory(client=client)

        resp = factory.create_bom(bom)
        assert resp.status_code == 406
        assert bom.id is False


class TestProductionOrder:
    def test_create_production_order_happy_path(self):
        order = StubRecord(vals={"product_id": 42, "product_qty": 10})
        client = FakeOdooClient(create_result=_resp(MANUFACTORY.PRODUCTION, 201, 3))
        factory = Factory(client=client)

        resp = factory.create_production_order(order)
        assert resp.status_code == 201
        assert order.id == 3
        assert client.calls[-1]["model"] == MANUFACTORY.PRODUCTION

    def test_confirm_production_order_calls_server_action(self):
        client = FakeOdooClient(execute_kw_result=True)
        factory = Factory(client=client)

        result = factory.confirm_production_order(3)

        assert result is True
        assert client.calls[-1] == {
            "method": "execute_kw",
            "model": MANUFACTORY.PRODUCTION,
            "kw": "action_confirm",
            "data": [3],
        }

    def test_check_components_availability_calls_assign(self):
        client = FakeOdooClient(execute_kw_result=True)
        factory = Factory(client=client)

        factory.check_components_availability([3, 4])
        assert client.calls[-1]["kw"] == "action_assign"
        assert client.calls[-1]["data"] == [3, 4]


class TestDeleteBom:
    def test_delete_bom_delegates_to_client(self):
        client = FakeOdooClient(
            delete_result=Response(action="delete", model=MANUFACTORY.BOM,
                                   status_code=200, object=True)
        )
        factory = Factory(client=client)

        resp = factory.delete_bom([1, 2])
        assert resp.status_code == 200
        assert client.calls[-1] == {
            "method": "delete", "model": MANUFACTORY.BOM, "ids": [1, 2]
        }
