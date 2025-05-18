'''
'''

from dataclasses import dataclass
import pandas as pd
from client import OdooClientServer  # Importa la clase para la conexión a Odoo
from models import PRODUCT, STOCK  # Importa los modelos de Odoo
from .objects import DisplayTypes, CreateVariants


@dataclass
class StockManager:
    """
    Inicializa el StockManager con un cliente de Odoo ya configurado.

    Args:
        odoo_client: Una instancia de la clase OdooClientServer.
    """
    client: OdooClientServer


    def _find_internal_location(self):
        """
        Busca la ubicación interna por defecto para el inventario.

        Returns:
            int or False: El ID de la ubicación interna o False si no se encuentra.
        """
        domain = [('usage', '=', 'internal')]
        location_ids = self.client.search(STOCK.LOCATION, domain)
        if location_ids:
            return location_ids[0]
        return False

    
    def create_product_category(self, category_name: str, parent_id: int = False):
        """
        Crea una nueva categoría de producto en Odoo.

        Args:
            client: Una instancia de la clase OdooClientServer.
            category_name (str): El nombre de la nueva categoría.
            parent_id (int, optional): El ID de la categoría padre. Defaults to False (categoría raíz).

        Returns:
            int or False: El ID de la nueva categoría creada en Odoo, o False si hubo un error.
        """
        
        category_data = {
            'name': category_name,
            'parent_id': parent_id,
        }

        new_category_id = self.client.create(
            model = PRODUCT.CATEGORY,
            vals = category_data
            )

        return new_category_id
        
    def create_product_attribute(self, name: str,
        display_type: DisplayTypes = "select",
        create_variant: CreateVariants = "dynamic"
        ):
        """
        Crea un nuevo atributo de producto en Odoo. Sin valores
        """
        
        att_id = self.client.create(
            model = 'product.attribute',
            vals = {
                    'name': name,
                    'display_type': display_type,
                    'create_variant': create_variant,
                }
        )
        
        return att_id

    def append_attribute_value(
        self, attribute_id: int | str, name: str,
        default_extra_price: float | None = None,
        html_color: str | None = None,
        image: str | None = None
        ):
        """
        Append values to an existing Attribute
        """
        # If it's a string, it's because it's not known the attribute_id
        if isinstance(attribute_id, str):
            domain_field = "name"
            domain_model = PRODUCT.ATTRIBUTE
            domain_value = [(domain_field, '=', attribute_id)]
            attribute_id = self.client.search(domain_model, domain_value)

            if isinstance(attribute_id, list):
                attribute_id = attribute_id[0]
            else:
                attribute_id = self.client.create(PRODUCT.ATTRIBUTE, {'name':name})
        
        attribute_data = {
                'name': name,
                'attribute_id': attribute_id
            }
        if html_color:
            attribute_data['html_color'] = html_color
        
        if default_extra_price:
            attribute_data['default_extra_price'] = default_extra_price

        if image:
            attribute_data['image'] = image

        att_val_id = self.client.create(
            PRODUCT.ATTRIBUTE_VALUE,
            attribute_data
        )

        return att_val_id

    def create_product_template(self):
        pass

    def create_initial_inventory(self, products_table: pd.DataFrame):
        """
        Crea nuevos productos en Odoo y establece su cantidad inicial en el inventario.

        Args:
            products_df (pd.DataFrame): DataFrame de pandas con la información de los productos.
        """
        internal_location_id = self._find_internal_location()
        if not internal_location_id:
            print("Error: No se encontró una ubicación interna para el inventario.")
            return

        for _, row in products_table.iterrows():
            # Preparar los datos para la creación del producto (variante)
            product_data = {
                'default_code': row['default_code'] if pd.notna(row['default_code']) else False,
                'barcode': row['barcode'] if pd.notna(row['barcode']) else False,
                'name': row['name'],
                'is_published': row['is_published'],
                'product_template_variant_value_ids': row['product_template_variant_value_ids'],
                'lst_price': row['lst_price'],
                'standard_price': row['standard_price'],
                'pos_categ_ids': [(6, 0, [row['pos_categ_ids']])] if pd.notna(row['pos_categ_ids']) else False,
                'categ_id': row['categ_id'],
                'type': row['type'],
                'uom_id': row['uom_id'],
            }

            # Intentar buscar si el producto ya existe por 'default_code' o 'barcode'
            domain = []
            if product_data['default_code']:
                domain.append(('default_code', '=', product_data['default_code']))
            if product_data['barcode']:
                domain.append(('barcode', '=', product_data['barcode']))

            existing_product_ids = self.client.search(
                model = PRODUCT.PRODUCT,
                domain = domain
                )

            if existing_product_ids:
                product_code = product_data.get('default_code', row['barcode'])
                product_id = existing_product_ids[0]
                print(f"El producto con código '{product_code}' ya existe (ID: {product_id})", end = '. ')
                print("No se creará un nuevo producto.")
            else:

                # Crear el nuevo producto (variante)
                new_product_id = self.client.create(
                    model = PRODUCT.PRODUCT,
                    vals = product_data
                )

                if new_product_id:
                    print(f"Producto creado con ID: {new_product_id} - {row['name']}")

                    # Crear el registro de cantidad en el inventario
                    if pd.notna(row['qty_available']) and row['qty_available'] > 0:
                        inventory_data = {
                            'product_id': new_product_id,
                            'location_id': internal_location_id,
                            'inventory_quantity': row['qty_available'],
                            # Se asume que la cantidad teórica inicial es la misma
                            # Cosas de Odoo, I guess...
                            'theoretical_quantity': row['qty_available'], 
                        }

                        # Crear el registro de inventario
                        inventory_id = self.client.create(
                            model = STOCK.QUANT,
                            vals = inventory_data
                        )

                        if inventory_id:
                            print(f"Cantidad inicial de {row['qty_available']} establecida para el producto.")
                        else:
                            print("Error al establecer la cantidad inicial para el producto.")
                else:
                    print(f"Error al crear el producto: {row['name']}")
