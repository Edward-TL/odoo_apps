"""
"""
# from copy import copy
from dataclasses import dataclass, field
from typing import Optional, Literal
from copy import copy
from pprint import pprint
from xmlrpc.client import Fault

import pandas as pd
from numpy import nan as np_nan

from odoo_apps.client import OdooClient
from odoo_apps.models import SALES
from odoo_apps.response import Response
from odoo_apps.sales.objects import Quotation, QuotationLine, Invoice
from odoo_apps.utils.multicompany import multicompany_correction, correction_error

@dataclass
class SalesManager:
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

    def __post_init__(self):
        if self.preload:
            pass
        pass

    def create_quotation(self, quotation: Quotation) -> Response:
        """
        By a given Quotation, creates it, considering that if there is a 
        multicompany setup, will update the fields that commonly cause conflicts
        when creating.
 
        """
        quotation_vals = quotation.export_to_dict()
        multicompany_check = multicompany_correction(quotation_vals)

        creation_response = self.client.create(
            SALES.ORDER,
            vals = quotation_vals,
            domains = [
                ['name', '=', quotation.name]
            ]
        )

        quotation.id = creation_response.object

        if multicompany_check:
            correction_response = self.client.update(
                SALES.ORDER,
                records_ids = [quotation.id],
                new_vals = multicompany_check
            )

            if correction_response.status_code not in [200,201]:
                correction_error(
                    update_response = creation_response,
                    correction_msg = correction_response.msg
                    )

        return creation_response

    def add_quotation_line(self, quotation: Quotation, quotation_line: QuotationLine) -> Response:
        """
        Creates a quoation line to a given quatation.
        """
        vals = quotation_line.export_to_dict()

        domain_keys = [k for k in vals.keys() if 'qty' not in k]

        order_line_domain = [
            [key, '=', vals[key]] for key in domain_keys
        ]

        # print(order_line_domain)
        resp = self.client.create(
            SALES.ORDER_LINE,
            vals = quotation_line.export_to_dict(),
            domains = order_line_domain
        )

        quotation_line.id = resp.object
        if quotation.product_lines is None:
            quotation.product_lines = [quotation_line.id]
        else:
            quotation.product_lines.append(quotation_line.id)

        return resp

    def make_invoice(self, quotation: Quotation) -> Response:
        """
        Updates state of given quotation to transform it into an Invoice
        """
        # 2. Llamada al asistente para crear la factura
        # El método 'sale.advance.payment.inv' es el asistente que Odoo usa para la creación de facturas.
        # Creamos una instancia de este asistente en el contexto de nuestra orden de venta.
        context = {
            'active_model': 'sale.order',
            'active_ids': [quotation.id],
            'active_id': quotation.id,
        }
        
        wizard_id = self.client.models.execute_kw(
            self.client.db, self.client.uid, self.client.password,
            'sale.advance.payment.inv', 'create',
            # Opción para facturar lo entregado (líneas facturables)
            [{'advance_payment_method': 'delivered'}]
            , {'context': context}
        )
        
        # logging.info(f"Asistente de facturación creado con ID: {wizard_id}")

        # 3. Ejecutar la acción del asistente para crear la factura final
        # Este método crea la factura borrador y devuelve la acción para abrir su vista.
        action = self.client.models.execute_kw(
            self.client.db, self.client.uid, self.client.password,
            'sale.advance.payment.inv', 'create_invoices',
            [wizard_id], {'context': context}
        )

        # 4. Extraer el ID de la factura creada desde la acción devuelta
        if action and action.get('res_id'):
            invoice_id = action.get('res_id')
            # logging.info(f"ÉXITO: Factura borrador creada con ID: {invoice_id} para la Orden de Venta ID: {order_id}")
            return invoice_id

        # Si no se devuelve un res_id, podemos buscar la factura en la orden de venta.
        order_data = self.client.models.execute_kw(
            self.client.db, self.client.uid, self.client.password,
            'sale.order', 'read',
            [quotation.id], {'fields': ['invoice_ids']}
        )
        if order_data and order_data[0]['invoice_ids']:
            # Tomamos la última factura creada
            invoice_id = order_data[0]['invoice_ids'][-1]
            # logging.info(f"ÉXITO (vía lectura): Factura borrador creada con ID: {invoice_id} para la Orden de Venta ID: {order_id}")
            return invoice_id
        else:
            # logging.error("No se pudo confirmar la creación de la factura. La acción no devolvió un ID.")
            return None


    def confirm_sale_order(self, quotation: Quotation) -> Response:
        """
        By confirming the given quotation, converts it to a sales order
        """
        # --- PASO 3: Confirmar la Cotización para convertirla en Orden de Venta ---
        # Esto automáticamente generará la factura en estado borrador
        # si el producto está configurado para ello.

        # Still missing a way to create a log for the managers.
        # log_msg = f"Quotation ID: {order_id} CONFIRMED."
        # log_msg += "Odoo should generate the corresponding invoice"
        # logging.info(log_msg)

        return self.client.models.execute_kw(
            self.client.db, self.client.uid, self.client.password,
            SALES.ORDER,
            'action_confirm',
            [quotation.id]
            )

    def delete_quotation(self, quotation: Quotation) -> Response:
        """
        Deletes the given quotation from Client's Odoo DB
        """

        return self.client.delete(
            SALES.ORDER,
            ids = quotation.id
        )

    def update_quation(self, quotation: Quotation, update_vals: dict) -> Response:
        """
        Updates quatation data
        """
        return self.client.update(
            SALES.ORDER,
            records_ids = quotation.id,
            new_vals = update_vals
        )

    def update_quotation_line(self, quotation_line: QuotationLine, update_vals: dict) -> Response:
        """
        Updates quatation data
        """
        return self.client.update(
            SALES.ORDER,
            records_ids = quotation_line.id,
            new_vals = update_vals
        )
