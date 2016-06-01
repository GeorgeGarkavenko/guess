from unittest import TestCase

from app.adjustment import Adjustment, AdjustmentDescription, AdjustmentSchedule


class ExportController(object):

    def __init__(self):
        self.current_adjustment_oid = None
        self.adjustments = {}

    DATA_TYPES = {
        "A" : "add_adjustment",
        "D" : "add_description",
        # "S" : "schedule",
        # "U" : "user_node",
        # "C" : "customer_node",
        # "L" : "location_node",
        # "P" : "product_hierarchy_node",
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


class TestExportController(TestCase):

    def setUp(self):
        self.c = ExportController()

    def test_add_adjustment(self):
        fields = "A|A25E3EE9AFA248A79DF07D2565410784||Back to school 10% off||Promotion % Off".split("|")[1:]
        self.c.add_adjustment(fields)
        self.assertEqual(self.c.current_adjustment_oid, "A25E3EE9AFA248A79DF07D2565410784")

        a = self.c.get_current_adjustment()
        self.assertEqual(a.external_id, "")
        self.assertEqual(a.name, "Back to school 10% off")
        self.assertEqual(a.event, "")
        self.assertEqual(a.rule_name, "Promotion % Off")

    def test_add_adjustment_description(self):
        fields = "A|A25E3EE9AFA248A79DF07D2565410784||Back to school 10% off||Promotion % Off".split("|")[1:]
        self.c.add_adjustment(fields)

        fields = "D|Pen|Back to school|".split("|")[1:]
        self.c.add_description(fields)

        a = self.c.get_current_adjustment()
        self.assertEqual(a.descriptions[fields[0]].description, "Back to school")

    def test_add_adjustment_schedule(self):
        fields = "A|A25E3EE9AFA248A79DF07D2565410784||Back to school 10% off||Promotion % Off".split("|")[1:]
        self.c.add_adjustment(fields)

        fields = "S|2016-06-01|2016-06-30||||1|1|1|1|1|1|1".split("|")[1:]
        self.c.add_schedule(fields)

        a = self.c.get_current_adjustment()
        self.assertEqual(a.schedule.start_date, "2016-06-01")
        self.assertEqual(a.schedule.end_date, "2016-06-30")
        self.assertEqual(a.schedule.start_time, "")
        self.assertEqual(a.schedule.end_time, "")
        self.assertEqual(a.schedule.duration, "")
        self.assertEqual(a.schedule.mon, "1")
        self.assertEqual(a.schedule.tue, "1")
        self.assertEqual(a.schedule.wed, "1")
        self.assertEqual(a.schedule.thu, "1")
        self.assertEqual(a.schedule.fri, "1")
        self.assertEqual(a.schedule.sat, "1")
        self.assertEqual(a.schedule.sun, "1")

        print a.schedule

    def test_line_processing(self):

        lines = """A|A25E3EE9AFA248A79DF07D2565410784||Back to school 10% off||Promotion % Off
D|Pen|Back to school|
S|2016-06-01|2016-06-30||||1|1|1|1|1|1|1
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
