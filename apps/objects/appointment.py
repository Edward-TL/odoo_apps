"""
"""
from dataclasses import dataclass
from typing import Literal
from datetime import datetime

from constants.account import PARTNER_ID, DOCTOR_RESOURCE_ID, DOCTOR_APPT_TYPE
from .time_management import standarize_datetime
from .calendar import Event, Alarm, BASIC_ALARM

ActivityExceptionDecorator = Literal['warning', 'danger']
ActivityState = Literal['overdue', 'today', 'planned']
AppointmentCategory = Literal[
    'recurring', # Regular
    'punctual', # Punctual
    'custom', # Specific Slots
    'anytime' # Shared Calendar'
]
AvatarsDisplay = Literal['hide', 'show']
AssignMethod = Literal[
    'resource_time', #'Pick User/Resource then Time
    'time_resource', #'Select Time then User/Resource
    'time_auto_assign' #'Select Time then auto-assign
]
# apps/objects/appointment.py
# Definiciones de tipos literales si son necesarios para campos específicos
# (Aunque para appointment.appointment, muchos campos son IDs o strings/datetimes)
AppointmentTz = Literal[
    'America/Mexico_City',
    'America/Monterrey',
    'UTC'
    ] # Añade más si es necesario

EventVideocallSource = Literal['discuss', 'google_meet'] #Discuss is Odoo Discuss
CategoryTimeDisplay = Literal[
    'recurring_fields', # Available now
    'punctual_fields', # Withina a date range
]
RecurreceRuleType = Literal['daily', 'weekly', 'monthly', 'yearly']
ShowAs = Literal['busy', 'free']

@dataclass
class Appointment:
    """
    Class representing an Appointment object to interact with Odoo's
    appointment.appointment model.

    Args:
        * start_datetime (datetime): Datetime object for the start time (in the specified timezone).
        * end_datetime (datetime): Datetime object for the end time (in the specified timezone).
        * name (str, optional): The title of the appointment. Odoo often generates this.
            Defaults to None.
        * resource_id (int, optional): The ID of the resource booked (e.g., a room, equipment).
            Defaults to None to consider "all resources available".
        * appointment_type_id (int): The ID of the appointment type (e.g., Consultation, Meeting).
        * partner_id (int): The ID of the main partner/customer for the appointment.
        * location (str, optional): The location of the appointment. Defaults to "".
        * description (str, optional): Detailed description of the appointment. Defaults to "".
        * timezone_str (AppointmentTz, optional): The timezone of the appointment.
            Defaults to 'America/Mexico_City'.
        * odoo_id (int, optional): The ID of the appointment in Odoo (assigned after creation).
            Defaults to None.
    """
    start_datetime: datetime
    end_datetime: datetime
    name: str = 'Consulta' # Odoo often generates the name
    resource_id: int = DOCTOR_RESOURCE_ID
    type_id: int = DOCTOR_APPT_TYPE
    partner_id: int = PARTNER_ID
    location: str = "Consultorio Privado 101"
    description: str = "Consulta de prueba"
    capacity_reserved: int = 1
    capacity_used: int = 1
    timezone_str: AppointmentTz | None = 'America/Mexico_City'
    alarm_id: Alarm = BASIC_ALARM
    odoo_id: int | None = None
    calendar_event_id: int | None = None

    def __post_init__(self):
        """
        Post-initialization to prepare data for Odoo RPC.
        Converts datetimes to UTC strings and prepares the data dictionary.
        """
        # Format for Odoo RPC
        self.start_utc_str = standarize_datetime(self.start_datetime, self.timezone_str)
        self.end_utc_str = standarize_datetime(self.end_datetime, self.timezone_str)

        self.event = Event(
            name = self.name,
            start_datetime = self.start_datetime,
            end_datetime = self.end_datetime,
            partner_ids = self.partner_id,
            alarm_ids = self.alarm_id,
            description = self.description,
            location = self.location,
            timezone_str = self.timezone_str
        )
    def extract_booking_data(self):
        return {
            # 'active': True,
            'appointment_resource_id': self.resource_id,
            'appointment_type_id': self.type_id,
            'capacity_reserved': self.capacity_reserved,
            'capacity_used': self.capacity_used,
            'calendar_event_id': self.calendar_event_id,
            'event_start': self.start_utc_str, # Odoo uses 'start' and 'stop' for datetimes
            'event_stop': self.end_utc_str,
            'display_name': self.event.name
            # 'create_uid': self.partner_id
        }



        # self.slot = {}
