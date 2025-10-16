from dataclasses import dataclass, field
from typing import Optional, Literal
from copy import copy
from pprint import pprint
from xmlrpc.client import Fault

import pandas as pd
from numpy import nan as np_nan

from odoo_apps.client import OdooClient
from odoo_apps.models import PRODUCT, POS
from odoo_apps.response import Response

from odoo_apps.type_hints.stock import DisplayTypes, CreateVariants
from odoo_apps.utils.cleaning import (
    transform_dict_array_to_dict,
    merge_dictionaries,
    gen_matrix,
    split_id_pair
    )

from odoo_apps.product.objects import ProductTemplate, AttributeLine
from odoo_apps.utils.cleaning import extract_cell_value

product_model = {
    'CATEGORY': PRODUCT.CATEGORY,
    'ATTRIBUTE_VALUE': PRODUCT.ATTRIBUTE_VALUE,
    'ATTRIBUTE': PRODUCT.ATTRIBUTE
}

def reference_clasifier(ref: list):
    """
    """
    if len(ref) == 1:
        return int(ref[0])
    
    if len(ref) == 0:
        return np_nan
    
    return ref

main_tmpl_att_val_fields = [
'id', 'display_name', "product_template_variant_value_ids"
]

@dataclass
class Pos:
    """
    Search for products store on Client's database.
    
    Args:
        - client: OdooClient.

    Every dictionary value is an ID, as every key is the
    value name. This makes it easier and faster to verify in
    further actions.
    """
    client: OdooClient
    preload: bool = True
    # Categories related
    stocl_cat_col: str = None
    categories: Optional[list | dict[str | int]] = None
    
    # Attributes_related
    attributes: Optional[dict | list] = None
    att_values: Optional[dict[str , list] | list | dict[str , dict]] = None
    
    # Templates related
    templates: Optional[dict[str, dict]] = None
    raw_templates_data: Optional[list[dict]] = None
    template_attributes_value_matrix: Optional[dict[str, list] | pd.DataFrame] = None
    
    # Products related
    products: Optional[dict[str, dict]] = None
    raw_products_data: Optional[list[dict]] = None
    products_matrix: Optional[dict[str, list] | pd.DataFrame] = None

    def get_all_categories(self) -> None:
        """
        Gets all categories stored on Odoo database, and stores it at `self.categories`
        """
        self.categories = transform_dict_array_to_dict(
                dict_array = self.get_all_values(PRODUCT.CATEGORY)
            )