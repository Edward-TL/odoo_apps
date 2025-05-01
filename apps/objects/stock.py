

from dataclasses import dataclass, fields
from typing import Literal

DisplayTypes = Literal["radio", "pills", "select", "color", "multi"]
# === FROM ODOO ===
# 'display_type': {'help': 'The display type used in the Product Configurator.',
#                   'selection': [['radio', 'Radio'],
#                                 ['pills', 'Pills'],
#                                 ['select', 'Select'],
#                                 ['color', 'Color'],
#                                 ['multi', 'Multi-checkbox']],
#                   'string': 'Display Type',



CreateVariants = Literal["always", "dynamic", "no_variant"]

# 'create_variant': {
#       'help': '- Instantly: All possible variants are created as '
            #     'soon as the attribute and its values are added to '
            #     'a product.\n'
            # '- Dynamically: Each variant is created '
            #     'only when its corresponding attributes and values '
            #     'are added to a sales order.\n'
            # '- Never: Variants are never created for '
            #     'the attribute.\n'
            # 'Note: this cannot be changed once the '
            #     'attribute is used on a product.',
# 'selection': [['always', 'Instantly'],
#                 ['dynamic', 'Dynamically'],
#                 ['no_variant', 'Never']],
# 'string': 'Variant Creation',
# 'type': 'selection'},

@dataclass
class ProductTemplate:
    name: str
    categ_id: str
    list_price: float
    qty_available: int
    pos_categ_ids: str | list
    public_categ_ids: str | list
    barcode: str
# 'public_categ_ids':
# {'help': 'The product will be available in each mentioned eCommerce category.
#           Go to Shop > Edit Click on the page and enable 'Categories' to view
#           all eCommerce categories.',
# 'string': 'Website Product Category',
#  'type': 'many2many'}
    allow_out_of_stock_order: bool = False
    available_in_pos: bool = True
    description: str = ""
    description_ecommerce: str = ""
    description_picking: str = ""
    description_pickingin: str = ""
    description_pickingout: str = ""
    description_purchase: str = ""
    description_sale: str = ""
    is_published: bool = False
    is_storable: bool = True
    sale_ok: bool = True
    show_availability: bool = True
    _type: Literal['consu', 'service', 'combo'] = 'consu'
# 'selection': [['consu', 'Goods'],
#             ['service', 'Service'],
#             ['combo', 'Combo']],
    def __post_init__(self):
        self.base_unit_price = self.list_price

    def export_to_dict(self) -> dict:
        """
        Returns the dictionary version of the class
        """
        return {
            field.name: getattr(self, field.name) \
                for field in fields(self) \
                    if getattr(self, field.name) not in {False, None}
            }
        