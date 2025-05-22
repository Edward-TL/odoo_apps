"""
APPOINTMENT MANAGER tests
"""
from datetime import datetime, timedelta

import pytest
from dotenv import dotenv_values
import json

from odoo_apps.client import OdooClient
from odoo_apps.appointment.manager import AppointmentManager


DOCTOR_APPT_TYPE = 4
DOCTOR_RESOURCE_ID = 1 

config = dotenv_values('./tests/test.env')
odoo = OdooClient(
    user_info = config
    )
def create_test_date() -> datetime:
    """
    function made only to return a weekday on work hours
    """
    date = datetime.today()
    appoinment_day = 0
    if date.weekday() < 4:
        appoinment_day = int(date.day) + 1
    else:
        appoinment_day = int(date.day) + (7 - date.weekday())

    return datetime(
        year = date.year,
        month = date.month,
        day = appoinment_day,
        hour = 11
    )


test_appt_manager = AppointmentManager(odoo)

class TestAppointmentManager:
    """
    Class that tests Appointment manager class
    """
    def test_book_appointment(self):
        appointment_date_test = create_test_date()

        request_test = {
            'event_start': appointment_date_test,
            'event_stop': appointment_date_test + timedelta(hours = 1),
            'appointment_type_id': DOCTOR_APPT_TYPE,
            'appointment_resource_id': DOCTOR_RESOURCE_ID,
            'timezone_str': 'UTC',
            'partner_id': 3,
            'name': f'Prueba de RPC {appointment_date_test.strftime("%Y-%m-%d %H:%M")}'
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
            
            appt_response['success'] is True
        ]

        for n, c in enumerate(check):
            print("test_book_appointment checks")
            print(n, c)
        assert all(check)
