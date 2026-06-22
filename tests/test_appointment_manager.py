"""
Integration tests for `AppointmentManager` against a live Odoo database.

Marked `live`: skipped in the default offline run. Run with: pytest -m live

NOTE: pre-existing integration test. Construction moved into the `odoo` fixture;
body otherwise unchanged and not re-validated against a database here.
"""
from datetime import datetime, timedelta
import json

import pytest

from odoo_apps.appointment.manager import AppointmentManager

pytestmark = pytest.mark.live

DOCTOR_APPT_TYPE = 4
DOCTOR_RESOURCE_ID = 1


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
        hour=11,
    )


class TestAppointmentManager:
    """Class that tests the Appointment manager."""

    def test_book_appointment(self, odoo):
        appointment_date_test = create_test_date()

        request_test = {
            'event_start': appointment_date_test,
            'event_stop': appointment_date_test + timedelta(hours=1),
            'appointment_type_id': DOCTOR_APPT_TYPE,
            'appointment_resource_id': DOCTOR_RESOURCE_ID,
            'timezone_str': 'UTC',
            'partner_id': 3,
            'name': f'Prueba de RPC {appointment_date_test.strftime("%Y-%m-%d %H:%M")}',
        }

        appt_manager = AppointmentManager(odoo)
        test_appt = appt_manager.extract_appointment_data(request_test)
        test_appt_data = test_appt.event.data

        response = appt_manager.book_appointment(test_appt, printer=False)

        appt_response = json.loads(response.get_data())
        check = [
            str(type(response)) == "<class 'flask.wrappers.Response'>",
            isinstance(appt_response, dict),
            'request' in appt_response,
            test_appt_data['name'] == request_test['name'],
            appt_response['response']['http_status'] in [201, 200],
            appt_response['response']['object'] > 0,
            appt_response['response']['model'] == 'appointment.booking.line',
            appt_response['success'] is True,
        ]
        assert all(check)
