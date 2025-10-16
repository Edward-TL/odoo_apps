"""
"""

from typing import Literal

ActivityExceptionDecoration = Literal['warning', 'danger']
ActivityState = Literal['overdue', 'today', 'planned']
AutopostBills = Literal['always', 'ask', 'never']
CompanyType = Literal['person', 'company']
FollowupReminderType = Literal['automatic', 'manual']
FollowupStatus = Literal['in_need_of_action', 'with_overdue_invoices', 'no_action_needed']
InvoiceEdiFormat = Literal['facturx', 'ubl_bis3', 'xrechnung', 'nlcius', 'ubl_a_nz', 'ubl_sg']
InvoiceSendingMethod = Literal['manual', 'email', 'snailmail']
L10nMxEdiFiscalRegime = Literal[
    '601', '603', '605', '606', '607', '608', '609', '610',
    '611', '612', '614', '615', '616',
    '620', '621', '622', '623', '624', '625', '626', '628', '629',
    '630'
]
L10nMxEdiPaymentPolicy = Literal['PPD', 'PUE']
L10nMxEdiUsage = Literal[
    'G01', 'G02', 'G03',
    'I01', 'I02', 'I03', 'I04', 'I05', 'I06', 'I07', 'I08',
    'D01', 'D02', 'D03', 'D04', 'D05', 'D06', 'D07', 'D08', 'D09', 'D10',
    'S01']
L10nMxTypeOfOperation = Literal['02', '03', '06', '07', '08', '85', '87']
Lang = Literal['es_419', 'es_MX']
PeppolEas = Literal[
    '9923', '9922', '0151', '9914', '9915',
    '0208', '9925', '9924', '9926', '9934',
    '9928', '9929', '0096', '0184', '0198',
    '0191', '9931', '0037', '0216', '0213',
    '0002', '0009', '9957', '0225', '0240',
    '0204', '9930', '9933', '9910', '0196',
    '9935', '0211', '0097', '0188', '0221',
    '0218', '9939', '9936', '0200', '9937',
    '9938', '9942', '0230', '9943', '9940',
    '9941', '0106', '0190', '9944', '0192',
    '9945', '9946', '9947', '9948', '0195',
    '9949', '9950', '9920', '0007', '9955',
    '9927', '0183', '9952', '0235', '9932',
    '9959', '0060', '0088', '0130', '0135',
    '0142', '0193', '0199', '0201', '0202',
    '0209', '0210', '9913', '9918', '9919',
    '9951', '9953', 'AN', 'AQ', 'AS', 'AU', 'EM'
    ]
Trust = Literal['good', 'normal', 'bad']
Type = Literal['contact', 'invoice', 'delivery', 'other']
