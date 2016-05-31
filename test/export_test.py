from unittest import TestCase

from app.adjustment import Adjustment


class TestAdjustment(TestCase):

    def setUp(self):
        self.a = Adjustment()

    def test_ajustment_can_be_created(self):
        pass

    def test_adjustment_oid(self):
        oid = self.a.get_oid()


    def test_adjustment_description(self):
        d = self.a.get_description()
        self.assertEqual(d, "", "Adjustment description is emtpy string")