"""
APPS init file
"""
from client import OdooClientServer
from models import *
from constants.account import USER_ID

from .calendar.scheduler import Scheduler
from .calendar.objects import Alarm, Event
from .stock.stock_manager import StockManager
from .appointment.appt_manager import AppointmentManager
from .helpers.time_management import *
