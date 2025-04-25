"""
Store interest Odoo models
"""

from dataclasses import dataclass

@dataclass
class Product:
    """
    Class representing a product in Odoo.
    """
    model = 'product.product'
    template = 'product.template'
    category = 'product.category'
    
product_model = Product()

@dataclass
class Stock:
    """
    Class representing the Stock in Odoo.
    """
    quant = 'stock.quant'
    location = 'stock.location'

stock_model = Stock()
