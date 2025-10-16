"""
Account Hint types
"""

from typing import Literal

AccountType = Literal[
    'asset_receivable',
    'asset_cash',
    'asset_current',
    'asset_non_current',
    'asset_prepayments',
    'asset_fixed',
    'liability_payable',
    'liability_credit_card',
    'liability_current',
    'liability_non_current',
    'equity',
    'equity_unaffected',
    'income',
    'income_other',
    'expense',
    'expense_other',
    'expense_depreciation',
    'expense_direct_cost',
    'off_balance'
    ]

CreateAsset = Literal['no', 'draft', 'validate']

InternalGroup = Literal[
    'equity',
    'asset',
    'liability',
    'income',
    'expense',
    'off'
]