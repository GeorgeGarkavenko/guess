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
        self.assertEqual(h_vals[9], "2016-06-01")  # StartDate
        self.assertEqual(h_vals[10], "2016-06-30")  # EndDate
        self.assertEqual(h_vals[11], "")  # % Off, never used

    def test_location_business_row(self):
        a = self.c.current_adjustment
        l = a.get_location_business_map()

        row = ["L"] + [lb for lb in l[1]]
        self.assertListEqual(row, ["L", "5012", "5501"])

    def test_pricing_events(self):
        a = self.c.current_adjustment
        events = a.get_pricing_events()
        self.assertEqual(1, len(events)) # up to 25 locations for event -> only one event

        # add third business and set event max=2. 3/2 should return two L rows: 1st with two LBs and 2nd with one
        a.location_business["1111"] = LocationBusiness("1111", "100", "R")
        a._MAX_EVENT_LOCATIONS = 2
        events = a.get_pricing_events()
        self.assertEqual(2, len(events))

        # compare two events: only difference should be in locations

        e1, e2 = events
        self.assertEqual(e1.headers, e2.headers)
        self.assertEqual(e1.headers, e2.headers)
        self.assertEqual(e1.items, e2.items)
        self.assertNotEqual(e1.name, e2.name)
        self.assertNotEqual(e1.locations, e2.locations)

    def test_pricing_event_export(self):
        a = self.c.current_adjustment
        event = a.get_pricing_events()[0]
        rows = event.get_export_rows()

        self.assertEqual(len(rows), 2+1+1+7) # headers(2), location row, item header, 7 items

        event.export_tab_delimited()

    def test_process_file(self):
        import os
        test_file = os.path.join('test', 'adjustment_mega_test.txt')
        with open(test_file, 'r') as f:
            for line in f.readlines():
                pass
                #print line
                self.c.process_line(line.rstrip())
        l = self.c.current_adjustment.get_pricing_events()
        for e in l:
            e.export_tab_delimited()
#        print "XXXXXXX", len(l)
