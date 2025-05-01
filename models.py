"""
Store interest Odoo models
"""

from dataclasses import dataclass

@dataclass
class Product:
    """
    Class representing a product in Odoo.
    """
    _name = 'product'
    _modules = (
        'attribute.custom.value','attribute.value','attribute',
        'catalog.mixin',
        'category',
        'combo.item','combo',
        'document',
        'image',
        'label.layout',
        'packaging',
        'pricelist.item', 'pricelist',
        'product',
        'public.category',
        'removal',
        'replenish',
        'ribbon',
        'supplierinfo',
        'tag',
        'template.attribute.exclusion','template.attribute.line',
        'template.attribute.value','template',
        'unspsc.code'
    )
    
    def __post_init__(self):
        for module in self._modules:
            attribute_name = module.upper().replace('.', '_')
            setattr(self, attribute_name, f"{self._name}.{module}")
    
PRODUCT = Product()

@dataclass
class Stock:
    """
    Class representing the Stock in Odoo.
    """
    QUANT = 'stock.quant'
    LOCATION = 'stock.location'

STOCK = Stock()


@dataclass
class Calendar:
    """
    Class representing Calendar tables in Odoo.
    """
    _name = 'calendar'
    _modules = (
    'alarm', 'alarm_manager',
    'attendee',
    'booking', 'booking.line',
    'event', 'event.type',
    'filters',
    'recurrence'
    )
    EVENT = 'calendar.event'
    def __post_init__(self):
        for module in self._modules:
            attribute_name = module.upper().replace('.', '_')
            setattr(self, attribute_name, f"{self._name}.{module}")
                
CALENDAR = Calendar()