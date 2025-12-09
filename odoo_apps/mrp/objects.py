"""
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional

from odoo_apps.utils.cleaning import sort_dict

MaterialsConsumption = Literal['flexible', 'warning', 'strict']
ReadyToProduce = Literal['all_available', 'asap']
Type = Literal['normal', 'phantom']

@dataclass
class Bom:
    """
    Bom = Bills of Materials

    Other ways to name it:
    * Product structure: This term emphasizes the hierarchical relationship between
        all the parts and sub-assemblies that make up a product. 
    * Assembly component list: This is a direct and descriptive alternative, focusing
        on the list of components needed for an assembly. 
    * Production recipe: This term is often used in industries like food, chemicals,
        and pharmaceuticals, where the product is created through a specific formula or recipe of ingredients. 
    * Parts list: A simpler term that highlights the individual components required for a product. 
    * Bill of resources: A more comprehensive term that includes not only parts but also the tools
        and people needed for a manufacturing or repair process. 
    * Software bill of materials (SBOM): Used specifically in the software industry to list
        all components, including open-source and third-party libraries, used in a software product. 

    `allow_operation_dependencies`: [boolean] Create operation level dependencies that will influence both planning and the status of work orders upon MO confirmation. If this feature is ticked, and nothing is specified, Odoo will assume that all operations can be started simultaneously.
    `bom_line_ids`: [one2many] BoM Lines
    `byproduct_ids`: [one2many] By-products
    `code`: [char] Reference
    `company_id`: [many2one] Company
    `consumption`: [selection] Defines if you can consume more or less components than the quantity defined on the BoM:
        * Allowed: allowed for all manufacturing users.
        * Allowed with warning: allowed for all manufacturing users with summary of consumption differences when closing the manufacturing order.
            Note that in the case of component Highlight Consumption, where consumption is registered manually exclusively, consumption warnings will still be issued when appropriate also.
        * Blocked: only a manager can close a manufacturing order when the BoM consumption is not respected.
                - `flexible` -> `Allowed`
                - `warning` -> `Allowed with warning`
                - `strict` -> `Blocked`
    `days_to_prepare_mo`: [integer] Create and confirm Manufacturing Orders this many days in advance,
        to have enough time to replenish components or manufacture semi-finished products.
        Note that security lead times will also be considered when appropriate.
    `display_name`: [char] Display Name
    `id`: [integer] ID
    `operation_ids`: [one2many] Operations
    `picking_type_id`: [many2one] When a procurement has a ‘produce’ route with a operation type set, it will try to create a Manufacturing Order for that product using a BoM of the same operation type.If not,the operation type is not taken into account in the BoM search. That allows to define stock rules which trigger different manufacturing orders with different BoMs.
    `possible_product_template_attribute_value_ids`: [many2many] Possible Product Template Attribute Value
    `produce_delay`: [integer] Average lead time in days to manufacture this product. In the case of multi-level BOM, the manufacturing lead times of the components will be added. In case the product is subcontracted, this can be used to determine the date at which components should be sent to the subcontractor.
    `product_id`: [many2one] If a product variant is defined the BOM is available only for this product.
    `product_qty`: [float] This should be the smallest quantity that this product can be produced in. If the BOM contains operations, make sure the work center capacity is accurate.
    `product_tmpl_id`: [many2one] Product
    `product_uom_id`: [many2one] Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control
    `ready_to_produce`: [selection] Manufacturing Readiness
        - `all_available` -> ` When all components are available`
        - `asap` -> `When components for 1st operation are available`
    `sequence`: [integer] Sequence
    `type`: [selection] BoM Type
        - `normal` -> `Manufacture this product`
        - `phantom` -> `Kit`

    """
    # display_name: str
    product_id: Optional[int]
    
    product_qty: float = 1.0
    product_uom_id: int = 1 # Units
    
    product_tmpl_id: Optional[int] = None
    
    code: Optional[str] = False
    
    bom_line_ids: Optional[list] = None # field(default_factory=[1, 2, 3, 4, 5, 6, 7, 8, 9])
    
    byproduct_ids: Optional[list] = False
    sequence: int = 0
    operation_ids: Optional[list] = False
    picking_type_id: list = False
    possible_product_template_attribute_value_ids: Optional[list] = False
    allow_operation_dependencies: bool = False
    produce_delay: int = 0
    days_to_prepare_mo: int = 0

    # bom_line_ids: list = field(default_factory=[1, 2, 3, 4, 5, 6, 7, 8, 9])

    company_id: int = 1 # Main Company
    id: Optional[int] = None

    # Optionals: 
    type: Type = 'normal' # Type = Literal['normal', 'phantom']
    ready_to_produce: ReadyToProduce = 'all_available' # ReadyToProduce = Literal['all_available', 'asap']
    consumption: MaterialsConsumption = 'warning' # Consumption = Literal['flexible', 'warning', 'strict']
    # `consumption`: [selection] Defines if you can consume more or less components than the quantity defined on the BoM:
    #     * Allowed: allowed for all manufacturing users.
    #     * Allowed with warning: allowed for all manufacturing users with summary of
    #           consumption differences when closing the manufacturing order.
    #         Note that in the case of component Highlight Consumption, where consumption is
    #           registered manually exclusively, consumption warnings will still be issued when appropriate also.
    #     * Blocked: only a manager can close a manufacturing order when the BoM consumption is not respected.
    #             - `flexible` -> `Allowed`
    #             - `warning` -> `Allowed with warning`
    #             - `strict` -> `Blocked`

    def __post_init__(self):
        if self.id is None:
            if self.product_id is not None:
                self.domain = [
                    ['product_id', '=', self.product_id]
                ]
            if self.code is not None:
                self.domain = [
                    ['code', '=', self.code]
                ]
            
    def __setattr__(self, name, value):
        # Call the default setattr to actually set the attribute
        super().__setattr__(name, value)
        if name in ['id']: # Only trigger for specific attributes
            self.domain = [
                ['id', '=', self.id]
            ]

    def export_to_dict(self, drop: Optional[tuple] = ('domain', 'id', 'studio_fields')) -> dict:
        """
        Returns the dictionary version of the class
        """
        data = self.__dict__.copy()
        if drop is not None:
            for field in drop:
                del data[field]

        return sort_dict(data)
    
Tracking = Literal['serial', 'lot', 'none']

@dataclass
class BomLine:
    """
    `allowed_operation_ids`: [one2many] Operations
    `allowed_uom_ids`: [many2many] Allowed Uom
    `attachments_count`: [integer] Attachments Count
    `bom_id`: [many2one] Parent BoM
    `bom_product_template_attribute_value_ids`: [many2many] BOM Product Variants needed to apply this line.
    `child_bom_id`: [many2one] Sub BoM
    `child_line_ids`: [one2many] BOM lines of the referred bom
    `company_id`: [many2one] Company
    `cost_share`: [float] The percentage of the component repartition cost when purchasing a kit.The total of all components' cost have to be equal to 100.
    `display_name`: [char] Display Name
    `id`: [integer] ID
    `operation_id`: [many2one] The operation where the components are consumed, or the finished products created.
    `parent_product_tmpl_id`: [many2one] Parent Product Template
    `possible_bom_product_template_attribute_value_ids`: [many2many] Possible Product Template Attribute Value
    `product_id`: [many2one] Component
    `product_qty`: [float] Quantity
    `product_tmpl_id`: [many2one] Product Template
    `product_uom_id`: [many2one] Unit
    `sequence`: [integer] Gives the sequence order when displaying.
    `tracking`: [selection] Ensure the traceability of a storable product in your warehouse.
        - `serial` -> `By Unique Serial Number`
        - `lot` -> `By Lots`
        - `none` -> `By Quantity`
    """

    product_id: int
    bom_id: int
    sequence: Optional[int] = None

    product_qty: float = 1.0
    product_tmpl_id: Optional[int] = None
    parent_product_tmpl_id: int = 81 # Camisola SEUT

    # display_name: str = 'Tela de gabardina'
    product_uom_id: int
    allowed_uom_ids: Optional[list] = False
    possible_bom_product_template_attribute_value_ids: Optional[list] = False
    bom_product_template_attribute_value_ids: Optional[list] = False
    allowed_operation_ids: Optional[list] = False
    operation_id: list = False
    child_bom_id: list = False
    child_line_ids: Optional[list] = False
    attachments_count: int = 0
    cost_share: float = 0.0

    tracking: Tracking = 'none'
    # `tracking`: [selection] Ensure the traceability of a storable product in your warehouse.
    #     - `serial` -> `By Unique Serial Number`
    #     - `lot` -> `By Lots`
    #     - `none` -> `By Quantity`

    company_id: int = 1
    id: Optional[int]

    def __post_init__(self):
        if self.id is None:
            if self.product_id is not None and self.bom_id is not None:
                self.domain = [
                    ['bom_id', '=', self.bom_id],
                    ['product_id', '=', self.product_id]
                ]
                if self.sequence is not None:
                    self.domain.append(['sequence', '=', self.sequence])

    def __setattr__(self, name, value):
        # Call the default setattr to actually set the attribute
        super().__setattr__(name, value)
        if name in ['id']: # Only trigger for specific attributes
            self.domain = [
                ['id', '=', self.id]
            ]
                

    def export_to_dict(self, drop: Optional[tuple] = ('domain', 'id', 'studio_fields')) -> dict:
        """
        Returns the dictionary version of the class
        """
        data = self.__dict__.copy()
        if drop is not None:
            for field in drop:
                del data[field]

        return sort_dict(data)

ActivityExceptionDecoration = Literal['warning', 'danger']
ActivityState = Literal['overdue', 'today', 'planned']
ComponentsAvailabilityState = Literal['available', 'expected', 'late', 'unavailable']
MaterialsConsumption = Literal['flexible', 'warning', 'strict']
Priority = Literal['0', '1']
ProductTracking = Literal['serial', 'lot', 'none']
ReservationState = Literal['confirmed', 'assigned', 'waiting']
SearchDateCategory = Literal['before', 'yesterday', 'today', 'day_1', 'day_2', 'after']
State = Literal['draft', 'confirmed', 'progress', 'to_close', 'done', 'cancel']

@dataclass
class ProductionOrder:
    """
    `activity_date_deadline`: [date] Next Activity Deadline
    `activity_exception_decoration`: [selection] Type of the exception activity on record.
        - `warning` -> `Alert`
        - `danger` -> `Error`
    `activity_exception_icon`: [char] Icon to indicate an exception activity.
    `activity_ids`: [one2many] Activities
    `activity_state`: [selection] Status based on activities
        Overdue: Due date is already passed
        Today: Activity date is today
        Planned: Future activities.
        - `overdue` -> `Overdue`
        - `today` -> `Today`
        - `planned` -> `Planned`
    `activity_summary`: [char] Next Activity Summary
    `activity_type_icon`: [char] Font awesome icon e.g. fa-tasks
    `activity_type_id`: [many2one] Next Activity Type
    `activity_user_id`: [many2one] Responsible User
    `all_move_ids`: [one2many] All Move
    `all_move_raw_ids`: [one2many] All Move Raw
    `allow_workorder_dependencies`: [boolean] Allow Work Order Dependencies
    `allowed_uom_ids`: [many2many] Allowed Uom
    `backorder_sequence`: [integer] Backorder sequence, if equals to 0 means there is not related backorder
    `bom_id`: [many2one] Bills of Materials, also called recipes, are used to autocomplete components and work order instructions.
    `company_id`: [many2one] Company
    `components_availability`: [char] Latest component availability status for this MO. If green, then the MO's readiness status is ready, as per BOM configuration.
    `components_availability_state`: [selection] Components Availability State
        - `available` -> `Available`
        - `expected` -> `Expected`
        - `late` -> `Late`
        - `unavailable` -> `Not Available`
    `consumption`: [selection] Consumption
        - `flexible` -> `Allowed`
        - `warning` -> `Allowed with warning`
        - `strict` -> `Blocked`
    `date_deadline`: [datetime] Informative date allowing to define when the manufacturing order should be processed at the latest to fulfill delivery on time.
    `date_finished`: [datetime] Date you expect to finish production or actual date you finished production.
    `date_start`: [datetime] Date you plan to start production or date you actually started production.
    `delay_alert_date`: [datetime] Delay Alert Date
    `delivery_count`: [integer] Delivery Orders
    `display_name`: [char] Display Name
    `duration`: [float] Total real duration (in minutes)
    `duration_expected`: [float] Total expected duration (in minutes)
    `extra_cost`: [float] Extra Unit Cost
    `finished_move_line_ids`: [one2many] Finished Product
    `forecasted_issue`: [boolean] Forecasted Issue
    `id`: [integer] ID
    `is_delayed`: [boolean] Is Delayed
    `is_locked`: [boolean] Is Locked
    `is_outdated_bom`: [boolean] The BoM has been updated since creation of the MO
    `is_planned`: [boolean] Its Operations are Planned
    `json_popover`: [char] JSON data for the popover widget
    `location_dest_id`: [many2one] Location where the system will stock the finished products.
    `location_final_id`: [many2one] Final Location from procurement
    `location_src_id`: [many2one] Location where the system will look for components.
    `lot_producing_id`: [many2one] Lot/Serial Number
    `move_byproduct_ids`: [one2many] Move Byproduct
    `move_dest_ids`: [one2many] Stock Movements of Produced Goods
    `move_finished_ids`: [one2many] Finished Products
    `move_raw_ids`: [one2many] Components
    `mrp_production_backorder_count`: [integer] Count of linked backorder
    `mrp_production_child_count`: [integer] Number of generated MO
    `mrp_production_source_count`: [integer] Number of source MO
    `my_activity_date_deadline`: [date] My Activity Deadline
    `name`: [char] Reference
    `never_product_template_attribute_value_ids`: [many2many] Never attribute values
    `orderpoint_id`: [many2one] Orderpoint
    `origin`: [char] Reference of the document that generated this production order request.
    `picking_ids`: [many2many] Picking associated to this manufacturing order
    `picking_type_id`: [many2one] Operation Type
    `priority`: [selection] Components will be reserved first for the MO with the highest priorities.
        - `0` -> `Normal`
        - `1` -> `Urgent`
    `procurement_group_id`: [many2one] Procurement Group
    `product_description_variants`: [char] Custom Description
    `product_id`: [many2one] Product
    `product_qty`: [float] Quantity To Produce
    `product_tmpl_id`: [many2one] Product Template
    `product_tracking`: [selection] Ensure the traceability of a storable product in your warehouse.
        - `serial` -> `By Unique Serial Number`
        - `lot` -> `By Lots`
        - `none` -> `By Quantity`
    `product_uom_id`: [many2one] Unit
    `product_uom_qty`: [float] Total Quantity
    `product_variant_attributes`: [many2many] Attribute Values
    `production_capacity`: [float] Quantity that can be produced with the current stock of components
    `production_location_id`: [many2one] Production Location
    `propagate_cancel`: [boolean] If checked, when the previous move of the move (which was generated by a next procurement) is cancelled or split, the move generated by this move will too
    `purchase_order_count`: [integer] Count of generated PO
    `qty_produced`: [float] Quantity Produced
    `qty_producing`: [float] Quantity Producing
    `reservation_state`: [selection] Manufacturing readiness for this MO, as per bill of material configuration:
            * Ready: The material is available to start the production.
            * Waiting: The material is not available to start the production.

        - `confirmed` -> `Waiting`
        - `assigned` -> `Ready`
        - `waiting` -> `Waiting Another Operation`
    `reserve_visible`: [boolean] Technical field to check when we can reserve quantities
    `sale_line_id`: [many2one] Origin sale order line
    `sale_order_count`: [integer] Count of Source SO
    `scrap_count`: [integer] Scrap Move
    `scrap_ids`: [one2many] Scraps
    `search_date_category`: [selection] Date Category
        - `before` -> `Before`
        - `yesterday` -> `Yesterday`
        - `today` -> `Today`
        - `day_1` -> `Tomorrow`
        - `day_2` -> `The day after tomorrow`
        - `after` -> `After`
    `show_allocation`: [boolean] Technical Field used to decide whether the button "Allocation" should be displayed.
    `show_final_lots`: [boolean] Show Final Lots
    `show_lock`: [boolean] Show Lock/unlock buttons
    `show_lot_ids`: [boolean] Display the serial number shortcut on the moves
    `show_produce`: [boolean] Technical field to check if produce button can be shown
    `show_produce_all`: [boolean] Technical field to check if produce all button can be shown
    `show_valuation`: [boolean] Show Valuation
    `state`: [selection]  * Draft: The MO is not confirmed yet.
        * Confirmed: The MO is confirmed, the stock rules and the reordering of the components are trigerred.
        * In Progress: The production has started (on the MO or on the WO).
        * To Close: The production is done, the MO has to be closed.
        * Done: The MO is closed, the stock moves are posted. 
        * Cancelled: The MO has been cancelled, can't be confirmed anymore.
                - `draft` -> `Draft`
                - `confirmed` -> `Confirmed`
                - `progress` -> `In Progress`
                - `to_close` -> `To Close`
                - `done` -> `Done`
                - `cancel` -> `Cancelled`
    `unbuild_count`: [integer] Number of Unbuilds
    `unbuild_ids`: [one2many] Unbuilds
    `unreserve_visible`: [boolean] Technical field to check when we can unreserve
    `use_create_components_lots`: [boolean] Allow to create new lot/serial numbers for the components
    `user_id`: [many2one] Responsible
    `valid_product_template_attribute_line_ids`: [many2many] Valid Product Attribute Lines
    `warehouse_id`: [many2one] Warehouse
    `wip_move_count`: [integer] WIP Journal Entry Count
    `wip_move_ids`: [many2many] Wip Move
    `workcenter_id`: [many2one] Workcenter
    `workorder_ids`: [one2many] Work Orders
    """
    product_id: int
    product_tmpl_id: int
    product_qty: float = 1.0
    product_uom_id: int = 1 # Units
    bom_id: int = 1 # Camisola SEUT

    # activity_ids: Optional[list] = False
    # activity_user_id: list = False
    # activity_type_id: list = False
    # activity_type_icon: str = False
    # activity_date_deadline: Optional[datetime | str] = False
    # my_activity_date_deadline: Optional[datetime | str] = False
    # activity_summary: str = False
    # activity_exception_icon: str = False
    # backorder_sequence: int = 0
    origin: str = False
    product_variant_attributes: Optional[list] = False
    # valid_product_template_attribute_line_ids: Optional[list] = False
    # never_product_template_attribute_value_ids: Optional[list] = False
    # workcenter_id: list = False
    # allowed_uom_ids: list = field(default_factory=[1])
    lot_producing_id: list = False
    qty_producing: float = 0.0
    product_uom_qty: float = 1.0
    picking_type_id: int = 13
    use_create_components_lots: bool = False
    location_src_id: int = 8 # WH/Stock
    
    warehouse_id: int = 1 
    location_dest_id: int = 8 # WH/Stock
    location_final_id: list = False
    
    # `production_capacity`: [float] Quantity that can be produced with the current
    # stock of components
    production_capacity: Optional[float] = None

    date_deadline: Optional[datetime | str] = False
    date_start: Optional[datetime | str] = None
    date_finished: Optional[datetime | str] = None
    duration_expected: Optional[float] = None
    duration: Optional[float] = None
    move_raw_ids: Optional[list] = None # field(default_factory=[184, 185, 186, 187, 188, 189, 190])
    move_finished_ids: Optional[list] = None #field(default_factory=[192])
    all_move_raw_ids: Optional[list] = None #field(default_factory=[184, 185, 186, 187, 188, 189, 190])
    all_move_ids: Optional[list] = None # field(default_factory=[192])
    move_byproduct_ids: Optional[list] = False
    finished_move_line_ids: Optional[list] = False
    workorder_ids: Optional[list] = False
    move_dest_ids: Optional[list] = False
    unreserve_visible: bool = False
    reserve_visible: bool = False
    
    company_id: int = 1 
    qty_produced: Optional[None] = 0.0
    
    product_description_variants: str = False
    # orderpoint_id: list = False
    # propagate_cancel: bool = False
    # delay_alert_date: Optional[datetime | str] = False
    # json_popover: str = False
    # scrap_ids: Optional[list] = False
    # scrap_count: int = 0
    # unbuild_ids: Optional[list] = False
    # unbuild_count: int = 0
    # is_locked: bool = True
    # is_planned: bool = False
    # show_final_lots: bool = False
    production_location_id: int = 15 # Virtual Locations/Production
    # picking_ids: Optional[list] = False
    # delivery_count: int = 0
    # mrp_production_child_count: int = 0
    # mrp_production_source_count: int = 0
    # mrp_production_backorder_count: int = 1
    # show_lock: bool = False
    
    # components_availability: str = False

    # show_lot_ids: bool = False
    # forecasted_issue: bool = False
    # show_allocation: bool = False
    # allow_workorder_dependencies: bool = False
    # show_produce: bool = False
    # show_produce_all: bool = False
    # is_outdated_bom: bool = False
    # is_delayed: bool = False
    extra_cost: float = 0.0
    # show_valuation: bool = False
    # wip_move_ids: Optional[list] = False
    # wip_move_count: int = 0
    # purchase_order_count: int = 0
    # sale_order_count: int = 0
    # sale_line_id: list = False

    # ActivityState = Literal['overdue', 'today', 'planned']
    activity_state: ActivityState = 'False'
    #     ActivityExceptionDecoration = Literal['warning', 'danger']
    activity_exception_decoration: ActivityExceptionDecoration = 'False'
    # Priority = Literal['0', '1']
    priority: Priority = '0'
    # ProductTracking = Literal['serial', 'lot', 'none']
    product_tracking: ProductTracking = 'none'
    # State = Literal['draft', 'confirmed', 'progress', 'to_close', 'done', 'cancel']
    state: State = 'draft'
    # ReservationState = Literal['confirmed', 'assigned', 'waiting']
    reservation_state: Optional[ReservationState] = False
    # Consumption = Literal['flexible', 'warning', 'strict']
    consumption: MaterialsConsumption = 'flexible'
    # ComponentsAvailabilityState = Literal['available', 'expected', 'late', 'unavailable']
    components_availability_state: ComponentsAvailabilityState = 'False'

    # SearchDateCategory = Literal['before', 'yesterday', 'today', 'day_1', 'day_2', 'after']
    search_date_category: Optional[SearchDateCategory] = None

    id: Optional[int] = None
    def __post_init__(self):
        if self.id is None:
            if self.product_id is not None and self.bom_id is not None:
                self.domain = [
                    # ['bom_id', '=', self.bom_id],
                    ['product_id', '=', self.product_id]
                ]

    def __setattr__(self, name, value):
        # Call the default setattr to actually set the attribute
        super().__setattr__(name, value)
        if name in ['id']: # Only trigger for specific attributes
            self.domain = [
                ['id', '=', self.id]
            ]
                

    def export_to_dict(self, drop: Optional[tuple] = ('domain', 'id', 'studio_fields')) -> dict:
        """
        Returns the dictionary version of the class
        """
        data = self.__dict__.copy()
        if drop is not None:
            for field in drop:
                del data[field]

        return sort_dict(data)