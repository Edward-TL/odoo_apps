

from datetime import datetime

import pytest
from dotenv import dotenv_values

from client import OdooClientServer
from apps.calendar import Scheduler
from apps.objects.calendar import Alarm

config = dotenv_values('./tests/test.env')
odoo = OdooClientServer(
    user_info = config
    )

scheduler = Scheduler(
    client = odoo
)

partners = [3, 35]

class TestScheduler:
    """
    Test Scheduler functions
    """

    # Crear un evento único
    def test_schedule_notification(self):
        alarms = [
            (
                0, 0, Alarm().export_to_dict()
            )
        ]

        event1_id = scheduler.create_calendar_event(
            name = "Reunión de equipo",
            start_datetime = datetime(2025, 4, 29, 16, 0, 0),
            end_datetime = datetime(2025, 4, 29, 17, 0, 0),
            partner_ids = partners, # IDs de los partners (contactos)
            alarm_ids = alarms,
            description = "Discusión sobre el proyecto actual.",
            location = "Sala de conferencias A"
        )
        
        print(f"Evento 1 creado con ID: {event1_id}")
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