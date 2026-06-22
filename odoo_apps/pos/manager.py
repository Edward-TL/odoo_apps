from dataclasses import dataclass
from typing import Optional, Literal
from datetime import datetime, date, timedelta

from odoo_apps.client import OdooClient, RPCHandlerMetaclass
from odoo_apps.models import PRODUCT, POS
from odoo_apps.response import Response

from odoo_apps.product.manager import ProductManager
from odoo_apps.pos.objects import PosOrder
from odoo_apps.utils.time_management import date_normalizer

product_model = {
    'CATEGORY': PRODUCT.CATEGORY,
    'ATTRIBUTE_VALUE': PRODUCT.ATTRIBUTE_VALUE,
    'ATTRIBUTE': PRODUCT.ATTRIBUTE
}

main_tmpl_att_val_fields = [
'id', 'display_name', "product_template_variant_value_ids"
]

GENERAL_PORPOUSE_POS_ORDER_LINE_FIELDS = (
    'full_product_name', # Nombre del producto
    'product_id',
    'qty',
    'product_uom_id',
    'attribute_value_ids',
    'create_date'
)



@dataclass
class PosManager(metaclass=RPCHandlerMetaclass):
    """
    Search for products store on Client's database.
    
    Args:
        - client: OdooClient.

    Every dictionary value is an ID, as every key is the
    value name. This makes it easier and faster to verify in
    further actions.
    """
    client: OdooClient
    preload: bool = True
    prod_manager: Optional[ProductManager] = None

    def __post_init__(self):
        if self.preload and self.prod_manager is None:
            self.prod_manager = ProductManager(self.client, preload=self.preload)
    
    def day_sales(self,
                  check_date: date | datetime | str,
                  fields = GENERAL_PORPOUSE_POS_ORDER_LINE_FIELDS) -> list:
        """
        Returns the sales of the given date

        It does not have a found way to call by ORDER, it's only by
        ORDER_LINE
        """
        day_start_str = date_normalizer(check_date)
        day_start = datetime.strptime(day_start_str, "%Y-%m-%d %H:%M:%S").replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        next_day = day_start + timedelta(days=1)
        fmt = "%Y-%m-%d %H:%M:%S"

        return self.client.search_read(
            POS.ORDER_LINE,
            domain = [
                ['create_date', '>=', day_start.strftime(fmt)],
                ['create_date', '<', next_day.strftime(fmt)],
            ],
            fields = fields
        )


    # ------------------------------------------------------------------ #
    # Session helpers
    # ------------------------------------------------------------------ #
    def get_config_id(self, config_name: Optional[str] = None) -> int:
        """
        Returns a `pos.config` id. If `config_name` is given it is searched by
        name, otherwise the first available POS is returned.
        """
        domain = [['name', '=', config_name]] if config_name else [['id', '>', 0]]
        configs = self.client.search_read(
            POS.CONFIG, domain=domain, fields=['id', 'name'], limit=1
        )
        if not configs:
            raise ValueError(
                f"No pos.config found for {config_name!r}. "
                "Make sure the Point of Sale app is installed and at least one POS exists."
            )
        return configs[0]['id']

    def get_open_session(self, config_id: int) -> Optional[int]:
        """Returns the id of an already-open session for the config, if any."""
        sessions = self.client.search_read(
            POS.SESSION,
            domain=[
                ['config_id', '=', config_id],
                ['state', 'in', ['opening_control', 'opened']],
            ],
            fields=['id', 'state'],
            limit=1,
        )
        return sessions[0]['id'] if sessions else None

    def open_session(self, config_id: int) -> int:
        """
        Returns an open session for `config_id`, creating and opening one if none
        exists. The opening transition is best-effort (wrapped in try/except) so it
        keeps working across Odoo majors.
        """
        session_id = self.get_open_session(config_id)
        if session_id:
            return session_id

        response = self.client.create(
            POS.SESSION,
            vals={'config_id': config_id},
            domains=[['config_id', '=', config_id], ['state', '=', 'opening_control']],
        )
        session_id = response.object

        for method in ('action_pos_session_open', 'action_pos_session_openning_control'):
            try:
                self.client.execute_kw(POS.SESSION, kw=method, data=[[session_id]])
                break
            except Exception:  # noqa: BLE001 - best effort across versions
                continue

        return session_id

    def get_payment_method_id(self, config_id: int) -> int:
        """Returns the first payment method id configured on the POS."""
        configs = self.client.read(
            POS.CONFIG, ids=[config_id], fields=['payment_method_ids']
        )
        methods = configs[0].get('payment_method_ids') if configs else None
        if not methods:
            raise ValueError(
                f"pos.config {config_id} has no payment methods configured."
            )
        return methods[0]

    def get_pricelist_id(self, config_id: int) -> Optional[int]:
        """Returns the default pricelist id of the POS, if any."""
        configs = self.client.read(
            POS.CONFIG, ids=[config_id], fields=['pricelist_id']
        )
        pricelist = configs[0].get('pricelist_id') if configs else None
        # many2one comes back as [id, name] or False
        return pricelist[0] if pricelist else None

    # ------------------------------------------------------------------ #
    # Sales
    # ------------------------------------------------------------------ #
    def register_sale(self, order: PosOrder, printer: bool = False) -> Response:
        """
        Creates a `pos.order` (with its lines and payments) on the client's DB.

        The order must already carry a valid `session_id`; use `open_session()` to
        obtain one. Creation is idempotent through `order.pos_reference`.
        """
        response = self.client.create(
            POS.ORDER,
            vals=order.export_to_dict(),
            domains=order.domain,
            printer=printer,
        )
        order.id = response.object
        return response

    def correct_sale(self, sale_id: str, sale_date: date | datetime, product: str | int, client: Optional[str | int]) -> Response:
        ...

    def cancel_sale(self, sale_id: str, sale_date: date | datetime, product: str | int, client: Optional[str | int]) -> Response:
        ...

