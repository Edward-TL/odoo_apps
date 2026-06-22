"""
Integration tests for the calendar `Scheduler` against a live Odoo database.

Marked `live`: skipped in the default offline run. Run with: pytest -m live

NOTE: pre-existing integration test. Construction moved into the `scheduler`
fixture; body otherwise unchanged and not re-validated against a database here.
"""
from datetime import datetime, timedelta

import pytest

from odoo_apps.calendar.objects import Event, BASIC_ALARM

pytestmark = pytest.mark.live

partners = [3, 35]


def create_test_date() -> datetime:
    """Return a weekday during working hours."""
    date = datetime.today()
    if date.weekday() < 4:
        appoinment_day = int(date.day) + 1
    else:
        appoinment_day = int(date.day) + (7 - date.weekday())

    return datetime(
        year=date.year,
        month=date.month,
        day=appoinment_day,
        hour=15,
    )


class TestScheduler:
    """Test Scheduler functions."""

    def test_schedule_notification(self, scheduler):
        event_test_day = create_test_date()

        response = scheduler.create_calendar_event(
            event=Event(
                name="prueba de evento",
                start_datetime=event_test_day,
                end_datetime=event_test_day + timedelta(hours=1),
                standarized_datetime=False,
                partner_ids=partners,
                alarm_ids=BASIC_ALARM,
                description="Discusión sobre el proyecto actual.",
                location="Sala de conferencias A",
                timezone_str="UTC",
            )
        )
        event1_id = response.object
        assert event1_id > 0
