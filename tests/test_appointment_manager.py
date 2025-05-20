"""
APPOINTMENT MANAGER tests
"""
from datetime import datetime, timedelta

import pytest
from dotenv import dotenv_values

from odoo_apps.client import OdooClientServer
from odoo_apps.appointment.appt_manager import AppointmentManager
from constants.account import DOCTOR_APPT_TYPE, DOCTOR_RESOURCE_ID

config = dotenv_values('./tests/test.env')
odoo = OdooClientServer(
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
        hour = 17
    )


test_appt_manager = AppointmentManager(odoo)

class TestAppointmentManager:
    """
    Class that tests Appointment manager class
    """
    def test_book_appointment(self):
        appointment_date_test = create_test_date()

        test_appt = test_appt_manager.extract_appointment_data(
            {
                'event_start': appointment_date_test,
                'event_stop': appointment_date_test + timedelta(hours = 1),
                'appointment_type_id': DOCTOR_APPT_TYPE,
                'appointment_resource_id': DOCTOR_RESOURCE_ID,
                'name': 'Prueba de RPC 5'
            }
        )

        appt_response = test_appt_manager.book_appointment(test_appt)
        check = [
            isinstance(appt_response, dict),
            'request' in appt_response,
            appt_response['request']['event_start'] == test_appt['event_start'],
            appt_response['request']['event_stop'] == test_appt['event_stop'],   
            appt_response['request']['name'] == test_appt['name'],

            appt_response['response']['http_status'] in [201, 200],
            appt_response['response']['object_id'] > 0
        ]

        assert all(check)
