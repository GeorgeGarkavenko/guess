class Adjustment(object):

    def __init__(self, oid, external_id, name, event, rule_name):
        self.oid = oid
        self.external_id = external_id
        self.name = name
        self.event = event
        self.rule_name = rule_name
        self.descriptions = {} # language id -> AdjustmentDescription()

        self.hierarchy = { # user, customer, location, product
            "U" : [],
            "C" : [],
            "L" : [],
            "P" : []
        }

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
