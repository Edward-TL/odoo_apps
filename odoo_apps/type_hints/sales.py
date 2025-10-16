"""
"""

from typing import Literal

ActivityExceptionDecoration = Literal[
    'warning',
    'danger'
    ]

ActivityState = Literal[
    'overdue',
    'today',
    'planned'
    ]

CompanyPriceInclude = Literal[
    'tax_included',
    'tax_excluded'
    ]

DeliveryStatus = Literal[
    'pending',
    'started',
    'partial',
    'full'
    ]

InvoiceStatus = Literal[
    'upselling',
    'invoiced',
    'to invoice',
    'no'
    ]

L10nMxEdiPaymentPolicy = Literal['PPD', 'PUE']

L10nMxEdiUsage = Literal[
    'G01', 'G02', 'G03',
    'I01', 'I02', 'I03', 'I04', 'I05', 'I06', 'I07', 'I08',
    'D01', 'D02', 'D03', 'D04', 'D05', 'D06', 'D07', 'D08', 'D09', 'D10',
    'S01'
    ]

PickingPolicy = Literal['direct', 'one']

State = Literal['draft', 'sent', 'sale', 'cancel']

TaxCalculationRoundingMethod = Literal['round_per_line', 'round_globally']

TermsType = Literal['plain', 'html']

# Order Lines
DisplayType = Literal['line_section', 'line_note']
ProductType = Literal['consu', 'service', 'combo']

QtyDeliveredMethod = Literal[
    'manual',
    'analytic',
    'stock_move',
    'milestones'
    ]

ServiceTracking = Literal[
    'no',
    'task_global_project',
    'task_in_project',
    'project_only'
    ]


