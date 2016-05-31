from unittest import TestCase


class Adjustment(object):
    def get_oid(self):
        pass


class TestAdjustment(TestCase):
    def test_ajustment_can_be_created(self):
        a = Adjustment()

    def test_adjustment_oid(self):
        a = Adjustment()
        oid = a.get_oid()