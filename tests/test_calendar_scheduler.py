

from datetime import datetime, timedelta

import pytest
from dotenv import dotenv_values

from odoo_apps.client import OdooClient
from odoo_apps.calendar import Scheduler
from odoo_apps.calendar.objects import Event, BASIC_ALARM

config = dotenv_values('./tests/test.env')
odoo = OdooClient(
    user_info = config
    )

scheduler = Scheduler(
    client = odoo
)

partners = [3, 35]

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
        hour = 15
    )
class TestScheduler:
    """
    Test Scheduler functions
    """

    # Crear un evento único
    def test_schedule_notification(self):
        
        event_test_day = create_test_date()

        response = scheduler.create_calendar_event(
            event = Event(
                name = "prueba de evento",
                start_datetime = event_test_day,
                end_datetime = event_test_day + timedelta(hours = 1),
                partner_ids = partners, # IDs de los partners (contactos)
                alarm_ids = BASIC_ALARM,
                description = "Discusión sobre el proyecto actual.",
                location = "Sala de conferencias A",
                timezone_str = "UTC",
            )
        )
        event1_id = response.object
        print(f"Evento de prueba creado con ID: {event1_id}")
        assert event1_id > 0

    # # Crear un evento recurrente semanalmente durante 4 semanas
    # start_recurring = datetime(2025, 5, 15, 14, 0, 0)
    # end_recurring = datetime(2025, 5, 15, 15, 0, 0)
    # recurrence_until = datetime(2025, 6, 5, 15, 0, 0) # Última fecha (inclusive)

    # event2_id = scheduler.create_calendar_event(
    #     name="Revisión semanal",
    #     start_datetime=start_recurring,
    #     end_datetime=end_recurring,
    #     recurrency=True,
    #     rrule_type='weekly',
    #     interval=1,
    #     until=recurrence_until
    # )
    # if event2_id:
    #     print(f"Evento recurrente creado con ID: {event2_id}")    