"""
"""

from dataclasses import dataclass
from pprint import pprint

from odoo_apps.client import OdooClientServer
from odoo_apps.models import CALENDAR
from odoo_apps.request import CreateRequest
from .objects import Event


@dataclass
class Scheduler:
    """
    Schedule activities
    """
    client: OdooClientServer

 # Para manejar zonas horarias

    def create_calendar_event(self, event: Event, printer=False):
        """
        Crea un nuevo evento en el calendario de Odoo utilizando RPC.
        Args:
            event (Event): Objeto Event que contiene la información del evento a crear.
        Returns:
            int or False: El ID del evento creado en Odoo si la creación fue exitosa,
                        False si ocurrió un error.
        """
        if printer:
            pprint(event.data)

        try:
            # Probablemente sea requerido hacer una funcion especial para esto,
            # ya que luego podria entrar el tema del lugar o los partners. Pero como
            # esto se esta considerando para una sola persona, no es necesario por ahora.
            #  
            event_response = self.client.create(
                CreateRequest(
                    model = CALENDAR.EVENT,
                    vals = event.data,
                    domain_check = ['start', 'stop'],
                    domain_comp = ['>=', '<=']
                ),
                printer=printer
            )

            event.odoo_id = event_response.object_id

            if printer:
                print(f"Evento de calendario '{event.name}' creado con ID: {event.odoo_id}")
            return event_response

        except Exception as e:
            print(f"Error al crear el event de calendario '{event.name}': {e}")
            return False

   