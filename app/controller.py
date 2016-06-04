from app.adjustment import Adjustment, AdjustmentDescription, AdjustmentSchedule, UserHierarchyNode, \
    CustomerHierarchyNode, LocationHierarchyNode, ProductHierarchyNode


class ExportController(object):

    def __init__(self):
        self.current_adjustment_oid = None
        self.adjustments = {}

    DATA_TYPES = {
        "A" : "add_adjustment",
        "D" : "add_description",
        "S" : "add_schedule",
        "U" : "add_user_hierarchy_node",
        "C" : "add_customer_node",
        "L" : "add_location_node",
        "P" : "add_product_hierarchy_node",
        # "V" : "adjustment parameters",
        # "CB" : "customer business",
        # "LB" : "location business",
        # "I" : "item price"
    }

    def process_line(self, line):
        fields = line.split("|")
        field_type = fields[0]
        type = self.DATA_TYPES.get(field_type)
        if type:
            exec "self.%s(%s)" % (type, fields[1:])
        # else:
        #     raise Exception("Invalid data type on line: %s" % line)

    def add_adjustment(self, fields):
        oid, external_id, description, event, rule_name = fields
        self.current_adjustment_oid = oid
        a = Adjustment(*fields)
        self.adjustments[oid] = a
        # print self.adjustments

    def add_description(self, fields):
        language_id = fields[0]
        self.get_current_adjustment().descriptions[language_id] = AdjustmentDescription(*fields)

    def get_current_adjustment(self):
        a = self.adjustments.get(self.current_adjustment_oid)
        if a:
            return a
        else:
            raise Exception("Current adjustment oid not set -> cannot find current adjustment!")

    def add_schedule(self, fields):
        self.get_current_adjustment().schedule = AdjustmentSchedule(*fields)

    def add_user_hierarchy_node(self, fields):
        #TODO: get_current_adjustment() -> property
        self.get_current_adjustment().hierarchy["U"].append(UserHierarchyNode(*fields))

    def add_customer_hierarchy_node(self, fields):
        self.get_current_adjustment().hierarchy["C"].append(CustomerHierarchyNode(*fields))

    def add_location_hierarchy_node(self, fields):
        self.get_current_adjustment().hierarchy["L"].append(LocationHierarchyNode(*fields))

    def add_product_hierarchy_node(self, fields):
        self.get_current_adjustment().hierarchy["P"].append(ProductHierarchyNode(*fields))