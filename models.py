"""
Store interest Odoo models
"""

from dataclasses import dataclass, fields

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
        self._modules = [module.name for module in fields(self)]

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
        self._modules = [module.name for module in fields(self)]

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
        self._modules = [module.name for module in fields(self)]

CALENDAR = Calendar()
