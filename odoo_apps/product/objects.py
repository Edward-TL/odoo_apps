"""
Stores all classes that can define:
    a) A product's attribute
    b) A product's attribute value
    c) A product's template
"""

from dataclasses import dataclass#, fields, field
import inspect
from typing import Literal, Optional

import numpy as np

# from odoo_apps.utils.cleaning import generate_dict

@dataclass
class ColsReference:
    """
    Class that helps storing relevance data for data wrangling process
    with DataFrames.
    
    attributes and drop will turn into sets for faster iteration, and renamer
    will turn to dict if a tuple of tuples is given.

    Consdier:
        renamer = (
        ("original_name", "odoo_field")
        ) 
    """
    attributes: Optional[tuple] = None
    drop: Optional[tuple] = None
    renamer: Optional[tuple[tuple[str, str]] | dict] = None
    generate_from: Optional[dict] = None

    def __post_init__(self):
        if self.generate_from is None:
            self.attributes = set(self.attributes)
            self.drop = set(self.drop)

            if isinstance(self.renamer, (tuple, list)):
                self.renamer = {
                    r[0]: r[1] for r in self.renamer
                }
        
        else:
            self.renamer = {
                k: v for k,v in self.generate_from.items() if v not in {'skip', 'attribute', '', 'drop'}
            }
            self.attributes = {
                k for k,v in self.generate_from.items() if v == 'attribute'
            }
            self.drop = {k for k,v in self.generate_from.items() if v in {'skip', 'drop'}}

@dataclass
class AttributeLine:
    """
    """
    attribute_id: int #[1, 'Color'],
    values_ids: tuple[int] #[35],
    product_tmpl_id: int #[18, 'POLO G500'],
    _id: Optional[int] = None
    error_msg: Optional[str] = None
    # Just in case you want a human reference
    attribute_name: Optional[str] = None
    values: Optional[list[str]] = None
    # product_template_value_ids: tuple[int] # [57],

    def __post_init__(self):
        self.domains = [
        ["attribute_id", '=', self.attribute_id],
        ["product_tmpl_id", '=', self.product_tmpl_id],
        ["value_ids", 'in', self.values_ids]
    ]
    
    def export_to_dict(self) -> dict:
        """
        Returns the dictionary version of the class
        """
        return {
            "attribute_id": self.attribute_id,
            "product_tmpl_id": self.product_tmpl_id,
            "value_ids": self.values_ids
        }
@dataclass
class ProductTemplate:
    name: str
    categ_id: str
    pos_categ_ids: Optional[list[int] | int] = None
    list_price: float | np.float32 | np.float64 = 0
    description: str | bool = False
    barcode: Optional[str | bool] = False
    default_code: Optional[str | bool] = False
    qty_available: int = 0
    responsible_id: int = 2
    valid_product_template_attribute_line_ids: Optional[tuple[int]] = False
    product_variant_ids: Optional[tuple[int]] = False
    attribute_values: Optional[dict[str, list[str]]] = None
    attribute_values_ids: Optional[dict[int, list[int]]] = None
    attribute_lines: Optional[list[AttributeLine]] = None

    # allow_out_of_stock_order: bool = False
    available_in_pos: bool = True
    # is_published: bool = False
    is_storable: bool = True
    sale_ok: bool = True
    # show_availability: bool = True
    _type: Literal['consu', 'service', 'combo'] = 'consu'
    currency_id: int = 33
    cost_currency_id: int = 33
    uom_id = 1
    fiscal_country_codes: str = 'MX'
    error_msg: Optional[str] = None
    _id: Optional[int] = None
# 'selection': [['consu', 'Goods'],
#             ['service', 'Service'],
#             ['combo', 'Combo']],
    def __post_init__(self):
        if type(self.list_price).__module__ == 'numpy':
            self.list_price = self.list_price.item()
        else:
            # print('its float')
            self.list_price = float(self.list_price)
        self.base_unit_price = self.list_price
        self.standard_price = self.list_price
        
        if self.attribute_lines is None:
            self.attribute_lines = []
        self.domains = [
            ['name', '=', self.name],
            ['categ_id', '=', self.categ_id]
        ]

    def export_to_dict(self) -> dict:
        """
        Returns the dictionary version of the class
        """
        members = inspect.getmembers(type(self))
        base_dict = {
            k: v for k,v in dict(members).items()\
                if not k.startswith('__') and k != "export_to_dict"}
        
        base_dict['name'] = self.name
        base_dict['categ_id'] = self.categ_id
        base_dict['pos_categ_ids'] = self.pos_categ_ids
        base_dict['description'] = self.description
        base_dict['list_price'] = self.list_price
        # base_dict['base_unit_price'] = self.list_price
        base_dict['standard_price'] = self.list_price


        if isinstance(base_dict, int):
            base_dict['pos_categ_ids'] = [base_dict['pos_categ_ids']]

        base_dict['type'] = base_dict['_type']
        if '_id' in base_dict:
            if base_dict["_id"] is None:
                del base_dict['_id']

        for key in [
            '_type',
            'attribute_lines',
            'attribute_values_ids',
            'attribute_values',
            'error_msg',
            'valid_product_template_attribute_line_ids'
            ]:
            del base_dict[key]

        return base_dict



products_order_cols = [
    'id',
    'categ_id',
    'categ_name',
    'display_name',
    'product_tmpl_id',
    'product_tmpl_name'
]

product_renamer = {
    'id': 'product_id',
    'display_name': 'product_name',
    'product_tmpl_name_x': 'product_tmpl_name',
    'product_template_variant_value_ids': 'attribute_value_id'
}

VITAL_PRODUCT_COLS = [
    'product_id',
    'product_name',
    'product_tmpl_id',
    'product_tmpl_name',
    'attribute_value_id',
    'categ_id',
    'categ_name',
]

attributes_renamer = {
    'id': 'attribute_value_id',
}

VITAL_ATTRIBUTES_COLS = [
    'attribute_value_id',
    'attribute_id',
    'attribute_name',
    'product_attribute_value_id',
    'product_attribute_value_name',
    'product_tmpl_id'
]
