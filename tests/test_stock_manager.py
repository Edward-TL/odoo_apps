"""
STOCK MANAGER functions
"""
import pytest
from dotenv import dotenv_values

from models import PRODUCT
from client import OdooClientServer
from apps.stock.stock_manager import StockManager

config = dotenv_values('./tests/test.env')
odoo = OdooClientServer(
    user_info = config
    )

stock_manager = StockManager(
    client = odoo
)

CREATION_TEST_SELECT_ATTR = "TEST SELECT"
CREATION_TEST_COLOR_ATTR = "TEST COLOR"
CREATION_TEST_OPTION_ATTR = "TEST RADIO"
CREATION_TEST_PILL_ATTR = "TEST PILLS"
CREATION_TEST_MULTI_ATTR = "TEST MULTI"

creation_attributes = [
    CREATION_TEST_COLOR_ATTR,
    CREATION_TEST_SELECT_ATTR,
    CREATION_TEST_OPTION_ATTR,
    CREATION_TEST_PILL_ATTR,
    CREATION_TEST_MULTI_ATTR
]

display_test = [test.replace("TEST ","").lower() for test in creation_attributes]
class TestStockManager:
    """
    Core activities for Stock manager
    """

    def test_create_product_attribute(self):
        """
        Simple attribute creation
        """
        for creation_type, display in zip(creation_attributes, display_test):
            if display == 'multi':
                variants = 'no_variant'
            else:
                variants = "dynamic"

            stock_manager.create_product_attribute(
                name = creation_type,
                display_type = display,
                create_variant = variants
            )
        
        check = [
            odoo.search_read(
                model = PRODUCT.ATTRIBUTE,
                domain = [(['name', '=', creation_type])]
            ) for creation_type in creation_attributes
        ]
        
        validate = 0
        creation_attributes_set = set(creation_attributes)
        for atts in check:
            if atts[0]['name'] in creation_attributes_set:
                validate += 1
        
        assert validate == len(creation_attributes)
                
        
    def test_append_product_select_attribute_value(self):
        """
        Adding values to attribute
        """
        attribute_id = stock_manager.append_attribute_value(
            attribute_id = CREATION_TEST_SELECT_ATTR,
            name = "Nuevo valor en select"
        )

        assert attribute_id > 0

    def test_append_product_multi_attribute_value(self):
        """
        Adding values to attribute
        """
        values = [f'Nuevo multi {n}' for n in range(1,11)]

        val_attributes = [
            stock_manager.append_attribute_value(
                attribute_id = CREATION_TEST_MULTI_ATTR,
                name = value
            ) for value in values
        ]

        check_vals = [
            True if isinstance(value, int) else False for value in val_attributes
            ]

        assert sum(check_vals) == len(values)

    def test_append_product_color_attribute_value(self):
        """
        Adding values to attribute
        """
        color_names = [
            "Black",
            "Charcoal",
            "Dark Green",
            "Dark Purple",
            "Jet Black",
            "Licorice",
            "Matte Black",
            "Midnight Blue",
            "Onyx"
        ]
        html_codes = [
                "#000000",
                "#36454F",
                "#023020",
                "#301934",
                "#343434",
                "#1B1212",
                "#28282B",
                "#191970",
                "#353935"
            ]


        val_attributes = [
            stock_manager.append_attribute_value(
                attribute_id = CREATION_TEST_COLOR_ATTR,
                name = name,
                html_color = code
            ) for name, code in zip(color_names, html_codes)
        ]

        check_vals = [
            True if isinstance(value, int) else False for value in val_attributes
            ]

        assert sum(check_vals) == len(val_attributes)

    def test_delete_tests(self):
        """
        Delete all test objects
        """
        for test_attribute in creation_attributes:
            odoo.delete(
                PRODUCT.ATTRIBUTE, ids = odoo.search(
                    PRODUCT.ATTRIBUTE, [('name', '=', test_attribute)]
                )
            )

        vals_check = [
            odoo.search(
                model = PRODUCT.ATTRIBUTE,
                domain = [('name', '=', test_attribute)]
            ) for test_attribute in creation_attributes
        ]

        check_vals = [
            True if isinstance(value, int) else False for value in vals_check
            ]

        assert sum(check_vals) == 0