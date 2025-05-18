"""
Time manager
"""

from datetime import datetime
from pytz import timezone

# Ensure datetimes are timezone-aware before converting to UTC
# If they are naive, assume they are in the specified timezone_str
def standarize_datetime(dt: datetime, tz_str: str) -> datetime:
    """
    Convert a naive datetime to UTC, assuming it's in the specified timezone.
    If the datetime is already timezone-aware, convert it to UTC.
    Args:
        dt (datetime): The datetime to convert.
        tz_str (str): The timezone string (e.g., 'America/Mexico_City').
    Returns:
        datetime: The UTC datetime as a string in the format 'YYYY-MM-DD HH:MM:SS'.
    """
    local_tz = timezone(tz_str)

    if dt.tzinfo is None:
        dt_utc = local_tz.localize(dt)
    else:
        dt_utc = dt.astimezone(local_tz)

    # Convert to UTC
    # dt_utc = dt_aware.astimezone(timezone('UTC'))

    return dt_utc.strftime('%Y-%m-%d %H:%M:%S')
    