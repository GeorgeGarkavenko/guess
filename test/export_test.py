from unittest import TestCase


class Adjustment(object):
    def get_oid(self):
        pass


class TestAdjustment(TestCase):

    def setUp(self):
        self.a = Adjustment()

    def test_ajustment_can_be_created(self):
        pass

    def test_adjustment_oid(self):
        oid = self.a.get_oid()