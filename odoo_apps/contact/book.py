"""
Contact book
"""

from dataclasses import dataclass
from typing import Literal

from odoo_apps.client import OdooClient
from odoo_apps.response import standarize_response
from odoo_apps.models import CONTACTS

from odoo_apps.utils.operators import Operator

ReferenceField = Literal[
    'phone',
    'name',
    'email',
    'employee',
    'complete_name'
]

@dataclass
class ContactBook:
    """
    Represents a Contact book, thinked for search clients/users info,
    create or edit it.
    """
    client: OdooClient

    def get_contact_id(
        self, by: ReferenceField, reference: str, operator: Operator = '='
        ) -> int:
        """
        Returns JUST id value according to a simple domain
        """
        return self.client.search_read(
            model = CONTACTS.PARTNER,
            domain = [
                [by, operator, reference]
            ]
        )[0]['id']
    