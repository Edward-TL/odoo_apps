"""
Shared pytest fixtures.

Offline unit tests use the in-memory doubles in ``tests.fakes`` and need none of
these fixtures. Integration tests are marked ``@pytest.mark.live`` and depend on
``odoo`` (and the manager fixtures derived from it), which connects to the
database described in ``tests/test.env``. When that file is missing or the
connection fails, the live fixtures **skip** (never error), so the default
offline suite stays green.

Run the live suite explicitly with: ``pytest -m live``.
"""
import os

import pytest


def _load_credentials():
    """Read Odoo credentials from tests/test.env (or repo-root test.env)."""
    from dotenv import dotenv_values

    here = os.path.dirname(__file__)
    candidates = [
        os.path.join(here, "test.env"),
        os.path.join(here, os.pardir, "test.env"),
    ]
    for path in candidates:
        if os.path.exists(path):
            values = dotenv_values(path)
            if values:
                return values
    return None


@pytest.fixture(scope="session")
def odoo_credentials():
    creds = _load_credentials()
    if not creds:
        pytest.skip("No test.env found — skipping live integration tests.")
    return creds


@pytest.fixture(scope="session")
def odoo(odoo_credentials):
    """A connected `OdooClient`, or skip if the instance is unreachable."""
    from odoo_apps.client import OdooClient

    try:
        return OdooClient(user_info=odoo_credentials)
    except Exception as exc:  # noqa: BLE001 - any auth/connection failure -> skip
        pytest.skip(f"Could not connect to Odoo for live tests: {exc}")


@pytest.fixture
def stock_manager(odoo):
    from odoo_apps.stock.manager import StockManager

    return StockManager(client=odoo)


@pytest.fixture
def scheduler(odoo):
    from odoo_apps.calendar import Scheduler

    return Scheduler(client=odoo)


@pytest.fixture
def appointment_manager(odoo):
    from odoo_apps.appointment.manager import AppointmentManager

    return AppointmentManager(odoo)
