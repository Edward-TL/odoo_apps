"""
Multicompany messy stuff
"""
# from odoo_apps.client import OdooClient
from odoo_apps.response import Response

def multicompany_correction(create_data: dict) -> dict | bool:
    """
    Sometimes, Odoo does not accept some procedures when multicompany is setup.
    This are the common fields that does not accept but can be updated and corrected
    """
    multicompany_non_acceptables = {}

    check_fields = [
        'company_id',
        'warehouse_id',
        'user_id'
        ]

    for check_field in check_fields:
        if check_field in create_data:
            if create_data[check_field] != 1:
                multicompany_non_acceptables[check_field] = create_data[check_field]
                del create_data[check_field]

    if len(multicompany_non_acceptables.keys()) == 0:
        return False

    return multicompany_non_acceptables

def correction_error(update_response: Response, correction_msg: str) -> None:
    """
    In place, updates the given response (update_response), changing:
    * msg
    * status_code to 409
    * status
    * action
    """
    update_response.msg = "Succes on creating, Error while correcting: \n"
    update_response.msg += correction_msg
    update_response.status_code = 409
    update_response.status = 'Creation OK, Update FAILED'
    update_response.action = 'create -> update'

