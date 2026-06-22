# `odoo_apps.calendar` — Calendar Events

Wrapper around Odoo's Calendar app (`calendar.event`, `calendar.alarm`).
Creates, moves, and cancels events with busy-conflict detection. Used directly
and as the backend of the [`appointment/`](../appointment/README.md) module.

## Files

| File | Purpose |
|------|---------|
| `objects.py` | `Event` dataclass (`name`, `start`, `stop`, `partner_ids`, `alarm_ids`, timezone handling, plus `add_appointment_data()` to link it to an appointment type) and `Alarm` (notification config with `export_to_dict()`). |
| `scheduler.py` | `Scheduler` dataclass: `search_events_in_range()`, `create_calendar_event()` (refuses overlapping events with a `409` busy response), `move_calendar_event()`, `cancel()`. Also helper response builders (`create_busy_response`, etc.). |
| `type_hints.py` | `Literal` types for calendar selection fields (e.g. recurrence `Frequency`). |

## Usage

```python
from odoo_apps.calendar.scheduler import Scheduler
from odoo_apps.calendar.objects import Event

scheduler = Scheduler(client=client)

event = Event(
    name="Team Meeting",
    start="2026-06-15 10:00:00",
    stop="2026-06-15 11:00:00",
    partner_ids=[1, 2, 3],
)
response = scheduler.create_calendar_event(event)   # FlaskResponse; 409 if slot busy
scheduler.move_calendar_event(event_id, new_start, new_stop)
scheduler.cancel(event_id)
```

## Notes

- Datetimes are normalized to UTC strings via `utils.time_management` before
  being sent to Odoo (Odoo stores datetimes in UTC).
- Scheduler methods return `flask.Response` objects, mirroring the
  appointment module's web-service orientation.
- Covered by `tests/test_calendar_scheduler.py`.
