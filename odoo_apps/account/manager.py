from dataclasses import dataclass, field
from typing import Optional, Literal
from copy import copy
from pprint import pprint

from odoo_apps.client import OdooClient, RPCHandlerMetaclass
from odoo_apps.models import ACCOUNT#, ACCOUNT_REPORTS
from odoo_apps.response import Response

from odoo_apps.account.objects import Account


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
