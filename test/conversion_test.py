import os
from unittest import TestCase

from app.adjustment import Adjustment, AdjustmentDescription, UserHierarchyNode, CustomerHierarchyNode, \
    LocationHierarchyNode, ProductHierarchyNode, AdjustmentParameters, LocationBusiness, ItemPrice, AdjustmentSchedule
from app.controller import ExportController


class TestExportController(TestCase):

    def setUp(self):
        self.c = ExportController()
        self.c._item_info_file = os.path.join('test', 'item_info.txt')

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

    def test_header(self):
        a = self.c.current_adjustment
        h_names, h_vals = a.get_header()
        self.assertEqual(len(h_names), len(h_vals))

        self.assertEqual(h_vals[0], "H")
        self.assertEqual(h_vals[1], "Back to school 10% off") # Description
        self.assertEqual(h_vals[2], "2")  # PriceCode
        self.assertEqual(h_vals[3], "A")  # EventType
        self.assertEqual(h_vals[4], "A")  # ReasonCode
        self.assertEqual(h_vals[5], "USA")  # Country
        self.assertEqual(h_vals[6], "")  # DataType
        self.assertEqual(h_vals[7], "2")  # BasedOn
        self.assertEqual(h_vals[8], "")  # OverrideAll
        self.assertEqual(h_vals[9], "06/01/2016")  # StartDate USA format
        self.assertEqual(h_vals[10], "06/30/2016")  # EndDate USA format
        self.assertEqual(h_vals[11], "")  # % Off, never used

    def test_location_business_row(self):
        a = self.c.current_adjustment
        l = a.get_location_business_map(a.location_business.keys())
        row = ["L"] + [lb for lb in l[1]]
        self.assertListEqual(row, ["L", "5012", "5501"])

        # add third business and set event max=2. 3/2 should return two L rows: 1st with two LBs and 2nd with one
        a.location_business["1111"] = LocationBusiness("1111", "100", "R")
        a._MAX_EVENT_LOCATIONS = 2

        l = a.get_location_business_map(a.location_business.keys())
        row = ["L"] + [lb for lb in l[1]]
        self.assertListEqual(row, ["L", "1111", "5012"])

        row = ["L"] + [lb for lb in l[2]]
        self.assertListEqual(row, ["L", "5501"])

    def test_pricing_events(self):
        a = self.c.current_adjustment
        events = a.get_pricing_events()
        self.assertEqual(2, len(events)) # 2 events as two locations share same 3 items and one location has one extra

    def test_pricing_event_export(self):
        a = self.c.current_adjustment
        e1, e2 = a.get_pricing_events() # 1st event: 1 loc, 1 item; 2nd event: 2 locs, 3 items
        rows = e1.get_export_rows()
        self.assertEqual(len(rows), 2+1+1+3) # headers(2), location row, item header, 3 items

        rows = e2.get_export_rows()
        self.assertEqual(len(rows), 2 + 1 + 1 + 2)  # headers(2), location row, item header, 2 items

    def test_process_file(self):
        import os
        test_file = os.path.join('test', 'adjustment_mega_test.txt')
        self.c.process_file(test_file)
        # how to verify results?
