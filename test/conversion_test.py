from unittest import TestCase

from app.adjustment import Adjustment, AdjustmentDescription, UserHierarchyNode, CustomerHierarchyNode, \
    LocationHierarchyNode, ProductHierarchyNode, AdjustmentParameters, LocationBusiness, ItemPrice, AdjustmentSchedule
from app.controller import ExportController


class TestExportController(TestCase):

    def setUp(self):
        self.c = ExportController()

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
            self.c.process_line(line)

    def test_header(self):
        a = self.c.current_adjustment
        h = a.get_header()

        self.assertEqual(h[0][1], "H")
        self.assertEqual(h[1][1], "Back to school 10% off") # Description
        self.assertEqual(h[2][1], "2")  # PriceCode
        self.assertEqual(h[3][1], "A")  # EventType
        self.assertEqual(h[4][1], "A")  # ReasonCode
        self.assertEqual(h[5][1], "USA")  # Country
        self.assertEqual(h[6][1], "")  # DataType
        self.assertEqual(h[7][1], "2")  # BasedOn
        self.assertEqual(h[8][1], "")  # OverrideAll
        self.assertEqual(h[9][1], "2016-06-01")  # StartDate
        self.assertEqual(h[10][1], "2016-06-30")  # EndDate

