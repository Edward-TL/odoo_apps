"""
Offline unit tests for `ContactBook` (Phase 2.6).
"""
from odoo_apps.contact.book import ContactBook
from odoo_apps.models import CONTACTS
from tests.fakes import FakeOdooClient


def test_get_contact_id_returns_id():
    client = FakeOdooClient(search_read_result=[{"id": 42, "name": "John"}])
    book = ContactBook(client=client)

    assert book.get_contact_id(by="name", reference="John") == 42
    call = client.calls[-1]
    assert call["method"] == "search_read"
    assert call["model"] == CONTACTS.PARTNER
    assert call["domain"] == [["name", "=", "John"]]


def test_check_register_contacts_all_found_returns_ids():
    client = FakeOdooClient(search_read_result=[{"id": 42}])
    book = ContactBook(client=client)

    result = book.check_register_contacts(["+521234567890"], by_field="phone")
    assert result == [42]
