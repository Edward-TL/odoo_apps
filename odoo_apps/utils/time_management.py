"""
Time manager
"""
from datetime import datetime, timedelta
from pytz import timezone
from .timezones import TzNames
# Ensure datetimes are timezone-aware before converting to UTC
# If they are naive, assume they are in the specified timezone_str

TIME_STR = "%Y-%m-%d %H:%M"
DATE_STR = "%Y-%m-%d"

from datetime import datetime, date

def date_normalizer(date_value):
    """
    Converts a value  (date, datetime or str) to format 'YYYY-MM-DD HH:MM:SS'.
    """
    if isinstance(date_value, datetime):
        return date_value.strftime("%Y-%m-%d %H:%M:%S")
    
    if isinstance(date_value, date):
        # Convertimos agregando hora 00:00:00
        return datetime(
            date_value.year,
            date_value.month,
            date_value.day
        ).strftime("%Y-%m-%d %H:%M:%S")
    
    if isinstance(date_value, str):
        # Intentamos distintos formatos posibles
        date_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y"
        ]
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_value, fmt)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
        raise ValueError(f"Not recognized date format: {date_value}")
    
    raise TypeError(f"Not supported type: {type(date_value)}")


def standarize_datetime(
        dt: datetime | str,
        tz_str: TzNames = 'America/Mexico_City',
        timeoffset = '-0600') -> str:
    """
    Convert a naive datetime to UTC, assuming it's in the specified timezone.
    If the datetime is already timezone-aware, convert it to UTC.
    Args:
        dt (datetime): The datetime to convert.
        tz_str (str): The timezone string (e.g., 'America/Mexico_City').
    Returns:
        datetime: The UTC datetime as a string in the format 'YYYY-MM-DD HH:MM:SS'.
    """

    if isinstance(dt, str):
        return adapt_datetime(dt, timeoffset)

    local_tz = timezone(tz_str)

    if dt.tzinfo is None:
        dt_utc = local_tz.localize(dt)
    else:
        dt_utc = dt.astimezone(local_tz)

    return dt_utc.strftime(TIME_STR)


def adapt_datetime(dt: datetime | str, timeoffset= '-0600', time_str = TIME_STR) -> str:
    """
    From a datetime object, with missing time zone name, but with time offset, adapts
    the value as is required
    """
    tzh = int(timeoffset[:3]) * -1
    tzm = int(timeoffset[3:])

    if isinstance(dt, str):
        dt = datetime.strptime(dt, time_str)

    corrected_datetime = dt + timedelta(hours = tzh, minutes=tzm)

    return corrected_datetime.strftime(time_str)


def extract_hour(strftime: str, time_str = TIME_STR) -> int:
    """
    From a string datetime, returns the int hour value.
    """
    return datetime.strptime(strftime, time_str).hour