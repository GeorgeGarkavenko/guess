import os
from unittest import TestCase

from app.adjustment import Adjustment, AdjustmentDescription, UserHierarchyNode, CustomerHierarchyNode, \
    LocationHierarchyNode, ProductHierarchyNode, AdjustmentParameters, LocationBusiness, ItemPrice, AdjustmentSchedule
from app.controller import ExportController


class TestExportController(TestCase):

    def setUp(self):
        self.c = ExportController()
        self.c._item_info_file = os.path.join('test', 'item_info.txt')
        self.c._store_info_file = os.path.join('test', 'store_info.txt')

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
        self.assertEqual(len(rows), 2+1+1+2) # headers(2), location row, item header, 2 items (1 filtered)

        rows = e2.get_export_rows()
        self.assertEqual(len(rows), 2 + 1 + 1 + 1)  # headers(2), location row, item header, 1 item (1 filtered)

    def test_process_file(self):
        import os
        test_file = os.path.join('test', 'adjustment_mega_test.txt')
        self.c.process_file(test_file)
        # how to verify results?

class TestExportLocationController(TestCase):

    def test_location_business_store_to_zone_merge(self):

        '''If event contains all stores from a zone -> replace store list with zone'''

        self.c = ExportController()
        self.c._item_info_file = os.path.join('test', 'item_info.txt')
        self.c._store_info_file = os.path.join('test', 'store_info.txt')

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
LB|6588|300|R
I||||||LUSA-100|100|5012|2016-06-01|2016-06-30|1|76074 32|||123.456|USD
I||||||LUSA-300|300|6588|2016-06-01|2016-06-30|1|23002G3|||1234.567|USD
I||||||LUSA-300|300|6588|2016-06-01|2016-06-30|1|23002G3|RED|11066278|1200|USD
I||||||LUSA-300|300|6588|2016-06-01|2016-06-30|1|23002G3|RED|11066279|1200|USD
I||||||LUSA-100|100|5012|2016-06-01|2016-06-30|1|23002G3|||1234.567|USD
I||||||LUSA-100|100|5012|2016-06-01|2016-06-30|1|23002G3|RED|11066278|1200|USD
I||||||LUSA-100|100|5012|2016-06-01|2016-06-30|1|23002G3|RED|11066279|1200|USD
I||||||LUSA-100|100|5501|2016-06-01|2016-06-30|1|23002G3|||1234.567|USD
I||||||LUSA-100|100|5501|2016-06-01|2016-06-30|1|23002G3|RED|11066278|1200|USD
I||||||LUSA-100|100|5501|2016-06-01|2016-06-30|1|23002G3|RED|11066279|1200|USD""".split("\n")

        for line in lines:
            self.c.process_line(line)

        # ok, now we have three stores and 5501+5012 form zone 100 so instead of
        # having them both in the event file we'll see only 100 (and then 6588 too
        # as that's not part of zone 100)

        a = self.c.current_adjustment
        e = a.get_pricing_events()[1] # second event has our zone 100 and store 6588

        self.assertListEqual(e.locations, ["100", "6588"])

    def test_location_with_zone_only(self):

        '''If event contains all stores from a zone -> replace store list with zone'''

        self.c = ExportController()
        self.c._item_info_file = os.path.join('test', 'item_info.txt')
        self.c._store_info_file = os.path.join('test', 'store_info.txt')

        lines = """A|5D3DA9128AE34D4BA9250D31D07499F7|5D3DA9128AE34D4BA9250D31D07499F7|BM RC 60% 5013+|BM RC 60% 5013+|Promotion %
S|2016-08-10|2016-08-15|||1|1|1|1|1|1|1
U|H|I||
C|H|I|||
L|H|I|LUSA-100|100|
P|H|I|P6-725-875|875 MN Beach||
P|H|I|P6-715-820|820 WM Sandals||
P|H|I|P6-715-825|825 WM Beach||
P|H|I|P6-725-870|870 MN Sandals||
V|PromotionPct|60|
V|PriceType|CLR|
V|PriceCode|Store|
V|EventType|A|
V|ReasonCode|B|
V|Country|USA|
V|DataType|I|
V|BasedOn||
V|OverrideAll|No|
V|PctOff||
I||||||LUSA-100|100||2016-08-10|2016-08-15|1|PRETZEL|||63.98|USD
I||||||LUSA-100|100||2016-08-10|2016-08-15|1|PRETZEL||11413408|767.62|USD
I||||||LUSA-100|100||2016-08-10|2016-08-15|1|SLIP|||63.98|USD
I||||||LUSA-100|100||2016-08-10|2016-08-15|1|SLIP||11355852|1151.42|USD
I||||||LUSA-100|100||2016-08-10|2016-08-15|1|GWKIRBY|||143.90|USD
I||||||LUSA-100|100||2016-08-10|2016-08-15|1|GWKIRBY||11507739|2591.42|USD
I||||||LUSA-100|100||2016-08-10|2016-08-15|1|GWKIRBY||11507745|1727.62|USD""".split("\n")

        for line in lines:
            self.c.process_line(line)

        # this adjustment does not have stores at all, check that events can use zone 100 for location

        a = self.c.current_adjustment
        e = a.get_pricing_events()[0]
        location_row = e.get_export_rows()[2]
        location = location_row[1]
        self.assertEqual(location, "100")

    def test_adjustment_with_empty_schedule(self):

        self.c = ExportController()
        self.c._item_info_file = os.path.join('test', 'item_info.txt')
        self.c._store_info_file = os.path.join('test', 'store_info.txt')

        lines = """A|5D3DA9128AE34D4BA9250D31D07499F7|5D3DA9128AE34D4BA9250D31D07499F7|BM RC 60% 5013+|BM RC 60% 5013+|Promotion %
U|H|I||
C|H|I|||
L|H|I|LUSA-100|100|
P|H|I|P6-725-875|875 MN Beach||
P|H|I|P6-715-820|820 WM Sandals||
P|H|I|P6-715-825|825 WM Beach||
P|H|I|P6-725-870|870 MN Sandals||
V|PromotionPct|60|
V|PriceType|CLR|
V|PriceCode|Store|
V|EventType|A|
V|ReasonCode|B|
V|Country|USA|
V|DataType|I|
V|BasedOn||
V|OverrideAll|No|
V|PctOff||
I||||||LUSA-100|100||2016-08-10|2016-08-15|1|PRETZEL|||63.98|USD
I||||||LUSA-100|100||2016-08-10|2016-08-15|1|PRETZEL||11413408|767.62|USD
I||||||LUSA-100|100||2016-08-10|2016-08-15|1|SLIP|||63.98|USD
I||||||LUSA-100|100||2016-08-10|2016-08-15|1|SLIP||11355852|1151.42|USD
I||||||LUSA-100|100||2016-08-10|2016-08-15|1|GWKIRBY|||143.90|USD
I||||||LUSA-100|100||2016-08-10|2016-08-15|1|GWKIRBY||11507739|2591.42|USD
I||||||LUSA-100|100||2016-08-10|2016-08-15|1|GWKIRBY||11507745|1727.62|USD""".split("\n")

        for line in lines:
            self.c.process_line(line)

        # this adjustment has no schedule so validate function should assign a default schedule

        a = self.c.current_adjustment
        a.get_pricing_events()[0]

        self.assertIsNotNone(a.schedule)
        #location_row = e.get_export_rows()[2]
        #location = location_row[1]
        #self.assertEqual(location, "100")
