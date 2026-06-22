from dataclasses import dataclass, field
from typing import Optional, Literal
from copy import copy
from pprint import pprint

from odoo_apps.client import OdooClient, RPCHandlerMetaclass
from odoo_apps.models import ACCOUNT#, ACCOUNT_REPORTS
from odoo_apps.response import Response

from odoo_apps.account.objects import Account, Invoice


@dataclass
class AccountManager(metaclass=RPCHandlerMetaclass):
    """
    Search for products store on Client's database.
    
    Args:
        - client: OdooClient.

    Every dictionary value is an ID, as every key is the
    value name. This makes it easier and faster to verify in
    further actions.
    """
    client: OdooClient
    # preload: bool = True
    accounts: Optional[list[dict]] = None
    studio_fields: Optional[list[str] | dict[str, str]] = None

    def create_account(self, account: Account, printer = False) -> Response:
        """
        Creates Account on the given OdooClient
        """
        account_data = account.export_to_dict()

        response = self.client.create(
            ACCOUNT.ACCOUNT,
            vals = account_data,
            domains = account.domain,
            printer = printer
        )
        account.id = response.object

        return response


@dataclass
class InvoiceManager(metaclass=RPCHandlerMetaclass):
    """
    Creates customer invoices / "notas" (`account.move`, `move_type='out_invoice'`)
    on the client's Odoo DB. Mirrors `odoo_apps.mrp.manager.Factory`: idempotent
    create through the object's `domain` (a unique `ref`).

    Args:
        - client: OdooClient.
    """
    client: OdooClient

    def create_invoice(self, invoice: Invoice, post: bool = False, printer = False) -> Response:
        """
        Creates a customer invoice. If `post=True`, the move is validated
        (`action_post`) so it becomes a registered invoice instead of a draft.
        """
        response = self.client.create(
            ACCOUNT.MOVE,
            vals = invoice.export_to_dict(),
            domains = invoice.domain,
            printer = printer
        )
        invoice.id = response.object

        # Solo validar si está en borrador: re-ejecutar el cargador encuentra
        # facturas ya existentes/posteadas (status 200) y `action_post` sobre una
        # ya posteada lanzaría "must be in draft".
        if post and invoice.id:
            states = self.client.read(ACCOUNT.MOVE, ids=[invoice.id], fields=["state"])
            if states and states[0].get("state") == "draft":
                self.post_invoice(invoice.id)

        return response

    def post_invoice(self, move_ids: int | list[int]):
        """
        Validates (posts) one or several invoices via `account.move.action_post`.
        """
        if not isinstance(move_ids, list):
            move_ids = [move_ids]

        # `data` is passed straight through as the positional-args list of Odoo's
        # execute_kw, so a recordset method needs `[ids]` (ids wrapped once).
        return self.client.execute_kw(
            ACCOUNT.MOVE,
            kw = 'action_post',
            data = [move_ids]
        )
