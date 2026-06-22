"""
Integration tests for `OdooClient` CRUD against a live Odoo database.

Marked `live`: skipped in the default offline run (pyproject `addopts`). Run with
credentials in tests/test.env via:  pytest -m live

NOTE: these are pre-existing integration tests. They exercise the real database
and assume seed data (category ids 1 "All", 17 "Servicios"); they have not been
re-validated against a database in this refactor — the change here is only the
move of client construction into the `odoo` / `stock_manager` fixtures.
"""
import pytest

from odoo_apps.models import PRODUCT

pytestmark = pytest.mark.live

CREATION_TEST_CATEGORY = "TEST SUITE"
UPDATE_TEST_CATEGORY = "TEST"
CHILD_TEST_CATEGORY = "CHILD TEST"


class TestOdooClient:
    """Basic CRUD round-trip on product categories."""

    def test_search_read_categories(self, odoo):
        response = odoo.search_read(
            model=PRODUCT.CATEGORY,
            domain=[(['parent_id', '=', False])],
        )
        categories_test = [
            {'id': 1, 'name': "All"},
            {'id': 17, 'name': "Servicios"},
        ]
        checker = [test in response for test in categories_test]
        assert sum(checker) == len(categories_test)

    def test_create_root_categories(self, odoo, stock_manager):
        stock_manager.create_product_category(category_name=CREATION_TEST_CATEGORY)

        categories = odoo.search_read(
            model=PRODUCT.CATEGORY,
            domain=[(['parent_id', '=', False])],
        )
        for category in categories:
            if category['name'] == CREATION_TEST_CATEGORY:
                assert category['id'] > 0
                break

    def test_search_test_category(self, odoo):
        categories = odoo.search(
            model=PRODUCT.CATEGORY,
            domain=[(['name', '=', CREATION_TEST_CATEGORY])],
        )
        assert len(categories) > 0

    def test_update_test_category(self, odoo):
        test_ids = odoo.search(
            model=PRODUCT.CATEGORY,
            domain=[(['name', '=', CREATION_TEST_CATEGORY])],
        )
        odoo.update(
            model=PRODUCT.CATEGORY,
            records_ids=test_ids[0],
            new_vals={'name': UPDATE_TEST_CATEGORY},
        )
        update_confirmation = odoo.search(
            model=PRODUCT.CATEGORY,
            domain=[(['name', '=', UPDATE_TEST_CATEGORY])],
        )
        assert len(update_confirmation) > 0

    def test_create_child_category(self, odoo, stock_manager):
        response = odoo.search(
            model=PRODUCT.CATEGORY,
            domain=[(['name', '=', UPDATE_TEST_CATEGORY])],
        )
        stock_manager.create_product_category(
            category_name=CHILD_TEST_CATEGORY,
            parent_id=response[0],
        )
        child_response = odoo.search(
            model=PRODUCT.CATEGORY,
            domain=[(['parent_id', '=', response[0]])],
        )
        assert len(child_response) > 0

    def test_delete_test_category(self, odoo):
        parents_id = odoo.search(
            model=PRODUCT.CATEGORY,
            domain=[(['name', '=', UPDATE_TEST_CATEGORY])],
        )
        child_id = odoo.search(
            model=PRODUCT.CATEGORY,
            domain=[(['name', '=', CHILD_TEST_CATEGORY])],
        )[0]
        delete_ids = [id_ for id_ in parents_id]
        delete_ids.append(child_id)

        odoo.delete(model=PRODUCT.CATEGORY, ids=delete_ids)

        assert len(odoo.search(
            model=PRODUCT.CATEGORY,
            domain=[(['name', '=', UPDATE_TEST_CATEGORY])],
        )) == 0
        assert len(odoo.search(
            model=PRODUCT.CATEGORY,
            domain=[(['name', '=', CHILD_TEST_CATEGORY])],
        )) == 0
