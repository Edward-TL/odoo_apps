"""
"""

from dataclasses import dataclass
from pprint import pprint

from datetime import datetime
from pytz import timezone

from client import OdooClientServer
from models import CALENDAR
from handlers.objects import (
    Alarm,
    Frequency, Privacy,
    ShowAs
)


@dataclass
class Scheduler:
    """
    Schedule activities
    """
    client: OdooClientServer

 # Para manejar zonas horarias

    def create_calendar_event(
        self,
        name: str,
        start_datetime: datetime,
        end_datetime: datetime,
        partner_ids: list[str] | list[int] | None = None,
        alarm_ids: list[Alarm] | list[str] | list[int] | None = None,
        description: str = "Espacio agendado",
        location: str = "",
        privacy: Privacy = 'public',  # Valores: 'public', 'private', 'confidential'
        show_as: ShowAs = 'busy',  # Valores: 'busy', 'free'
        recurrency: bool = False,
        interval: int = 1, # Days/Week/Month/Year Yeap, it's setted as intenger, I know...
        rrule_type: Frequency = 'daily',
        count: int = 0,  # Número de repeticiones (0 para indefinido si recurrencia es True)
        until: datetime = None,  # Fecha límite de recurrencia
        timezone_str: str = 'America/Mexico_City'  # Zona horaria del evento (ej. 'America/Mexico_City')
    ):
        """
        Crea un nuevo evento en el calendario de Odoo utilizando RPC.

        Args:
            name (str): El título del evento.
            start_datetime (datetime): Objeto datetime con la hora de inicio del evento (en la zona horaria especificada).
            end_datetime (datetime): Objeto datetime con la hora de fin del evento (en la zona horaria especificada).
            partner_ids (list, optional): Lista de IDs de los contactos asociados al evento. Por defecto es [].
            alarm_ids (list, optional): Lista de tuplas con la configuración de las alarmas.
                Ejemplo: [(0, 0, {'alarm_type': 'email', 'interval': 5, 'unit': 'minutes'})]. Por defecto es [].
            description (str, optional): Descripción detallada del evento. Por defecto es "".
            location (str, optional): Ubicación del evento. Por defecto es "".
            privacy (str, optional): Nivel de privacidad del evento. Por defecto es 'public'.
            show_as (str, optional): Cómo se muestra la disponibilidad durante el evento. Por defecto es 'busy'.
            recurrency (bool, optional): Indica si el evento es recurrente. Por defecto es False.
            interval (int, optional): Intervalo de repetición (ej. cada 2 días, cada 3 semanas). Por defecto es 1.
            rrule_type (str, optional): Tipo de regla de recurrencia. Por defecto es 'daily'.
            count (int, optional): Número de veces que se repetirá el evento (0 para indefinido si recurrencia es True). Por defecto es 0.
            until (datetime, optional): Fecha límite para la recurrencia. Por defecto es None.
            timezone_str (str, optional): Zona horaria del evento. Por defecto es 'UTC'.

        Returns:
            int or False: El ID del evento creado en Odoo si la creación fue exitosa,
                        False si ocurrió un error.
        """

        # Convertir las datetimes a UTC, que es la zona horaria que Odoo espera para el almacenamiento.
        # Asumimos que las datetimes proporcionadas ya están en la timezone_str especificada.
        # local_tz = timezone(timezone_str)
        # print("local_tz: ", local_tz)
        # start_naive = start_datetime.replace(tzinfo=None)
        # print("start_naive: ", start_naive)
        # end_naive = end_datetime.replace(tzinfo=None)
        # start_utc = local_tz.localize(start_naive).astimezone(timezone(timezone_str))
        # print("start_utc: ", start_utc)
        # end_utc = local_tz.localize(end_naive).astimezone(timezone(timezone_str))
        # print("end_utc: ", end_utc)

        diferencia = abs(end_datetime - start_datetime)
        diferencia_en_horas = diferencia.total_seconds() / 3600

        is_all_day = bool(diferencia_en_horas % 24 == 0)

        event_data = {
            'name': name,
            'start': start_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'stop': end_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'partner_ids': [(6, 0, partner_ids)],
            'alarm_ids': alarm_ids,
            'description': description,
            'location': location,
            'privacy': privacy,
            'show_as': show_as,
            'recurrency': recurrency,
            'interval': interval,
            'rrule_type': rrule_type,
            'count': count if recurrency else False,
            # 'until': until.astimezone(timezone('UTC')).strftime('%Y-%m-%d') if recurrency and until else False,
            'allday': is_all_day,  # Por defecto, los eventos tienen una hora específica
            'event_tz': timezone_str, # Almacenar la zona horaria para la visualización
        }
        
        pprint(event_data)

        try:
            new_event_id = self.client.create(CALENDAR.EVENT, event_data)
            print(f"Evento de calendario '{name}' creado con ID: {new_event_id}")
            return new_event_id
        except Exception as e:
            print(f"Error al crear el evento de calendario '{name}': {e}")
            return False

   