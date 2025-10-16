"""
"""
# from datetime import datetime
from dataclasses import dataclass, fields# , field
from typing import Literal, Optional#, Union
import inspect

from odoo_apps.client import OdooClient
from odoo_apps.response import Response
from odoo_apps.models import ACCOUNT
from odoo_apps.utils.cleaning import sort_dict
# from odoo_apps.type_hints.account import (
#     AccountType,
#     CreateAsset,
#     InternalGroup
#     )


   # `account_type`: [selection] Account Type is used for information purpose,
    #     to generate country-specific legal reports, and set the rules to close a fiscal
    #     year and generate opening entries.
    #         - `asset_receivable` -> `Receivable`
    #         - `asset_cash` -> `Bank and Cash`
    #         - `asset_current` -> `Current Assets`
    #         - `asset_non_current` -> `Non-current Assets`
    #         - `asset_prepayments` -> `Prepayments`
    #         - `asset_fixed` -> `Fixed Assets`
    #         - `liability_payable` -> `Payable`
    #         - `liability_credit_card` -> `Credit Card`
    #         - `liability_current` -> `Current Liabilities`
    #         - `liability_non_current` -> `Non-current Liabilities`
    #         - `equity` -> `Equity`
    #         - `equity_unaffected` -> `Current Year Earnings`
    #         - `income` -> `Income`
    #         - `income_other` -> `Other Income`
    #         - `expense` -> `Expenses`
    #         - `expense_other` -> `Other Expenses`
    #         - `expense_depreciation` -> `Depreciation`
    #         - `expense_direct_cost` -> `Cost of Revenue`
    #         - `off_balance` -> `Off-Balance Sheet`
    # `active`: [boolean] Active
    # `asset_model_ids`: [many2many] An asset wil be created for each asset model when
    #     this account is used on a vendor bill or a refund
    # `budget_item_ids`: [one2many] Budget Item
    # `can_create_asset`: [boolean] Can Create Asset
    # `code`: [char] Code
    # `code_mapping_ids`: [one2many] Code Mapping
    # `code_store`: [char] Code Store
    # `company_currency_id`: [many2one] Company Currency
    # `company_fiscal_country_code`: [char] Company Fiscal Country Code
    # `company_ids`: [many2many] Companies
    # `create_asset`: [selection] Create Asset
    #     - `no` -> `No`
    #     - `draft` -> `Create in draft`
    #     - `validate` -> `Create and validate`
    # `create_date`: [datetime] Created on
    # `create_uid`: [many2one] Created by

    # `current_balance`: [float] Current Balance
    # `description`: [text] Description
    # `disallowed_expenses_category_id`: [many2one] Disallowed Expenses Category
    # `display_mapping_tab`: [boolean] Display Mapping Tab
    # `display_name`: [char] Display Name
    # `exclude_provision_currency_ids`: [many2many] Whether or not we have to make
    #     provisions for the selected foreign currencies.
    # `form_view_ref`: [char] Form View Ref
    # `group_id`: [many2one] Account prefixes can determine account groups.
    # `has_message`: [boolean] Has Message
    # `id`: [integer] ID
    # `include_initial_balance`: [boolean] Used in reports to know if we should consider
    #     journal items from the beginning of time instead of from the fiscal year only.
    #     Account types that should be reset to zero at each new fiscal year (like expenses,
    #     revenue..) should not have this option set.
    # `internal_group`: [selection] Internal Group
    #     - `equity` -> `Equity`
    #     - `asset` -> `Asset`
    #     - `liability` -> `Liability`
    #     - `income` -> `Income`
    #     - `expense` -> `Expense`
    #     - `off` -> `Off Balance`
    # `l10n_mx_is_sat_invalid`: [boolean] L10N Mx Is Sat Invalid
    # `message_attachment_count`: [integer] Attachment Count
    # `message_follower_ids`: [one2many] Followers
    # `message_has_error`: [boolean] If checked, some messages have a delivery error.
    # `message_has_error_counter`: [integer] Number of messages with delivery error
    # `message_has_sms_error`: [boolean] If checked, some messages have a delivery error.
    # `message_ids`: [one2many] Messages
    # `message_is_follower`: [boolean] Is Follower
    # `message_needaction`: [boolean] If checked, new messages require your attention.
    # `message_needaction_counter`: [integer] Number of messages requiring action
    # `message_partner_ids`: [many2many] Followers (Partners)
    # `multiple_assets_per_line`: [boolean] Multiple asset items will be generated
    #     depending on the bill line quantity instead of 1 global asset.
    # `name`: [char] Account Name
    # `non_trade`: [boolean] If set, this account will belong to Non Trade
    #     Receivable/Payable in reports and filters.
    #     If not, this account will belong to Trade Receivable/Payable in reports and filters.
    # `note`: [text] Internal Notes
    # `opening_balance`: [monetary] Opening Balance
    # `opening_credit`: [monetary] Opening Credit
    # `opening_debit`: [monetary] Opening Debit
    # `placeholder_code`: [char] Display code
    # `rating_ids`: [one2many] Ratings
    # `reconcile`: [boolean] Check this box if this account allows invoices & payments
    #     matching of journal items.
    # `related_taxes_amount`: [integer] Related Taxes Amount
    # `root_id`: [many2one] Root
    # `tag_ids`: [many2many] Optional tags you may want to assign for custom reporting
    # `tax_ids`: [many2many] Default Taxes
    # `used`: [boolean] Used
    # `website_message_ids`: [one2many] Website communication history
    # `write_date`: [datetime] Last Updated on
    # `write_uid`: [many2one] Last Updated by

# ---------- CLASS ATTRIBUTES ----------- 
   # create_asset: CreateAsset = 'no'
    # account_type: AccountType
    # internal_group: InternalGroup = 'asset'
    # company_fiscal_country_code: str = 'MX'
    
    # company_ids: list[int] = field(default_factory=[1])
    # group_id: int = 4 # 101.01 Cash in hand
    # tax_ids: Optional[list] = None

    # description: str | bool = False

    # rating_ids: Optional[list] = None

    # exclude_provision_currency_ids: Optional[list] = None
    # budget_item_ids: Optional[list] = None
    # l10n_mx_is_sat_invalid: bool = False
    # asset_model_ids: Optional[list] = None
    # can_create_asset: bool = False
    # multiple_assets_per_line: bool = False
    
    # tag_ids: list = field(default_factory=[4])
    # root_id: list = field(default_factory=['10', '10'])
    # include_initial_balance: bool = True
    # opening_debit: float = 0.0
    # opening_credit: float = 0.0
    # opening_balance: float = 0.0
    # current_balance: float = 0.0
    
    # related_taxes_amount: int = 0

    # message_is_follower: bool = False
    # message_follower_ids: Optional[list] = None
    # message_partner_ids: Optional[list] = None
    # message_ids: list = field(default_factory=[307])
    # has_message: bool = True
    # message_needaction: bool = False
    # message_needaction_counter: int = 0
    # message_has_error: bool = False
    # message_has_error_counter: int = 0
    # message_attachment_count: int = 0
    # website_message_ids: Optional[list] = None
    # message_has_sms_error: bool = False
    # note: str | bool = False
    # code_mapping_ids: list = field(default_factory=[1270001])
    # display_mapping_tab: bool = False
    
    # form_view_ref: str = 'account_asset.view_account_asset_form'

@dataclass
class Account:
    """
    `code`: [char] Code
    `currency_id`: [many2one] Forces all journal items in this account to have a
        specific currency (i.e. bank journals).
        If no currency is set, entries can useany currency.
        {33: "MXN", 1: "USD"}
    `name`: [char] Account Name
    `non_trade`: [boolean] If set, this account will belong to Non Trade
        Receivable/Payable in reports and filters.
        If not, this account will belong to Trade Receivable/Payable in reports and filters.
    `reconcile`: [boolean] Check this box if this account allows invoices & payments
        matching of journal items.
    """

    name: str
    code: str # '101.01.01'
    reconcile: bool = True
    id: Optional[int] = None
    non_trade: bool = False
    currency_id: int = 33 # MXN 1 (one) for USD
    studio_fields: Optional[list[str] | dict[str, str]] = None

    def __post_init__(self):
        self.domain = [
            ['code', '=', self.code]
        ]
        if self.studio_fields is not None:
            if isinstance(self.studio_fields, list):
                for field in self.studio_fields:
                    setattr(self, field, None)

            if isinstance(self.studio_fields, dict):
                for field, val in self.studio_fields.items():
                    setattr(self, field, val)

    def export_to_dict(self, drop: Optional[tuple] = ('domain', 'id', 'studio_fields')) -> dict:
        """
        Returns the dictionary version of the class
        """
        data = self.__dict__.copy()
        if drop is not None:
            for field in drop:
                del data[field]

        return sort_dict(data)
