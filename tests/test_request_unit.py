"""
Offline unit tests for `request.py` (Phase 1.4).

The request dataclasses previously used `field(default_factory=['name'])`, which
raises `TypeError` on instantiation because a list is not callable.
"""


def test_request_module_imports():
    import odoo_apps.request  # noqa: F401


def test_read_request_default_fields():
    from odoo_apps.request import ReadRequest

    req = ReadRequest(model="res.partner", ids=[1, 2])
    assert req.fields == ["name"]


def test_search_read_request_default_fields():
    from odoo_apps.request import SearchReadRequest

    req = SearchReadRequest(model="res.partner")
    assert req.fields == ["name"]
    assert req.query == {"fields": ["name"]}
