"""
Offline unit tests for appointment slot-overlap logic (Phase 2.4).

`events_overlaps` is the core availability check: given a candidate slot and an
existing event (both same-timezone, standardized), is the slot taken?
"""
from odoo_apps.appointment.objects import SlotEvent
from odoo_apps.appointment.slots import events_overlaps

# Reference slot: 10:00–11:00.
SLOT = SlotEvent("2026-06-15 10:00", "2026-06-15 11:00")


def test_event_entirely_before_slot_does_not_overlap():
    event = SlotEvent("2026-06-15 08:00", "2026-06-15 09:00")
    assert events_overlaps(SLOT, event) is False


def test_event_entirely_after_slot_does_not_overlap():
    event = SlotEvent("2026-06-15 11:00", "2026-06-15 12:00")
    assert events_overlaps(SLOT, event) is False


def test_event_inside_slot_overlaps():
    event = SlotEvent("2026-06-15 10:15", "2026-06-15 10:45")
    assert events_overlaps(SLOT, event) is True


def test_event_straddling_slot_start_overlaps():
    event = SlotEvent("2026-06-15 09:30", "2026-06-15 10:30")
    assert events_overlaps(SLOT, event) is True


def test_event_straddling_slot_end_overlaps():
    event = SlotEvent("2026-06-15 10:30", "2026-06-15 11:30")
    assert events_overlaps(SLOT, event) is True
