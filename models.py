"""
Store interest Odoo models
"""

from dataclasses import dataclass
from inspect import getmembers

def generate_modules_dict(data_obj) -> dict:
    """
    Generate a dictionary of modules from the class attributes.
    :param data_obj: Data Class to generate the dictionary from.
    :return: Dictionary of modules.
    """
    return {
        module[0]:module[1] for module in getmembers(
            data_obj
            ) if not module[0].startswith('__')}

def string_class(data_obj) -> str:
    """
    Generate a string representation of the class.
    :param data_obj: Data Class to generate the string from.
    :return: String representation of the class.
    """
    str_class = ""
    for k,v in data_obj._modules.items():
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
        self._modules = generate_modules_dict(self)

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
        self._modules = generate_modules_dict(self)

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
        self._modules = generate_modules_dict(self)

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
        self._modules = generate_modules_dict(self)

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
        self._modules = generate_modules_dict(self)

    def __str__(self):
        return string_class(self)

RESOURCE = Resource()
