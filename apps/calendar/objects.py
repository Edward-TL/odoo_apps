
from dataclasses import dataclass, fields, field
from datetime import datetime
from pytz import timezone

from apps.type_hints.calendar import AlarmType, Frequency, Interval
from apps.type_hints.media_relations import Privacy, ShowAs
from apps.type_hints.time_zone import TimeZone

@dataclass
class Alarm:
    """
    Describes an Odoo minimum alarm requirements
    """
    name: str = "Alarma de Evento"
    body: str = "Recordatorio de evento en 30 minutos"
    alarm_type: AlarmType = 'notification'
    duration: int = 30
    interval: Interval = 'minutes'
    mail_template_id: str | list[int] | None = None
    sms_template_id: str | list[int] | None = None
    sms_notify_responsible: str | list[int] | None = None

    def export_to_dict(self) -> dict:
        """
        Returns the dictionary version of the class
        """

        return {
            field.name: getattr(self, field.name) \
                for field in fields(self) \
                    if (getattr(self, field.name) not in {False, None})
            }

BASIC_ALARM = tuple([
    (
        0, 0, Alarm().export_to_dict()
    )
])

@dataclass
class Event:
    """
    Class representing Event to add on Odoo
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
    """
    name: str
    start_datetime: datetime
    end_datetime: datetime
    partner_ids: list[str] | list[int] | None = field(default_factory=[3])
    alarm_ids: list[Alarm] | list[str] | list[int] | None = BASIC_ALARM
    description: str = "Espacio agendado"
    location: str = ""
    privacy: Privacy = 'public'  # Valores: 'public', 'private', 'confidential'
    show_as: ShowAs = 'busy'  # Valores: 'busy', 'free'
    recurrency: bool = False
    interval: int = 1 # Days/Week/Month/Year Yeap, it's setted as intenger, I know...
    # resource_ids: list[int] = DOCTOR_RESOURCE_ID
    rrule_type: Frequency = 'daily'
    count: int = 0  # Número de repeticiones (0 para indefinido si recurrencia es True)
    until: datetime = None  # Fecha límite de recurrencia
    timezone_str: TimeZone = 'UTC'  # Zona horaria del self. (ej. 'America/Mexico_City')
    odoo_id: int | None = None  # ID del evento en Odoo (opcional, se asigna al crear el evento)
    is_all_day: bool = False  # Indica si el evento es de todo el día (True) o tiene hora específica (False)

    def __post_init__(self):

        # Convertir las datetimes a UTC, que es la zona horaria que Odoo espera para el almacenamiento.
        # Asumimos que las datetimes proporcionadas ya están en la timezone_str especificada.
        start_naive = self.start_datetime.replace(tzinfo=None)
        print("start_naive: ", start_naive)
        end_naive = self.end_datetime.replace(tzinfo=None)
        print("end_naive: ", end_naive)

        self.start_utc = start_naive.astimezone(timezone(self.timezone_str))
        print("start_utc: ", self.start_utc)
        self.end_utc = end_naive.astimezone(timezone(self.timezone_str))
        print("end_utc: ", self.end_utc)

        diferencia = abs(self.end_datetime - self.start_datetime)
        diferencia_en_horas = diferencia.total_seconds() / 3600

        self.is_all_day = bool(diferencia_en_horas % 24 == 0)

        self.data = {
        'name': self.name,
        'start': self.start_utc.strftime('%Y-%m-%d %H:%M:%S'),
        'stop': self.end_utc.strftime('%Y-%m-%d %H:%M:%S'),
        'partner_ids': [self.partner_ids],
        'alarm_ids': self.alarm_ids,
        'description': self.description,
        'location': self.location,
        'privacy': self.privacy,
        'show_as': self.show_as,
        'recurrency': self.recurrency,
        # 'resource_ids': self.resource_ids,
        'interval': self.interval,
        'rrule_type': self.rrule_type,
        'count': self.count if self.recurrency else False,
        # 'until': until.astimezone(timezone('UTC')).strftime('%Y-%m-%d') if recurrency and until else False,
        'allday': self.is_all_day,  # Por defecto, los self.s tienen una hora específica
        'event_tz': self.timezone_str, # Almacenar la zona horaria para la visualización
        }
