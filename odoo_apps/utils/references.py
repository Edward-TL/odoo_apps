"""
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class ProductsReference:
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
            if self.attributes is not None:
                self.attributes = set(self.attributes)
            if self.drop is not None:
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

MEXICAN_STATES = {
    'Aguascalientes': 485,
    'Baja California': 486,
    'Baja California Sur': 487,
    'Campeche': 490,
    'Chihuahua': 488,
    'Chiapas': 492,
    'Ciudad de México': 493,
    'Coahuila': 491,
    'Colima': 489,
    'Durango': 494,
    'Guerrero': 495,
    'Guanajuato': 496,
    'Hidalgo': 497,
    'Jalisco': 498,
    'México': 501,
    'Michoacán': 499,
    'Morelos': 500,
    'Nayarit': 502,
    'Nuevo León': 503,
    'Oaxaca': 504,
    'Puebla': 505,
    'Querétaro': 507,
    'Quintana Roo': 506,
    'Sinaloa': 508,
    'San Luis Potosí': 509,
    'Sonora': 510,
    'Tabasco': 511,
    'Tamaulipas': 513,
    'Tlaxcala': 512,
    'Veracruz': 514,
    'Yucatán': 515,
    'Zacatecas': 516
 }
