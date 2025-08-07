"""
Store interest Odoo models
"""

from dataclasses import dataclass, fields
import inspect
from .utils.cleaning import generate_dict

@dataclass
class TableExample:
    """
    Example of a table
    """
    _name = 'name'
    module = 'name.module'
    def __post_init__(self):
        self.modules = generate_dict(self)

def string_class(data_obj: TableExample) -> str:
    """
    Generate a string representation of the class.
    :param data_obj: Data Class to generate the string from.
    :return: String representation of the class.
    """
    str_class = ""
    print(data_obj.modules.items)
    for k,v in data_obj.modules.items():
        str_class += f"{k}: {v} \n"

    return str_class

@dataclass
class Product:
    """
    Class representing a product in Odoo.
    """
    _name = 'product'
    ATTRIBUTE_CUSTOM_VALUE = 'product.attribute.custom.value'
    ATTRIBUTE_VALUE = 'product.attribute.value'
    ATTRIBUTE = 'product.attribute'
    CATALOG_MIXIN = 'product.catalog.mixin'
    CATEGORY = 'product.category'
    COMBO_ITEM = 'product.combo.item'
    COMBO = 'product.combo'
    DOCUMENT = 'product.document'
    IMAGE = 'product.image'
    LABEL_LAYOUT = 'product.label.layout'
    PACKAGING = 'product.packaging'
    PRICELIST_ITEM = 'product.pricelist.item'
    PRICELIST = 'product.pricelist'
    PRODUCT = 'product.product'
    PUBLIC_CATEGORY = 'product.public.category'
    REMOVAL = 'product.removal'
    REPLENISH = 'product.replenish'
    RIBBON = 'product.ribbon'
    SUPPLIERINFO = 'product.supplierinfo'
    TAG = 'product.tag'
    TEMPLATE_ATTRIBUTE_EXCLUSION = 'product.template.attribute.exclusion'
    TEMPLATE_ATTRIBUTE_LINE = 'product.template.attribute.line'
    TEMPLATE_ATTRIBUTE_VALUE = 'product.template.attribute.value'
    TEMPLATE = 'product.template'
    UNSPSC_CODE = 'product.unspsc.code'

    def __post_init__(self):
        self.modules = generate_dict(self)
        self.members = inspect.getmembers(type(self))
        self.fields = {k: v for k,v in dict(self.members).items() if not k.startswith('__')}

    def __str__(self):
        return string_class(self)

PRODUCT = Product()

@dataclass
class Stock:
    """
    Class representing the Stock in Odoo.
    """
    BACKORDER_CONFIRMATION = 'stock.backorder.confirmation'
    BACKORDER_CONFIRMATION_LINE = 'stock.backorder.confirmation.line'
    CHANGE_PRODUCT_QTY = 'stock.change.product.qty'
    FORECASTED_PRODUCT_PRODUCT = 'stock.forecasted_product_product'
    FORECASTED_PRODUCT_TEMPLATE = 'stock.forecasted_product_template'
    INVENTORY_ADJUSTMENT_NAME = 'stock.inventory.adjustment.name'
    INVENTORY_CONFLICT = 'stock.inventory.conflict'
    INVENTORY_WARNING = 'stock.inventory.warning'
    LOCATION = 'stock.location'
    LOT_REPORT = 'stock.lot.report'
    LOT = 'stock.lot'
    MOVE_LINE = 'stock.move.line'
    MOVE = 'stock.move'
    ORDERPOINT_SNOOZE = 'stock.orderpoint.snooze'
    PACKAGE_DESTINATION = 'stock.package.destination'
    PACKAGE_TYPE = 'stock.package.type'
    PACKAGE_LEVEL = 'stock.package_level'
    PICKING_TYPE = 'stock.picking.type'
    PICKING = 'stock.picking'
    PUTAWAY_RULE = 'stock.putaway.rule'
    QUANT_PACKAGE = 'stock.quant.package'
    QUANT_RELOCATE = 'stock.quant.relocate'
    QUANT = 'stock.quant'
    QUANTITY_HISTORY = 'stock.quantity.history'
    REPLENISH_MIXIN = 'stock.replenish.mixin'
    REPLENISHMENT_INFO = 'stock.replenishment.info'
    REPLENISHMENT_OPTION = 'stock.replenishment.option'
    REPORT = 'stock.report'
    REQUEST_COUNT = 'stock.request.count'
    RETURN_PICKING = 'stock.return.picking'
    RETURN_PICKING_LINE = 'stock.return.picking.line'
    ROUTE = 'stock.route'
    RULE = 'stock.rule'
    RULES_REPORT = 'stock.rules.report'
    SCRAP_REASON_TAG = 'stock.scrap.reason.tag'
    SCRAP = 'stock.scrap'
    STORAGE_CATEGORY = 'stock.storage.category'
    STORAGE_CATEGORY_CAPACITY = 'stock.storage.category.capacity'
    TRACEABILITY_REPORT = 'stock.traceability.report'
    TRACK_CONFIRMATION = 'stock.track.confirmation'
    TRACK_LINE = 'stock.track.line'
    VALUATION_LAYER = 'stock.valuation.layer'
    VALUATION_LAYER_REVALUATION = 'stock.valuation.layer.revaluation'
    WAREHOUSE_ORDERPOINT = 'stock.warehouse.orderpoint'
    WAREHOUSE = 'stock.warehouse'
    WARN_INSUFFICIENT_QTY = 'stock.warn.insufficient.qty'
    WARN_INSUFFICIENT_QTY_SCRAP = 'stock.warn.insufficient.qty.scrap'
    WARN_INSUFFICIENT_QTY_UNBUILD = 'stock.warn.insufficient.qty.unbuild'

    def __post_init__(self):
        self.modules = generate_dict(self)
        self.members = inspect.getmembers(type(self))
        self.fields = {k: v for k,v in dict(self.members).items() if not k.startswith('__')}

    def __str__(self):
        return string_class(self)

STOCK = Stock()


@dataclass
class Calendar:
    """
    Class representing Calendar tables in Odoo.
    """
    _name = 'calendar'
    ALARM = 'calendar.alarm'
    ALARM_MANAGER = 'calendar.alarm_manager'
    ATTENDEE = 'calendar.attendee'
    BOOKING_LINE = 'calendar.booking.line'
    BOOKING = 'calendar.booking'
    EVENT_TYPE = 'calendar.event.type'
    EVENT = 'calendar.event'
    FILTERS = 'calendar.filters'
    POPOVER_DELETE_WIZARD = 'calendar.popover.delete.wizard'
    PROVIDER_CONFIG = 'calendar.provider.config'
    RECURRENCE = 'calendar.recurrence'

    def __post_init__(self):
        self.modules = generate_dict(self)
        self.members = inspect.getmembers(type(self))
        self.fields = {k: v for k,v in dict(self.members).items() if not k.startswith('__')}

    def __str__(self):
        return string_class(self)

CALENDAR = Calendar()

@dataclass
class Appointment:
    """
    Class representing Appointment tables in Odoo.
    """
    _name = 'appointment'
    ANSWER_INPUT = 'appointment.answer.input'
    ANSWER = 'appointment.answer'
    BOOKING_LINE = 'appointment.booking.line'
    INVITE = 'appointment.invite'
    MANAGE_LEAVES = 'appointment.manage.leaves'
    QUESTION = 'appointment.question'
    RESOURCE = 'appointment.resource'
    SLOT = 'appointment.slot'
    TYPE = 'appointment.type'

    def __post_init__(self):
        self.modules = generate_dict(self)
        self.members = inspect.getmembers(type(self))
        self.fields = {k: v for k,v in dict(self.members).items() if not k.startswith('__')}

    def __str__(self):
        return string_class(self)
        
APPOINTMENT = Appointment()

@dataclass
class Resource:
    """
    ** CALENDAR_ATTENDANCE = Work Detail.
    ** CALENDAR_LEAVES = Resource Time Off Detail.
     - CALENDAR = Resource Working Time: Calendar model for a resource.
        It has:
            * attendance_ids: list of `resource.calendar.attendance` that are a working interval
                in a given weekday.
            * leave_ids: list of leaves linked to this calendar.
                A leave can be general or linked to a specific resource, depending on its
                `resource_id`.
                
        All methods in this class use "intervals".
            An "interval" is a tuple -> (begin_datetime, end_datetime).
            A list of intervals is therefore a list of tuples:
            
                            [(begin_datetime, end_datetime)]
            
            holding several intervals of work or leaves. 
    - MIXIN = Resource Mixin: The base model, which is implicitly inherited by all models.
    ** RESOURCE = Resources

    ** [Main super-class for regular database-persisted.
        Odoo models are created by inheriting from this class]
    """


    _name = "resource"
    CALENDAR_ATTENDANCE = 'resource.calendar.attendance'
    CALENDAR_LEAVES = 'resource.calendar.leaves'
    CALENDAR = 'resource.calendar'
    MIXIN = 'resource.mixin'
    RESOURCE = 'resource.resource'

    def __post_init__(self):
        self.modules = generate_dict(self)
        self.members = inspect.getmembers(type(self))
        self.fields = {k: v for k,v in dict(self.members).items() if not k.startswith('__')}

    def __str__(self):
        return string_class(self)

RESOURCE = Resource()

@dataclass
class Contacts:
    """
    Tables here are the one related to the Contacts info
    """
    _name = 'res'
    COMPANY = 'res.company'
    GROUPS = 'res.groups'
    PARTNER_BANK = 'res.partner.bank'
    PARTNER_CATEGORY = 'res.partner.category'
    PARTNER_INDUSTRY = 'res.partner.industry'
    PARTNER_TITLE = 'res.partner.title'
    PARTNER = 'res.partner'
    USERS = 'res.users'

    def __post_init__(self):
        self.modules = generate_dict(self)
        self.members = inspect.getmembers(type(self))
        self.fields = {k: v for k,v in dict(self.members).items() if not k.startswith('__')}

    def __str__(self):
        return string_class(self)

CONTACTS = Contacts()

@dataclass
class Pos:
    """Point Of Sale tables"""
    _name = 'pos'
    BILL = 'pos.bill'
    BUS_MIXIN = 'pos.bus.mixin'
    CATEGORY = 'pos.category'
    CLOSE_SESSION_WIZARD = 'pos.close.session.wizard'
    CONFIG = 'pos.config'
    DAILY_SALES_REPORTS_WIZARD = 'pos.daily.sales.reports.wizard'
    DETAILS_WIZARD = 'pos.details.wizard'
    LOAD_MIXIN = 'pos.load.mixin'
    MAKE_PAYMENT = 'pos.make.payment'
    NOTE = 'pos.note'
    ORDER_LINE = 'pos.order.line'
    ORDER = 'pos.order'
    PACK_OPERATION_LOT = 'pos.pack.operation.lot'
    PAYMENT_METHOD = 'pos.payment.method'
    PAYMENT = 'pos.payment'
    PRINTER = 'pos.printer'
    SESSION = 'pos.session'
    DISPLAY = 'pos_preparation_display.display'
    ORDER_STAGE = 'pos_preparation_display.order.stage'
    ORDER = 'pos_preparation_display.order'
    ORDERLINE = 'pos_preparation_display.orderline'
    RESET_WIZARD = 'pos_preparation_display.reset.wizard'
    STAGE = 'pos_preparation_display.stage'
    CUSTOM_LINK = 'pos_self_order.custom_link'

    def __post_init__(self):
        self.modules = generate_dict(self)
        self.members = inspect.getmembers(type(self))
        self.fields = {k: v for k,v in dict(self.members).items() if not k.startswith('__')}

    def __str__(self):
        return string_class(self)

POS = Pos()

@dataclass
class Sales:
    """Sales tables"""
    _name = 'sale'
    ADVANCE_PAYMENT_INV = 'sale.advance.payment.inv'
    EDI_COMMON = 'sale.edi.common'
    EDI_XML_UBL_BIS3 = 'sale.edi.xml.ubl_bis3'
    LOYALTY_COUPON_WIZARD = 'sale.loyalty.coupon.wizard'
    LOYALTY_REWARD_WIZARD = 'sale.loyalty.reward.wizard'
    MASS_CANCEL_ORDERS = 'sale.mass.cancel.orders'
    ORDER_ALERT = 'sale.order.alert'
    ORDER_CANCEL = 'sale.order.cancel'
    ORDER_CLOSE_REASON = 'sale.order.close.reason'
    ORDER_COUPON_POINTS = 'sale.order.coupon.points'
    ORDER_DISCOUNT = 'sale.order.discount'
    ORDER_LINE = 'sale.order.line'
    ORDER_LOG = 'sale.order.log'
    ORDER_LOG_REPORT = 'sale.order.log.report'
    ORDER_OPTION = 'sale.order.option'
    ORDER_SPREADSHEET = 'sale.order.spreadsheet'
    ORDER_TEMPLATE = 'sale.order.template'
    ORDER_TEMPLATE_LINE = 'sale.order.template.line'
    ORDER_TEMPLATE_OPTION = 'sale.order.template.option'
    ORDER = 'sale.order'
    PAYMENT_PROVIDER_ONBOARDING_WIZARD = 'sale.payment.provider.onboarding.wizard'
    PDF_FORM_FIELD = 'sale.pdf.form.field'
    REPORT = 'sale.report'
    SUBSCRIPTION_CHANGE_CUSTOMER_WIZARD = 'sale.subscription.change.customer.wizard'
    SUBSCRIPTION_CLOSE_REASON_WIZARD = 'sale.subscription.close.reason.wizard'
    SUBSCRIPTION_PLAN = 'sale.subscription.plan'
    SUBSCRIPTION_PRICING = 'sale.subscription.pricing'
    SUBSCRIPTION_REPORT = 'sale.subscription.report'
    def __post_init__(self):
        self.modules = generate_dict(self)

    def __str__(self):
        return string_class(self)

SALES = Sales()
