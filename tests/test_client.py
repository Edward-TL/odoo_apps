"""
Client functions
"""
import pytest
from dotenv import dotenv_values

from odoo_apps.models import PRODUCT
from odoo_apps.client import OdooClient
from odoo_apps.request import (
    SearchReadRequest,
    SearchRequest,
    UpdateRequest,
    DeleteRequest
)

from odoo_apps.stock.manager import StockManager

config = dotenv_values('./tests/test.env')
odoo = OdooClient(
    user_info = config
    )

CREATION_TEST_CATEGORY = "TEST SUITE"
UPDATE_TEST_CATEGORY = "TEST"
CHILD_TEST_CATEGORY = "CHILD TEST"

class TestOdooClient:
    """
    Basic test class for Odoo client
    """

    def test_search_read_categories(self):
        """
        Simple search_read functional test
        """
        response = odoo.search_read(
                model = PRODUCT.CATEGORY,
                domain = [(['parent_id', '=', False])]
        )

        categories_test = [
            {'id': 1, 'name': "All"},
            {'id': 17, 'name': "Servicios"}
        ]

        checker = [test in response for test in categories_test]
        
        assert sum(checker) == len(categories_test)

    def test_create_root_categories(self):
        """
        Simple search_read functional test
        """
        test_stock_manager = StockManager(client = odoo)
        
        test_stock_manager.create_product_category(
            category_name = CREATION_TEST_CATEGORY
        )

        categories = odoo.search_read(
            model = PRODUCT.CATEGORY,
            domain = [(['parent_id', '=', False])]
        )

        for category in categories:
            if category['name'] == CREATION_TEST_CATEGORY:
                assert category['id'] > 0
                break
        
    def test_search_test_category(self):
        """
        Simple search_read functional test
        """
        categories = odoo.search(
            model = PRODUCT.CATEGORY,
            domains = [(['name', '=', CREATION_TEST_CATEGORY])]
        )
        # print(f"{CREATION_TEST_CATEGORY} IDs: {response}")
        assert len(categories) > 0

    def test_update_test_category(self):
        """
        Simple search_read functional test
        """
        test_ids = odoo.search(
            model = PRODUCT.CATEGORY,
            domains = [(['name', '=', CREATION_TEST_CATEGORY])]
        )
        
        odoo.update(
            model = PRODUCT.CATEGORY,
            # MUST BE a single integer
            records_ids = test_ids[0],
            new_vals = {'name': UPDATE_TEST_CATEGORY}
        )

        update_confirmation_response = odoo.search(
            model = PRODUCT.CATEGORY,
            domains = [(['name', '=', UPDATE_TEST_CATEGORY])]
        )
        assert len(update_confirmation_response) > 0

    def test_create_child_category(self):
        """
        Create a child category from an existing one
        """
        test_stock_manager = StockManager(client = odoo)
        
        response = odoo.search(
                model = PRODUCT.CATEGORY,
                domains = [(['name', '=', UPDATE_TEST_CATEGORY])]
        )
        
        test_stock_manager.create_product_category(
            category_name = CHILD_TEST_CATEGORY,
            parent_id = response[0]
        )

        child_response = odoo.search(
                model = PRODUCT.CATEGORY,
                domains = [(['parent_id', '=', response[0]])]
        )

        assert len(child_response) > 0

    def test_delete_test_category(self):
        """
        Simple search_read functional test
        """
        
        parents_id = odoo.search(
            model = PRODUCT.CATEGORY,
            domains = [(['name', '=', UPDATE_TEST_CATEGORY])]
        )

        child_id = odoo.search(
            model = PRODUCT.CATEGORY,
            domains = [(['name', '=', CHILD_TEST_CATEGORY])]
        )[0]

        delete_ids = [id_ for id_ in parents_id]
        delete_ids.append(child_id)

        # print(f"Deleting IDs: {delete_ids}")

        odoo.delete(
            model = PRODUCT.CATEGORY,
            ids = delete_ids
        )

        # delete_confirmation_response = odoo.search(
        #     model = PRODUCT.CATEGORY,
        #     domain = [(['name', '=', "TEST"])]
        #     )

        # print(f"Delete Confirmation response: {delete_confirmation_response}")

        assert len(
            odoo.search(
                model = PRODUCT.CATEGORY,
                domains = [(['name', '=', UPDATE_TEST_CATEGORY])]
            )
        ) == 0

        assert len(
            odoo.search(
                model = PRODUCT.CATEGORY,
                domains = [(['name', '=', CHILD_TEST_CATEGORY])]
            )
        ) == 0
