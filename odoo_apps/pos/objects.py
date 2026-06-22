"""
Dataclasses that define Point of Sale records:
    a) A sale line (`pos.order.line`)
    b) A payment (`pos.payment`)
    c) An order (`pos.order`)

Same pattern as `odoo_apps.mrp.objects`: `PosOrder` builds a `self.domain`
(idempotent create on a unique `pos_reference`) and exposes `export_to_dict()`,
translating its child lines / payments into Odoo `(0, 0, {...})` commands.
"""

from dataclasses import dataclass, field
from typing import Literal, Optional

from odoo_apps.utils.cleaning import sort_dict

# Customer Invoice, Paid, Posted, etc. For demo data 'paid' is enough.
OrderState = Literal['draft', 'paid', 'done', 'invoiced', 'cancel']


@dataclass
class PosOrderLine:
    """
    A single `pos.order.line`.

    `product_id`: [many2one] Sold product.
    `qty`: [float] Quantity.
    `price_unit`: [float] Unit price (tax-included final price for this demo).
    `price_subtotal`: [float] Line total WITHOUT taxes.
    `price_subtotal_incl`: [float] Line total WITH taxes (what the customer pays).
    `tax_ids`: [many2many] List of `account.tax` ids (plain ints -> `(6, 0, ids)`).
    `full_product_name`: [char] Display label of the product.
    `discount`: [float] Discount (%).
    """
    product_id: int
    qty: float = 1.0
    price_unit: float = 0.0
    price_subtotal: float = 0.0
    price_subtotal_incl: float = 0.0
    tax_ids: Optional[list[int]] = None
    full_product_name: Optional[str] = False
    discount: float = 0.0

    def export_to_dict(self) -> dict:
        """Returns the line as an Odoo write-command-ready dict."""
        data = {
            'product_id': self.product_id,
            'qty': self.qty,
            'price_unit': self.price_unit,
            'price_subtotal': self.price_subtotal,
            'price_subtotal_incl': self.price_subtotal_incl,
            'discount': self.discount,
        }
        if self.full_product_name:
            data['full_product_name'] = self.full_product_name
        if self.tax_ids:
            data['tax_ids'] = [(6, 0, list(self.tax_ids))]
        return data


@dataclass
class PosPayment:
    """
    A single `pos.payment`.

    `payment_method_id`: [many2one] Payment method (cash, card...).
    `amount`: [float] Paid amount.
    """
    payment_method_id: int
    amount: float = 0.0

    def export_to_dict(self) -> dict:
        """Returns the payment as an Odoo write-command-ready dict."""
        return {
            'payment_method_id': self.payment_method_id,
            'amount': self.amount,
        }


@dataclass
class PosOrder:
    """
    A `pos.order`.

    `session_id`: [many2one] Open POS session this order belongs to.
    `lines`: list of `PosOrderLine` (converted to `(0, 0, {...})` on export).
    `payment_ids`: list of `PosPayment` (converted to `(0, 0, {...})` on export).
    `pos_reference`: [char] Receipt reference. Used for idempotent create.
    `amount_total`: [float] Total WITH taxes.
    `amount_tax`: [float] Total taxes.
    `amount_paid`: [float] Amount paid (== amount_total for a fully paid order).
    `amount_return`: [float] Change returned.
    `partner_id`: [many2one] Customer, optional.
    `date_order`: [datetime] Order date ('YYYY-MM-DD HH:MM:SS').
    `state`: [selection] Order state. 'paid' for demo data.
    """
    session_id: int
    lines: list  # list[PosOrderLine]
    pos_reference: str
    amount_total: float = 0.0
    amount_tax: float = 0.0
    amount_paid: float = 0.0
    amount_return: float = 0.0
    payment_ids: list = field(default_factory=list)  # list[PosPayment]
    partner_id: Optional[int] = None
    pricelist_id: Optional[int] = None
    fiscal_position_id: Optional[int] = None
    date_order: Optional[str] = None
    state: OrderState = 'paid'
    company_id: Optional[int] = None
    id: Optional[int] = None

    def __post_init__(self):
        self.domain = [
            ['pos_reference', '=', self.pos_reference]
        ]

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name == 'id' and value is not None:
            self.domain = [
                ['id', '=', self.id]
            ]

    def export_to_dict(self, drop: Optional[tuple] = ('domain', 'id', 'studio_fields')) -> dict:
        """
        Returns the dictionary version of the class, translating `lines` and
        `payment_ids` into Odoo `(0, 0, {...})` create commands and dropping empties.
        """
        data = self.__dict__.copy()
        if drop is not None:
            for field_name in drop:
                if field_name in data:
                    del data[field_name]

        data['lines'] = [(0, 0, line.export_to_dict()) for line in self.lines]
        data['payment_ids'] = [
            (0, 0, payment.export_to_dict()) for payment in self.payment_ids
        ]

        data_ref = data.copy()
        for k, v in data_ref.items():
            if k in ('lines', 'payment_ids'):
                continue
            if v is None or str(v) == 'nan':
                del data[k]

        return sort_dict(data)
