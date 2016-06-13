class Adjustment(object):

    def __init__(self, oid, external_id, name, event, rule_name):
        self.oid = oid
        self.external_id = external_id
        self.name = name
        self.event = event
        self.rule_name = rule_name
        self.descriptions = {} # language id -> AdjustmentDescription()
        self.schedule = None

        self.hierarchy = { # user, customer, location, product
            "U" : [],
            "C" : [],
            "L" : [],
            "P" : []
        }

        self.parameters = {} # parameter name -> AdjustmentParameter
        self.location_business = []
        self.item_price = []

    def get_header(self):
        header_rows = [("H", "H")]
        header_rows.append(("Description", self.name))
        header_rows.append(("Price Code", self.parameters["PriceCode"].value))
        header_rows.append(("Event Type", self.parameters["EventType"].value))
        header_rows.append(("Reason Code", self.parameters["ReasonCode"].value))
        header_rows.append(("Country", self.parameters["Country"].value))
        header_rows.append(("Data Type", self.parameters["DataType"].value)) # Should always be 'I'
        header_rows.append(("Based On", self.parameters["BasedOn"].value))
        header_rows.append(("Override All", self.parameters["OverrideAll"].value))
        header_rows.append(("Start Date", self.schedule.start_date)) # format?
        header_rows.append(("End Date", self.schedule.end_date)) # format?
        header_rows.append(("% Off", ""))
        return header_rows

class AdjustmentDescription(object):

    def __init__(self, language_id, description, image):
        self.language_id = language_id
        self.description = description
        self.image = image

class AdjustmentSchedule(object):

    def __init__(self, start_date, end_date, start_time, duration, mon, tue, wed, thu, fri, sat, sun):
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.duration = duration
        self.mon = mon
        self.tue = tue
        self.wed = wed
        self.thu = thu
        self.fri = fri
        self.sat = sat
        self.sun = sun

class AdjustmentParameters(object):
    def __init__(self, name, value, currency):
        self.name = name
        self.value = value
        self.currency = currency

class HierarchyNode(object):

    def __init__(self, node_type, hierarchy_oid, hierarchy_name):
        self.node_type = node_type
        self.hierarchy_oid = hierarchy_oid
        self.hierarchy_name = hierarchy_name

class UserHierarchyNode(HierarchyNode):

    def __init__(self, node_type, hierarchy_oid, hierarchy_name):
        super(UserHierarchyNode, self).__init__(node_type, hierarchy_oid, hierarchy_name)

class CustomerHierarchyNode(HierarchyNode):

    def __init__(self, node_type, hierarchy_oid, hierarchy_name, customer_external_id):
        super(CustomerHierarchyNode, self).__init__(node_type, hierarchy_oid, hierarchy_name)
        self.customer_external_id = customer_external_id

class LocationHierarchyNode(HierarchyNode):

    def __init__(self, node_type, hierarchy_oid, hierarchy_name, location_external_id):
        super(LocationHierarchyNode, self).__init__(node_type, hierarchy_oid, hierarchy_name)
        self.location_external_id = location_external_id

class ProductHierarchyNode(HierarchyNode):

    def __init__(self, node_type, hierarchy_oid, hierarchy_name, product_group_id, item_name):
        super(ProductHierarchyNode, self).__init__(node_type, hierarchy_oid, hierarchy_name)
        self.product_group_id = product_group_id
        self.item_name = item_name

class LocationBusiness(object):
    def __init__(self, external_id, pricing_zone, business_unit):
        self.external_id = external_id
        self.pricing_zone = pricing_zone
        self.business_unit = business_unit

class ItemPrice(object):
    def __init__(self, user_hierarchy_oid, user_hierarchy_name,
                 customer_hierarchy_oid, customer_hierarchy_name, customer_external_id,
                 location_hierarchy_oid, location_hierarchy_name, location_external_id,
                 start_date, end_date, product_group_id, item_style_code, item_color, variant_item_name,
                 item_price, currency):

        self.user_hierarchy_oid = user_hierarchy_oid
        self.user_hierarchy_name = user_hierarchy_name

        self.customer_hierarchy_oid = customer_hierarchy_oid
        self.customer_hierarchy_name = customer_hierarchy_name
        self.customer_external_id = customer_external_id

        self.location_hierarchy_oid = location_hierarchy_oid
        self.location_hierarchy_name = location_hierarchy_name
        self.location_external_id = location_external_id

        self.start_date = start_date
        self.end_date = end_date
        self.product_group_id = product_group_id
        self.item_style_code = item_style_code
        self.item_color = item_color
        self.variant_item_name = variant_item_name
        self.item_price = item_price
        self.currency = currency


