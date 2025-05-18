"""
"""

from dataclasses import dataclass
from pprint import pprint

from client import OdooClientServer
from models import CALENDAR
from .objects.calendar import Event


@dataclass
class Scheduler:
    """
    Schedule activities
    """
    client: OdooClientServer

 # Para manejar zonas horarias

    def create_calendar_event(
        self,
        event: Event
        ):
        """
        Crea un nuevo evento en el calendario de Odoo utilizando RPC.
        Args:
            event (Event): Objeto Event que contiene la información del evento a crear.
        Returns:
            int or False: El ID del evento creado en Odoo si la creación fue exitosa,
                        False si ocurrió un error.
        """
        
        pprint(event.data)

        try:
            # Probablemente sea requerido hacer una funcion especial para esto,
            # ya que luego podria entrar el tema del lugar o los partners. Pero como
            # esto se esta considerando para una sola persona, no es necesario por ahora.
            #  
            event.odoo_id = self.client.create(
                model = CALENDAR.EVENT,
                vals = event.data,
                domain_check = ['start', 'stop'],
                domain_comp = ['>=', '<=']
                )
            print(f"Evento de calendario '{event.name}' creado con ID: {event.odoo_id}")
            return event.odoo_id
        except Exception as e:
            print(f"Error al crear el event de calendario '{event.name}': {e}")
            return False

   