'''
'''

from dataclasses import dataclass
import pandas as pd
from client import OdooClientServer  # Importa la clase para la conexión a Odoo
from models import product_model, stock_model  # Importa los modelos de Odoo


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
        location_ids = self.client.search(stock_model.location, domain)
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
        product_category_model = product_model.category
        category_data = {
            'name': category_name,
            'parent_id': parent_id,
        }

        # Verificar si la categoría ya existe por nombre (en la raíz o bajo el padre especificado)
        domain = [('name', '=', category_name)]
        if parent_id:
            domain.append(('parent_id', '=', parent_id))
        else:
            domain.append(('parent_id', '=', False))

        existing_category_ids = self.client.search(product_category_model, domain)

        if not existing_category_ids:
            try:
                new_category_id = self.client.create(product_category_model, category_data)
                print(f"Categoría '{category_name}' creada con ID: {new_category_id}")
                return new_category_id
            except Exception as e:
                print(f"Error al crear la categoría '{category_name}': {e}")
                return False
        else:
            print(f"La categoría '{category_name}' ya existe (ID: {existing_category_ids[0]}).")
            return existing_category_ids[0]


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
                model = product_model.model,
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
                    model = product_model.model,
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
                            model = stock_model.quant,
                            vals = inventory_data
                        )

                        if inventory_id:
                            print(f"Cantidad inicial de {row['qty_available']} establecida para el producto.")
                        else:
                            print("Error al establecer la cantidad inicial para el producto.")
                else:
                    print(f"Error al crear el producto: {row['name']}")

# Ejemplo de uso (esto iría en un flujo o en un script principal):
if __name__ == '__main__':
    # Crear una instancia del cliente de Odoo
    odoo_client = OdooClientServer(
        user_info={'db': 'your_db', 'uid': 1, 'password': 'your_password'})

    # Crear una instancia del StockManager
    stock_manager = StockManager(client=odoo_client)

    # Leer el DataFrame de productos desde un archivo CSV (o cualquier otra fuente)
    products_df = pd.read_csv('path_to_your_products_file.csv')

    # Crear el inventario inicial
    stock_manager.create_initial_inventory(products_df)