# `odoo_apps.appointment` — Appointments & Online Booking

The most workflow-complete module of the library. Wraps Odoo's Appointment app
to **search available slots, book, reschedule, and cancel appointments**,
returning Flask-ready responses — it is designed to back a booking web service.

## Files

| File | Purpose |
|------|---------|
| `manager.py` | `AppointmentManager` — the orchestrator. Key methods: `get_booking_url()`, `look_for_slots()`, `check_slots_conditions()`, `extract_appointment_data()` (parses a JSON request body into an `Appointment`), `book_appointment()`, `reschedule()`, `cancel()`. |
| `objects.py` | `Appointment` dataclass (type id, contact data, start/stop, timezone…) and `SlotEvent` (a normalized time interval used for overlap checks). |
| `slots.py` | Slot computation pipeline: `clean_slots_info()`, `slots_search_info()`, `events_overlaps()`, `confirm_slots_availability()`, `get_slots_available()`. Cross-checks configured appointment slots against existing calendar events. |
| `checkers.py` | Request validation: date/hour range checks (`check_dates_range`, `check_hours_range`, `validate_dates`), weekday expansion (`weekdays_requested`, `create_next_week_days`), and prebuilt error responses (`create_busy_response`, `create_bad_request_response`, `create_error_response`). |

## Flow

```
request body (dict)
  → checkers.validate_dates / check_*_range      # 400 on bad input
  → manager.look_for_slots                       # query appointment.slot + calendar.event
      → slots.confirm_slots_availability         # drop slots overlapping existing events
  → manager.book_appointment(Appointment)        # create calendar event via Scheduler
  → FlaskResponse (200/201/409 CONFLICT when busy)
```

## Usage

```python
from odoo_apps.appointment.manager import AppointmentManager

am = AppointmentManager(client=client)
slots = am.look_for_slots(appointment_type_id=3, dates_range=["2026-06-15", "2026-06-19"])
response = am.book_appointment(am.extract_appointment_data(request_json))
```

## Notes

- Depends on [`calendar/`](../calendar/README.md) for event creation and on
  `utils.time_management` / `utils.timezones` for timezone-aware datetimes.
- Returns `flask.Response` objects from booking endpoints (HTTP semantics:
  `409 CONFLICT` when the slot is busy).
- Covered by `tests/test_appointment_manager.py`.
