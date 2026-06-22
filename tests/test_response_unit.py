"""
Offline unit tests for `Response` status derivation (Phase 2.4).
"""
from odoo_apps.response import Response


def test_status_code_derives_status_and_default_msg():
    r = Response(action="create", model="x", status_code=201)
    assert r.status == "CREATED"
    assert r.msg == "Success on creating"


def test_status_derives_status_code():
    r = Response(action="read", model="x", status="OK")
    assert r.status_code == 200


def test_complete_response_sets_fields():
    r = Response(action="update", model="x")
    r.complete_response(obj_id=[5], status=201)
    assert r.status_code == 201
    assert r.status == "CREATED"
    assert r.object == [5]


def test_complete_response_custom_message_preserved():
    r = Response(action="create", model="x")
    r.complete_response(obj_id=False, status=406, msg="boom")
    assert r.status_code == 406
    assert r.msg == "boom"


def test_get_data_shape():
    r = Response(action="create", model="x", status_code=201, object=3)
    data = r.get_data()
    assert data["action"] == "create"
    assert data["status_code"] == 201
    assert data["object"] == 3
