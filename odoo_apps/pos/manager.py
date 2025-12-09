from dataclasses import dataclass
from typing import Optional, Literal
from datetime import datetime, date, timedelta

from odoo_apps.client import OdooClient, RPCHandlerMetaclass
from odoo_apps.models import PRODUCT, POS
from odoo_apps.response import Response

from odoo_apps.product.manager import ProductManager
from odoo_apps.utils.time_management import date_normalizer

product_model = {
    'CATEGORY': PRODUCT.CATEGORY,
    'ATTRIBUTE_VALUE': PRODUCT.ATTRIBUTE_VALUE,
    'ATTRIBUTE': PRODUCT.ATTRIBUTE
}

main_tmpl_att_val_fields = [
'id', 'display_name', "product_template_variant_value_ids"
]

GENERAL_PORPOUSE_POS_ORDER_LINE_FIELDS = (
    'full_product_name', # Nombre del producto
    'product_id',
    'qty',
    'product_uom_id',
    'attribute_value_ids',
    'create_date'
)



@dataclass
class PosManager(metaclass=RPCHandlerMetaclass):
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
    prod_manager: Optional[ProductManager] = None

    def __post_init__(self):
        if self.preload and self.prod_manager is None:
            self.prod_manager = ProductManager(self.client, preload=self.preload)
    
    def day_sales(self,
                  check_date: date | datetime | str,
                  fields = GENERAL_PORPOUSE_POS_ORDER_LINE_FIELDS) -> list:
        """
        Returns the sales of the given date

        It does not have a found way to call by ORDER, it's only by
        ORDER_LINE
        """
        check_date = date_normalizer(check_date)
        
        model = POS.ORDER_LINE
        
        return self.client.search_read(
            model,
            domain = [
                ['create_date', '>', check_date]
            ],
            fields = fields
        )


    def register_sale(self, sale_date: date | datetime, product: str | int, client: Optional[str | int]) -> Response:
        ...
    
    def correct_sale(self, sale_id: str, sale_date: date | datetime, product: str | int, client: Optional[str | int]) -> Response:
        ...

    def cancel_sale(self, sale_id: str, sale_date: date | datetime, product: str | int, client: Optional[str | int]) -> Response:
        ...

    