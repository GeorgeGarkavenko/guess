import csv


class PricingEvent(object):

    def __init__(self, name, headers, locations, items):
        self.name = name
        self.headers = headers
        self.locations = locations
        self.items = items

    def get_export_rows(self):
        rv = [self.headers[0], self.headers[1]]
        rv.append(["L"] + self.locations)
        rv.append(["D", "Sku", "Style", "Color", "New Price"]) # header for items

        rv += [["", "", item.item_style_code, item.item_color, item.item_price] for item in self.items]
        return rv

    @property
    def filename(self): # may need to more complicated
        return self.name

    def export_tab_delimited(self):
        with open("%s.txt" % self.filename, 'wb') as f:
            writer = csv.writer(f, dialect=csv.excel, delimiter="\t")
            [writer.writerow(row) for row in self.get_export_rows()]


class Adjustment(object):

    def __init__(self, oid, external_id, name, event, rule_name):
        self.oid = oid
        self.external_id = external_id
        self.name = name
        self.event = event
        self.rule_name = rule_name
        self.descriptions = {}  # language id -> AdjustmentDescription()
        self.schedule = None

        self.hierarchy = {  # user, customer, location, product
            "U": [],
            "C": [],
            "L": [],
            "P": []
        }

        self.parameters = {}  # parameter name -> AdjustmentParameter
        self.location_business = {} # location id -> LocationBusiness
        self.item_price = []

        self._MAX_EVENT_LOCATIONS = 25 # 25 or less stores/zones in one event (or file)

    def get_header(self):
        """Return two lists: 1st header names, 2nd header values"""

        header_names = ["H", "Description", "Price Code", "Event Type", "Reason Code", "Country", "Data Type",
                        "Based On", "Override All", "Start Date", "End Date", "% Off"]

        header_values = ["H"]
        header_values.append(self.name)
        header_values.append(self.parameters["PriceCode"].value)
        header_values.append(self.parameters["EventType"].value)
        header_values.append(self.parameters["ReasonCode"].value)
        header_values.append(self.parameters["Country"].value)
        header_values.append(self.parameters["DataType"].value) # Should always be 'I'
        header_values.append(self.parameters["BasedOn"].value)
        header_values.append(self.parameters["OverrideAll"].value)
        header_values.append(self.schedule.start_date)
        header_values.append(self.schedule.end_date)
        header_values.append("")

        return [header_names, header_values]

    def get_location_business_map(self):
        """Return a dictionary where keys are file numbers starting from 1 and values are
        lists of store/zone ids that will be written to that file on L row.
        Rule is max 25 stores/zones in a file."""

        location_chunks = self.location_business.values()
        location_chunks = [location_chunks[i:i + self._MAX_EVENT_LOCATIONS]
                           for i in range(0, len(location_chunks), self._MAX_EVENT_LOCATIONS)]

        # overwrite LocationBusiness instance with printable LB external id
        location_chunks = [ [lb.external_id for lb in location_chunks[i]] for i in range(len(location_chunks))]

        return {i + 1: location_chunks[i] for i in range(len(location_chunks))}

    def get_pricing_events(self):
        """Return a list of PricingEvents.

        If adjustment has more LocationBusinesses than fits one PricingEvent (25)
        then list contains more than one PricingEvent."""

        locations = self.get_location_business_map()

        rv = [PricingEvent("%s_%s" % (self.name, key), self.get_header(), locations[key], self.item_price)
              for key in sorted(locations.keys()) ]

        return rv


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
    def __init__(self, node_type, include_exclude_flag, hierarchy_oid, hierarchy_name):
        self.node_type = node_type
        self.include_exclude_flag = include_exclude_flag
        self.hierarchy_oid = hierarchy_oid
        self.hierarchy_name = hierarchy_name


class UserHierarchyNode(HierarchyNode):
    def __init__(self, node_type, include_exclude_flag, hierarchy_oid, hierarchy_name):
        super(UserHierarchyNode, self).__init__(node_type, include_exclude_flag, hierarchy_oid, hierarchy_name)


class CustomerHierarchyNode(HierarchyNode):
    def __init__(self, node_type, include_exclude_flag, hierarchy_oid, hierarchy_name, customer_external_id):
        super(CustomerHierarchyNode, self).__init__(node_type, include_exclude_flag, hierarchy_oid, hierarchy_name)
        self.customer_external_id = customer_external_id


class LocationHierarchyNode(HierarchyNode):
    def __init__(self, node_type, include_exclude_flag, hierarchy_oid, hierarchy_name, location_external_id):
        super(LocationHierarchyNode, self).__init__(node_type, include_exclude_flag, hierarchy_oid, hierarchy_name)
        self.location_external_id = location_external_id


class ProductHierarchyNode(HierarchyNode):
    def __init__(self, node_type, include_exclude_flag, hierarchy_oid, hierarchy_name, product_group_id, item_name):
        super(ProductHierarchyNode, self).__init__(node_type, include_exclude_flag, hierarchy_oid, hierarchy_name)
        self.product_group_id = product_group_id
        self.item_name = item_name


class LocationBusiness(object):
    def __init__(self, external_id, pricing_zone, business_unit):
        self.external_id = external_id  # store id
        self.pricing_zone = pricing_zone
        self.business_unit = business_unit

    def __repr__(self):  # pragma: no cover
        return "<LocationBusiness: store id=%s, pricing zone=%s, business unit=%s>" % \
               (self.external_id, self.pricing_zone, self.business_unit)


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
