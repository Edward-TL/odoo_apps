"""
Offline unit tests for `AccountManager` (Phase 2.6).
"""
from odoo_apps.account.manager import AccountManager
from odoo_apps.models import ACCOUNT
from odoo_apps.response import Response
from tests.fakes import FakeOdooClient, StubRecord


def _resp(code, obj=None):
    return Response(action="create", model=ACCOUNT.ACCOUNT, status_code=code, object=obj)


def test_create_account_happy_path():
    account = StubRecord(
        vals={"code": "601", "name": "Software"}, domain=[("code", "=", "601")]
    )
    client = FakeOdooClient(create_result=_resp(201, 99))
    am = AccountManager(client=client)

    resp = am.create_account(account)

    assert resp.status_code == 201
    assert account.id == 99
    call = client.calls[-1]
    assert call["method"] == "create"
    assert call["model"] == ACCOUNT.ACCOUNT
    assert call["vals"] == {"code": "601", "name": "Software"}
    assert call["kwargs"]["domains"] == [("code", "=", "601")]


def test_create_account_failure_path():
    account = StubRecord(vals={"code": "X"}, domain=[("code", "=", "X")])
    client = FakeOdooClient(create_result=_resp(406, False))
    am = AccountManager(client=client)

    resp = am.create_account(account)

    assert resp.status_code == 406
    assert account.id is False
