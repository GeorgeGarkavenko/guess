import csv, collections
import logging

import datetime
import os


class PricingEvent(object):
    """Class that represents an exportable entity which MMS will import from file."""

    def __init__(self, name, headers, locations, items, basedir):
        self.name = name
        self.headers = headers
        self.locations = locations
        self.items = items
        self.logger = logging.getLogger("adjustment")
        self.basedir = basedir

    def __repr__(self):  # pragma: no cover
        return "<PricingEvent: name=%s, locations=%s, items=%s>" % \
               (self.name, self.locations, self.items)

    def get_export_rows(self):
        rv = [self.headers[0], self.headers[1]]
        rv.append(["L"] + self.locations)
        rv.append(["D", "Sku", "Style", "Color", "New Price"])  # header for items

        rv += [["", "", item.item_style_code, item.item_color, item.item_price] for item in self.items]
        return rv

    @property
    def filename(self):  #
        return os.path.join(self.basedir, self.name)

    def export_tab_delimited(self):
        self.logger.info("Writing MMS file: %s" % self.filename)
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
        self.zone_sets = set() # will be updated by controller after reading store information file

        self.hierarchy = {  # user, customer, location, product
            "U": [],
            "C": [],
            "L": [],
            "P": []
        }

        self.parameters = {}  # parameter name -> AdjustmentParameter
        self.location_business = {}  # location id -> LocationBusiness
        self.item_price = []

        self._MAX_EVENT_LOCATIONS = 25  # 25 or less stores/zones in one event (or file)
        self.logger = logging.getLogger("adjustment")

        self.basedir = '/tmp' if os.name == 'posix' else r'C:\temp'

    def get_header(self):
        """Return two lists: 1st header names, 2nd header values"""

        header_names = ["H", "Description", "Price Code", "Event Type", "Reason Code", "Country", "Data Type",
                        "Based On", "Override All", "Start Date", "End Date", "% Off"]

        country = self.parameters["Country"].value

        header_values = ["H"]
        header_values.append(self.name)
        header_values.append(self.parameters["PriceCode"].value)
        header_values.append(self.parameters["EventType"].value)
        header_values.append(self.parameters["ReasonCode"].value)
        header_values.append(country)
        header_values.append(self.parameters["DataType"].value)  # Should always be 'I'
        header_values.append(self.parameters["BasedOn"].value)
        header_values.append(self.parameters["OverrideAll"].value)
        header_values.append(self.schedule.start_date(country))
        header_values.append(self.schedule.end_date(country))
        header_values.append("")

        return [header_names, header_values]

    def get_location_business_map(self, location_ids):
        """Return a dictionary where keys are file numbers starting from 1 and values are
        lists of store/zone ids that will be written to that file on L row.
        Rule is max 25 stores/zones in a file."""

        location_chunks = [location_ids[i:i + self._MAX_EVENT_LOCATIONS]
                           for i in range(0, len(location_ids), self._MAX_EVENT_LOCATIONS)]

        return {i + 1: location_chunks[i] for i in range(len(location_chunks))}

    def get_pricing_events(self):

        self.validate()

        d = collections.defaultdict(set)
        [d[ip].add(ip.location_external_id) for ip in self.item_price]  # location is not part of key

        # d is now a dictionary with item prices as keys (without location info) and values are sets of locations
        # where that specific item is available. Next step is to use the locations as dict keys and list all items
        # available there. And then the end result is a list of locations sharing identical list of items.

        d2 = collections.defaultdict(list)
        [d2[str(sorted(v))].append(k) for k, v in d.items()]  # need to use str() to store set as key

        # d2: sorted list of locations as keys, values list of items for that list of locations

        from operator import attrgetter
        for k, v in d2.items():
            d2[k] = sorted(v, key=attrgetter('item_style_code', 'item_color')) # sort item list by style, color

        # check if event contains all stores for a zone and if so, replace store list with the zone

        for location_list in d2.keys():
            use_zones = False

            location_set = set(eval(location_list))
            for zone in self.zone_sets:
                if self.zone_sets[zone].issubset(location_set):
                    use_zones = True
                    location_set = location_set - self.zone_sets[zone]
                    location_set.add(zone)

            if use_zones:
                new_key = str(sorted(list(location_set)))
                d2[new_key] = d2.pop(location_list)
                self.logger.info("Replaced store list %s with zone %s" % (location_list, new_key))

        # done store -> zone update

        pricing_events = []
        for index, key_locations in enumerate(d2, 1):
            locations = self.get_location_business_map(sorted(eval(key_locations))) # eval returns str back to list
            for key in locations:
                pricing_events.append(PricingEvent("%s_%s_%s" % (self.name, index, key), self.get_header(),
                                                   locations[key], d2[key_locations], self.basedir))
        return pricing_events

    def validate(self):

        self.validate_country()
        self.validate_schedule()

    def validate_country(self):
        country = self.parameters["Country"].value
        if not country in AdjustmentSchedule.EXPORT_FORMATS.keys():
            raise Exception("Adjustment country has invalid value: %s. Valid values are: %s" %
                   (country, AdjustmentSchedule.EXPORT_FORMATS.keys()))

    def validate_schedule(self):
        if not self.schedule:
            self.schedule = AdjustmentSchedule(*"S|||||1|1|1|1|1|1|1".split("|")[1:])

class AdjustmentDescription(object):
    def __init__(self, language_id, description, image):
        self.language_id = language_id
        self.description = description
        self.image = image


class AdjustmentSchedule(object):
    INPUT_DATE_FORMAT = "%Y-%m-%d" # Pricer exports dates in ISO format
    EXPORT_FORMATS = {
        "USA" : "%m/%d/%Y",
        "CAN" : "%m/%d/%Y" # TODO: verify
    }

    def __init__(self, start_date, end_date, start_time, duration, mon, tue, wed, thu, fri, sat, sun):
        self._start_date = datetime.datetime.strptime(start_date, self.INPUT_DATE_FORMAT) if start_date else ''
        self._end_date = datetime.datetime.strptime(end_date, self.INPUT_DATE_FORMAT) if end_date else ''
        self.start_time = start_time
        self.duration = duration
        self.mon = mon
        self.tue = tue
        self.wed = wed
        self.thu = thu
        self.fri = fri
        self.sat = sat
        self.sun = sun

    def start_date(self, country="USA"):
        return datetime.datetime.strftime(self._start_date, self.EXPORT_FORMATS[country]) if self._start_date else ''

    def end_date(self, country="USA"):
        return datetime.datetime.strftime(self._end_date, self.EXPORT_FORMATS[country]) if self._end_date else ''


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

    def __hash__(self):
        """Override so that ItemPrice can be used directly as dictionary key (location not part of key)."""

        return hash((self.currency, self.product_group_id, self.item_style_code, self.item_color,
                     self.variant_item_name, self.start_date, self.end_date, self.item_price))

    def __eq__(self, other):
        return (self.currency, self.product_group_id, self.item_style_code, self.item_color, self.variant_item_name,
                self.start_date, self.end_date, self.item_price) == \
               (
                   other.currency, other.product_group_id, other.item_style_code, other.item_color,
                   other.variant_item_name,
                   other.start_date, other.end_date, other.item_price)

    def __repr__(self):  # pragma: no cover
        return "<ItemPrice: currency=%s, price=%s, product group=%s, item style code=%s, color=%s, variant name=%s, start date=%s, end date=%s>" % \
               (self.currency, self.item_price, self.product_group_id, self.item_style_code, self.item_color,
                self.variant_item_name, self.start_date, self.end_date)
