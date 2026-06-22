"""
Offline unit test for `PosManager.day_sales` bounding (Phase 1.5).
"""
from odoo_apps.models import POS
from odoo_apps.pos.manager import PosManager
from tests.fakes import FakeOdooClient


def test_day_sales_bounds_the_calendar_day():
    client = FakeOdooClient(search_read_result=[])
    # preload=False so no ProductManager (and its many lookups) is built.
    pm = PosManager(client=client, preload=False)

    pm.day_sales("2026-06-12")

    call = client.calls[-1]
    assert call["method"] == "search_read"
    assert call["model"] == POS.ORDER_LINE
    domain = call["domain"]
    # Inclusive lower bound at day start, exclusive upper bound at next day.
    assert ["create_date", ">=", "2026-06-12 00:00:00"] in domain
    assert ["create_date", "<", "2026-06-13 00:00:00"] in domain


def test_day_sales_ignores_time_component():
    client = FakeOdooClient(search_read_result=[])
    pm = PosManager(client=client, preload=False)

    pm.day_sales("2026-06-12 15:30:00")

    domain = client.calls[-1]["domain"]
    assert ["create_date", ">=", "2026-06-12 00:00:00"] in domain
    assert ["create_date", "<", "2026-06-13 00:00:00"] in domain
