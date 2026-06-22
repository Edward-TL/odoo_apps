"""
Offline unit tests for `ProductManager.create_category` (Phase 2.6).

ProductManager is large and preload-heavy; constructing it with `preload=False`
and a seeded `categories={}` exercises the category-creation path without any
network lookups.
"""
from odoo_apps.models import PRODUCT
from odoo_apps.product.manager import ProductManager
from odoo_apps.response import Response
from tests.fakes import FakeOdooClient


def _resp(code, obj=None):
    return Response(action="create", model=PRODUCT.CATEGORY, status_code=code, object=obj)


def _manager(client):
    return ProductManager(client=client, preload=False, categories={})


def test_create_category_happy_path_caches_id():
    client = FakeOdooClient(create_result=_resp(201, 7))
    pm = _manager(client)

    resp = pm.create_category("Electronics")

    assert resp.status_code == 201
    assert pm.categories["Electronics"] == 7
    call = client.calls[-1]
    assert call["model"] == PRODUCT.CATEGORY
    assert call["vals"] == {"name": "Electronics"}
    assert call["kwargs"]["domains"] == [["name", "=", "Electronics"]]


def test_create_category_with_parent_adds_domain():
    client = FakeOdooClient(create_result=_resp(201, 8))
    pm = _manager(client)

    pm.create_category("Phones", parent_id=7)

    call = client.calls[-1]
    assert call["vals"] == {"name": "Phones", "parent_id": 7}
    assert ["parent_id", "=", 7] in call["kwargs"]["domains"]


def test_create_category_failure_does_not_cache():
    client = FakeOdooClient(create_result=_resp(406, False))
    pm = _manager(client)

    resp = pm.create_category("Bad")
    assert resp.status_code == 406
    assert "Bad" not in pm.categories
