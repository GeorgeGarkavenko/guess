from unittest import TestCase

from app.adjustment import Adjustment, AdjustmentDescription, UserHierarchyNode, CustomerHierarchyNode, \
    LocationHierarchyNode, ProductHierarchyNode, AdjustmentParameters, LocationBusiness
from app.controller import ExportController


class TestExportController(TestCase):

    def setUp(self):
        self.c = ExportController()

    def test_add_adjustment(self):
        fields = "A|A25E3EE9AFA248A79DF07D2565410784||Back to school 10% off||Promotion % Off".split("|")[1:]
        self.c.add_adjustment(fields)
        self.assertEqual(self.c._current_adjustment_oid, "A25E3EE9AFA248A79DF07D2565410784")

        a = self.c.current_adjustment
        self.assertEqual(a.external_id, "")
        self.assertEqual(a.name, "Back to school 10% off")
        self.assertEqual(a.event, "")
        self.assertEqual(a.rule_name, "Promotion % Off")

    def test_add_adjustment_description(self):
        fields = "A|A25E3EE9AFA248A79DF07D2565410784||Back to school 10% off||Promotion % Off".split("|")[1:]
        self.c.add_adjustment(fields)

        fields = "D|Pen|Back to school|".split("|")[1:]
        self.c.add_description(fields)

        a = self.c.current_adjustment
        self.assertEqual(a.descriptions[fields[0]].description, "Back to school")

    def test_add_adjustment_schedule(self):
        fields = "A|A25E3EE9AFA248A79DF07D2565410784||Back to school 10% off||Promotion % Off".split("|")[1:]
        self.c.add_adjustment(fields)

        fields = "S|2016-06-01|2016-06-30|||1|1|1|1|1|1|1".split("|")[1:]
        self.c.add_schedule(fields)

        a = self.c.current_adjustment
        self.assertEqual(a.schedule.start_date, "2016-06-01")
        self.assertEqual(a.schedule.end_date, "2016-06-30")
        self.assertEqual(a.schedule.start_time, "")
        self.assertEqual(a.schedule.duration, "")
        self.assertEqual(a.schedule.mon, "1")
        self.assertEqual(a.schedule.tue, "1")
        self.assertEqual(a.schedule.wed, "1")
        self.assertEqual(a.schedule.thu, "1")
        self.assertEqual(a.schedule.fri, "1")
        self.assertEqual(a.schedule.sat, "1")
        self.assertEqual(a.schedule.sun, "1")

    def test_add_user_hierarchy_node(self):
        fields = "A|A25E3EE9AFA248A79DF07D2565410784||Back to school 10% off||Promotion % Off".split("|")[1:]
        self.c.add_adjustment(fields)

        fields = "U|H||All".split("|")[1:]
        self.c.add_user_hierarchy_node(fields)

        user_node = self.c.current_adjustment.hierarchy["U"][0]
        self.assertIsInstance(user_node, UserHierarchyNode)

        self.assertEqual(user_node.node_type, "H")
        self.assertEqual(user_node.hierarchy_oid, "")
        self.assertEqual(user_node.hierarchy_name, "All")

    def test_add_customer_hierarchy_node(self):
        fields = "A|A25E3EE9AFA248A79DF07D2565410784||Back to school 10% off||Promotion % Off".split("|")[1:]
        self.c.add_adjustment(fields)

        fields = "C|H||All|".split("|")[1:]
        self.c.add_customer_hierarchy_node(fields)

        customer_node = self.c.current_adjustment.hierarchy["C"][0]
        self.assertIsInstance(customer_node, CustomerHierarchyNode)

        self.assertEqual(customer_node.node_type, "H")
        self.assertEqual(customer_node.hierarchy_oid, "")
        self.assertEqual(customer_node.hierarchy_name, "All")


    def test_add_location_hierarchy_node(self):
        fields = "A|A25E3EE9AFA248A79DF07D2565410784||Back to school 10% off||Promotion % Off".split("|")[1:]
        self.c.add_adjustment(fields)

        fields = "L|H|LUSA-100|100|".split("|")[1:]
        self.c.add_location_hierarchy_node(fields)

        location_node = self.c.current_adjustment.hierarchy["L"][0]
        self.assertIsInstance(location_node, LocationHierarchyNode)

        self.assertEqual(location_node.node_type, "H")
        self.assertEqual(location_node.hierarchy_oid, "LUSA-100")
        self.assertEqual(location_node.hierarchy_name, "100")
        self.assertEqual(location_node.location_external_id, "")

        self.assertIsInstance(self.c.current_adjustment.hierarchy["L"][0], LocationHierarchyNode)

    def test_add_product_hierarchy_node(self):
        fields = "A|A25E3EE9AFA248A79DF07D2565410784||Back to school 10% off||Promotion % Off".split("|")[1:]
        self.c.add_adjustment(fields)

        fields = "P|I|||1|76074 32".split("|")[1:]
        self.c.add_product_hierarchy_node(fields)

        a = self.c.current_adjustment
        product_node = a.hierarchy["P"][0]
        self.assertIsInstance(product_node, ProductHierarchyNode)

        self.assertEqual(product_node.node_type, "I")
        self.assertEqual(product_node.hierarchy_oid, "")
        self.assertEqual(product_node.hierarchy_name, "")
        self.assertEqual(product_node.product_group_id, "1")
        self.assertEqual(product_node.item_name, "76074 32")

        fields = "P|I|||1|11066279".split("|")[1:]
        self.c.add_product_hierarchy_node(fields)
        self.assertEqual(2, len(a.hierarchy["P"]))

    def test_add_adjustment_parameters(self):
        fields = "A|A25E3EE9AFA248A79DF07D2565410784||Back to school 10% off||Promotion % Off".split("|")[1:]
        self.c.add_adjustment(fields)

        fields = "V|PromotionPct|-10|".split("|")[1:]
        self.c.add_parameters(fields)

        a = self.c.current_adjustment
        p = a.parameters[0]

        self.assertIsInstance(p, AdjustmentParameters)
        self.assertEqual(p.name, "PromotionPct")
        self.assertEqual(p.value, "-10")
        self.assertEqual(p.currency, "")

        fields = "V|ReasonCode|A|".split("|")[1:]
        self.c.add_parameters(fields)
        self.assertEqual(2, len(a.parameters))

    def test_add_location_business(self):
        fields = "A|A25E3EE9AFA248A79DF07D2565410784||Back to school 10% off||Promotion % Off".split("|")[1:]
        self.c.add_adjustment(fields)

        fields = "LB|5012|100|R".split("|")[1:]
        self.c.add_location_business(fields)

        a = self.c.current_adjustment
        l = a.location_business[0]

        self.assertIsInstance(l, LocationBusiness)
        self.assertEqual(l.external_id, "5012")
        self.assertEqual(l.pricing_zone, "100")
        self.assertEqual(l.business_unit, "R")

        fields = "LB|5501|100|R".split("|")[1:]
        self.c.add_location_business(fields)
        self.assertEqual(2, len(a.location_business))

    def test_line_processing(self):

        lines = """A|A25E3EE9AFA248A79DF07D2565410784||Back to school 10% off||Promotion % Off
D|Pen|Back to school|
S|2016-06-01|2016-06-30|||1|1|1|1|1|1|1
U|H||All
C|H||All|
L|H|LUSA-100|100|
P|I|||1|76074 32
P|I|||1|23002G3
P|I|||1|11066278
P|I|||1|11066279
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
            a = self.c.process_line(line)

        try:
            self.c.process_line("abcd|invalid line")
        except Exception:
            pass

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
