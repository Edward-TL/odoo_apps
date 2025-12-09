"""
"""

from dataclasses import dataclass
from typing import Optional

from odoo_apps.client import OdooClient, RPCHandlerMetaclass
from odoo_apps.response import Response
from odoo_apps.models import MANUFACTORY

from odoo_apps.mrp.objects import Bom, BomLine, ProductionOrder

@dataclass
class Factory(metaclass=RPCHandlerMetaclass):
    """
    Factory representation
    """

    client: OdooClient
    boms: Optional[list] = None

    def create_bom(self, bom: Bom, printer = False) -> Response:
        """
        Creates a Bill of Materials on Client's Odoo DB
        """
        bom_data = bom.export_to_dict()

        response = self.client.create(
            MANUFACTORY.BOM,
            vals = bom_data,
            domains = bom.domain,
            printer = printer
        )
        bom.id = response.object

        return response
    
    def create_bom_line(self, line: BomLine, printer = False) -> Response:
        """
        Creates a Bill of Materials Line on Client's Odoo DB
        """
        response = self.client.create(
            MANUFACTORY.BOM_LINE,
            domains = line.domain,
            vals = line.export_to_dict(),
            printer= printer
        )

        if response.status_code in [200, 201]:
            line.id = response.object
            return response
        
        return response
    
    def append_bom_line(self, bom: Bom, line: BomLine, printer = False) -> Optional[Response]:
        """
        Creates a Bill of Materials Line on Client's Odoo DB and adds it to the given BOM object
        """

        bom_line_response = None
        if line.id is None:
            bom_line_response = self.create_bom_line(line, printer)
            if bom_line_response.status_code in [200, 201]:
                line.id = bom_line_response.object

        if line.id not in bom.bom_line_ids:
            bom.bom_line_ids.append(line.id)
        # Don't know, something weird happen and Odoo didn't update it?

        if bom_line_response is None:
            return bom_line_response

        return None

    def update_bom_line(self, old_line: BomLine, new_line: BomLine, printer = False) -> Response:
        """
        Replace a Bill of Materials Line on Client's Odoo DB with it's new value
        """

        return self.client.update(
            MANUFACTORY.BOM_LINE,
            self.client.search(
                MANUFACTORY.BOM_LINE,
                old_line.domain
            ),
            new_vals = new_line.export_to_dict(),
            printer = printer
        )

    def delete_bom(self, boms_ids: list[int], printer = False) -> Response:
        """
        Deletes a Bill of Materials Line on Client's Odoo DB
        """

        return self.client.delete(
            MANUFACTORY.BOM,
            ids =  boms_ids,
            printer = printer
        )

    def delete_bom_lines(self, bom_lines_ids: list[int], printer = False) -> Response:
        """
        Deletes a Bill of Materials Line on Client's Odoo DB
        """

        return self.client.delete(
            MANUFACTORY.BOM_LINE,
            ids =  bom_lines_ids,
            printer = printer
        )
    
    def create_production_order(self, order: ProductionOrder, printer = False) -> Response:
        """
        Creates production order
        """
        order_data = order.export_to_dict()

        response = self.client.create(
            MANUFACTORY.PRODUCTION,
            vals = order_data,
            domains = order.domain,
            printer = printer
        )
        order.id = response.object

        return response

    def confirm_production_order(self, order_ids: int | list[int]):
        """
        Confirms production order
        """
        if not isinstance(order_ids, list):
            order_ids = [order_ids]

        return self.client.execute_kw(
            MANUFACTORY.PRODUCTION,
            kw = 'action_confirm',
            data = order_ids
        )
    
    def check_components_availability(self, order_ids: int | list[int]):
        """
        Check components availability
        """
        if not isinstance(order_ids, list):
            order_ids = [order_ids]

        return self.client.execute_kw(
            MANUFACTORY.PRODUCTION,
            kw = 'action_assign',
            data = order_ids
        )
