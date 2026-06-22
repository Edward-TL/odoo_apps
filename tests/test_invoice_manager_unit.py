"""
Offline unit tests for the `InvoiceManager` (account.move customer invoices).
"""
from odoo_apps.models import ACCOUNT
from odoo_apps.account.manager import InvoiceManager
from odoo_apps.response import Response
from tests.fakes import FakeOdooClient, StubRecord


def _resp(model, code, obj=None):
    return Response(action="create", model=model, status_code=code, object=obj)


class TestCreateInvoice:
    def test_happy_path_draft(self):
        invoice = StubRecord(
            vals={"partner_id": 5, "ref": "NOTA-1"},
            domain=[("ref", "=", "NOTA-1")],
        )
        client = FakeOdooClient(create_result=_resp(ACCOUNT.MOVE, 201, 9))
        manager = InvoiceManager(client=client)

        resp = manager.create_invoice(invoice)

        assert resp.status_code == 201
        assert invoice.id == 9
        assert client.calls[-1]["model"] == ACCOUNT.MOVE
        # No posting requested -> last call is the create
        assert client.calls[-1]["method"] == "create"

    def test_post_triggers_action_post_with_wrapped_ids(self):
        invoice = StubRecord(vals={"ref": "NOTA-2"})
        client = FakeOdooClient(create_result=_resp(ACCOUNT.MOVE, 201, 10))
        # create_invoice reads the state and only posts drafts.
        client.read = lambda model, ids, fields=None: [{"state": "draft"}]
        manager = InvoiceManager(client=client)

        manager.create_invoice(invoice, post=True)

        last = client.calls[-1]
        assert last["method"] == "execute_kw"
        assert last["kw"] == "action_post"
        # recordset method => ids wrapped once
        assert last["data"] == [[10]]

    def test_does_not_repost_already_posted(self):
        invoice = StubRecord(vals={"ref": "NOTA-3"})
        client = FakeOdooClient(create_result=_resp(ACCOUNT.MOVE, 200, 12))
        client.read = lambda model, ids, fields=None: [{"state": "posted"}]
        manager = InvoiceManager(client=client)

        manager.create_invoice(invoice, post=True)

        # An already-posted invoice must NOT be posted again.
        assert all(c.get("kw") != "action_post" for c in client.calls)
