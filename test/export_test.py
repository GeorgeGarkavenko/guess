from unittest import TestCase

import datetime

from app.adjustment import Adjustment, AdjustmentDescription, UserHierarchyNode, CustomerHierarchyNode, \
    LocationHierarchyNode, ProductHierarchyNode, AdjustmentParameters, LocationBusiness, ItemPrice, AdjustmentSchedule
from app.controller import ExportController


class TestExportController(TestCase):

    def setUp(self):
        self.c = ExportController()
        fields = "A|A25E3EE9AFA248A79DF07D2565410784||Back to school 10% off||Promotion % Off".split("|")[1:]
        self.c.add_adjustment(fields)

    def test_add_adjustment(self):
        self.assertEqual(self.c._current_adjustment_oid, "A25E3EE9AFA248A79DF07D2565410784")

        a = self.c.current_adjustment
        self.assertEqual(a.external_id, "")
        self.assertEqual(a.name, "Back to school 10% off")
        self.assertEqual(a.event, "")
        self.assertEqual(a.rule_name, "Promotion % Off")

    def test_add_adjustment_description(self):
        fields = "D|Pen|Back to school|".split("|")[1:]
        self.c.add_description(fields)

        a = self.c.current_adjustment
        d = a.descriptions[fields[0]]
        self.assertIsInstance(d, AdjustmentDescription)

        fields = "D|Pen_GB|Back to school, in the UK|".split("|")[1:]
        self.c.add_description(fields)
        self.assertEqual(2, len(a.descriptions.keys()))

    def test_add_adjustment_schedule(self):
        a = self.c.current_adjustment
        self.assertIsNone(a.schedule, None)

        fields = "S|2016-06-01|2016-06-30|||1|1|1|1|1|1|1".split("|")[1:]
        self.c.add_schedule(fields)
        self.assertIsInstance(a.schedule, AdjustmentSchedule)

    def test_add_user_hierarchy_node(self):
        fields = "U|H|I||All".split("|")[1:]
        self.c.add_user_hierarchy_node(fields)

        user_node = self.c.current_adjustment.hierarchy["U"][0]
        self.assertIsInstance(user_node, UserHierarchyNode)

    def test_add_customer_hierarchy_node(self):
        fields = "C|H|I||All|".split("|")[1:]
        self.c.add_customer_hierarchy_node(fields)

        customer_node = self.c.current_adjustment.hierarchy["C"][0]
        self.assertIsInstance(customer_node, CustomerHierarchyNode)

    def test_add_location_hierarchy_node(self):
        fields = "L|H|I|LUSA|USA|".split("|")[1:]
        self.c.add_location_hierarchy_node(fields)

        location_node = self.c.current_adjustment.hierarchy["L"][0]
        self.assertIsInstance(location_node, LocationHierarchyNode)

    def test_add_product_hierarchy_node(self):
        fields = "P|I|I|||1|23002G3".split("|")[1:]
        self.c.add_product_hierarchy_node(fields)

        a = self.c.current_adjustment
        product_node = a.hierarchy["P"][0]
        self.assertIsInstance(product_node, ProductHierarchyNode)

        fields = "P|I|I|||1|11066279".split("|")[1:]
        self.c.add_product_hierarchy_node(fields)
        self.assertEqual(2, len(a.hierarchy["P"]))

    def test_add_adjustment_parameters(self):
        fields = "V|PromotionPct|-10|".split("|")[1:]
        self.c.add_parameters(fields)

        a = self.c.current_adjustment
        p = a.parameters["PromotionPct"]
        self.assertIsInstance(p, AdjustmentParameters)

        fields = "V|ReasonCode|A|".split("|")[1:]
        self.c.add_parameters(fields)
        self.assertEqual(2, len(a.parameters))

    def test_add_location_business(self):
        fields = "LB|5012|100|R".split("|")[1:]
        self.c.add_location_business(fields)

        a = self.c.current_adjustment
        l = a.location_business["5012"]
        self.assertIsInstance(l, LocationBusiness)

        fields = "LB|5501|100|R".split("|")[1:]
        self.c.add_location_business(fields)
        self.assertEqual(2, len(a.location_business))

    def test_add_item_price(self):  # needs to have location business already on adjustment
        fields = "LB|5012|100|R".split("|")[1:]
        self.c.add_location_business(fields)

        fields = "I||||||LUSA-100|100|5012|2016-06-01|2016-06-30|1|76074 32|||123.456|USD".split("|")[1:]
        self.c.add_item_price(fields)

        p = self.c.current_adjustment.item_price[0]
        self.assertIsInstance(p, ItemPrice)

        fields = "LB|5501|100|R".split("|")[1:]
        self.c.add_location_business(fields)

        fields = "I||||||LUSA-100|100|5501|2016-06-01|2016-06-30|1|23002G3|RED|11066278|1200|USD".split("|")[1:]
        self.c.add_item_price(fields)

        a = self.c.current_adjustment
        self.assertEqual(2, len(a.item_price))

    def test_add_item_price_with_invalid_location(self): # needs to have location business already on adjustment
        fields = "LB|5012|100|R".split("|")[1:]
        self.c.add_location_business(fields)

        fields = "I||||||LUSA-100|100|1234|2016-06-01|2016-06-30|1|76074 32|||123.456|USD".split("|")[1:]
        self.assertRaises(Exception, self.c.add_item_price, fields)

    def test_line_processing(self):

        lines = """A|A25E3EE9AFA248A79DF07D2565410784||Back to school 10% off||Promotion % Off
D|Pen|Back to school|
S|2016-06-01|2016-06-30|||1|1|1|1|1|1|1
U|H|I||All
C|H|I||All|
L|H|I|LUSA|USA|
P|I|I|||1|23002G3
P|I|I|||1|11066278
P|I|I|||1|11066279
V|PromotionPct|-10|
V|PriceType||
V|PriceCode|2|
V|EventType|A|
V|ReasonCode|A|
V|Country|USA|
V|DataType||
V|BasedOn|2|
V|OverrideAll||
LB|5012|100|R
LB|5501|100|R
I||||||LUSA-100|100|5012|2016-06-01|2016-06-30|1|76074 32|||123.456|USD
I||||||LUSA-100|100|5012|2016-06-01|2016-06-30|1|23002G3|||1234.567|USD
I||||||LUSA-100|100|5012|2016-06-01|2016-06-30|1|23002G3|RED|11066278|1200|USD
I||||||LUSA-100|100|5012|2016-06-01|2016-06-30|1|23002G3|RED|11066279|1200|USD
I||||||LUSA-100|100|5501|2016-06-01|2016-06-30|1|23002G3|||1234.567|USD
I||||||LUSA-100|100|5501|2016-06-01|2016-06-30|1|23002G3|RED|11066278|1200|USD
I||||||LUSA-100|100|5501|2016-06-01|2016-06-30|1|23002G3|RED|11066279|1200|USD""".split("\n")

        for line in lines:
            self.c.process_line(line)

        self.assertRaises(Exception, self.c.process_line, "abcd|invalid line")

    def test_that_adjustment_fields_are_valid(self):
        lines = """A|A25E3EE9AFA248A79DF07D2565410784||Back to school 10% off||Promotion % Off
D|Pen|Back to school|
S|2016-06-01|2016-06-30|||1|1|1|1|1|1|1
U|H|I||All
C|H|I||All|
L|H|I|LUSA|USA|
P|I|I|||1|23002G3
P|I|I|||1|11066278
P|I|I|||1|11066279
V|PromotionPct|-10|
V|PriceType||
V|PriceCode|2|
V|EventType|A|
V|ReasonCode|A|
V|Country||
V|DataType||
V|BasedOn|2|
V|OverrideAll||
LB|5012|100|R
LB|5501|100|R
I||||||LUSA-100|100|5012|2016-06-01|2016-06-30|1|76074 32|||123.456|USD
I||||||LUSA-100|100|5012|2016-06-01|2016-06-30|1|23002G3|||1234.567|USD
I||||||LUSA-100|100|5012|2016-06-01|2016-06-30|1|23002G3|RED|11066278|1200|USD
I||||||LUSA-100|100|5012|2016-06-01|2016-06-30|1|23002G3|RED|11066279|1200|USD
I||||||LUSA-100|100|5501|2016-06-01|2016-06-30|1|23002G3|||1234.567|USD
I||||||LUSA-100|100|5501|2016-06-01|2016-06-30|1|23002G3|RED|11066278|1200|USD
I||||||LUSA-100|100|5501|2016-06-01|2016-06-30|1|23002G3|RED|11066279|1200|USD""".split("\n")

        for line in lines:
            self.c.process_line(line)

        a = self.c.current_adjustment
        self.assertRaises(Exception, a.validate_country)

class TestAdjustment(TestCase):

    def setUp(self):
        self.a = Adjustment("A25E3EE9AFA248A79DF07D2565410784", "", "Back to school 10% off", "", "Promotion % Off")

    # def test_ajustment_can_be_created(self):
    #     pass

    def test_adjustment_oid(self):
        self.assertEqual(self.a.oid, "A25E3EE9AFA248A79DF07D2565410784")

    def test_adjustment_name(self):
        self.assertEqual(self.a.name, "Back to school 10% off")

    def test_adjustment_external_id(self):
        self.assertEqual(self.a.external_id, "")

    def test_adjustment_event(self):
        self.assertEqual(self.a.event, "")

    def test_adjustment_rule_name(self):
        self.assertEqual(self.a.rule_name, "Promotion % Off")


class TestAdjustmentDescription(TestCase):

    def setUp(self):
        self.d = AdjustmentDescription("Pen", "Back to school", "")

    # def test_adjustment_description_can_be_created(self):
    #     pass

    def test_adjustment_description_language_id(self):
        self.assertEqual(self.d.language_id, "Pen")

    def test_adjustment_description_text(self):
        self.assertEqual(self.d.description, "Back to school")


    def test_adjustment_description_image(self):
        self.assertEqual(self.d.image, "")

class TestAdjustmentSchedule(TestCase):

    def test_adjustment_schedule(self):
        fields = "S|2016-06-01|2016-06-30|||1|1|1|1|1|1|1".split("|")[1:]
        a = AdjustmentSchedule(*fields)

        d_start = datetime.datetime.strptime(fields[0], a.INPUT_DATE_FORMAT)
        d_start = datetime.date.strftime(d_start, a.EXPORT_FORMATS["USA"])
        self.assertEqual(a.start_date(), d_start)

        d_end = datetime.datetime.strptime(fields[1], a.INPUT_DATE_FORMAT)
        d_end = datetime.date.strftime(d_end, a.EXPORT_FORMATS["USA"])
        self.assertEqual(a.end_date(), d_end)

        self.assertEqual(a.start_time, "")
        self.assertEqual(a.duration, "")
        self.assertEqual(a.mon, "1")
        self.assertEqual(a.tue, "1")
        self.assertEqual(a.wed, "1")
        self.assertEqual(a.thu, "1")
        self.assertEqual(a.fri, "1")
        self.assertEqual(a.sat, "1")
        self.assertEqual(a.sun, "1")

    def test_schedule_date_with_unsupported_country(self):
        fields = "S|2016-06-01|2016-06-30|||1|1|1|1|1|1|1".split("|")[1:]
        a = AdjustmentSchedule(*fields)
        self.assertRaises(KeyError, a.start_date, "FIN")

class TestUserHierarchy(TestCase):

    def test_user_hierarchy_node(self):
        fields = "U|H|I||All".split("|")[1:]
        u = UserHierarchyNode(*fields)

        self.assertEqual(u.node_type, "H")
        self.assertEqual(u.hierarchy_oid, "")
        self.assertEqual(u.hierarchy_name, "All")

class TestCustomerHierarchy(TestCase):

    def test_customer_hierarchy_node(self):
        fields = "C|H|I||All|".split("|")[1:]
        c = CustomerHierarchyNode(*fields)

        self.assertEqual(c.node_type, "H")
        self.assertEqual(c.hierarchy_oid, "")
        self.assertEqual(c.hierarchy_name, "All")

class TestLocationHierarchy(TestCase):

    def test_location_hierarchy_node(self):
        fields = "L|H|I|LUSA|USA|".split("|")[1:]
        l = LocationHierarchyNode(*fields)

        self.assertEqual(l.node_type, "H")
        self.assertEqual(l.hierarchy_oid, "LUSA")
        self.assertEqual(l.hierarchy_name, "USA")
        self.assertEqual(l.location_external_id, "")

class TestProductHierarchy(TestCase):

    def test_product_hierarchy_node(self):
        fields = "P|I|I|||1|23002G3".split("|")[1:]
        p = ProductHierarchyNode(*fields)

        self.assertEqual(p.node_type, "I")
        self.assertEqual(p.hierarchy_oid, "")
        self.assertEqual(p.hierarchy_name, "")
        self.assertEqual(p.product_group_id, "1")
        self.assertEqual(p.item_name, "23002G3")

class TestAdjustmentParameters(TestCase):

    def test_product_hierarchy_node(self):
        fields = "V|PromotionPct|-10|".split("|")[1:]
        p = AdjustmentParameters(*fields)

        self.assertEqual(p.name, "PromotionPct")
        self.assertEqual(p.value, "-10")
        self.assertEqual(p.currency, "")

class TestLocationBusiness(TestCase):

    def test_location_business(self):
        fields = "LB|5012|100|R".split("|")[1:]
        l = LocationBusiness(*fields)

        self.assertEqual(l.external_id, "5012")
        self.assertEqual(l.pricing_zone, "100")
        self.assertEqual(l.business_unit, "R")

class TestItemPrice(TestCase):

    def test_item_price(self):
        fields = "I||||||LUSA-100|100|5012|2016-06-01|2016-06-30|1|76074 32|||123.456|USD".split("|")[1:]
        p = ItemPrice(*fields)

        self.assertEqual(p.user_hierarchy_oid, "")
        self.assertEqual(p.user_hierarchy_name, "")
        self.assertEqual(p.customer_hierarchy_oid, "")
        self.assertEqual(p.customer_hierarchy_name, "")
        self.assertEqual(p.customer_external_id, "")
        self.assertEqual(p.location_hierarchy_oid, "LUSA-100")
        self.assertEqual(p.location_hierarchy_name, "100")
        self.assertEqual(p.location_external_id, "5012")
        self.assertEqual(p.start_date, "2016-06-01")
        self.assertEqual(p.end_date, "2016-06-30")
        self.assertEqual(p.product_group_id, "1")
        self.assertEqual(p.item_style_code, "76074 32")
        self.assertEqual(p.item_color, "")
        self.assertEqual(p.variant_item_name, "")
        self.assertEqual(p.item_price, "123.456")
        self.assertEqual(p.currency, "USD")
