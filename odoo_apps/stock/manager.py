'''
'''

from dataclasses import dataclass
# from typing import Optional
import pandas as pd
from typing import Optional

# from odoo_apps.utils.operators import Operator
from odoo_apps.client import OdooClient, RPCHandlerMetaclass
from odoo_apps.response import Response
from odoo_apps.models import PRODUCT, STOCK



@dataclass
class StockManager(metaclass=RPCHandlerMetaclass):
    """
    Inicializa el StockManager con un cliente de Odoo ya configurado.

    Args:
        odoo_client: Una instancia de la clase OdooClient.
    """
    client: OdooClient
    picking_type_id: Optional[int] = None
    location_src_id: Optional[int] = None
    location_dest_id: Optional[int] = None
    internal_stock_id: Optional[int] = None

    def __post_init__(self):
        print([
                self.picking_type_id is not None,
                self.location_src_id is not None,
                self.location_dest_id is not  None
                ])
        print(all(
            [
                self.picking_type_id is not None,
                self.location_src_id is not None,
                self.location_dest_id is not  None
                ]
        ))
        if self.internal_stock_id is None:
            self.internal_stock_id = self.client.search(
                STOCK.LOCATION,
                [
                    ['usage', '=', 'internal'],
                    ['name', '=', 'Stock']
                ]
            )

        if all(
            [
                self.picking_type_id is not None,
                self.location_src_id is not None,
                self.location_dest_id is not  None
                ]) is False:

            print('buscando info')
            picking_type = self.client.search_read(
                STOCK.PICKING_TYPE,
                [
                    ['code', '=', 'incoming']
                    # ['id', '>', 0]
                ],
                fields = [
                    'id',
                    'default_location_src_id',
                    'name',
                    'default_location_dest_id'
                ]
                # fields = odoo.get_models_fields(STOCK.PICKING_TYPE)
            )

            self.picking_type_id = picking_type[0]['id']
            self.location_src_id = picking_type[0]['default_location_src_id'][0]
            self.location_dest_id = picking_type[0]['default_location_dest_id'][0]

    def _find_internal_location(self):
        """
        Busca la ubicación interna por defecto para el inventario.

        Returns:
            int or False: El ID de la ubicación interna o False si no se encuentra.
        """
        location_ids = self.client.search(
            model = STOCK.LOCATION,
            domain = [('usage', '=', 'internal')]
        )
        if location_ids:
            return location_ids[0]
        return False

    def create_new_picking_line(self, product_name, product_id: int, quantity: int | float) -> list:
        """
        """
        return [
            # Comando: (0, 0, {valores}) para crear un nuevo registro.
            0, 0, {
                'name': f"Recibo de producto: {product_name}",
                'product_id': product_id,
                'product_uom_qty': quantity,
                'location_id': self.location_src_id,
                'location_dest_id': self.location_dest_id,
            }
        ]
    
    def create_picking_order(self, picking_lines: list) -> Response:
        """
        """

        picking_response = self.client.create(
            STOCK.PICKING,
            vals = [
                {
                    'picking_type_id': self.picking_type_id,
                    'location_id': self.location_src_id,
                    'location_dest_id': self.location_dest_id,
                    'move_ids_without_package': picking_lines,
                }
            ],
            hard = True
        )
        picking_id = picking_response.object
        if picking_response.status_code == 200:
            print(f"📦 Recibo de inventario CREADO CON ÉXITO. ID: {picking_id}")
        elif picking_response.status_code == 201:
            print(f"📦 Recibo de inventario ENCONTRADO. ID: {picking_id}")
        else:
            print(f"❌ Ocurrió un error: {picking_response.msg}")

        if picking_response.status_code in [200, 201]:
            action_confirm = self.client.models.execute_kw(
                self.client.db, self.client.uid, self.client.password,
                'stock.picking', 'action_confirm', [picking_id]
                )
            
            if not action_confirm:
                print("Problemas al momento de confirmar la orden", picking_id)
        



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
