"""
Offline unit tests for `SalesManager` (Phase 2.6).
"""
from odoo_apps.models import SALES
from odoo_apps.response import Response
from odoo_apps.sales.manager import SalesManager
from tests.fakes import FakeOdooClient, StubRecord


def _resp(model, code, obj=None):
    return Response(action="create", model=model, status_code=code, object=obj)


class TestCreateQuotation:
    def test_happy_path_no_multicompany(self):
        quotation = StubRecord(
            vals={"name": "Q1", "partner_id": 7}, name="Q1", product_lines=None
        )
        client = FakeOdooClient(create_result=_resp(SALES.ORDER, 201, 55))
        sm = SalesManager(client=client, preload=False)

        resp = sm.create_quotation(quotation)

        assert resp.status_code == 201
        assert quotation.id == 55
        call = client.calls[-1]
        assert call["model"] == SALES.ORDER
        assert call["kwargs"]["domains"] == [["name", "=", "Q1"]]
        # No multicompany fields -> no follow-up update call.
        assert [c["method"] for c in client.calls] == ["create"]

    def test_failure_path(self):
        quotation = StubRecord(vals={"name": "Q1"}, name="Q1", product_lines=None)
        client = FakeOdooClient(create_result=_resp(SALES.ORDER, 406, False))
        sm = SalesManager(client=client, preload=False)

        resp = sm.create_quotation(quotation)
        assert resp.status_code == 406
        assert quotation.id is False


def test_confirm_sale_order_calls_server_action():
    quotation = StubRecord(id=55)
    client = FakeOdooClient(execute_kw_result=True)
    sm = SalesManager(client=client, preload=False)

    result = sm.confirm_sale_order(quotation)

    assert result is True
    assert client.calls[-1] == {
        "method": "execute_kw",
        "model": SALES.ORDER,
        "kw": "action_confirm",
        "data": [55],
    }


def test_delete_quotation_delegates_to_client():
    quotation = StubRecord(id=55)
    client = FakeOdooClient(
        delete_result=Response(action="delete", model=SALES.ORDER,
                               status_code=200, object=True)
    )
    sm = SalesManager(client=client, preload=False)

    resp = sm.delete_quotation(quotation)
    assert resp.status_code == 200
    assert client.calls[-1] == {"method": "delete", "model": SALES.ORDER, "ids": 55}
