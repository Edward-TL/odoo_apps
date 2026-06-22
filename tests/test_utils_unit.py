"""
Offline unit tests for pure helpers in `odoo_apps.utils` (Phase 2.4).

Covers the domain builders (`cleaning`) and datetime helpers
(`time_management`) — the logic that backs `client.create`'s idempotency check
and the date-bounded queries.
"""
from datetime import date, datetime

import pytest

from odoo_apps.utils.cleaning import (
    check_domains,
    flat_list,
    gen_domains_from_list,
    gen_domains_from_str,
)
from odoo_apps.utils.time_management import date_normalizer, extract_hour


class TestDomainBuilders:
    def test_gen_domains_from_str_single_dict(self):
        assert gen_domains_from_str("name", "=", {"name": "John"}) == [
            ("name", "=", "John")
        ]

    def test_gen_domains_from_str_list_of_dicts(self):
        result = gen_domains_from_str(
            "name", "=", [{"name": "John"}, {"name": "Jane"}]
        )
        assert result == [("name", "=", "John"), ("name", "=", "Jane")]

    def test_gen_domains_from_list_single_dict(self):
        result = gen_domains_from_list(
            ["name", "age"], ["=", ">"], {"name": "John", "age": 30}
        )
        assert result == [("name", "=", "John"), ("age", ">", 30)]

    def test_check_domains_dispatches_str(self):
        assert check_domains("name", "=", {"name": "X"}) == [("name", "=", "X")]

    def test_check_domains_dispatches_list(self):
        assert check_domains(["name"], ["="], {"name": "X"}) == [("name", "=", "X")]


class TestFlatList:
    def test_flattens_matrix(self):
        assert flat_list([[1, 2], [3, 4]]) == [1, 2, 3, 4]


class TestTimeManagement:
    def test_date_normalizer_from_date(self):
        assert date_normalizer(date(2026, 6, 12)) == "2026-06-12 00:00:00"

    def test_date_normalizer_from_datetime(self):
        assert (
            date_normalizer(datetime(2026, 6, 12, 15, 30, 0))
            == "2026-06-12 15:30:00"
        )

    def test_date_normalizer_from_iso_string(self):
        assert date_normalizer("2026-06-12") == "2026-06-12 00:00:00"

    def test_date_normalizer_from_dmy_string(self):
        assert date_normalizer("12/06/2026") == "2026-06-12 00:00:00"

    def test_date_normalizer_rejects_garbage(self):
        with pytest.raises(ValueError):
            date_normalizer("not-a-date")

    def test_extract_hour(self):
        assert extract_hour("2026-06-12 15:30") == 15
