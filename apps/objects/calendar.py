
from dataclasses import dataclass, fields
from typing import Literal


Privacy = Literal['public', 'private', 'confidential']
ShowAs = Literal['busy', 'free']
Frequency = Literal['daily', 'weekly', 'monthly', 'yearly']
AlarmType = Literal['notification', 'email', 'sms']
Interval = Literal['minutes', 'hours', 'days']

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
    mail_template_id: str | list[id] | None = None
    sms_template_id: str | list[id] | None = None
    sms_notify_responsible: str | list[id] | None = None

    def export_to_dict(self) -> dict:
        """
        Returns the dictionary version of the class
        """

        return {
            field.name: getattr(self, field.name) \
                for field in fields(self) \
                    if (getattr(self, field.name) not in {False, None})
            }