"""
Offline unit tests for the CRM `CrmManager`.
"""
from odoo_apps.models import CRM
from odoo_apps.crm.manager import CrmManager
from odoo_apps.response import Response
from tests.fakes import FakeOdooClient, StubRecord


def _resp(model, code, obj=None):
    return Response(action="create", model=model, status_code=code, object=obj)


class TestCreateLead:
    def test_happy_path(self):
        lead = StubRecord(
            vals={"name": "Cotización", "expected_revenue": 1500},
            domain=[("name", "=", "Cotización")],
        )
        client = FakeOdooClient(create_result=_resp(CRM.LEAD, 201, 11))
        manager = CrmManager(client=client, preload=False)

        resp = manager.create_lead(lead)

        assert resp.status_code == 201
        assert lead.id == 11
        assert client.calls[-1]["model"] == CRM.LEAD

    def test_failure_path(self):
        lead = StubRecord(vals={"name": "X"})
        client = FakeOdooClient(create_result=_resp(CRM.LEAD, 406, False))
        manager = CrmManager(client=client, preload=False)

        resp = manager.create_lead(lead)
        assert resp.status_code == 406
        assert lead.id is False


class TestCreateStage:
    def test_updates_cache(self):
        stage = StubRecord(vals={"name": "Nuevo"}, name="Nuevo")
        client = FakeOdooClient(create_result=_resp(CRM.STAGE, 201, 5))
        manager = CrmManager(client=client, preload=False, stages={})

        manager.create_stage(stage)
        assert manager.stages["Nuevo"] == 5
        assert client.calls[-1]["model"] == CRM.STAGE
